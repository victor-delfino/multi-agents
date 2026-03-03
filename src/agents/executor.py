"""
Agente Executor
===============

Responsabilidade: Receber um plano e executar cada passo, produzindo um resultado.

CONCEITO — COMO O EXECUTOR "SABE" O QUE FAZER?
    Ele NÃO sabe magicamente. Ele lê o campo 'plan' do estado compartilhado,
    que foi escrito pelo Planejador no nó anterior do grafo.

    Essa é a essência do padrão Blackboard:
    - O Planejador escreve: state["plan"] = "1. Pesquisar..."
    - O Executor lê:       plan = state["plan"]
    - Nenhum dos dois sabe que o outro existe

    Quem garante a ordem? O GRAFO. A aresta Planejador → Executor
    garante que quando o Executor rodar, o plano já estará escrito.

POR QUE O EXECUTOR EXISTE SEPARADO DO PLANEJADOR?
    Planejamento e execução são habilidades diferentes.
    - O Planejador pensa em ESTRATÉGIA (o quê fazer)
    - O Executor pensa em TÁTICA (como fazer)

    Separar permite:
    1. Trocar a estratégia sem mudar a execução (e vice-versa)
    2. Usar modelos diferentes (planejador com modelo analítico, executor com modelo criativo)
    3. Testar cada um isoladamente
    4. No futuro: paralelizar múltiplos executores
"""

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from src.config.settings import GROQ_API_KEY, MODEL_NAME, MODEL_TEMPERATURE
from src.config.prompts import EXECUTOR_PROMPT
from src.state.agent_state import AgentState


def build_executor_llm() -> ChatGroq:
    """
    Cria a instância da LLM usada pelo Executor.

    Nota: Usa o mesmo modelo do Planejador por enquanto.
    Em produção, você poderia usar um modelo diferente:
    - Planejador: modelo analítico (temperatura baixa)
    - Executor: modelo criativo (temperatura alta)
    """
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

    IMPORTANTE: Este nó DEPENDE do Planejador ter rodado antes.
    Se 'plan' estiver vazio, o Executor não terá instruções.
    O grafo garante essa ordem via a aresta Planejador → Executor.
    """
    # 1. Monta o prompt com os dados do estado
    prompt = EXECUTOR_PROMPT.format(
        objective=state["objective"],
        plan=state["plan"],
    )

    # 2. Chama a LLM
    llm = build_executor_llm()
    response = llm.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=f"Execute o plano para atingir o objetivo: {state['objective']}"),
    ])

    result = response.content

    # 3. Atualiza o histórico
    history = state.get("history", [])
    iteration = state.get("iteration", 1)
    history = history + [f"[Iteração {iteration}] Executor produziu resultado:\n{result[:200]}..."]

    # 4. Retorna APENAS os campos que este nó modifica
    return {
        "result": result,
        "history": history,
    }
