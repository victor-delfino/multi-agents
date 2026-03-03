"""
Orquestrador (Roteador Condicional)
====================================

Responsabilidade: Decidir se o fluxo termina ou volta ao Planejador.

FASE 5 — O QUE MUDOU?
    - print() substituído por logging estruturado
    - Log de decisão com contexto (iteração, motivo)
"""

from src.config.logging_config import get_logger
from src.state.agent_state import AgentState

logger = get_logger("orchestrator")


def should_continue(state: AgentState) -> str:
    """
    Função de roteamento do Orquestrador.
    Retorna "end" ou "planejador".
    """
    iteration = state.get("iteration", 1)
    max_iterations = state.get("max_iterations", 3)

    # Caso 1: Aprovado → Finaliza
    if state.get("is_approved", False):
        logger.info(f"APROVADO na iteracao {iteration} — finalizando")
        return "end"

    # Caso 2: Limite atingido → Finaliza
    if iteration >= max_iterations:
        logger.warning(f"Limite de {max_iterations} iteracoes atingido sem aprovacao — finalizando")
        return "end"

    # Caso 3: Reprovado, ainda há tentativas → Retry
    logger.info(f"REPROVADO na iteracao {iteration}/{max_iterations} — reenviando ao Planejador")
    return "planejador"


def increment_iteration(state: AgentState) -> dict:
    """
    Nó auxiliar que incrementa o contador de iterações.
    Sem LLM — apenas modifica estado.
    """
    new_iteration = state.get("iteration", 1) + 1
    logger.info(f"Incrementando iteracao: {new_iteration - 1} -> {new_iteration}")
    return {
        "iteration": new_iteration,
    }
