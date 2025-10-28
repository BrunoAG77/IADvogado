# Configuração do Edge TTS - IADvogado

## 🚀 Instalação Rápida

### 1. Instalar Dependências

```bash
pip install edge-tts
```

### 2. Testar Instalação

```bash
python test_edge_tts_basic.py
```

### 3. Executar API

```bash
uvicorn main:app --reload
```

## 📋 Funcionalidades Implementadas

### ✅ **Fase 1 - Implementação Básica**

- **EdgeTTSWorker**: Classe principal para conversão de texto em áudio
- **Suporte a SSML**: Geração de áudio com qualidade profissional
- **Múltiplas Vozes**: Suporte a vozes brasileiras e portuguesas
- **Integração com /upload**: Endpoint atualizado para gerar áudio
- **Configuração Flexível**: Parâmetros personalizáveis via config.py

## 🎵 Vozes Disponíveis

### **Português Brasileiro (pt-BR)**
- **pt-BR-FranciscaNeural** (Feminina) - Padrão
- **pt-BR-AntonioNeural** (Masculina)
- **pt-BR-DanielNeural** (Masculina)
- **pt-BR-HeloisaNeural** (Feminina)
- **pt-BR-ManuelaNeural** (Feminina)

### **Português Português (pt-PT)**
- **pt-PT-RaquelNeural** (Feminina)
- **pt-PT-DuarteNeural** (Masculina)

## ⚙️ Configurações

### **config.py**
```python
# Configurações do Edge TTS
tts_provider: str = "edge"
tts_voice: str = "pt-BR-FranciscaNeural"
tts_rate: str = "+5%"  # Velocidade: -100% a +200%
tts_volume: str = "+0%"  # Volume: -100% a +100%
tts_pitch: str = "+2Hz"  # Tom: -100Hz a +100Hz
tts_use_ssml: bool = True  # Usar SSML para melhor qualidade
tts_cache_enabled: bool = True  # Cache de áudios
tts_cache_ttl: int = 3600  # TTL do cache em segundos
```

## 🔧 Uso Básico

### **Geração de Áudio Simples**
```python
from edge_tts_worker import text_to_speech_bytes

# Gerar áudio
audio_bytes = await text_to_speech_bytes("Seu texto aqui")
```

### **Geração com Parâmetros Personalizados**
```python
from edge_tts_worker import edge_tts_worker

# Gerar áudio com voz específica
audio_bytes = await edge_tts_worker.text_to_speech_bytes(
    text="Seu texto aqui",
    voice="pt-BR-AntonioNeural",
    rate="+10%",
    volume="+5%",
    pitch="+3Hz"
)
```

### **Listar Vozes Disponíveis**
```python
from edge_tts_worker import list_available_voices

# Listar vozes em português
voices = await list_available_voices("pt-BR")
for voice in voices:
    print(f"{voice['ShortName']}: {voice['FriendlyName']}")
```

## 📱 Integração com API

### **Endpoint /upload**
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@documento.pdf" \
  -F "as_audio=true" \
  -F "phone_number=+5511999999999"
```

### **Resposta**
```json
{
  "success": true,
  "text": "O que aconteceu: ...\nO que significa: ...\nO que fazer agora: ..."
}
```

## 🧪 Testes

### **Teste Básico**
```bash
python test_edge_tts_basic.py
```

### **Teste de Integração**
```bash
# Testar endpoint
curl -X POST "http://localhost:8000/upload" \
  -F "file=@teste.pdf" \
  -F "as_audio=true"
```

## 🔍 Troubleshooting

### **Problemas Comuns**

1. **Erro de instalação do edge-tts**
   ```bash
   pip install --upgrade edge-tts
   ```

2. **Voz não encontrada**
   ```python
   # Listar vozes disponíveis
   voices = await list_available_voices("pt-BR")
   print(voices)
   ```

3. **Áudio vazio gerado**
   - Verificar se o texto não está vazio
   - Testar com texto simples primeiro
   - Verificar logs de erro

4. **Erro de SSML**
   - Desabilitar SSML: `tts_use_ssml = False`
   - Verificar caracteres especiais no texto

### **Logs de Debug**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📊 Performance

### **Métricas Típicas**
- **Texto curto (50 chars)**: ~1-2 segundos
- **Texto médio (200 chars)**: ~3-5 segundos
- **Texto longo (500 chars)**: ~8-12 segundos

### **Otimizações**
- **Cache habilitado**: Reduz tempo de regeneração
- **SSML**: Melhora qualidade, aumenta tempo
- **Vozes neurais**: Melhor qualidade, mais recursos

## 🚀 Próximos Passos

### **Fase 2 - Otimizações**
1. Sistema de cache avançado
2. Compressão de áudio
3. Múltiplas vozes por usuário
4. Métricas de performance

### **Fase 3 - Integração WhatsApp**
1. Upload de mídia
2. Envio de áudio via WhatsApp
3. Fallbacks de erro
4. Notificações de status

## 💡 Dicas de Uso

1. **Para texto jurídico**: Use SSML habilitado
2. **Para performance**: Desabilite SSML se necessário
3. **Para qualidade**: Use vozes neurais
4. **Para economia**: Use cache habilitado
5. **Para acessibilidade**: Sempre inclua opção de áudio

## 📞 Suporte

- **Documentação**: [Edge TTS GitHub](https://github.com/rany2/edge-tts)
- **Issues**: Reportar problemas no repositório do projeto
- **Logs**: Verificar logs da aplicação para detalhes de erro
