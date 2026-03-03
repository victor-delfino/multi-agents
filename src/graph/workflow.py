"""
Workflow — Montagem do Grafo LangGraph
=======================================

Aqui é onde os agentes se conectam. Este arquivo define:
- Quais nós existem (agentes)
- Quais arestas existem (quem fala com quem)
- Onde o fluxo começa e termina

CONCEITO — COMO LANGGRAPH FUNCIONA POR BAIXO:

    1. Você cria um StateGraph tipado com seu AgentState
    2. Adiciona nós (funções que recebem/retornam estado)
    3. Adiciona arestas (conexões entre nós)
    4. Compila o grafo (transforma em um objeto executável)

    Quando você executa o grafo com .invoke(estado_inicial):
    - LangGraph roda o primeiro nó (entry point)
    - Faz merge do retorno com o estado
    - Segue a aresta para o próximo nó
    - Repete até chegar ao END

    O estado FLUI pelo grafo como água em canos.
    Cada nó pode ler qualquer campo e escrever nos campos que quiser.

FASE ATUAL (Fase 3): Grafo simples Planejador → Executor
PRÓXIMA FASE (Fase 4): + Validador + aresta condicional (loop)
"""

from langgraph.graph import StateGraph, END

from src.state.agent_state import AgentState
from src.agents.planner import planner_node
from src.agents.executor import executor_node


def build_workflow() -> StateGraph:
    """
    Constrói e compila o grafo de agentes.

    Grafo atual (Fase 3):

        [START] → Planejador → Executor → [END]

    Retorna o grafo compilado, pronto para .invoke()
    """
    # 1. Cria o grafo com o tipo do estado
    #    Isso garante que todos os nós trabalham com o mesmo formato de dados
    workflow = StateGraph(AgentState)

    # 2. Registra os nós (agentes)
    #    O primeiro argumento é o NOME do nó (usado nas arestas)
    #    O segundo é a FUNÇÃO que será executada
    workflow.add_node("planejador", planner_node)
    workflow.add_node("executor", executor_node)

    # 3. Define o ponto de entrada
    #    "Quando o grafo começar, rode o nó 'planejador' primeiro"
    workflow.set_entry_point("planejador")

    # 4. Define as arestas (conexões)
    #    "Depois do 'planejador', rode o 'executor'"
    workflow.add_edge("planejador", "executor")

    #    "Depois do 'executor', termine"
    workflow.add_edge("executor", END)

    # 5. Compila o grafo
    #    Transforma a definição em um objeto executável
    #    O .compile() valida que o grafo é válido (sem nós órfãos, etc.)
    app = workflow.compile()

    return app
