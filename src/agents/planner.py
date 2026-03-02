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

    Exemplo:
        Estado antes:  {"objective": "...", "plan": "", "result": ""}
        Retorno do nó: {"plan": "1. Pesquisar\n2. Escrever"}
        Estado depois: {"objective": "...", "plan": "1. Pesquisar\n2. Escrever", "result": ""}

POR QUE O PLANEJADOR EXISTE?
    Sem ele, o Executor receberia o objetivo bruto e tentaria resolver tudo
    de uma vez. O Planejador adiciona uma camada de RACIOCÍNIO ESTRATÉGICO:
    ele decide COMO resolver antes de resolver.

    Isso espelha como humanos trabalham:
    1. Entendo o problema (Planejador)
    2. Executo a solução (Executor)
    3. Verifico se ficou bom (Validador)
"""

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from src.config.settings import GROQ_API_KEY, MODEL_NAME, MODEL_TEMPERATURE
from src.config.prompts import PLANNER_PROMPT
from src.state.agent_state import AgentState


def build_planner_llm() -> ChatGroq:
    """
    Cria a instância da LLM usada pelo Planejador.

    Separar a criação da LLM permite:
    - Trocar o modelo facilmente (llama, mixtral, gemma)
    - Usar temperaturas diferentes por agente
    - Mockar nos testes

    Usamos ChatGroq que é compatível com a interface ChatModel do LangChain.
    Isso significa que trocar de provedor no futuro requer mudar APENAS esta função.
    """
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

    Este é o formato padrão de um nó LangGraph:
    - Recebe o estado inteiro
    - Retorna apenas os campos que modifica
    """
    # 1. Prepara o contexto de feedback (se houver iteração anterior)
    feedback_context = ""
    if state.get("feedback") and state.get("iteration", 0) > 1:
        feedback_context = (
            f"\n## Feedback da iteração anterior (IMPORTANTE — corrija os problemas!)\n"
            f"{state['feedback']}"
        )

    # 2. Monta o prompt com os dados do estado
    prompt = PLANNER_PROMPT.format(
        objective=state["objective"],
        iteration=state.get("iteration", 1),
        max_iterations=state.get("max_iterations", 3),
        feedback_context=feedback_context,
    )

    # 3. Chama a LLM
    llm = build_planner_llm()
    response = llm.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=f"Crie o plano para: {state['objective']}"),
    ])

    plan = response.content

    # 4. Atualiza o histórico
    history = state.get("history", [])
    iteration = state.get("iteration", 1)
    history = history + [f"[Iteração {iteration}] Planejador criou plano:\n{plan}"]

    # 5. Retorna APENAS os campos que este nó modifica
    return {
        "plan": plan,
        "history": history,
    }
