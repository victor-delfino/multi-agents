"""
Script de teste rapido — Fase 5: Sistema com observabilidade
==============================================================

Observe no output:
- Logs estruturados com timestamps e nomes de modulos
- Metricas de tempo por agente
- Arquivo de log salvo em logs/
"""

from src.config.logging_config import setup_logging
from src.config.observer import ExecutionMetrics
from src.graph.workflow import build_workflow

# Inicializa logging (DEBUG para ver tudo no teste)
setup_logging(level="INFO", log_to_file=True)

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

print("Construindo grafo com observabilidade...")
workflow = build_workflow()

metrics = ExecutionMetrics()
metrics.start()

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

# Métricas de tempo
print(f"\nTempo total: {metrics.total_time:.2f}s")
print("Log salvo em: logs/")

print("\n" + "=" * 60)
print("HISTORICO COMPLETO:")
print("=" * 60)
for i, h in enumerate(final_state["history"], 1):
    print(f"\n--- Entrada {i} ---")
    # Substitui caracteres Unicode que o Windows cp1252 não suporta
    print(h.encode("ascii", errors="replace").decode("ascii"))
