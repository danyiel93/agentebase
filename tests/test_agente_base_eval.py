"""Evals que conferem o uso real de somar e o resultado mostrado ao usuário."""

import json
import os
import re
from decimal import Decimal

import pytest

import agent

pytestmark = [
    pytest.mark.eval,
    pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="Os evals do agente base precisam da API real da OpenAI.",
    ),
]


@pytest.mark.parametrize(
    ("pergunta", "esperado"),
    [
        pytest.param(
            "Use a ferramenta somar para calcular -74 mais 19. Responda somente com o resultado numérico.",
            -55,
            id="inteiro-negativo",
        ),
        pytest.param(
            "Use a ferramenta somar para calcular 1,25 mais 2,5. Responda somente com o resultado numérico.",
            3.75,
            id="decimal",
        ),
    ],
)
def test_soma_com_a_ferramenta_e_responde_o_resultado(pergunta, esperado):
    mensagens = [
        {"role": "system", "content": agent.carregar_contexto()},
        {"role": "user", "content": pergunta},
    ]

    resposta = agent.responder(mensagens)

    resultados_das_ferramentas = [
        json.loads(mensagem["content"])
        for mensagem in mensagens
        if mensagem["role"] == "tool"
    ]
    assert {"resultado": esperado} in resultados_das_ferramentas

    numeros = re.findall(r"-?\d+(?:[.,]\d+)?", resposta.replace("−", "-"))
    assert [Decimal(numero.replace(",", ".")) for numero in numeros] == [Decimal(str(esperado))]
