# 🤖 Multi-Agents System

Sistema multi-agentes educacional construído com **LangGraph** e **LangChain**, focado em aprender como agentes de IA se comunicam, se coordenam e se complementam.

4 agentes especializados colaboram via estado compartilhado (Blackboard Pattern) para resolver problemas de forma coordenada, com loop de autocorreção e observabilidade completa.

---

## Arquitetura

```
                    ┌──────────────────────────────────────────┐
                    │                                          │
                    ▼                                          │
              ┌───────────┐     ┌──────────┐     ┌───────────┐│
  Objetivo →  │ Planejador │ ──→ │ Executor │ ──→ │ Validador ││
              └───────────┘     └──────────┘     └─────┬─────┘│
                                                       │      │
                                                       ▼      │
                                                 ┌───────────┐│
                                                 │ Aprovado?  ││
                                                 └─────┬─────┘│
                                                  sim/ │ \não  │
                                                  ▼    │  ▼    │
                                                 FIM   │ incrementar
                                                       │  iteração
                                                       └──────┘
```

| Agente | Responsabilidade | Usa LLM? |
|---|---|---|
| **Planejador** | Decompõe o objetivo em até 5 passos concretos | ✅ |
| **Executor** | Executa os passos do plano fielmente | ✅ |
| **Validador** | Avalia qualidade com notas (1-10) em 4 critérios | ✅ |
| **Orquestrador** | Decide se finaliza ou reenvia (aresta condicional) | ❌ |

---

## Conceitos Demonstrados

| Conceito | Implementação |
|---|---|
| **Blackboard Pattern** | Estado compartilhado tipado (`AgentState`) como canal de comunicação entre agentes |
| **Orquestração com LangGraph** | `StateGraph` com nós, arestas fixas e arestas condicionais |
| **Loop de autocorreção** | Validador rejeita → Orquestrador incrementa → Planejador refaz com feedback |
| **Fail-safe design** | Regex parsing com fallback (rejeita se não conseguir parsear) |
| **Observabilidade** | Logging estruturado (console + arquivo), métricas de tempo por agente |
| **Tratamento de erros** | `try/except` em todos agentes com logging de nível ERROR |
| **Prompt engineering** | Prompts separados com Role/Context/Task/Format/Limits |
| **Factory pattern** | `build_*_llm()` isolando criação do modelo LLM |

---

## Setup

```bash
# 1. Criar ambiente virtual (Python 3.11+)
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar variáveis de ambiente
copy .env.example .env     # Windows
cp .env.example .env       # Linux/Mac

# Edite .env com sua GROQ_API_KEY (https://console.groq.com/keys)

# 4. Executar
python main.py
```

### Variáveis de Ambiente

