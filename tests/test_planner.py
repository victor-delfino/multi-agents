"""
Teste do Agente Planejador
==========================

Valida que o Planejador:
1. Retorna um plano quando recebe um objetivo
2. Atualiza o histórico corretamente
3. Incorpora feedback quando disponível
"""

import pytest

from src.agents.planner import planner_node


# Fixture: estado inicial padrão para testes
@pytest.fixture
def initial_state():
    return {
        "objective": "Criar um resumo sobre machine learning",
        "plan": "",
        "result": "",
        "feedback": "",
        "is_approved": False,
        "iteration": 1,
        "max_iterations": 3,
        "history": [],
    }


class TestPlannerNode:
    """Testes para o nó do Planejador."""

    def test_planner_returns_plan(self, initial_state):
        """O Planejador deve retornar um campo 'plan' não vazio."""
        result = planner_node(initial_state)
        assert "plan" in result
        assert len(result["plan"]) > 0

    def test_planner_returns_history(self, initial_state):
        """O Planejador deve adicionar uma entrada ao histórico."""
        result = planner_node(initial_state)
        assert "history" in result
        assert len(result["history"]) == 1
        assert "Planejador" in result["history"][0]

    def test_planner_does_not_return_unexpected_fields(self, initial_state):
        """O Planejador deve retornar APENAS 'plan' e 'history'."""
        result = planner_node(initial_state)
        expected_keys = {"plan", "history"}
        assert set(result.keys()) == expected_keys

    def test_planner_handles_feedback(self, initial_state):
        """Na iteração 2+, o Planejador deve processar feedback anterior."""
        initial_state["iteration"] = 2
        initial_state["feedback"] = "O plano anterior era vago demais. Seja mais específico."
        result = planner_node(initial_state)
        assert "plan" in result
        assert len(result["plan"]) > 0
