# Configuração do Llama 3.1 8B-Instruct

## Instalação e Configuração

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente

Copie o arquivo `env_example.txt` para `.env` e configure as variáveis:

```bash
cp env_example.txt .env
```

Edite o arquivo `.env` com suas configurações:

```env
# Configurações obrigatórias
SUPABASE_URL=sua_url_do_supabase
SUPABASE_KEY=sua_chave_do_supabase

# Configurações opcionais do Llama
LLAMA_MODEL_NAME=meta-llama/Llama-3.1-8B-Instruct
LLAMA_DEVICE=auto
LLAMA_MAX_TOKENS=512
LLAMA_TEMPERATURE=0.2
LLAMA_USE_QUANTIZATION=true
LLAMA_QUANTIZATION_CONFIG=4bit
```

### 3. Testar a Instalação

```bash
python test_llama.py
```

## Requisitos de Hardware

### Mínimo Recomendado:
- **RAM:** 8GB (com quantização 4bit)
- **GPU:** Opcional, mas recomendada (NVIDIA com 6GB+ VRAM)
- **Armazenamento:** 16GB livres

### Configurações por Hardware:

#### CPU Only (8GB RAM):
```env
LLAMA_DEVICE=cpu
LLAMA_USE_QUANTIZATION=true
LLAMA_QUANTIZATION_CONFIG=4bit
```

#### GPU NVIDIA (6GB+ VRAM):
```env
LLAMA_DEVICE=cuda
LLAMA_USE_QUANTIZATION=true
LLAMA_QUANTIZATION_CONFIG=4bit
```

#### GPU NVIDIA (12GB+ VRAM):
```env
LLAMA_DEVICE=cuda
LLAMA_USE_QUANTIZATION=false
```

## Uso

### Importar e Usar:

```python
from llama_client import simplify_text

# Uso assíncrono
result = await simplify_text("Texto jurídico aqui...")

# Uso síncrono
from llama_client import LlamaClient
client = LlamaClient()
result = client.simplify_text("Texto jurídico aqui...")
```

### Estrutura da Resposta:

```python
{
    "what_happened": "Resumo do que aconteceu",
    "what_it_means": "Explicação do significado",
    "what_to_do_now": "Próximos passos"
}
```

## Troubleshooting

### Erro de Memória Insuficiente:
- Ative quantização 4bit: `LLAMA_USE_QUANTIZATION=true`
- Reduza max_tokens: `LLAMA_MAX_TOKENS=256`
- Use CPU: `LLAMA_DEVICE=cpu`

### Erro de Download do Modelo:
- Verifique conexão com internet
- O modelo será baixado automaticamente na primeira execução (~16GB)

### Performance Lenta:
- Use GPU se disponível
- Desative quantização se tiver VRAM suficiente
- Aumente max_tokens para respostas mais completas

## Comparação com OpenAI

| Aspecto | OpenAI GPT-4o | Llama 3.1 8B |
|---------|---------------|---------------|
| Custo | $0.03/1K tokens | Gratuito |
| Privacidade | Dados enviados | Dados locais |
| Customização | Limitada | Total |
| Performance | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Português | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

## Próximos Passos

1. **Fine-tuning:** Treinar modelo específico para texto jurídico
2. **Otimização:** Implementar cache de respostas
3. **Monitoramento:** Adicionar métricas de performance
4. **Backup:** Implementar modelo alternativo (Mistral/Qwen)
