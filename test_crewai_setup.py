# test_crewai_setup.py - ARQUIVO COMPLETO CORRIGIDO

"""
Script de teste para validar configuração CrewAI + LLM
"""

import sys
from pathlib import Path

# CRÍTICO: Adicionar src ao path ANTES de qualquer import
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

# Agora podemos importar
from utils.llm_config import verify_llm_connection, get_provider_name, create_llm
from crew.tools.db_tools import create_database_query_tool
from crew.agents.test_agent import create_test_agent
from crewai import Task, Crew


def test_1_llm_config():
    """Teste 1: Configuração LLM"""
    print("\n" + "="*60)
    print("TESTE 1: Configuração LLM")
    print("="*60)
    
    try:
        if verify_llm_connection():
            print("✅ Configuração LLM válida!")
            return True
        else:
            print("❌ Configuração LLM inválida!")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_2_llm_creation():
    """Teste 2: Criação de LLM"""
    print("\n" + "="*60)
    print("TESTE 2: Criação de LLM")
    print("="*60)
    
    try:
        llm = create_llm()
        provider = get_provider_name()
        print(f"✅ LLM criada: {type(llm).__name__}")
        print(f"✅ Provider ativo: {provider}")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar LLM: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_3_database_tool():
    """Teste 3: Database Tool"""
    print("\n" + "="*60)
    print("TESTE 3: Database Tool")
    print("="*60)
    
    try:
        tool = create_database_query_tool()
        print(f"✅ Tool criada: {tool.name}")
        
        # Testar consulta
        result = tool._run("stats")
        print("\nResultado da consulta:")
        print(result)
        
        return True
    except Exception as e:
        print(f"❌ Erro ao testar tool: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_4_agent_creation():
    """Teste 4: Criação de Agente"""
    print("\n" + "="*60)
    print("TESTE 4: Criação de Agente")
    print("="*60)
    
    try:
        agent = create_test_agent()
        print(f"✅ Agente criado: {agent.role}")
        print(f"   Tools disponíveis: {len(agent.tools)}")
        print(f"   LLM: {type(agent.llm).__name__}")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar agente: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_5_simple_crew():
    """Teste 5: Crew Simples com Task"""
    print("\n" + "="*60)
    print("TESTE 5: Crew com Task Simples")
    print("="*60)
    
    try:
        # Criar agente
        agent = create_test_agent()
        
        # Criar task simples
        task = Task(
            description=(
                "Consulte o banco de dados e me informe quantos documentos "
                "fiscais foram processados no sistema Fiscalia."
            ),
            expected_output="Número total de documentos processados",
            agent=agent
        )
        
        # Criar crew
        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=True
        )
        
        print("\n🚀 Executando Crew...\n")
        
        # Executar
        result = crew.kickoff()
        
        print("\n" + "="*60)
        print("RESULTADO:")
        print("="*60)
        print(result)
        
        print("\n✅ Crew executado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao executar crew: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Executa todos os testes"""
    print("\n" + "="*60)
    print("🧪 TESTE COMPLETO DE CONFIGURAÇÃO CREWAI")
    print("="*60)
    print(f"Python Path: {sys.path[0]}")
    
    results = []
    
    # Executar testes em sequência
    results.append(("Configuração LLM", test_1_llm_config()))
    
    if not results[0][1]:
        print("\n⚠️ Primeiro teste falhou. Verifique .env e API keys.")
        return
    
    results.append(("Criação LLM", test_2_llm_creation()))
    results.append(("Database Tool", test_3_database_tool()))
    results.append(("Criação Agente", test_4_agent_creation()))
    results.append(("Crew Simples", test_5_simple_crew()))
    
    # Resumo
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES")
    print("="*60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print("\n" + "="*60)
    print(f"Total: {passed}/{len(results)} testes passaram")
    print("="*60)
    
    if passed == len(results):
        print("\n🎉 TODOS OS TESTES PASSARAM! Sistema pronto para usar.")
    else:
        print(f"\n⚠️  {len(results) - passed} teste(s) falharam. Verificar erros acima.")


if __name__ == "__main__":
    main()
