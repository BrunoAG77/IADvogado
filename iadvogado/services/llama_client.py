import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from typing import Dict
import json
import re
from ..config.config import settings
import logging
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LlamaClient:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = self._get_device()
        self.model_loaded = False
        self.load_error = None
        # Não carrega o modelo imediatamente - lazy loading
        # self._load_model()  # Removido - será carregado quando necessário
    
    def _get_device(self):
        """Determina o melhor dispositivo disponível"""
        if torch.cuda.is_available():
            return "cuda"
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"
    
    def _get_quantization_config(self):
        """Configura quantização para economizar memória"""
        if not settings.llama_use_quantization:
            return None
            
        if settings.llama_quantization_config == "4bit":
            return BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
            )
        elif settings.llama_quantization_config == "8bit":
            return BitsAndBytesConfig(
                load_in_8bit=True,
            )
        return None
    
    def _ensure_model_loaded(self):
        """Garante que o modelo está carregado (lazy loading)"""
        if self.model_loaded:
            return True
        
        if self.load_error:
            raise RuntimeError(f"Modelo não pode ser carregado: {self.load_error}")
        
        return self._load_model()
    
    def _load_model(self):
        """Carrega o modelo Llama 3.1 8B"""
        try:
            logger.info(f"Carregando modelo {settings.llama_model_name}...")
            
            # Verificar token do Hugging Face
            hf_token = (
                os.getenv("HUGGING_FACE_HUB_TOKEN") or 
                os.getenv("HF_TOKEN") or 
                settings.hugging_face_hub_token
            )
            if not hf_token:
                logger.warning(
                    "⚠️ Token do Hugging Face não encontrado!\n"
                    "Para usar o modelo Llama 3.1, você precisa:\n"
                    "1. Acessar https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct\n"
                    "2. Aceitar os termos de uso\n"
                    "3. Criar um token em https://huggingface.co/settings/tokens\n"
                    "4. Definir a variável de ambiente: HUGGING_FACE_HUB_TOKEN=seu_token\n"
                    "Ou adicionar no .env: HUGGING_FACE_HUB_TOKEN=seu_token"
                )
                raise RuntimeError(
                    "Token do Hugging Face necessário. "
                    "Defina HUGGING_FACE_HUB_TOKEN ou HF_TOKEN no ambiente."
                )
            
            # Configurar tokenizer com autenticação
            tokenizer_kwargs = {
                "trust_remote_code": True,
            }
            if hf_token:
                tokenizer_kwargs["token"] = hf_token
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                settings.llama_model_name,
                **tokenizer_kwargs
            )
            
            # Configurar quantização
            quantization_config = self._get_quantization_config()
            
            # Carregar modelo com autenticação
            model_kwargs = {
                "trust_remote_code": True,
                "torch_dtype": torch.float16 if self.device != "cpu" else torch.float32,
            }
            
            if hf_token:
                model_kwargs["token"] = hf_token
            
            if quantization_config:
                model_kwargs["quantization_config"] = quantization_config
                model_kwargs["device_map"] = "auto"
            else:
                model_kwargs["device_map"] = {"": self.device}
            
            self.model = AutoModelForCausalLM.from_pretrained(
                settings.llama_model_name,
                **model_kwargs
            )
            
            # Configurar padding token se necessário
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            logger.info(f"Modelo carregado com sucesso no dispositivo: {self.device}")
            self.model_loaded = True
            return True
            
        except RuntimeError as e:
            # Erro de autenticação ou configuração
            self.load_error = str(e)
            logger.error(f"Erro ao carregar modelo: {e}")
            raise
        except Exception as e:
            # Outros erros
            error_msg = str(e)
            self.load_error = error_msg
            
            # Verificar se é erro de autenticação
            if "gated" in error_msg.lower() or "401" in error_msg or "unauthorized" in error_msg.lower():
                logger.error(
                    f"\n{'='*60}\n"
                    f"❌ ERRO DE AUTENTICAÇÃO NO HUGGING FACE\n"
                    f"{'='*60}\n"
                    f"O modelo Llama 3.1 requer autenticação.\n\n"
                    f"Para resolver:\n"
                    f"1. Acesse: https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct\n"
                    f"2. Aceite os termos de uso\n"
                    f"3. Crie um token em: https://huggingface.co/settings/tokens\n"
                    f"4. Configure o token:\n"
                    f"   - Windows PowerShell: $env:HUGGING_FACE_HUB_TOKEN='seu_token'\n"
                    f"   - Linux/Mac: export HUGGING_FACE_HUB_TOKEN='seu_token'\n"
                    f"   - Ou adicione no .env: HUGGING_FACE_HUB_TOKEN=seu_token\n"
                    f"{'='*60}\n"
                )
            else:
                logger.error(f"Erro ao carregar modelo: {e}")
            
            raise RuntimeError(f"Não foi possível carregar o modelo: {error_msg}")
    
    def _create_prompt(self, text: str) -> str:
        """Cria prompt otimizado para simplificação de texto jurídico"""
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

