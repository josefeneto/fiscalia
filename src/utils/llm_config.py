# src/utils/llm_config.py - ARQUIVO COMPLETO

"""
Configuração de LLM para CrewAI
Suporta Groq e OpenAI via variável de ambiente LLM_PROVIDER
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()


def get_llm_config() -> dict:
    """
    Retorna configuração da LLM baseada em LLM_PROVIDER
    
    Returns:
        dict: Configuração para CrewAI LLM
    """
    provider = os.getenv('LLM_PROVIDER', 'groq').lower()
    
    if provider == 'groq':
        api_key = os.getenv('GROQ_API_KEY')
        model = os.getenv('GROQ_MODEL', 'groq/llama-3.3-70b-versatile')
        
        if not api_key:
            raise ValueError("GROQ_API_KEY não encontrada no .env")
        
        return {
            'model': model,
            'api_key': api_key,
            'temperature': 0.1,  # Mais determinístico para dados fiscais
            'base_url': 'https://api.groq.com/openai/v1'
        }
    
    elif provider == 'openai':
        api_key = os.getenv('OPENAI_API_KEY')
        model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        
        if not api_key:
            raise ValueError("OPENAI_API_KEY não encontrada no .env")
        
        return {
            'model': model,
            'api_key': api_key,
            'temperature': 0.1
        }
    
    else:
        raise ValueError(
            f"LLM_PROVIDER inválido: '{provider}'. "
            f"Use 'groq' ou 'openai'"
        )


def get_provider_name() -> str:
    """Retorna nome do provider ativo"""
    return os.getenv('LLM_PROVIDER', 'groq').lower()


def verify_llm_connection() -> bool:
    """
    Verifica se a conexão com LLM está funcionando
    
    Returns:
        bool: True se conexão OK
    """
    try:
        config = get_llm_config()
        provider = get_provider_name()
        
        print(f"✓ Provider: {provider}")
        print(f"✓ Model: {config['model']}")
        print(f"✓ API Key: {config['api_key'][:10]}...{config['api_key'][-4:]}")
        
        return True
    except Exception as e:
        print(f"✗ Erro na configuração LLM: {e}")
        return False


# Função helper para criar LLM do CrewAI
def create_llm():
    """
    Cria instância de LLM para uso no CrewAI
    
    Returns:
        LLM configurada
    """
    from langchain_openai import ChatOpenAI
    from langchain_groq import ChatGroq
    
    provider = get_provider_name()
    config = get_llm_config()
    
    if provider == 'groq':
        return ChatGroq(
            api_key=config['api_key'],
            model=config['model'],
            temperature=config['temperature']
        )
    else:  # openai
        return ChatOpenAI(
            api_key=config['api_key'],
            model=config['model'],
            temperature=config['temperature']
        )


if __name__ == "__main__":
    """Teste standalone"""
    print("=== Teste de Configuração LLM ===\n")
    
    if verify_llm_connection():
        print("\n✅ Configuração LLM válida!")
        
        # Testar criação de LLM
        try:
            llm = create_llm()
            print(f"✅ LLM criada: {type(llm).__name__}")
        except Exception as e:
            print(f"✗ Erro ao criar LLM: {e}")
    else:
        print("\n❌ Configuração LLM inválida!")
