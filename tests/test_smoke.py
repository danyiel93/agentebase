"""Smoke com a API real. No CI, roda na main antes dos evals e do deploy."""

import json
import os

import pytest

import agent

pytestmark = pytest.mark.smoke

requer_chave_real = pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="precisa de OPENAI_API_KEY de verdade — não roda no CI de PR por padrão",
)


@requer_chave_real
def test_agente_soma_de_verdade_via_ferramenta():
    mensagens = [
        {"role": "system", "content": agent.carregar_contexto()},
        {"role": "user", "content": "quanto é 1234 mais 5678? responda só o número"},
    ]

    resposta = agent.responder(mensagens)

    assert "6912" in resposta
    assert any(
        mensagem["role"] == "tool" and json.loads(mensagem["content"]) == {"resultado": 6912}
        for mensagem in mensagens
    )
