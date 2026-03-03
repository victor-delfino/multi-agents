"""
Agente Executor
===============

Responsabilidade: Receber um plano e executar cada passo, produzindo um resultado.

CONCEITO — COMO O EXECUTOR "SABE" O QUE FAZER?
    Ele lê o campo 'plan' do estado compartilhado (padrão Blackboard).
    O Planejador escreve. O Executor lê. Nenhum sabe do outro.

FASE 5 — O QUE MUDOU?
    - Logging estruturado com métricas de tempo
    - Tratamento de erros (API failures)
    - Validação de pré-condições (plan não pode estar vazio)
"""

import time

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from src.config.settings import GROQ_API_KEY, MODEL_NAME, MODEL_TEMPERATURE
from src.config.prompts import EXECUTOR_PROMPT
from src.config.logging_config import get_logger
from src.state.agent_state import AgentState

logger = get_logger("executor")


def build_executor_llm() -> ChatGroq:
    """Cria a instância da LLM usada pelo Executor."""
    return ChatGroq(
        model=MODEL_NAME,
        temperature=MODEL_TEMPERATURE,
        api_key=GROQ_API_KEY,
    )


def executor_node(state: AgentState) -> dict:
    """
    Nó do Executor no grafo LangGraph.

    Recebe: Estado com 'objective' e 'plan' preenchidos
    Retorna: {"result": "...", "history": [...]}
    """
    iteration = state.get("iteration", 1)
    logger.info(f"Iniciando (iteracao {iteration})")

    # Validação de pré-condição
    plan = state.get("plan", "")
    if not plan:
        logger.warning("Campo 'plan' vazio — executando sem plano estruturado")

    logger.debug(f"Plano recebido ({len(plan)} chars): {plan[:150]}...")

    # Monta o prompt
    prompt = EXECUTOR_PROMPT.format(
        objective=state["objective"],
        plan=plan,
    )

    # Chama a LLM com tratamento de erros
    try:
        llm = build_executor_llm()
        start_time = time.time()

        response = llm.invoke([
            SystemMessage(content=prompt),
            HumanMessage(content=f"Execute o plano para atingir o objetivo: {state['objective']}"),
        ])

        elapsed = time.time() - start_time
        result = response.content

        logger.info(f"Resultado gerado em {elapsed:.2f}s ({len(result)} chars)")
        logger.debug(f"Resultado: {result[:200]}...")

    except Exception as e:
        logger.error(f"Erro ao chamar LLM: {e}", exc_info=True)
        result = f"[ERRO] Falha ao executar plano: {str(e)}"

    # Atualiza o histórico
    history = state.get("history", [])
    history = history + [f"[Iteração {iteration}] Executor produziu resultado:\n{result[:200]}..."]

    return {
        "result": result,
        "history": history,
    }
