# src/crew/agents/xml_agents.py - ARQUIVO COMPLETO

"""
Agentes especializados para processamento de XMLs de Notas Fiscais
"""

from crewai import Agent
import sys
from pathlib import Path

# Adicionar src ao path
src_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(src_path))

from utils.llm_config import create_llm
from crew.tools.xml_tools import (
    create_batch_processor_tool,
    create_single_xml_processor_tool
)
from crew.tools.fiscal_tools import create_fiscal_analysis_tool
from crew.tools.db_tools import create_database_query_tool


def create_xml_processing_coordinator() -> Agent:
    """
    Agente Coordenador de Processamento XML
    Responsável por orquestrar o processamento de arquivos XML
    """
    
    llm = create_llm()
    
    agent = Agent(
        role="Coordenador de Processamento XML",
        goal="Processar eficientemente arquivos XML de Notas Fiscais, garantindo que todos os documentos sejam extraídos, validados e armazenados corretamente",
        backstory=(
            "Você é um especialista em processamento de documentos fiscais eletrônicos brasileiros. "
            "Com anos de experiência em NFe/NFCe, você coordena o processamento de XMLs com precisão, "
            "garantindo que cada nota fiscal seja corretamente extraída e validada conforme a legislação brasileira. "
            "Você identifica rapidamente problemas nos arquivos e reporta de forma clara e objetiva."
        ),
        tools=[
            create_single_xml_processor_tool(),
            create_batch_processor_tool(),
            create_database_query_tool()
        ],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=3  # Limitar iterações para ser mais rápido
    )
    
    return agent


def create_fiscal_compliance_auditor() -> Agent:
    """
    Agente Auditor de Conformidade Fiscal
    Responsável por validar conformidade e detectar inconsistências
    """
    
    llm = create_llm()
    
    agent = Agent(
        role="Auditor de Conformidade Fiscal",
        goal="Garantir que todos os documentos fiscais processados estejam em conformidade com a legislação brasileira e identificar anomalias ou inconsistências",
        backstory=(
            "Você é um auditor fiscal experiente com profundo conhecimento da legislação tributária brasileira. "
            "Especializado em NFe/NFCe, você analisa padrões de documentos fiscais, detecta valores atípicos, "
            "identifica possíveis erros de preenchimento e garante conformidade com CFOP, NCM, CST e cálculos de impostos. "
            "Seu olhar crítico ajuda empresas a evitarem problemas com o fisco e otimizarem sua carga tributária."
        ),
        tools=[
            create_fiscal_analysis_tool(),
            create_database_query_tool()
        ],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=3
    )
    
    return agent


def create_business_analyst() -> Agent:
    """
    Agente Analista de Negócios
    Responsável por gerar insights e relatórios executivos
    """
    
    llm = create_llm()
    
    agent = Agent(
        role="Analista de Business Intelligence Fiscal",
        goal="Transformar dados fiscais em insights acionáveis e relatórios executivos que auxiliem na tomada de decisão estratégica",
        backstory=(
            "Você é um analista de BI especializado em dados fiscais e financeiros. "
            "Com habilidade única para identificar padrões e tendências, você transforma números complexos "
            "em informações claras e acionáveis. Você cria relatórios executivos que destacam os principais "
            "KPIs, identifica oportunidades de economia tributária e aponta riscos operacionais. "
            "Sua análise ajuda gestores a tomarem decisões informadas baseadas em dados reais."
        ),
        tools=[
            create_fiscal_analysis_tool(),
            create_database_query_tool()
        ],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=3
    )
    
    return agent


if __name__ == "__main__":
    """Teste standalone dos agentes"""
    print("=== Teste de Criação de Agentes XML ===\n")
    
    try:
        # Teste 1: Coordenador
        print("1. Criando XML Processing Coordinator...")
        coordinator = create_xml_processing_coordinator()
        print(f"   ✅ {coordinator.role}")
        print(f"   Tools: {len(coordinator.tools)}\n")
        
        # Teste 2: Auditor
        print("2. Criando Fiscal Compliance Auditor...")
        auditor = create_fiscal_compliance_auditor()
        print(f"   ✅ {auditor.role}")
        print(f"   Tools: {len(auditor.tools)}\n")
        
        # Teste 3: Analista
        print("3. Criando Business Analyst...")
        analyst = create_business_analyst()
        print(f"   ✅ {analyst.role}")
        print(f"   Tools: {len(analyst.tools)}\n")
        
        print("✅ Todos os agentes criados com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao criar agentes: {e}")
        import traceback
        traceback.print_exc()
