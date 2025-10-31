# 🔧 Configuração do Token do Hugging Face

## Problema Identificado

O modelo **Llama 3.1 8B-Instruct** é um repositório "gated" (protegido) no Hugging Face, o que significa que requer:
1. Aceitar os termos de uso
2. Autenticação com token

## Erro Encontrado

```
401 Client Error: Unauthorized
Cannot access gated repo for url https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct
Access to model meta-llama/Llama-3.1-8B-Instruct is restricted.
```

## ✅ Solução

### Passo 1: Obter Acesso ao Modelo

1. Acesse: https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct
2. Faça login (ou crie uma conta gratuita)
3. **Aceite os termos de uso** do modelo
4. Aguarde aprovação (geralmente instantânea)

### Passo 2: Criar Token de Acesso

1. Acesse: https://huggingface.co/settings/tokens
2. Clique em "New token"
3. Escolha um nome (ex: "IADvogado")
4. Selecione o tipo "Read" (leitura é suficiente)
5. Clique em "Generate token"
6. **Copie o token** (você só verá ele uma vez!)

### Passo 3: Configurar o Token

#### Opção A: Variável de Ambiente (Recomendado para desenvolvimento)

**Windows PowerShell:**
```powershell
$env:HUGGING_FACE_HUB_TOKEN="seu_token_aqui"
```

**Windows CMD:**
```cmd
set HUGGING_FACE_HUB_TOKEN=seu_token_aqui
```

**Linux/Mac:**
```bash
export HUGGING_FACE_HUB_TOKEN="seu_token_aqui"
```

#### Opção B: Arquivo .env (Recomendado para produção)

1. Crie um arquivo `.env` na **raiz do projeto** (`IADvogado/`)
2. Adicione:
```env
HUGGING_FACE_HUB_TOKEN=seu_token_aqui
```

3. O arquivo `.env` já está configurado para ser lido automaticamente

### Passo 4: Verificar Configuração

Após configurar, reinicie o servidor:
```bash
python run_server.py
```

O modelo será carregado automaticamente quando necessário (lazy loading).

## 🔍 Verificação

Para verificar se está funcionando:

1. Inicie o servidor (deve iniciar sem erros agora)
2. Faça uma requisição de upload de documento
3. Verifique os logs - deve aparecer "Carregando modelo..." na primeira requisição

## ⚠️ Notas Importantes

- O token é **confidencial** - não compartilhe publicamente
- Adicione `.env` ao `.gitignore` se usar Git
- O modelo só será carregado quando necessário (primeira requisição)
- Se o token não estiver configurado, o sistema usará fallback (respostas genéricas)

## 🆘 Fallback

Se o modelo não puder ser carregado (token inválido, sem acesso, etc.), o sistema:
- ✅ Continuará funcionando
- ✅ Usará respostas de fallback genéricas
- ✅ Não quebrará o servidor

## 📝 Alternativas (Sem Token)

Se você não quiser configurar o token agora, o sistema funcionará com respostas de fallback. Para testar o chatbot sem o modelo:

1. Execute o servidor normalmente
2. Faça upload de documentos
3. Receberá respostas genéricas mas estruturadas

Para usar IA real, configure o token conforme acima.

