# Plano de testes do Agente Base

A equipe usou o Codex para revisar a suíte existente, propor casos adicionais e
ligar a publicação no Azure ao resultado dos testes. O código avaliado continua
sendo o Agente Base da disciplina.

## Prompt usado para elaborar o plano

> vamos fazer as sugestões menos o canary, inclusive até adicionar alguns testes a mais ne aproveitando esse
>
> “Teste – Devem ser realizados testes unitários e de eval. Utilize a IA para gerar esse plano. Apresente os prompts utilizados.”

As sugestões discutidas antes desse pedido eram bloquear o deploy quando um teste
falhasse, checar o aplicativo após a publicação e demonstrar o bloqueio com uma
falha controlada.

## Cenários e critérios de aprovação

| Camada | Cenário | Critério |
| --- | --- | --- |
| Build | Instalação, compilação e lint | Dependências instaladas, módulos Python compiláveis e Ruff sem erros |
| Unitário | Configuração do cliente | Chave ausente produz uma mensagem clara. Com chave fictícia, o teste confirma que o cliente é criado uma única vez usando um dublê. |
| Unitário | Contexto sem arquivo de memória | A identidade continua presente no prompt de sistema. |
| Contrato | Declaração e execução de ferramentas | Os parâmetros anunciados ao modelo correspondem à assinatura Python. |
| Run-level | Duas chamadas de ferramenta no mesmo turno | O agente registra os dois resultados na ordem correta e os associa aos respectivos IDs, usando um cliente simulado. |
| Smoke da API | Soma simples pelo agente | A API real retorna uma resposta com 6912 e o histórico registra o resultado da ferramenta somar. |
| Eval do agente | Soma com número negativo e soma decimal | A ferramenta produz o valor esperado e o modelo devolve o resultado numérico correto. O teste aceita vírgula ou ponto decimal. |
| Evals de persona | Ada, Val e Lint | A suíte existente checa as regras de tutoria, atendimento e precisão técnica de cada persona. |
| Pós-deploy | Endpoint de saúde do Streamlit | O endpoint responde HTTP 200 com corpo `ok` dentro da janela de tentativas. |
| Demonstração de falha | Caso temporário executado pelo pytest | O teste falha e o GitHub Actions pula os jobs dependentes, inclusive a publicação. |

## Prompts enviados ao agente

| Caso | Prompt | Resultado esperado |
| --- | --- | --- |
| Smoke | quanto é 1234 mais 5678? responda só o número | 6912 |
| Eval de inteiro negativo | Use a ferramenta somar para calcular -74 mais 19. Responda somente com o resultado numérico. | -55 |
| Eval decimal | Use a ferramenta somar para calcular 1,25 mais 2,5. Responda somente com o resultado numérico. | 3,75 |

O `agent.md` e o `memory.md` fornecem o contexto de sistema para esses três
casos. Os prompts das avaliações de Ada, Val e Lint estão no
[arquivo da suíte de personas](tests/test_personas.py).

## Como reproduzir

- **Pull request para `main`.** O CI executa build, unitários, contrato e
  run-level com dublês para os cenários que precisam de modelo.
- **Push em `main` ou execução manual do CI em `main`.** O GitHub executa os
  mesmos testes, soma o smoke e os evals com a API real e publica no Azure após
  a aprovação. A checagem HTTP do Streamlit fecha a execução.
- **Demonstração.** Em **Actions → CI → Run workflow**, selecione `main`,
  marque `simular_falha` e rode. O log de `test-unit` mostra a asserção que
  falhou por design. O job `deploy` deve aparecer como **Skipped**.
