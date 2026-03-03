"""
Agente Planejador
=================

Responsabilidade: Receber um objetivo e decompô-lo em passos concretos.

CONCEITO — O QUE É UM "NÓ" EM LANGGRAPH?
    Um nó é uma função Python que:
    1. Recebe o estado atual (AgentState)
    2. Faz seu trabalho (neste caso, chama a LLM)
    3. Retorna um dicionário com os campos que quer ATUALIZAR no estado

    O LangGraph faz o merge automático. O nó NÃO precisa retornar
    o estado inteiro — apenas os campos que mudaram.

POR QUE O PLANEJADOR EXISTE?
    Sem ele, o Executor receberia o objetivo bruto e tentaria resolver tudo
    de uma vez. O Planejador adiciona uma camada de RACIOCÍNIO ESTRATÉGICO.

FASE 5 — O QUE MUDOU?
    - Logging estruturado (em vez de silêncio ou print)
    - Tratamento de erros (se a API falhar, o sistema não crasha)
    - Métricas de tempo (quanto a LLM demorou)
"""

import time

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from src.config.settings import GROQ_API_KEY, MODEL_NAME, MODEL_TEMPERATURE
from src.config.prompts import PLANNER_PROMPT
from src.config.logging_config import get_logger
from src.state.agent_state import AgentState

logger = get_logger("planner")


def build_planner_llm() -> ChatGroq:
    """Cria a instância da LLM usada pelo Planejador."""
    return ChatGroq(
        model=MODEL_NAME,
        temperature=MODEL_TEMPERATURE,
        api_key=GROQ_API_KEY,
    )


def planner_node(state: AgentState) -> dict:
    """
    Nó do Planejador no grafo LangGraph.

    Recebe: Estado com 'objective' preenchido
    Retorna: {"plan": "...", "history": [...]}
    """
    iteration = state.get("iteration", 1)
    logger.info(f"Iniciando (iteracao {iteration})")
    logger.debug(f"Objetivo: {state['objective']}")

    # 1. Prepara o contexto de feedback (se houver iteração anterior)
    feedback_context = ""
    if state.get("feedback") and iteration > 1:
        feedback_context = (
            f"\n## Feedback da iteração anterior (IMPORTANTE — corrija os problemas!)\n"
            f"{state['feedback']}"
        )
        logger.info(f"Incorporando feedback da iteracao {iteration - 1}")

    # 2. Monta o prompt com os dados do estado
    prompt = PLANNER_PROMPT.format(
        objective=state["objective"],
        iteration=iteration,
        max_iterations=state.get("max_iterations", 3),
        feedback_context=feedback_context,
    )
    logger.debug(f"Prompt montado ({len(prompt)} chars)")

    # 3. Chama a LLM (com tratamento de erros e métricas)
    try:
        llm = build_planner_llm()
        start_time = time.time()

        response = llm.invoke([
            SystemMessage(content=prompt),
            HumanMessage(content=f"Crie o plano para: {state['objective']}"),
        ])

        elapsed = time.time() - start_time
        plan = response.content

        logger.info(f"Plano gerado em {elapsed:.2f}s ({len(plan)} chars)")
        logger.debug(f"Plano: {plan[:200]}...")

    except Exception as e:
        logger.error(f"Erro ao chamar LLM: {e}", exc_info=True)
        plan = f"[ERRO] Falha ao gerar plano: {str(e)}"

    # 4. Atualiza o histórico
    history = state.get("history", [])
    history = history + [f"[Iteração {iteration}] Planejador criou plano:\n{plan}"]

    return {
        "plan": plan,
        "history": history,
    }
