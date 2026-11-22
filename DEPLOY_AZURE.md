# Deploy no Azure — guia para alunos

Este guia coloca **a sua própria cópia** do agente no ar, em um Azure Web
App só seu. O GitHub Actions chama o workflow de deploy após build, testes e
evals passarem na `main`. Configure o Azure e os secrets do seu fork
nos passos abaixo.

---

## Passo 1 — Fork

Faça um fork deste repositório para a sua conta do GitHub e clone o fork
(não o original).

## Passo 2 — Criar o Azure Web App

No [Azure Portal](https://portal.azure.com):

1. **Create a resource → Web App**
2. Runtime stack: **Python 3.11**
3. Operating System: **Linux**
4. Pricing plan: **Free F1** (suficiente para uma demo)
5. Criar

## Passo 3 — Configurar variáveis do app

No recurso criado, vá em **Configuration → Application settings** e
adicione:

| Nome | Valor |
|---|---|
| `OPENAI_API_KEY` | sua chave da OpenAI (nunca vai para o Git) |
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | `true` |

A segunda é o que faz o Azure instalar o `requirements.txt` automaticamente
a cada deploy (via Oryx).

## Passo 4 — Configurar o Startup Command

Ainda em **Configuration → General settings**, campo **Startup Command**:

```
python -m streamlit run app.py --server.port 8000 --server.address 0.0.0.0
```

Sem isso o Azure não sabe como iniciar um app Streamlit.

## Passo 5 — Habilitar a autenticação básica e baixar o Publish Profile

Apps novos vêm com a autenticação básica **desligada**. Sem ela, o botão de
download do publish profile fica desabilitado e o deploy falha com erro 401.

Em **Configuration → General settings**, ligue (**On**):

- **SCM Basic Auth Publishing Credentials**
- **FTP Basic Auth Publishing Credentials**

Clique em **Save**. Ou, pelo Azure CLI:

```bash
az resource update -g <rg> --namespace Microsoft.Web \
  --resource-type basicPublishingCredentialsPolicies \
  --parent sites/<nome-do-seu-app> -n scm --set properties.allow=true
```

Depois, na página **Overview** do Web App, clique em **Download publish profile**.
Guarde o arquivo — você vai colar o conteúdo dele no próximo passo.

## Passo 6 — Configurar secrets no seu fork

No GitHub, no seu fork: **Settings → Secrets and variables → Actions → New
repository secret**. Cadastre os segredos de deploy e da API.

| Nome do secret | Valor |
|---|---|
| `AZURE_WEBAPP_NAME` | o nome que você deu ao Web App |
| `AZURE_WEBAPP_PUBLISH_PROFILE` | conteúdo completo do arquivo baixado no passo 5 |
| `OPENAI_API_KEY` | chave da API usada pelo smoke e pelos evals do CI |

## Passo 7 — Deploy

Faça um `git push` na `main` ou abra **Actions → CI → Run workflow** e
selecione a `main`. Após os testes e evals, o CI chama **Deploy Azure** e
verifica `/_stcore/health` no app publicado. O
[plano de testes](PLANO_TESTES.md) descreve a demonstração de falha controlada.

## Passo 8 — Acessar

No portal do Azure, abra **Visão geral** e clique no **Domínio padrão** do
Web App. A etapa de deploy também exibe a URL do aplicativo.

---

## Problemas comuns

| Sintoma | Causa provável |
|---|---|
| Tela em branco / erro genérico do Azure | Faltou configurar o Startup Command (passo 4) |
| `OPENAI_API_KEY não encontrada` na tela do app | Faltou o Application Setting `OPENAI_API_KEY` (passo 3), ou o nome está escrito errado |
| A validação de secrets falha no GitHub Actions | Confira os nomes e valores dos secrets no fork (passo 6) |
| Deploy falha com `401 Unauthorized` na Action, ou o botão *Download publish profile* está desabilitado | Autenticação básica desligada no Web App (passo 5) |
| Build falha nos logs do Azure, pacotes não encontrados | Faltou `SCM_DO_BUILD_DURING_DEPLOYMENT=true` (passo 3) |
| Erro 401 dentro do app | Chave da OpenAI inválida ou expirada |
| Erro 429 dentro do app | Limite de cota da sua conta OpenAI — normal em uso intenso de aula |
