"""
Orquestrador (Roteador Condicional)
====================================

Responsabilidade: Decidir se o fluxo termina ou volta ao Planejador.

CONCEITO — POR QUE ISSO NÃO É UM AGENTE?

    O Orquestrador NÃO usa LLM. Ele é uma função determinística que:
    1. Lê is_approved e iteration do estado
    2. Retorna o nome do próximo nó (string)

    Em LangGraph, isso se chama "função de roteamento" (routing function).
    Ela é usada em arestas condicionais para decidir o próximo passo.

    Decisão:
    ┌─────────────────────────────────┐
    │ is_approved == True?            │──sim──→ "end" (finaliza)
    │                                 │
    │ iteration >= max_iterations?    │──sim──→ "end" (limite atingido)
    │                                 │
    │ caso contrário                  │──────→ "planejador" (retry com feedback)
    └─────────────────────────────────┘

CONCEITO — ARESTA CONDICIONAL vs NÓ

    Poderíamos ter feito o Orquestrador como um NÓ (função que modifica estado).
    Mas ele não modifica nada — apenas decide o caminho.
    
    Em LangGraph, a forma idiomática é usar add_conditional_edges():
    - A função de roteamento é passada como argumento
    - O LangGraph chama essa função e segue o caminho retornado
    - É mais leve, mais claro, e mais performático

    Se no futuro o Orquestrador precisar modificar estado (ex: incrementar
    iteration, logar decisão), aí sim promovemos ele a nó.
"""

from src.state.agent_state import AgentState


def should_continue(state: AgentState) -> str:
    """
    Função de roteamento do Orquestrador.

    Retorna:
        "end" → Fluxo termina (resultado aprovado ou limite atingido)
        "planejador" → Volta ao Planejador (resultado reprovado, ainda há tentativas)

    NOTA: Os valores retornados são mapeados para nós reais no grafo
    via o dicionário de mapeamento em add_conditional_edges().
    """
    # Caso 1: Resultado aprovado pelo Validador → Finaliza
    if state.get("is_approved", False):
        print(f"   🟢 Orquestrador: APROVADO na iteração {state.get('iteration', 1)}")
        return "end"

    # Caso 2: Limite de iterações atingido → Finaliza (mesmo sem aprovação)
    iteration = state.get("iteration", 1)
    max_iterations = state.get("max_iterations", 3)

    if iteration >= max_iterations:
        print(f"   🟡 Orquestrador: Limite de {max_iterations} iterações atingido. Finalizando.")
        return "end"

    # Caso 3: Não aprovado e ainda há tentativas → Retry
    print(f"   🔴 Orquestrador: REPROVADO na iteração {iteration}. Reenviando ao Planejador.")
    return "planejador"


def increment_iteration(state: AgentState) -> dict:
    """
    Nó auxiliar que incrementa o contador de iterações.

    POR QUE EXISTE?
        Quando o Orquestrador decide reenviar ao Planejador, precisamos
        incrementar o contador ANTES de rodar o Planejador novamente.
        Caso contrário, a iteração ficaria sempre em 1.

        Este é um nó simples, sem LLM — apenas modifica o estado.
        É um exemplo de que nem todo nó precisa ser um "agente inteligente".
        Às vezes um nó é apenas uma operação de estado.
    """
    return {
        "iteration": state.get("iteration", 1) + 1,
    }
