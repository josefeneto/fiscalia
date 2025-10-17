# copy_test_xmls.py - ARQUIVO COMPLETO (criar na raiz)

"""
Helper para copiar XMLs de teste para pasta /entrados
"""

import shutil
from pathlib import Path

def copy_test_files():
    """Copia arquivos XML de teste para /entrados"""
    
    # Paths
    project_root = Path(__file__).parent
    source = project_root / "arquivos_teste_NF"
    dest = project_root / "arquivos" / "entrados"
    
    # Verificar source
    if not source.exists():
        print(f"❌ Pasta de teste não encontrada: {source}")
        print("\n💡 Certifique-se que a pasta arquivos_teste_NF existe")
        return
    
    # Buscar XMLs
    xml_files = list(source.glob("*.xml"))
    
    if not xml_files:
        print(f"⚠️  Nenhum arquivo XML encontrado em {source}")
        return
    
    print(f"📁 Encontrados {len(xml_files)} arquivo(s) XML\n")
    print(f"Origem: {source}")
    print(f"Destino: {dest}\n")
    
    # Perguntar quantos copiar
    print(f"Quantos arquivos deseja copiar? (1-{len(xml_files)})")
    try:
        n = int(input("Quantidade [5]: ") or "5")
        n = min(n, len(xml_files))
    except:
        n = 5
    
    # Copiar
    print(f"\n🔄 Copiando {n} arquivo(s)...")
    
    copied = 0
    for xml_file in xml_files[:n]:
        try:
            dest_file = dest / xml_file.name
            shutil.copy2(xml_file, dest_file)
            print(f"  ✅ {xml_file.name}")
            copied += 1
        except Exception as e:
            print(f"  ❌ {xml_file.name}: {e}")
    
    print(f"\n✅ {copied} arquivo(s) copiado(s) com sucesso!")
    print(f"📁 Destino: {dest}")
    print("\n💡 Agora você pode executar: python test_xml_crew_complete.py")


if __name__ == "__main__":
    print("="*70)
    print("  📋 COPIAR ARQUIVOS XML DE TESTE")
    print("="*70 + "\n")
    
    copy_test_files()
