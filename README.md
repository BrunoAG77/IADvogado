# IADvogado

## Visão Geral

Justiça Simples é uma iniciativa tecnológica que busca democratizar o acesso à Justiça no Brasil por meio de Inteligência Artificial. A proposta consiste em um sistema capaz de traduzir documentos jurídicos — petições, decisões e andamentos processuais — em linguagem clara e acessível para a população.

A solução é acessível via WhatsApp e, futuramente, por meio de aplicativo dedicado, oferecendo respostas em formato texto e áudio para aumentar a inclusão de pessoas com baixa escolaridade, idosos e cidadãos com deficiência visual.

O projeto tem como foco principal reduzir as barreiras de entendimento que afastam os cidadãos de seus direitos, promovendo transparência e cidadania. Além disso, a iniciativa está alinhada aos seguintes Objetivos de Desenvolvimento Sustentável (ODS) da ONU:

- ODS 10 – Redução das Desigualdades  
- ODS 16 – Paz, Justiça e Instituições Eficazes  
- ODS 9 – Indústria, Inovação e Infraestrutura  

---

## Objetivos

- Democratizar a linguagem jurídica: tornar compreensíveis termos técnicos e documentos judiciais.  
- Ampliar a acessibilidade: oferecer opções de saída em texto e áudio.  
- Promover cidadania: garantir que os cidadãos compreendam os prazos, as etapas e as implicações de seus processos.  
- Suporte à Defensoria Pública e ONGs: fornecer uma ferramenta de apoio que fortaleça o atendimento a populações vulneráveis.

---

## Público-Alvo

- Cidadãos em ações simples (trabalhistas, previdenciárias, pequenas causas).  
- Usuários da Defensoria Pública.  
- Idosos, analfabetos funcionais e pessoas com deficiência visual.  
- Comunidades que enfrentam barreiras de acesso à linguagem jurídica.

---

## Funcionalidades do MVP

- Upload de documentos ou fornecimento de número do processo.  
- Tradução automática para linguagem acessível em três blocos principais:  
  1. O que aconteceu  
  2. O que significa  
  3. O que fazer agora  
- Retorno em texto no WhatsApp.  
- Geração opcional de áudio com explicação simplificada.  
- Inclusão de mensagens de responsabilidade e disclaimers legais.

---

## Arquitetura em Alto Nível

1. **Interação**: WhatsApp (usando API do tipo Evolution ou similar) como principal canal de comunicação.  
2. **Backend**: FastAPI em Python, com banco de dados Supabase/Postgres.  
3. **Processamento**:  
   - OCR para leitura de documentos;  
   - LLM para simplificação da linguagem jurídica;  
   - TTS para conversão em áudio.  
4. **Entrega**: resposta clara em texto e/ou áudio enviada ao usuário em ritmo rápido (por exemplo, em menos de dois minutos).

---

## Licença e Ética

- O projeto adota postura ética rigorosa e respeita os limites do exercício legal da advocacia. O sistema atua como tradutor popular e **não substitui advogados**.  
- Todos os dados processados estarão sujeitos à **Lei Geral de Proteção de Dados (LGPD)**, com exclusão periódica das informações e uso restrito ao propósito do serviço.  
- Licença sugerida: MIT ou AGPL, permitindo uso e expansão comunitária.

---

