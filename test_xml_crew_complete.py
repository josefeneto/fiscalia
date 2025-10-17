# test_xml_crew_complete.py - ARQUIVO COMPLETO CORRIGIDO

"""
Teste completo do sistema XML CrewAI
Testa tools, agentes e crews com XMLs reais
"""

import sys
from pathlib import Path

# Adicionar src ao path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from crew.tools.xml_tools import create_batch_processor_tool, create_single_xml_processor_tool
from crew.tools.fiscal_tools import create_fiscal_analysis_tool
from crew.tools.db_tools import create_database_query_tool
from crew.agents.xml_agents import (
    create_xml_processing_coordinator,
    create_fiscal_compliance_auditor,
    create_business_analyst
)
from crew.crews.xml_crew import SingleXMLCrew, BatchXMLCrew, AnalysisOnlyCrew
from utils.config import get_settings


def print_section(title: str):
    """Helper para imprimir seções"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def test_1_tools():
    """Teste 1: Validar todas as tools"""
    print_section("TESTE 1: TOOLS")
    
    results = []
    
    # Tool 1: Database Query
    try:
        print("1.1 DatabaseQueryTool...")
        tool = create_database_query_tool()
        result = tool._run("stats")
        print(f"✅ {tool.name} - OK")
        print(f"    Resultado: {result[:100]}...")
        results.append(("DatabaseQueryTool", True))
    except Exception as e:
        print(f"❌ DatabaseQueryTool - ERRO: {e}")
        results.append(("DatabaseQueryTool", False))
    
    # Tool 2: Fiscal Analysis
    try:
        print("\n1.2 FiscalAnalysisTool...")
        tool = create_fiscal_analysis_tool()
        result = tool._run("summary")
        print(f"✅ {tool.name} - OK")
        print(f"    Resultado: {result[:100]}...")
        results.append(("FiscalAnalysisTool", True))
    except Exception as e:
        print(f"❌ FiscalAnalysisTool - ERRO: {e}")
        results.append(("FiscalAnalysisTool", False))
    
    # Tool 3: Single XML Processor
    try:
        print("\n1.3 SingleXMLProcessorTool...")
        tool = create_single_xml_processor_tool()
        print(f"✅ {tool.name} - OK (criada)")
        results.append(("SingleXMLProcessorTool", True))
    except Exception as e:
        print(f"❌ SingleXMLProcessorTool - ERRO: {e}")
        results.append(("SingleXMLProcessorTool", False))
    
    # Tool 4: Batch XML Processor
    try:
        print("\n1.4 BatchProcessorTool...")
        tool = create_batch_processor_tool()
        print(f"✅ {tool.name} - OK (criada)")
        results.append(("BatchProcessorTool", True))
    except Exception as e:
        print(f"❌ BatchProcessorTool - ERRO: {e}")
        results.append(("BatchProcessorTool", False))
    
    return results


def test_2_agents():
    """Teste 2: Criar todos os agentes"""
    print_section("TESTE 2: AGENTES")
    
    results = []
    
    # Agente 1: Coordinator
    try:
        print("2.1 XML Processing Coordinator...")
        agent = create_xml_processing_coordinator()
        print(f"✅ {agent.role}")
        print(f"    Tools: {len(agent.tools)}")
        print(f"    LLM: {type(agent.llm).__name__}")
        results.append(("Coordinator", True))
    except Exception as e:
        print(f"❌ Coordinator - ERRO: {e}")
        results.append(("Coordinator", False))
    
    # Agente 2: Auditor
    try:
        print("\n2.2 Fiscal Compliance Auditor...")
        agent = create_fiscal_compliance_auditor()
        print(f"✅ {agent.role}")
        print(f"    Tools: {len(agent.tools)}")
        print(f"    LLM: {type(agent.llm).__name__}")
        results.append(("Auditor", True))
    except Exception as e:
        print(f"❌ Auditor - ERRO: {e}")
        results.append(("Auditor", False))
    
    # Agente 3: Analyst
    try:
        print("\n2.3 Business Analyst...")
        agent = create_business_analyst()
        print(f"✅ {agent.role}")
        print(f"    Tools: {len(agent.tools)}")
        print(f"    LLM: {type(agent.llm).__name__}")
        results.append(("Analyst", True))
    except Exception as e:
        print(f"❌ Analyst - ERRO: {e}")
        results.append(("Analyst", False))
    
    return results


def test_3_crews():
    """Teste 3: Criar todas as crews"""
    print_section("TESTE 3: CREWS")
    
    results = []
    
    # Crew 1: Single XML
    try:
        print("3.1 SingleXMLCrew...")
        crew = SingleXMLCrew()
        print("✅ SingleXMLCrew criado")
        print("    Agentes: 1 (Coordinator)")
        results.append(("SingleXMLCrew", True))
    except Exception as e:
        print(f"❌ SingleXMLCrew - ERRO: {e}")
        results.append(("SingleXMLCrew", False))
    
    # Crew 2: Batch XML
    try:
        print("\n3.2 BatchXMLCrew...")
        crew = BatchXMLCrew()
        print("✅ BatchXMLCrew criado")
        print("    Agentes: 3 (Coordinator, Auditor, Analyst)")
        results.append(("BatchXMLCrew", True))
    except Exception as e:
        print(f"❌ BatchXMLCrew - ERRO: {e}")
        results.append(("BatchXMLCrew", False))
    
    # Crew 3: Analysis Only
    try:
        print("\n3.3 AnalysisOnlyCrew...")
        crew = AnalysisOnlyCrew()
        print("✅ AnalysisOnlyCrew criado")
        print("    Agentes: 2 (Auditor, Analyst)")
        results.append(("AnalysisOnlyCrew", True))
    except Exception as e:
        print(f"❌ AnalysisOnlyCrew - ERRO: {e}")
        results.append(("AnalysisOnlyCrew", False))
    
    return results


def test_4_batch_processing():
    """Teste 4: Processamento batch real (OPCIONAL - só se tiver XMLs)"""
    print_section("TESTE 4: PROCESSAMENTO BATCH (OPCIONAL)")
    
    settings = get_settings()
    pasta_entrados = settings.pasta_entrados
    
    # Verificar se há XMLs para processar
    xml_files = list(pasta_entrados.glob("*.xml"))
    
    if not xml_files:
        print("⚠️  Nenhum arquivo XML encontrado em /entrados")
        print(f"   Pasta: {pasta_entrados}")
        print("\n💡 DICA: Copie alguns XMLs de teste para a pasta /entrados")
        print("   Exemplo: arquivos_teste_NF/*.xml -> arquivos/entrados/")
        return [("Batch Processing", "Skipped")]
    
    print(f"📁 Encontrados {len(xml_files)} arquivo(s) XML em /entrados")
    print(f"   Pasta: {pasta_entrados}\n")
    
    resposta = input("Deseja processar estes arquivos? [s/N]: ").lower()
    
    if resposta != 's':
        print("⏭️  Processamento batch pulado pelo usuário")
        return [("Batch Processing", "Skipped")]
    
    try:
        print("\n🚀 Iniciando processamento batch...\n")
        
        crew = BatchXMLCrew()
        result = crew.process(folder_path="entrados", max_files=10)
        
        if result['success']:
            print("\n✅ PROCESSAMENTO BATCH COMPLETO!")
            print("\nRESULTADO:")
            print("="*70)
            print(result['result'])
            print("="*70)
            return [("Batch Processing", True)]
        else:
            print(f"\n❌ Erro no processamento: {result['error']}")
            return [("Batch Processing", False)]
            
    except Exception as e:
        print(f"\n❌ Erro no processamento batch: {e}")
        import traceback
        traceback.print_exc()
        return [("Batch Processing", False)]


def test_5_analysis_only():
    """Teste 5: Análise de documentos existentes"""
    print_section("TESTE 5: ANÁLISE DE DOCUMENTOS EXISTENTES")
    
    # Verificar se há documentos no banco
    from database.db_manager import DatabaseManager
    db = DatabaseManager()
    count = db.count_documents()
    
    if count == 0:
        print("⚠️  Nenhum documento no banco de dados")
        print("   Pulando análise (sem dados para analisar)")
        return [("Analysis Only", "Skipped")]
    
    print(f"📊 Encontrados {count} documento(s) no banco de dados\n")
    
    resposta = input("Deseja executar análise completa? [s/N]: ").lower()
    
    if resposta != 's':
        print("⏭️  Análise pulada pelo usuário")
        return [("Analysis Only", "Skipped")]
    
    try:
        print("\n🚀 Iniciando análise completa...\n")
        
        crew = AnalysisOnlyCrew()
        result = crew.analyze()
        
        if result['success']:
            print("\n✅ ANÁLISE COMPLETA!")
            print("\nRESULTADO:")
            print("="*70)
            print(result['result'])
            print("="*70)
            return [("Analysis Only", True)]
        else:
            print(f"\n❌ Erro na análise: {result['error']}")
            return [("Analysis Only", False)]
            
    except Exception as e:
        print(f"\n❌ Erro na análise: {e}")
        import traceback
        traceback.print_exc()
        return [("Analysis Only", False)]


def print_summary(all_results):
    """Imprime resumo final"""
    print_section("📊 RESUMO FINAL DOS TESTES")
    
    total = 0
    passed = 0
    skipped = 0
    
    for test_name, results in all_results.items():
        print(f"\n{test_name}:")
        for name, status in results:
            if status == "Skipped":
                print(f"  ⏭️  {name} - PULADO")
                skipped += 1
            elif status:
                print(f"  ✅ {name} - PASS")
                passed += 1
            else:
                print(f"  ❌ {name} - FAIL")
            total += 1
    
    print("\n" + "="*70)
    print(f"TOTAL: {passed}/{total - skipped} testes passaram ({skipped} pulados)")
    print("="*70)
    
    if passed == total - skipped and total > 0:
        print("\n🎉 TODOS OS TESTES DISPONÍVEIS PASSARAM!")
        print("✅ Sistema XML CrewAI pronto para uso!")
    elif passed > 0:
        print(f"\n⚠️  {total - skipped - passed} teste(s) falharam")
        print("   Verifique os erros acima")
    else:
        print("\n❌ Todos os testes falharam. Verificar configuração.")


def main():
    """Executa todos os testes"""
    print("\n" + "="*70)
    print("  🧪 TESTE COMPLETO DO SISTEMA XML CREWAI")
    print("="*70)
    
    all_results = {}
    
    # Teste 1: Tools
    all_results["TESTE 1: TOOLS"] = test_1_tools()
    
    # Teste 2: Agentes
    all_results["TESTE 2: AGENTES"] = test_2_agents()
    
    # Teste 3: Crews
    all_results["TESTE 3: CREWS"] = test_3_crews()
    
    # Teste 4: Batch Processing (opcional)
    all_results["TESTE 4: BATCH PROCESSING"] = test_4_batch_processing()
    
    # Teste 5: Analysis Only (opcional)
    all_results["TESTE 5: ANALYSIS ONLY"] = test_5_analysis_only()
    
    # Resumo final
    print_summary(all_results)


if __name__ == "__main__":
    main()
