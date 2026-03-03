"""
Workflow — Montagem do Grafo LangGraph
=======================================

Aqui é onde os agentes se conectam. Este arquivo define:
- Quais nós existem (agentes)
- Quais arestas existem (quem fala com quem)
- Quais arestas são condicionais (decisões de roteamento)
- Onde o fluxo começa e onde pode terminar

CONCEITO — O GRAFO COMPLETO (Fase 4)

    ┌──────────────────────────────────────────────────────────┐
    │                                                          │
    │  [START]                                                 │
    │     │                                                    │
    │     ▼                                                    │
    │  Planejador ──→ Executor ──→ Validador                   │
    │     ▲                           │                        │
    │     │                     [should_continue]              │
    │     │                      ╱           ╲                 │
    │     │                 "planejador"    "end"               │
    │     │                    │               │               │
    │     │                    ▼               ▼               │
    │  increment_iteration   [volta]         [END]             │
    │                                                          │
    └──────────────────────────────────────────────────────────┘

    O CICLO: Validador → (reprovado) → increment → Planejador → Executor → Validador
    Cada ciclo é uma ITERAÇÃO. O Planejador recebe o feedback e adapta o plano.

CONCEITO — add_conditional_edges()

    Sintaxe:
        workflow.add_conditional_edges(
            "nó_origem",           # De onde sai
            função_de_roteamento,  # Função que decide
            {                      # Mapa: retorno → destino
                "valor_a": "nó_destino_a",
                "valor_b": "nó_destino_b",
            }
        )

    A função de roteamento recebe o estado e retorna uma string.
    Essa string é usada como chave no mapa para encontrar o próximo nó.
"""

from langgraph.graph import StateGraph, END

from src.state.agent_state import AgentState
from src.agents.planner import planner_node
from src.agents.executor import executor_node
from src.agents.validator import validator_node
from src.agents.orchestrator import should_continue, increment_iteration


def build_workflow() -> StateGraph:
    """
    Constrói e compila o grafo completo de 4 agentes.

    Grafo (Fase 4):

        [START] → Planejador → Executor → Validador
                      ▲                      │
                      │              [should_continue]
                      │               ╱          ╲
                 increment_iteration   "end"→[END]
                      ▲
                      │
                 "planejador"

    Retorna o grafo compilado, pronto para .invoke()
    """
    # 1. Cria o grafo tipado
    workflow = StateGraph(AgentState)

    # 2. Registra TODOS os nós
    workflow.add_node("planejador", planner_node)
    workflow.add_node("executor", executor_node)
    workflow.add_node("validador", validator_node)
    workflow.add_node("incrementar", increment_iteration)  # Nó auxiliar (sem LLM)

    # 3. Ponto de entrada
    workflow.set_entry_point("planejador")

    # 4. Arestas FIXAS (sempre seguem o mesmo caminho)
    workflow.add_edge("planejador", "executor")     # Planejador → Executor (sempre)
    workflow.add_edge("executor", "validador")      # Executor → Validador (sempre)
    workflow.add_edge("incrementar", "planejador")  # Incrementar → Planejador (quando há retry)

    # 5. Aresta CONDICIONAL (o Orquestrador decide)
    #    Depois do Validador, a função should_continue decide:
    #    - "end" → vai para END (finaliza)
    #    - "planejador" → vai para "incrementar" (que incrementa e volta ao Planejador)
    workflow.add_conditional_edges(
        "validador",           # Nó de origem
        should_continue,       # Função de roteamento (Orquestrador)
        {
            "end": END,                # Se retorna "end" → termina
            "planejador": "incrementar",  # Se retorna "planejador" → incrementa e volta
        }
    )

    # 6. Compila o grafo
    app = workflow.compile()

    return app
