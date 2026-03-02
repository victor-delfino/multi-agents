"""
Ponto de Entrada do Sistema Multi-Agentes
==========================================

Por enquanto, estamos na Fase 2 — apenas o Planejador rodando isolado.
Este arquivo vai evoluir conforme adicionamos agentes.

FASE ATUAL: Planejador isolado (sem grafo ainda)
PRÓXIMA FASE: Dois agentes conversando via LangGraph
"""

from src.config.settings import validate_config
from src.agents.planner import planner_node


def main():
    """
    Executa o Planejador isolado para validar que tudo funciona.

    Nesta fase, não usamos LangGraph ainda — chamamos o nó diretamente.
    Isso é intencional: queremos validar que o agente funciona
    ANTES de conectá-lo ao grafo. Teste unitário antes de integração.
    """
    print("=" * 60)
    print("🤖 Sistema Multi-Agentes — Fase 2: Planejador Isolado")
    print("=" * 60)

    # Valida configuração
    validate_config()

    # Simula o estado inicial (como o LangGraph faria)
    initial_state = {
        "objective": "",
        "plan": "",
        "result": "",
        "feedback": "",
        "is_approved": False,
        "iteration": 1,
        "max_iterations": 3,
        "history": [],
    }

    # Pede o objetivo ao usuário
    print("\n📝 Digite o objetivo que o Planejador deve decompor em passos:")
    print("   (Exemplo: 'Criar um artigo sobre inteligência artificial')\n")
    objective = input("🎯 Objetivo: ").strip()

    if not objective:
        objective = "Criar um artigo sobre inteligência artificial"
        print(f"   (Usando objetivo padrão: '{objective}')")

    initial_state["objective"] = objective

    # Executa o Planejador
    print("\n⏳ Planejador trabalhando...\n")
    result = planner_node(initial_state)

    # Mostra o resultado
    print("=" * 60)
    print("📋 PLANO GERADO")
    print("=" * 60)
    print(result["plan"])
    print("\n" + "=" * 60)
    print("📜 HISTÓRICO")
    print("=" * 60)
    for entry in result["history"]:
        print(entry)
    print("=" * 60)

    print("\n✅ Fase 2 completa! O Planejador funciona isoladamente.")
    print("   Próximo passo: Fase 3 — conectar Planejador + Executor via LangGraph.\n")


if __name__ == "__main__":
    main()
