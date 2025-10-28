# IADvogado - Sistema de IA para Simplificação de Documentos Jurídicos

## Estrutura do Projeto

```
iadvogado/
├── api/                    # Endpoints da API FastAPI
│   ├── __init__.py
│   └── main.py            # Aplicação principal FastAPI
├── config/                 # Configurações do sistema
│   ├── __init__.py
│   ├── config.py          # Settings usando Pydantic
│   └── env_example.txt    # Exemplo de variáveis de ambiente
├── core/                   # Modelos de dados e estruturas core
│   ├── __init__.py
│   └── models.py          # Modelos Pydantic
├── services/               # Serviços de IA, OCR e TTS
│   ├── __init__.py
│   ├── llama_client.py    # Cliente Llama 3.1 para simplificação
│   ├── llm_client.py      # Cliente OpenAI (legacy)
│   ├── edge_tts_worker.py # Text-to-Speech usando Edge TTS
│   ├── tts_worker.py      # Worker TTS (legacy)
│   └── ocr_worker.py      # OCR usando Pytesseract
├── integrations/           # Integrações externas
│   ├── __init__.py
│   └── whatsapp_adapter.py # Integração com WhatsApp
├── storage/                # Camada de persistência
│   ├── __init__.py
│   └── storage.py          # Integração com Supabase
├── utils/                  # Utilitários e funções auxiliares
│   ├── __init__.py
│   └── utils.py           # Funções auxiliares
├── __init__.py            # Pacote principal
├── run.py                 # Ponto de entrada da aplicação
└── requirements.txt       # Dependências Python
```

## Funcionalidades

### 🤖 IA e Processamento de Texto
- **Llama 3.1 8B**: Simplificação de documentos jurídicos usando modelo local
- **OCR**: Extração de texto de imagens usando Pytesseract
- **TTS**: Conversão de texto em áudio usando Microsoft Edge TTS

### 📱 Integrações
- **WhatsApp**: Envio de respostas via WhatsApp
- **Supabase**: Armazenamento de dados e histórico

### 🔧 Configuração
- Configuração via variáveis de ambiente
- Suporte a diferentes provedores de IA
- Cache inteligente para TTS

## Como Executar

1. **Instalar dependências**:
```bash
pip install -r requirements.txt
```

2. **Configurar variáveis de ambiente**:
```bash
cp config/env_example.txt .env
# Editar .env com suas configurações
```

3. **Executar a aplicação**:
```bash
python run.py
```

## Endpoints da API

- `POST /upload` - Upload e processamento de documentos
- `POST /process-number` - Processamento por número do processo
- `GET /health` - Health check geral
- `GET /health/tts` - Health check específico do TTS
- `GET /tts/metrics` - Métricas de performance do TTS
- `GET /tts/cache/info` - Informações do cache
- `POST /tts/cache/clear` - Limpar cache

## Tecnologias Utilizadas

- **FastAPI**: Framework web moderno e rápido
- **Llama 3.1**: Modelo de linguagem local
- **Edge TTS**: Text-to-Speech da Microsoft
- **Pytesseract**: OCR para extração de texto
- **Supabase**: Backend-as-a-Service
- **Pydantic**: Validação de dados