Você é um assistente especializado em traduzir documentos jurídicos brasileiros para linguagem clara e acessível. Sua tarefa é simplificar textos jurídicos complexos em três blocos específicos.

Responda APENAS com um JSON válido contendo as seguintes chaves:
- "what_happened": Resumo do que aconteceu no processo/documento
- "what_it_means": Explicação do que isso significa em linguagem simples
- "what_to_do_now": Orientações sobre próximos passos

Use linguagem clara, evite jargões jurídicos e seja objetivo.<|eot_id|><|start_header_id|>user<|end_header_id|>

Simplifique este texto jurídico:

{text}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
        return prompt
    
    def simplify_text(self, text: str) -> Dict[str, str]:
        """Simplifica texto jurídico usando Llama 3.1"""
        try:
            # Carregar modelo se ainda não foi carregado (lazy loading)
            if not self.model_loaded:
                self._ensure_model_loaded()
            
            # Verificar se o modelo está disponível
            if self.model is None or self.tokenizer is None:
                logger.warning("Modelo não disponível, usando fallback")
                return self._fallback_response(text)
            
            prompt = self._create_prompt(text)
            
            # Tokenizar entrada
            inputs = self.tokenizer(
                prompt, 
                return_tensors="pt", 
                truncation=True, 
                max_length=2048,
                padding=True
            )
            
            # Mover para o dispositivo correto
            if self.device != "cpu":
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Gerar resposta
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=settings.llama_max_tokens,
                    temperature=settings.llama_temperature,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                )
            
            # Decodificar resposta
            response = self.tokenizer.decode(
                outputs[0][inputs['input_ids'].shape[1]:], 
                skip_special_tokens=True
            ).strip()
            
            # Tentar extrair JSON da resposta
            parsed_response = self._parse_response(response)
            
            return parsed_response
            
        except RuntimeError as e:
            # Erro de carregamento do modelo
            logger.error(f"Erro ao simplificar texto: {e}")
            return self._fallback_response(text)
        except Exception as e:
            logger.error(f"Erro ao simplificar texto: {e}")
            # Fallback para resposta estruturada manual
            return self._fallback_response(text)
    
    def _parse_response(self, response: str) -> Dict[str, str]:
        """Tenta extrair JSON da resposta do modelo"""
        try:
            # Limpar resposta e extrair JSON
            response = response.strip()
            
            # Tentar encontrar JSON na resposta
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed = json.loads(json_str)
                
                # Validar se tem as chaves necessárias
                required_keys = ['what_happened', 'what_it_means', 'what_to_do_now']
                if all(key in parsed for key in required_keys):
                    return {
                        'what_happened': parsed['what_happened'].strip(),
                        'what_it_means': parsed['what_it_means'].strip(),
                        'what_to_do_now': parsed['what_to_do_now'].strip(),
                    }
            
            # Se não conseguir extrair JSON, usar parsing manual
            return self._manual_parse(response)
            
        except Exception as e:
            logger.warning(f"Erro ao fazer parse da resposta: {e}")
            return self._manual_parse(response)
    
    def _manual_parse(self, response: str) -> Dict[str, str]:
        """Parse manual da resposta quando JSON falha"""
        # Dividir resposta em seções baseado em palavras-chave
        sections = {
            'what_happened': '',
            'what_it_means': '',
            'what_to_do_now': ''
        }
        
        # Padrões para identificar seções
        patterns = {
            'what_happened': r'(o que aconteceu|what happened|aconteceu|ocorreu)',
            'what_it_means': r'(o que significa|what it means|significa|implica)',
            'what_to_do_now': r'(o que fazer|what to do|próximos passos|agora)'
        }
        
        # Dividir texto em parágrafos
        paragraphs = [p.strip() for p in response.split('\n') if p.strip()]
        
        current_section = 'what_happened'
        
        for paragraph in paragraphs:
            paragraph_lower = paragraph.lower()
            
            # Verificar se parágrafo indica nova seção
            for section, pattern in patterns.items():
                if re.search(pattern, paragraph_lower):
                    current_section = section
                    break
            
            # Adicionar parágrafo à seção atual
            if sections[current_section]:
                sections[current_section] += ' ' + paragraph
            else:
                sections[current_section] = paragraph
        
        return sections
    
    def _fallback_response(self, text: str) -> Dict[str, str]:
        """Resposta de fallback quando o modelo falha"""
        return {
            'what_happened': f"Documento jurídico analisado: {text[:100]}...",
            'what_it_means': "Este é um documento jurídico que requer análise profissional. Recomenda-se consultar um advogado para interpretação adequada.",
            'what_to_do_now': "Procure a Defensoria Pública ou um advogado para orientação específica sobre este caso."
        }

# Instância global do cliente (lazy loading - não carrega o modelo imediatamente)
llama_client = LlamaClient()

# Função de compatibilidade com o código existente
async def simplify_text(text: str) -> Dict[str, str]:
    """Função assíncrona para compatibilidade com o código existente"""
    return llama_client.simplify_text(text)
