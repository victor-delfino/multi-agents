# 🤖 Multi-Agents System

Sistema multi-agentes educacional construído com **LangGraph** e **LangChain**.

4 agentes especializados que se comunicam via estado compartilhado para resolver problemas de forma coordenada.

## Arquitetura

```
Planejador → Executor → Validador → [Aprovado?] → Fim ou → Planejador (retry)
```

| Agente | Responsabilidade |
|---|---|
| **Planejador** | Decompõe o objetivo em passos concretos |
| **Executor** | Executa os passos do plano |
| **Validador** | Avalia qualidade e coerência do resultado |
| **Orquestrador** | Decide se finaliza ou reenvia (aresta condicional) |

## Setup

```bash
# 1. Criar ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar variáveis de ambiente
copy .env.example .env
# Edite .env com sua GROQ_API_KEY (https://console.groq.com/keys)

# 4. Executar
python main.py
```

## Estrutura do Projeto

```
src/
├── agents/          # Agentes individuais
├── state/           # Estado compartilhado (contrato entre agentes)
├── graph/           # Montagem do grafo LangGraph
└── config/          # Configurações e prompts
```

## Conceitos Demonstrados

- Comunicação entre agentes via Blackboard Pattern
- Orquestração explícita com LangGraph
- Fluxos condicionais e loops
- Estado compartilhado tipado
- Separação de responsabilidades

## Tecnologias

- Python 3.11+
- LangGraph
- LangChain
- Groq + Llama 3.3 70B (gratuito, open-source)
