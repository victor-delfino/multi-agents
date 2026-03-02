"""Script de teste rápido para o Planejador (Fase 2)."""

from src.agents.planner import planner_node

state = {
    "objective": "Criar um artigo sobre inteligencia artificial",
    "plan": "",
    "result": "",
    "feedback": "",
    "is_approved": False,
    "iteration": 1,
    "max_iterations": 3,
    "history": [],
}

print("Chamando o Planejador...")
result = planner_node(state)

print("\n" + "=" * 60)
print("PLANO GERADO:")
print("=" * 60)
print(result["plan"])

print("\n" + "=" * 60)
print("HISTORICO:")
print("=" * 60)
for h in result["history"]:
    print(h)
