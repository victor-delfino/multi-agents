"""
Agente Validador
================

Responsabilidade: Avaliar se o resultado do Executor atende ao objetivo original.

CONCEITO — O PAPEL DO VALIDADOR NO SISTEMA

    O Validador é o "controle de qualidade" do sistema. Sem ele, qualquer 
    resultado passaria — bom ou ruim. Com ele, o sistema ganha a capacidade
    de AUTO-CORREÇÃO: se o resultado não é bom, o Validador rejeita e o 
    fluxo volta ao Planejador com feedback específico.

    Isso cria um loop de melhoria:
    
    Iteração 1: Plano genérico → Resultado raso → Validador rejeita
    Iteração 2: Plano ajustado (com feedback) → Resultado melhor → Validador aprova

    É o mesmo princípio de code review:
    - Desenvolvedor escreve código (Executor)
    - Reviewer avalia (Validador)
    - Se reprovado, dev corrige (Planejador replaneja)

DECISÃO DE DESIGN — PARSING DO OUTPUT

    O Validador precisa retornar dados ESTRUTURADOS (is_approved, feedback).
    Mas a LLM retorna texto livre. Precisamos fazer parsing.

    Alternativas:
    1. JSON mode da LLM → Mais confiável, mas nem todo modelo suporta bem
    2. Parsing com regex → Simples, funciona com qualquer modelo
    3. Output parser do LangChain → Mais robusto, mais complexo

    Escolhemos regex (opção 2) por ser:
    - Transparente (você vê exatamente o que acontece)
    - Educativo (mostra o problema real de parsing de LLMs)
    - Resistente a variações de formato
"""

import re

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from src.config.settings import GROQ_API_KEY, MODEL_NAME, MODEL_TEMPERATURE
from src.config.prompts import VALIDATOR_PROMPT
from src.state.agent_state import AgentState


def build_validator_llm() -> ChatGroq:
    """
    Cria a instância da LLM usada pelo Validador.

    Nota: Usamos temperatura MAIS BAIXA para o Validador.
    Por quê? Queremos avaliações consistentes e previsíveis.
    Se o Validador for "criativo", pode aprovar um resultado ruim
    ou reprovar um bom — dependendo do "humor" da LLM.
    """
    return ChatGroq(
        model=MODEL_NAME,
        temperature=0.3,  # Mais baixa que os outros agentes — queremos consistência
        api_key=GROQ_API_KEY,
    )


def parse_approval(response_text: str) -> bool:
    """
    Extrai a decisão de aprovação do texto do Validador.

    Procura por "APROVADO: sim" ou "APROVADO: não" no texto.
    Se não encontrar, assume NÃO aprovado (fail-safe).

    CONCEITO — FAIL-SAFE vs FAIL-OPEN:
        - Fail-safe: na dúvida, rejeita (mais qualidade, mais iterações)
        - Fail-open: na dúvida, aprova (menos iterações, menos qualidade)
        Escolhemos fail-safe porque preferimos gastar uma iteração extra
        do que entregar um resultado ruim.
    """
    # Procura "APROVADO: sim" (case insensitive)
    match = re.search(r"APROVADO:\s*(sim|não|nao|yes|no)", response_text, re.IGNORECASE)

    if match:
        value = match.group(1).lower()
        return value in ("sim", "yes")

    # Se não encontrou o padrão, fail-safe: não aprovado
    return False


def validator_node(state: AgentState) -> dict:
    """
    Nó do Validador no grafo LangGraph.

    Recebe: Estado com 'objective', 'plan' e 'result' preenchidos
    Retorna: {"feedback": "...", "is_approved": bool, "history": [...]}

    IMPORTANTE: Este nó depende do Executor ter rodado antes.
    O grafo garante isso via a aresta Executor → Validador.
    """
    # 1. Monta o prompt com os dados do estado
    prompt = VALIDATOR_PROMPT.format(
        objective=state["objective"],
        plan=state["plan"],
        result=state["result"],
        iteration=state.get("iteration", 1),
        max_iterations=state.get("max_iterations", 3),
    )

    # 2. Chama a LLM
    llm = build_validator_llm()
    response = llm.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content="Avalie o resultado produzido."),
    ])

    feedback = response.content

    # 3. Extrai a decisão de aprovação do texto
    is_approved = parse_approval(feedback)

    # 4. Atualiza o histórico
    history = state.get("history", [])
    iteration = state.get("iteration", 1)
    status = "APROVADO ✓" if is_approved else "REPROVADO ✗"
    history = history + [
        f"[Iteração {iteration}] Validador: {status}\n{feedback[:300]}..."
    ]

    # 5. Retorna os campos que este nó modifica
    return {
        "feedback": feedback,
        "is_approved": is_approved,
        "history": history,
    }
