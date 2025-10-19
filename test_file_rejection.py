"""
Teste específico para validar rejeição de arquivos não suportados
"""

import sys
from pathlib import Path

# Adicionar src ao path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from processors.nfe_processor import NFeProcessor
from database.db_manager import DatabaseManager

def test_rejection():
    """Testa rejeição de arquivos não suportados"""
    
    print("=" * 70)
    print("  🧪 TESTE DE REJEIÇÃO DE ARQUIVOS")
    print("=" * 70)
    
    processor = NFeProcessor()
    pasta_entrados = Path('arquivos/entrados')
    
    # Listar TODOS os arquivos (não só XML)
    all_files = [f for f in pasta_entrados.iterdir() if f.is_file()]
    
    if not all_files:
        print("\n⚠️  Nenhum arquivo encontrado em /entrados")
        print("   Coloque arquivos de teste (.xml, .pdf, .doc, .txt) na pasta")
        return
    
    print(f"\n📁 Encontrados {len(all_files)} arquivo(s) em /entrados:")
    for f in all_files:
        print(f"   - {f.name} ({f.suffix})")
    
    print("\n" + "=" * 70)
    print("  🚀 PROCESSANDO ARQUIVOS")
    print("=" * 70)
    
    results = []
    for file_path in all_files:
        print(f"\n📄 Processando: {file_path.name}")
        print("-" * 70)
        
        result = processor.process_file(file_path)
        results.append((file_path.name, result))
        
        if result['success']:
            print(f"   ✅ SUCESSO: {result['message']}")
        else:
            print(f"   ❌ FALHA: {result['message']}")
    
    # Verificar estado das pastas
    print("\n" + "=" * 70)
    print("  📊 ESTADO DAS PASTAS APÓS PROCESSAMENTO")
    print("=" * 70)
    
    stats = processor.file_handler.get_stats()
    print(f"\n📂 entrados/: {stats['entrados']} arquivo(s)")
    print(f"📂 processados/: {stats['processados']} arquivo(s)")
    print(f"📂 rejeitados/: {stats['rejeitados']} arquivo(s)")
    
    # Verificar registros no banco
    print("\n" + "=" * 70)
    print("  💾 REGISTROS NO BANCO DE DADOS")
    print("=" * 70)
    
    db = DatabaseManager()
    recent_results = db.get_recent_results(10)
    
    print(f"\n📋 Últimos {len(recent_results)} registros:")
    for r in recent_results:
        status = "✅" if r.resultado == "Sucesso" else "❌"
        print(f"   {status} {Path(r.path_nome_arquivo).name}")
        print(f"      └─ {r.causa}")
    
    # Resumo final
    print("\n" + "=" * 70)
    print("  📈 RESUMO")
    print("=" * 70)
    
    sucessos = sum(1 for _, r in results if r['success'])
    falhas = len(results) - sucessos
    
    print(f"\n✅ Sucessos: {sucessos}")
    print(f"❌ Falhas: {falhas}")
    print(f"📊 Total: {len(results)}")
    
    # Validar se arquivos foram movidos
    print("\n" + "=" * 70)
    print("  🔍 VALIDAÇÃO")
    print("=" * 70)
    
    entrados_after = list(pasta_entrados.glob('*.*'))
    
    if entrados_after:
        print(f"\n⚠️  ATENÇÃO: {len(entrados_after)} arquivo(s) ainda em /entrados:")
        for f in entrados_after:
            print(f"   - {f.name}")
        print("\n❌ TESTE FALHOU: Arquivos deveriam ter sido movidos!")
    else:
        print("\n✅ TESTE PASSOU: Todos arquivos foram movidos de /entrados!")

if __name__ == "__main__":
    test_rejection()
