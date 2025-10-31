# Chatbot IADvogado - Interface de Teste

Interface web para testar o funcionamento do IADvogado antes de integrar com WhatsApp.

## Como usar

1. **Inicie o servidor FastAPI:**
   ```bash
   python iadvogado/run.py
   ```

2. **Acesse no navegador:**
   - `http://localhost:8000/` (redireciona para o chatbot)
   - `http://localhost:8000/static/chatbot.html` (acesso direto)

3. **Teste o chatbot:**
   - Clique em "📎 Arquivo" para selecionar um documento (PDF, PNG, JPG)
   - Marque "Áudio" se quiser receber resposta em áudio
   - Clique em "Enviar"
   - Aguarde o processamento (OCR + IA + TTS)
   - Veja a resposta simplificada em 3 blocos

## Funcionalidades

- ✅ Upload de documentos (PDF, imagens)
- ✅ Visualização da resposta simplificada
- ✅ Geração e reprodução de áudio (opcional)
- ✅ Interface responsiva e moderna
- ✅ Feedback visual de processamento

## Notas

- A API deve estar rodando em `http://localhost:8000`
- Para mudar a URL da API, edite a variável `API_URL` em `chatbot.html`

