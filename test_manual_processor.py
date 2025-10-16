"""
Script para teste manual do processador de Notas Fiscais
Execute este script para testar o processamento de XMLs
"""

from pathlib import Path
import sys

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.processors.nfe_processor import NFeProcessor
from src.utils.logger import get_logger

logger = get_logger(__name__)


def print_separator():
    """Imprime separador visual"""
    print("\n" + "=" * 80 + "\n")


def test_single_file():
    """Testa processamento de arquivo único"""
    print_separator()
    print("🔍 TESTE: Processamento de Arquivo Único")
    print_separator()
    
    # Caminho do arquivo de teste
    test_file = Path('arquivos_teste_NF/exemplo_nfe.xml')
    
    if not test_file.exists():
        print(f"❌ Arquivo de teste não encontrado: {test_file}")
        print("📝 Crie o arquivo exemplo_nfe.xml na pasta arquivos_teste_NF/")
        return
    
    # Inicializa processador
    processor = NFeProcessor()
    
    # Copia arquivo para entrados
    print(f"📄 Arquivo: {test_file.name}")
    success, copied_file = processor.file_handler.copy_to_entrados(test_file)
    
    if not success:
        print("❌ Erro ao copiar arquivo para pasta entrados/")
        return
    
    print(f"✅ Arquivo copiado para: {copied_file}")
    
    # Processa
    print("\n⚙️  Processando...")
    result = processor.process_single_file(copied_file)
    
    # Exibe resultado
    print_separator()
    print("📊 RESULTADO DO PROCESSAMENTO")
    print_separator()
    
    print(f"Status: {'✅ SUCESSO' if result.success else '❌ FALHA'}")
    print(f"Mensagem: {result.message}")
    print(f"Hash: {result.hash}")
    print(f"Tempo: {result.processing_time:.2f}s")
    
    if result.errors:
        print(f"\n❌ Erros ({len(result.errors)}):")
        for i, error in enumerate(result.errors, 1):
            print(f"   {i}. {error}")
    
    if result.warnings:
        print(f"\n⚠️  Avisos ({len(result.warnings)}):")
        for i, warning in enumerate(result.warnings, 1):
            print(f"   {i}. {warning}")
    
    if result.data:
        print("\n📋 Dados Extraídos:")
        print(f"   Tipo: {result.data.get('tipo_documento')}")
        
        metadata = result.data.get('metadados', {})
        print(f"   Chave: {metadata.get('chave_acesso', 'N/A')[:20]}...")
        print(f"   Número: {metadata.get('numero')}")
        print(f"   Série: {metadata.get('serie')}")
        print(f"   Data: {metadata.get('data_emissao')}")
        
        valores = result.data.get('valores', {})
        print(f"   Valor Total: R$ {valores.get('valor_total', 0):.2f}")
        print(f"   Valor Produtos: R$ {valores.get('valor_produtos', 0):.2f}")
        
        itens = result.data.get('itens', [])
        print(f"   Itens: {len(itens)}")


def test_batch():
    """Testa processamento em batch"""
    print_separator()
    print("📦 TESTE: Processamento em Batch")
    print_separator()
    
    processor = NFeProcessor()
    
    # Verifica arquivos pendentes
    pending = processor.file_handler.get_pending_files()
    print(f"📄 Arquivos pendentes: {len(pending)}")
    
    if not pending:
        print("⚠️  Nenhum arquivo pendente na pasta entrados/")
        print("💡 Copie alguns XMLs para arquivos/entrados/ antes de executar")
        return
    
    for file in pending:
        print(f"   - {file.name}")
    
    # Processa batch
    print("\n⚙️  Processando batch...")
    results = processor.process_batch()
    
    # Estatísticas
    success_count = sum(1 for r in results if r.success)
    failed_count = len(results) - success_count
    
    print_separator()
    print("📊 RESULTADO DO BATCH")
    print_separator()
    
    print(f"Total processado: {len(results)}")
    print(f"✅ Sucesso: {success_count}")
    print(f"❌ Falha: {failed_count}")
    
    # Detalhes por arquivo
    print("\n📄 Detalhes por arquivo:")
    for i, result in enumerate(results, 1):
        status = "✅" if result.success else "❌"
        print(f"\n{i}. {status} {result.file_path.name}")
        print(f"   {result.message}")
        if result.errors:
            print(f"   Erros: {len(result.errors)}")
        if result.warnings:
            print(f"   Avisos: {len(result.warnings)}")


def show_statistics():
    """Exibe estatísticas do sistema"""
    print_separator()
    print("📈 ESTATÍSTICAS DO SISTEMA")
    print_separator()
    
    processor = NFeProcessor()
    stats = processor.get_statistics()
    
    # Estatísticas de arquivos
    file_stats = stats['arquivos']
    print("📁 Arquivos:")
    print(f"   Entrados: {file_stats['entrados']}")
    print(f"   Processados: {file_stats['processados']}")
    print(f"   Rejeitados: {file_stats['rejeitados']}")
    print(f"   Caminho base: {file_stats['base_path']}")
    
    # Estatísticas do banco
    db_stats = stats['banco_dados']
    print("\n💾 Banco de Dados:")
    print(f"   Documentos para ERP: {db_stats.get('total_docs_para_erp', 0)}")
    print(f"   Registros de resultado: {db_stats.get('total_registros_resultado', 0)}")
    print(f"   Sucesso: {db_stats.get('sucesso', 0)}")
    print(f"   Insucesso: {db_stats.get('insucesso', 0)}")
    
    print(f"\n🕐 Última atualização: {stats['timestamp']}")


def show_menu():
    """Exibe menu principal"""
    print_separator()
    print("🏢 SISTEMA FISCALIA - TESTE DE PROCESSADORES")
    print_separator()
    
    print("\nOpções:")
    print("  1. Testar arquivo único (exemplo_nfe.xml)")
    print("  2. Processar batch (todos em entrados/)")
    print("  3. Ver estatísticas")
    print("  4. Executar testes pytest")
    print("  0. Sair")
    
    choice = input("\nEscolha uma opção: ").strip()
    return choice


def run_pytest():
    """Executa os testes pytest"""
    print_separator()
    print("🧪 EXECUTANDO TESTES PYTEST")
    print_separator()
    
    import pytest
    pytest.main([
        'tests/test_xml_processor.py',
        '-v',
        '--tb=short'
    ])


def main():
    """Função principal"""
    while True:
        choice = show_menu()
        
        if choice == '1':
            test_single_file()
            input("\nPressione ENTER para continuar...")
        
        elif choice == '2':
            test_batch()
            input("\nPressione ENTER para continuar...")
        
        elif choice == '3':
            show_statistics()
            input("\nPressione ENTER para continuar...")
        
        elif choice == '4':
            run_pytest()
            input("\nPressione ENTER para continuar...")
        
        elif choice == '0':
            print("\n👋 Até logo!\n")
            break
        
        else:
            print("\n❌ Opção inválida! Tente novamente.")
            input("\nPressione ENTER para continuar...")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrompido pelo usuário. Até logo!\n")
    except Exception as e:
        logger.error(f"Erro inesperado: {e}", exc_info=True)
        print(f"\n❌ Erro inesperado: {e}\n")
        sys.exit(1)