| Variável | Obrigatória | Default | Descrição |
|---|---|---|---|
| `GROQ_API_KEY` | ✅ | — | Chave de API do Groq ([obter aqui](https://console.groq.com/keys)) |
| `MODEL_NAME` | ❌ | `llama-3.3-70b-versatile` | Modelo LLM. Alternativas: `llama-3.1-8b-instant`, `mixtral-8x7b-32768` |
| `MODEL_TEMPERATURE` | ❌ | `0.7` | Criatividade do modelo (0.0 = determinístico, 1.0 = criativo) |

---

## Estrutura do Projeto

```
multi-agents/
├── main.py                         # Ponto de entrada (input interativo)
├── test_quick.py                   # Teste rápido com objetivo fixo
├── requirements.txt                # Dependências do projeto
├── .env.example                    # Template de variáveis de ambiente
│
├── src/
│   ├── agents/                     # Agentes individuais (nós do grafo)
│   │   ├── planner.py              #   Decomposição de objetivos em passos
│   │   ├── executor.py             #   Execução fiel do plano
│   │   ├── validator.py            #   Avaliação com notas e aprovação
│   │   └── orchestrator.py         #   Roteamento condicional (sem LLM)
│   │
│   ├── state/
│   │   └── agent_state.py          # TypedDict — contrato entre agentes
│   │
│   ├── graph/
│   │   └── workflow.py             # Montagem e compilação do StateGraph
│   │
│   └── config/
│       ├── settings.py             # Carregamento de .env e validação
│       ├── prompts.py              # Templates de prompt (Role/Context/Task)
│       ├── logging_config.py       # Logging estruturado (console + arquivo)
│       └── observer.py             # ExecutionMetrics (dataclass de métricas)
│
├── logs/                           # Logs de execução (gitignored)
│   └── execution_YYYYMMDD_HHMMSS.log
│
└── tests/
    └── test_planner.py             # Testes unitários (pytest)
```

---

## Como Funciona

### Fluxo de Dados

1. **Usuário** define um objetivo (ex: *"Criar 3 dicas para aprender Python"*)
2. **Planejador** decompõe em até 5 passos numerados
3. **Executor** executa cada passo e produz um resultado completo
4. **Validador** avalia em 4 critérios (Completude, Qualidade, Coerência, Clareza) com notas 1-10
5. **Orquestrador** decide:
   - **Aprovado** → Encerra o grafo
   - **Rejeitado + tentativas restantes** → Incrementa iteração e volta ao Planejador com feedback
   - **Rejeitado + limite atingido** → Encerra com o melhor resultado disponível

### Estado Compartilhado (`AgentState`)

```python
class AgentState(TypedDict):
    objective: str        # Objetivo original do usuário
    plan: str             # Plano gerado pelo Planejador
    result: str           # Resultado produzido pelo Executor
    feedback: str         # Feedback do Validador
    is_approved: bool     # Decisão de aprovação
    iteration: int        # Iteração atual (1-based)
    max_iterations: int   # Limite de tentativas (default: 3)
    history: list[str]    # Histórico completo de todas as iterações
```

### Logging

O sistema gera logs estruturados em dois destinos:

```
[18:05:37] INFO     | multi_agents.planner      | Iniciando (iteracao 1)
[18:05:40] INFO     | multi_agents.planner      | Plano gerado em 1.27s (781 chars)
[18:05:40] INFO     | multi_agents.executor     | Iniciando (iteracao 1)
[18:05:45] INFO     | multi_agents.executor     | Resultado gerado em 3.54s (4065 chars)
[18:05:45] INFO     | multi_agents.validator    | Iniciando avaliacao (iteracao 1)
[18:05:47] INFO     | multi_agents.validator    | Avaliacao gerada em 1.61s (1462 chars)
[18:05:47] INFO     | multi_agents.validator    | Decisao: APROVADO
[18:05:47] INFO     | multi_agents.orchestrator | APROVADO na iteracao 1 — finalizando
```

- **Console**: Nível configurável (INFO por padrão)
- **Arquivo**: Sempre DEBUG, salvo em `logs/execution_*.log`

---

## Tecnologias

| Tecnologia | Versão | Propósito |
|---|---|---|
| Python | 3.11+ | Linguagem base |
| LangGraph | ≥ 0.2.0 | Orquestração de agentes via grafos de estado |
| LangChain | ≥ 0.3.0 | Framework de interação com LLMs |
| langchain-groq | ≥ 0.2.0 | Provider Groq para LangChain |
| Groq + Llama 3.3 70B | — | LLM gratuito e open-source |
| python-dotenv | ≥ 1.0.0 | Gerenciamento de variáveis de ambiente |

---

## Testes

```bash
# Teste rápido (objetivo fixo, sem input)
python test_quick.py

# Teste interativo
python main.py

# Testes unitários
pytest tests/ -v
```

---

## Fases de Desenvolvimento

Este projeto foi construído de forma progressiva:

| Fase | Descrição | Status |
|---|---|---|
| **Fase 1** | Fundamentos teóricos (conceitos, sem código) | ✅ |
| **Fase 2** | Setup + Planejador isolado | ✅ |
| **Fase 3** | Comunicação (Planejador + Executor via LangGraph) | ✅ |
| **Fase 4** | Sistema completo (4 agentes + loop condicional) | ✅ |
| **Fase 5** | Observabilidade (logging, métricas, tratamento de erros) | ✅ |

---

## Licença

Este é um projeto educacional.
