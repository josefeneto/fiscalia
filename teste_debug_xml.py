# teste_debug_xml.py
from pathlib import Path
from src.processors.xml_processor import XMLProcessor

xml_file = Path('arquivos/entrados/NFe00120954494003622218027814120519723516936553.xml')

processor = XMLProcessor()
if processor.load_xml(xml_file):
    data = processor.extract_data()
    
    print("=" * 60)
    print("DADOS EXTRAÍDOS:")
    print("=" * 60)
    print(f"Chave de acesso: {data.get('metadata', {}).get('chave_acesso')}")
    print(f"Número NF: {data.get('metadata', {}).get('numero')}")
    print(f"Série: {data.get('metadata', {}).get('serie')}")
    print(f"Emitente: {data.get('emitente', {}).get('xNome')}")
    print(f"CNPJ Emitente: {data.get('emitente', {}).get('CNPJ')}")
    print("=" * 60)
else:
    print("❌ Erro ao carregar XML")
