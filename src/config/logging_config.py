"""
Sistema de Logging do Projeto
==============================

CONCEITO — POR QUE NÃO USAR print()?

    print() funciona para debug rápido, mas em produção:
    - Não tem níveis (INFO, WARNING, ERROR)
    - Não tem timestamp
    - Não vai para arquivo (só console)
    - Não tem contexto (qual módulo gerou?)
    - Não é filtrável (tudo ou nada)

    O módulo logging do Python resolve tudo isso.
    Um bom sistema de logging permite que você:
    1. Veja tudo no console durante desenvolvimento
    2. Grave em arquivo para análise posterior
    3. Filtre por nível (só erros em produção, tudo em dev)
    4. Saiba EXATAMENTE onde cada mensagem foi gerada

CONCEITO — NÍVEIS DE LOG

    DEBUG    → Detalhes internos (prompt completo, estado raw)
    INFO     → Eventos normais (agente iniciou, agente terminou)
    WARNING  → Algo inesperado mas não crítico (parsing falhou, usando fallback)
    ERROR    → Algo deu errado (API falhou, exceção capturada)
    CRITICAL → Sistema não pode continuar (config inválida)

"""

import logging
import sys
from datetime import datetime
from pathlib import Path


def setup_logging(level: str = "INFO", log_to_file: bool = True) -> logging.Logger:
    """
    Configura e retorna o logger principal do sistema.

    Args:
        level: Nível mínimo de log ("DEBUG", "INFO", "WARNING", "ERROR")
        log_to_file: Se True, também grava logs em arquivo

    Returns:
        Logger configurado para todo o projeto

    USO:
        from src.config.logging_config import setup_logging
        logger = setup_logging()
        logger.info("Mensagem informativa")
        logger.error("Algo deu errado", exc_info=True)
    """
    # Cria o logger raiz do projeto
    logger = logging.getLogger("multi_agents")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Evita duplicar handlers se chamado mais de uma vez
    if logger.handlers:
        return logger

    # Formato das mensagens
    # [TIMESTAMP] NÍVEL | módulo | mensagem
    formatter = logging.Formatter(
        fmt="[%(asctime)s] %(levelname)-8s | %(name)-20s | %(message)s",
        datefmt="%H:%M:%S",
    )

    # Handler 1: Console (sempre ativo)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Handler 2: Arquivo (opcional)
    if log_to_file:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_handler = logging.FileHandler(
            log_dir / f"execution_{timestamp}.log",
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)  # Arquivo sempre grava tudo
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Retorna um sub-logger para um módulo específico.

    Cada agente/módulo deve usar seu próprio sub-logger:
        logger = get_logger("planner")
        logger.info("Plano gerado com sucesso")

    Isso aparece no log como:
        [12:30:45] INFO     | multi_agents.planner | Plano gerado com sucesso

    O sub-logger herda a configuração do logger pai.
    """
    return logging.getLogger(f"multi_agents.{name}")
