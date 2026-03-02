"""
Estado Compartilhado do Sistema Multi-Agentes
=============================================

Este é o CONTRATO entre todos os agentes. Cada campo aqui é um dado
que pode ser lido ou escrito por qualquer nó do grafo.

CONCEITO IMPORTANTE:
    Em LangGraph, o estado é um TypedDict que flui pelo grafo.
    Cada nó (agente) recebe o estado atual, faz seu trabalho,
    e retorna um dicionário com os campos que quer ATUALIZAR.

    Exemplo: Se o Planejador quer escrever o plano, ele retorna:
        {"plan": "1. Pesquisar\n2. Escrever\n3. Revisar"}

    O LangGraph faz o merge automático com o estado existente.

POR QUE USAR TypedDict e não um dicionário comum?
    - Autocomplete no editor (VS Code mostra os campos)
    - Erros de digitação são pegos pelo linter
    - Documentação viva: olhar o estado = entender o sistema
    - Portfólio: mostra maturidade técnica
"""

from typing import TypedDict


class AgentState(TypedDict):
    """
    Estado compartilhado entre todos os agentes do sistema.

    Fluxo de dados:
        1. 'objective' é definido pelo usuário (input inicial)
        2. 'plan' é escrito pelo Planejador
        3. 'result' é escrito pelo Executor
        4. 'feedback' é escrito pelo Validador
        5. 'is_approved' é escrito pelo Validador
        6. 'iteration' é incrementado a cada ciclo
        7. 'history' acumula o histórico de todas as iterações
    """

    # --- Input do usuário ---
    objective: str  # O que o usuário quer que o sistema resolva

    # --- Saída do Planejador ---
    plan: str  # Plano de ação gerado pelo Planejador

    # --- Saída do Executor ---
    result: str  # Resultado da execução do plano

    # --- Saída do Validador ---
    feedback: str  # Feedback qualitativo sobre o resultado
    is_approved: bool  # Decisão binária: aprovado ou não

    # --- Controle de fluxo ---
    iteration: int  # Contador de iterações (evita loops infinitos)
    max_iterations: int  # Limite máximo de iterações

    # --- Histórico ---
    history: list[str]  # Log de cada iteração para observabilidade
