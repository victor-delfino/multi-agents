"""
Ponto de Entrada do Sistema Multi-Agentes
==========================================

FASE ATUAL: Fase 5 — Sistema completo com observabilidade e logging

EVOLUÇÃO:
    Fase 2: planner_node(state) ← chamada direta, sem grafo
    Fase 3: workflow.invoke(state) ← grafo com 2 agentes (linear)
    Fase 4: workflow.invoke(state) ← grafo com 4 agentes + loop
    Fase 5: workflow.invoke(state) ← + logging + métricas + erros ← ESTAMOS AQUI
"""

from src.config.settings import validate_config
from src.config.logging_config import setup_logging, get_logger
from src.config.observer import ExecutionMetrics
from src.graph.workflow import build_workflow


def main():
    """
    Executa o sistema completo com observabilidade.

    Novidades da Fase 5:
    - Logging estruturado (console + arquivo)
    - Métricas de tempo por nó
    - Tratamento de erros global
    - Arquivo de log em logs/execution_YYYYMMDD_HHMMSS.log
    """
    # Inicializa logging ANTES de tudo
    setup_logging(level="INFO", log_to_file=True)
    logger = get_logger("main")

    print("=" * 60)
    print("  Sistema Multi-Agentes — Fase 5: Producao")
    print("=" * 60)

    # Valida configuração
    validate_config()

    # Pede o objetivo ao usuário
    print("\n  Digite o objetivo para o sistema resolver:")
    print("  (Exemplo: 'Criar um artigo sobre inteligencia artificial')\n")
    objective = input("  Objetivo: ").strip()

    if not objective:
        objective = "Criar um artigo sobre inteligencia artificial"
        print(f"  (Usando objetivo padrao: '{objective}')")

    logger.info(f"Objetivo recebido: {objective}")

    # Estado inicial
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
    logger.info("Construindo grafo de agentes")
    workflow = build_workflow()

    # Métricas de execução
    metrics = ExecutionMetrics()
    metrics.start()

    # Executa o grafo com tratamento de erros global
    logger.info("Iniciando execucao do grafo")
    print("\n  Executando grafo (maximo 3 iteracoes)...\n")

    try:
        final_state = workflow.invoke(initial_state)
        logger.info("Grafo executado com sucesso")
    except Exception as e:
        logger.critical(f"Erro fatal na execucao do grafo: {e}", exc_info=True)
        print(f"\n  ERRO FATAL: {e}")
        print("  Verifique o arquivo de log em logs/ para detalhes.")
        return

    # Registra métricas (tempo total)
    # Os tempos individuais são logados por cada agente
    logger.info(f"Tempo total de execucao: {metrics.total_time:.2f}s")

    # === EXIBIÇÃO DOS RESULTADOS ===

    print("\n" + "=" * 60)
    print("  PLANO FINAL")
    print("=" * 60)
    print(final_state["plan"])

    print("\n" + "=" * 60)
    print("  RESULTADO FINAL")
    print("=" * 60)
    print(final_state["result"])

    print("\n" + "=" * 60)
    print("  VALIDACAO")
    print("=" * 60)
    status = "APROVADO" if final_state["is_approved"] else "NAO APROVADO (limite de iteracoes)"
    print(f"  Status: {status}")
    print(f"  Iteracoes usadas: {final_state['iteration']}/{final_state['max_iterations']}")

    print("\n" + "=" * 60)
    print("  FEEDBACK DO VALIDADOR")
    print("=" * 60)
    print(final_state["feedback"])

    print("\n" + "=" * 60)
    print("  HISTORICO COMPLETO")
    print("=" * 60)
    for i, entry in enumerate(final_state["history"], 1):
        print(f"\n--- Entrada {i} ---")
        print(entry)

    # Métricas finais
    print(f"\n  Tempo total: {metrics.total_time:.2f}s")
    print("  Log salvo em: logs/")

    logger.info("Execucao finalizada com sucesso")

    print("\n" + "=" * 60)
    print("  Sistema Multi-Agentes — Todas as fases completas!")
    print("=" * 60)


if __name__ == "__main__":
    main()
