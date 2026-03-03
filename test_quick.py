"""
Script de teste rápido — Fase 3: Planejador + Executor via LangGraph
=====================================================================

Diferença da Fase 2:
  - Antes: planner_node(state) ← chamada direta
  - Agora: workflow.invoke(state) ← grafo orquestra os agentes

O grafo garante: Planejador roda primeiro → Executor roda depois.
O estado compartilhado carrega os dados entre eles.
"""

from src.graph.workflow import build_workflow

state = {
    "objective": "Criar um guia rapido sobre como usar Git",
    "plan": "",
    "result": "",
    "feedback": "",
    "is_approved": False,
    "iteration": 1,
    "max_iterations": 3,
    "history": [],
}

print("Construindo grafo: Planejador -> Executor")
workflow = build_workflow()

print("Executando grafo...\n")
final_state = workflow.invoke(state)

print("=" * 60)
print("PLANO (escrito pelo Planejador):")
print("=" * 60)
print(final_state["plan"])

print("\n" + "=" * 60)
print("RESULTADO (escrito pelo Executor):")
print("=" * 60)
print(final_state["result"])

print("\n" + "=" * 60)
print("HISTORICO (rastreabilidade):")
print("=" * 60)
for h in final_state["history"]:
    print(f"\n{h}")
