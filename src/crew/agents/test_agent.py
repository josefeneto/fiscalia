# src/crew/agents/test_agent.py - ARQUIVO COMPLETO

"""
Agente de teste para validar integração CrewAI + LLM
"""

from crewai import Agent
import sys
from pathlib import Path

# Adicionar src ao path
src_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(src_path))

from utils.llm_config import create_llm
from crew.tools.db_tools import create_database_query_tool


def create_test_agent() -> Agent:
    """
    Cria agente de teste simples para validar configuração
    
    Returns:
        Agent configurado
    """
    
    llm = create_llm()
    db_tool = create_database_query_tool()
    
    agent = Agent(
        role="Analista de Dados Fiscais",
        goal="Fornecer informações sobre documentos fiscais processados no sistema",
        backstory=(
            "Você é um analista de dados especializado em documentos fiscais brasileiros. "
            "Você tem acesso ao banco de dados do sistema Fiscalia e pode consultar "
            "informações sobre notas fiscais processadas, estatísticas e registros."
        ),
        tools=[db_tool],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    return agent


if __name__ == "__main__":
    """Teste standalone do agente"""
    print("=== Teste de Criação de Agente ===\n")
    
    try:
        agent = create_test_agent()
        print(f"✅ Agente criado com sucesso!")
        print(f"   Role: {agent.role}")
        print(f"   Goal: {agent.goal}")
        print(f"   Tools: {len(agent.tools)} tool(s)")
        print(f"   LLM: {type(agent.llm).__name__}")
        
    except Exception as e:
        print(f"❌ Erro ao criar agente: {e}")
