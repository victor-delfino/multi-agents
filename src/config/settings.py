"""
Configurações do Projeto
========================

Centraliza todas as configurações: chaves de API, parâmetros do modelo,
e constantes do sistema.

CONCEITO IMPORTANTE:
    Nunca hardcode chaves de API no código. Use variáveis de ambiente.
    O python-dotenv carrega automaticamente o arquivo .env na raiz do projeto.

    Isso é essencial para:
    - Segurança (chaves não vão para o Git)
    - Flexibilidade (diferentes configs para dev/prod)
    - Portabilidade (cada dev tem sua própria chave)
"""

import os

from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()


# --- API Keys ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# --- Modelo ---
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")
MODEL_TEMPERATURE = float(os.getenv("MODEL_TEMPERATURE", "0.7"))

# --- Sistema ---
MAX_ITERATIONS = 3  # Máximo de ciclos Planejador→Executor→Validador


def validate_config() -> None:
    """
    Valida que todas as configurações obrigatórias estão presentes.
    Chamada na inicialização do sistema.
    """
    if not GROQ_API_KEY or GROQ_API_KEY == "gsk_your-key-here":
        raise ValueError(
            "\n❌ GROQ_API_KEY não configurada!\n"
            "   1. Copie .env.example para .env\n"
            "   2. Coloque sua chave da Groq no arquivo .env\n"
            "      (Obtenha em: https://console.groq.com/keys)\n"
            "   3. Execute novamente\n"
        )
    print(f"✅ Configuração válida | Modelo: {MODEL_NAME} | Temperatura: {MODEL_TEMPERATURE}")
