"""
Agente Validador
================

Responsabilidade: Avaliar se o resultado do Executor atende ao objetivo original.

CONCEITO — O PAPEL DO VALIDADOR
    Controle de qualidade. Sem ele, qualquer resultado passaria.
    Com ele, o sistema ganha AUTO-CORREÇÃO via loop de feedback.

FASE 5 — O QUE MUDOU?
    - Logging estruturado com métricas
    - Tratamento de erros
    - Log de WARNING quando parsing falha (fail-safe)
"""

import re
import time

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from src.config.settings import GROQ_API_KEY, MODEL_NAME, MODEL_TEMPERATURE
from src.config.prompts import VALIDATOR_PROMPT
from src.config.logging_config import get_logger
from src.state.agent_state import AgentState

logger = get_logger("validator")


def build_validator_llm() -> ChatGroq:
    """Cria a LLM do Validador (temperatura baixa para consistência)."""
    return ChatGroq(
        model=MODEL_NAME,
        temperature=0.3,
        api_key=GROQ_API_KEY,
    )


def parse_approval(response_text: str) -> bool:
    """
    Extrai a decisão de aprovação do texto do Validador.
    Fail-safe: se não encontrar o padrão, rejeita.
    """
    match = re.search(r"APROVADO:\s*(sim|não|nao|yes|no)", response_text, re.IGNORECASE)

    if match:
        value = match.group(1).lower()
        approved = value in ("sim", "yes")
        logger.debug(f"Parsing encontrou 'APROVADO: {value}' -> {approved}")
        return approved

    logger.warning("Parsing nao encontrou padrao 'APROVADO: sim/nao' — usando fail-safe (reprovado)")
    return False


def validator_node(state: AgentState) -> dict:
    """
    Nó do Validador no grafo LangGraph.

    Recebe: Estado com 'objective', 'plan' e 'result' preenchidos
    Retorna: {"feedback": "...", "is_approved": bool, "history": [...]}
    """
    iteration = state.get("iteration", 1)
    logger.info(f"Iniciando avaliacao (iteracao {iteration})")

    # Monta o prompt
    prompt = VALIDATOR_PROMPT.format(
        objective=state["objective"],
        plan=state["plan"],
        result=state["result"],
        iteration=iteration,
        max_iterations=state.get("max_iterations", 3),
    )

    # Chama a LLM com tratamento de erros
    try:
        llm = build_validator_llm()
        start_time = time.time()

        response = llm.invoke([
            SystemMessage(content=prompt),
            HumanMessage(content="Avalie o resultado produzido."),
        ])

        elapsed = time.time() - start_time
        feedback = response.content

        logger.info(f"Avaliacao gerada em {elapsed:.2f}s ({len(feedback)} chars)")

    except Exception as e:
        logger.error(f"Erro ao chamar LLM: {e}", exc_info=True)
        feedback = f"[ERRO] Falha na validação: {str(e)}\nAPROVADO: não"

    # Extrai a decisão
    is_approved = parse_approval(feedback)
    status = "APROVADO" if is_approved else "REPROVADO"
    logger.info(f"Decisao: {status}")

    # Atualiza o histórico
    history = state.get("history", [])
    status_icon = "APROVADO ✓" if is_approved else "REPROVADO ✗"
    history = history + [
        f"[Iteração {iteration}] Validador: {status_icon}\n{feedback[:300]}..."
    ]

    return {
        "feedback": feedback,
        "is_approved": is_approved,
        "history": history,
    }
