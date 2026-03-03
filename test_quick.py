"""
Script de teste rápido — Fase 4: Sistema completo com 4 agentes
================================================================

Fluxo: Planejador → Executor → Validador → [Aprovado?] → END ou retry

Observe no output:
- Quantas iterações o sistema precisou
- O que o Validador criticou
- Como o Planejador adaptou o plano no retry
"""

from src.graph.workflow import build_workflow

state = {
    "objective": "Criar uma lista com 3 dicas praticas para aprender Python",
    "plan": "",
    "result": "",
    "feedback": "",
    "is_approved": False,
    "iteration": 1,
    "max_iterations": 3,
    "history": [],
}

print("Construindo grafo: Planejador -> Executor -> Validador -> [Orquestrador]")
workflow = build_workflow()

print("Executando grafo (maximo 3 iteracoes)...\n")
final_state = workflow.invoke(state)

print("\n" + "=" * 60)
print("PLANO FINAL:")
print("=" * 60)
print(final_state["plan"])

print("\n" + "=" * 60)
print("RESULTADO FINAL:")
print("=" * 60)
print(final_state["result"])

print("\n" + "=" * 60)
print("VALIDACAO:")
print("=" * 60)
status = "APROVADO" if final_state["is_approved"] else "NAO APROVADO (limite)"
print(f"Status: {status}")
print(f"Iteracoes: {final_state['iteration']}/{final_state['max_iterations']}")

print("\n" + "=" * 60)
print("FEEDBACK DO VALIDADOR:")
print("=" * 60)
print(final_state["feedback"])

print("\n" + "=" * 60)
print("HISTORICO COMPLETO:")
print("=" * 60)
for i, h in enumerate(final_state["history"], 1):
    print(f"\n--- Entrada {i} ---")
    print(h)
