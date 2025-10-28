import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from typing import Dict
import json
import re
from ..config.config import settings
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LlamaClient:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = self._get_device()
        self._load_model()
    
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
    
    def _load_model(self):
        """Carrega o modelo Llama 3.1 8B"""
        try:
            logger.info(f"Carregando modelo {settings.llama_model_name}...")
            
            # Configurar tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                settings.llama_model_name,
                trust_remote_code=True
            )
            
            # Configurar quantização
            quantization_config = self._get_quantization_config()
            
            # Carregar modelo
            model_kwargs = {
                "trust_remote_code": True,
                "torch_dtype": torch.float16 if self.device != "cpu" else torch.float32,
            }
            
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
            
        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {e}")
            raise
    
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

# Instância global do cliente
llama_client = LlamaClient()

# Função de compatibilidade com o código existente
async def simplify_text(text: str) -> Dict[str, str]:
    """Função assíncrona para compatibilidade com o código existente"""
    return llama_client.simplify_text(text)
