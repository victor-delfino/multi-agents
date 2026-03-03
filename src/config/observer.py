"""
Callback de Observabilidade do Grafo
=====================================

CONCEITO — O QUE SÃO CALLBACKS EM LANGGRAPH?

    Callbacks são funções que são chamadas AUTOMATICAMENTE pelo LangGraph
    em momentos específicos da execução:
    - Antes de um nó rodar (on_chain_start)
    - Depois de um nó rodar (on_chain_end)
    - Quando ocorre um erro (on_chain_error)

    Isso permite OBSERVAR o grafo sem modificar o código dos agentes.
    É o princípio Open/Closed: aberto para extensão, fechado para modificação.

CONCEITO — POR QUE OBSERVABILIDADE IMPORTA?

    Em produção, você precisa responder:
    - Qual nó está lento? → Métricas de tempo
    - Qual nó está falhando? → Contagem de erros
    - O que cada nó recebeu/produziu? → Tracing
    - Quantas iterações o loop faz em média? → Estatísticas

    Sem observabilidade, debugging é adivinhar.
    Com observabilidade, debugging é ciência.

"""

import time
from dataclasses import dataclass, field

from src.config.logging_config import get_logger

logger = get_logger("observer")


@dataclass
class ExecutionMetrics:
    """
    Coleta métricas de execução do grafo.

    CONCEITO — POR QUE DATACLASS?
        Dataclass é uma forma concisa de criar classes de dados em Python.
        É melhor que dicionário porque:
        - Tem autocomplete no editor
        - Tem tipos definidos
        - Tem __repr__ automático (fácil de imprimir)
    """
    total_start_time: float = 0.0
    node_times: dict = field(default_factory=dict)  # {"planejador": 1.2, "executor": 3.4}
    node_calls: dict = field(default_factory=dict)  # {"planejador": 2, "executor": 2}
    errors: list = field(default_factory=list)

    def start(self):
        """Marca o início da execução total."""
        self.total_start_time = time.time()

    def record_node(self, node_name: str, elapsed: float):
        """Registra tempo de execução de um nó."""
        if node_name not in self.node_times:
            self.node_times[node_name] = 0.0
            self.node_calls[node_name] = 0
        self.node_times[node_name] += elapsed
        self.node_calls[node_name] += 1

    def record_error(self, node_name: str, error: str):
        """Registra um erro de um nó."""
        self.errors.append({"node": node_name, "error": error})

    @property
    def total_time(self) -> float:
        """Tempo total de execução."""
        return time.time() - self.total_start_time if self.total_start_time else 0.0

    def summary(self) -> str:
        """
        Gera um resumo legível das métricas.

        Exemplo de output:
            ╔══════════════════════════════════════╗
            ║     MÉTRICAS DE EXECUÇÃO             ║
            ╠══════════════════════════════════════╣
            ║ Tempo total: 5.23s                   ║
            ║                                      ║
            ║ Nó            Tempo   Chamadas       ║
            ║ planejador    1.20s   2x             ║
            ║ executor      2.80s   2x             ║
            ║ validador     1.10s   2x             ║
            ║ incrementar   0.00s   1x             ║
            ║                                      ║
            ║ Erros: 0                             ║
            ╚══════════════════════════════════════╝
        """
        lines = []
        lines.append("=" * 50)
        lines.append("  METRICAS DE EXECUCAO")
        lines.append("=" * 50)
        lines.append(f"  Tempo total: {self.total_time:.2f}s")
        lines.append("")
        lines.append(f"  {'No':<18} {'Tempo':>8} {'Chamadas':>10}")
        lines.append(f"  {'-'*18} {'-'*8} {'-'*10}")

        for node_name in self.node_times:
            t = self.node_times[node_name]
            c = self.node_calls[node_name]
            lines.append(f"  {node_name:<18} {t:>7.2f}s {c:>9}x")

        lines.append("")
        lines.append(f"  Erros: {len(self.errors)}")

        if self.errors:
            for err in self.errors:
                lines.append(f"    - [{err['node']}] {err['error']}")

        lines.append("=" * 50)
        return "\n".join(lines)
