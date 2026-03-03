"""
Ponto de Entrada do Sistema Multi-Agentes
==========================================

FASE ATUAL: Fase 3 — Planejador + Executor conectados via LangGraph
PRÓXIMA FASE: Fase 4 — + Validador + Orquestrador (loop condicional)

EVOLUÇÃO:
    Fase 2: planner_node(state) ← chamada direta, sem grafo
    Fase 3: workflow.invoke(state) ← grafo orquestra 2 agentes   ← ESTAMOS AQUI
    Fase 4: workflow.invoke(state) ← grafo com 4 agentes + loop
"""

from src.config.settings import validate_config
from src.graph.workflow import build_workflow


def main():
    """
    Executa o grafo Planejador → Executor via LangGraph.

    ANTES (Fase 2): chamávamos planner_node() diretamente
    AGORA (Fase 3): chamamos workflow.invoke() — o grafo decide a ordem

    A diferença? Agora NÃO controlamos quem roda quando.
    O grafo cuida disso. Só passamos o estado inicial.
    """
    print("=" * 60)
    print("🤖 Sistema Multi-Agentes — Fase 3: Planejador + Executor")
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
    print("\n🔧 Construindo grafo: Planejador → Executor")
    workflow = build_workflow()

    # Executa o grafo inteiro
    # O LangGraph vai:
    # 1. Rodar planner_node(state) → atualizar state com "plan"
    # 2. Rodar executor_node(state) → atualizar state com "result"
    # 3. Retornar o estado final completo
    print("⏳ Executando grafo...\n")
    final_state = workflow.invoke(initial_state)

    # Mostra os resultados
    print("=" * 60)
    print("📋 PLANO (gerado pelo Planejador)")
    print("=" * 60)
    print(final_state["plan"])

    print("\n" + "=" * 60)
    print("📄 RESULTADO (gerado pelo Executor)")
    print("=" * 60)
    print(final_state["result"])

    print("\n" + "=" * 60)
    print("📜 HISTÓRICO (rastreabilidade do fluxo)")
    print("=" * 60)
    for entry in final_state["history"]:
        print(f"\n{entry}")

    print("\n" + "=" * 60)
    print("✅ Fase 3 completa!")
    print("   O Planejador criou o plano → O Executor executou → Resultado gerado")
    print("   Próximo: Fase 4 — Validador + loop condicional")
    print("=" * 60)


if __name__ == "__main__":
    main()
