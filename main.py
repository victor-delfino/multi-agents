"""
Ponto de Entrada do Sistema Multi-Agentes
==========================================

FASE ATUAL: Fase 4 — Sistema completo com 4 agentes + loop condicional

EVOLUÇÃO:
    Fase 2: planner_node(state) ← chamada direta, sem grafo
    Fase 3: workflow.invoke(state) ← grafo com 2 agentes (linear)
    Fase 4: workflow.invoke(state) ← grafo com 4 agentes + loop ← ESTAMOS AQUI
"""

from src.config.settings import validate_config
from src.graph.workflow import build_workflow


def main():
    """
    Executa o sistema completo de 4 agentes via LangGraph.

    Fluxo:
        Planejador → Executor → Validador → [Aprovado?]
            ▲                                    │
            └──── increment ◄── (não aprovado) ──┘
                                    │
                              (aprovado) → END

    O código aqui NÃO controla o fluxo. O grafo decide tudo.
    Nós apenas passamos o estado inicial e recebemos o final.
    """
    print("=" * 60)
    print("🤖 Sistema Multi-Agentes — Fase 4: Sistema Completo")
    print("=" * 60)

    # Valida configuração
    validate_config()

    # Pede o objetivo ao usuário
    print("\n📝 Digite o objetivo para o sistema resolver:")
    print("   (Exemplo: 'Criar um artigo sobre inteligência artificial')\n")
    objective = input("🎯 Objetivo: ").strip()

    if not objective:
        objective = "Criar um artigo sobre inteligência artificial"
        print(f"   (Usando objetivo padrão: '{objective}')")

    # Estado inicial — o grafo vai preenchendo conforme os agentes rodam
    initial_state = {
        "objective": objective,
        "plan": "",
        "result": "",
        "feedback": "",
        "is_approved": False,
        "iteration": 1,
        "max_iterations": 3,
        "history": [],
    }

    # Constrói o grafo
    print("\n🔧 Construindo grafo: Planejador → Executor → Validador → [Orquestrador]")
    workflow = build_workflow()

    # Executa o grafo inteiro com loop de auto-correção
    print("⏳ Executando grafo (máximo 3 iterações)...\n")
    final_state = workflow.invoke(initial_state)

    # Mostra os resultados
    print("\n" + "=" * 60)
    print("📋 PLANO FINAL (última versão do Planejador)")
    print("=" * 60)
    print(final_state["plan"])

    print("\n" + "=" * 60)
    print("📄 RESULTADO FINAL (última versão do Executor)")
    print("=" * 60)
    print(final_state["result"])

    print("\n" + "=" * 60)
    print("✅ VALIDAÇÃO")
    print("=" * 60)
    status = "APROVADO ✓" if final_state["is_approved"] else "NÃO APROVADO ✗ (limite de iterações)"
    print(f"   Status: {status}")
    print(f"   Iterações usadas: {final_state['iteration']}/{final_state['max_iterations']}")

    print("\n" + "=" * 60)
    print("💬 FEEDBACK DO VALIDADOR")
    print("=" * 60)
    print(final_state["feedback"])

    print("\n" + "=" * 60)
    print("📜 HISTÓRICO COMPLETO (rastreabilidade)")
    print("=" * 60)
    for i, entry in enumerate(final_state["history"], 1):
        print(f"\n--- Entrada {i} ---")
        print(entry)

    print("\n" + "=" * 60)
    print("✅ Fase 4 completa! Sistema com 4 agentes funcionando.")
    print("   Planejador → Executor → Validador → Orquestrador (loop)")
    print("=" * 60)


if __name__ == "__main__":
    main()
