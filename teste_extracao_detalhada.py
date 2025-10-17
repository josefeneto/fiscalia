# teste_extracao_detalhada.py
from pathlib import Path
from src.processors.xml_processor import XMLProcessor
import json

xml_file = Path('arquivos/entrados/NFe00120954494003622218027814120519723516936553.xml')

processor = XMLProcessor()
if processor.load_xml(xml_file):
    data = processor.extract_data()
    
    print("=" * 80)
    print("DADOS EXTRAÍDOS DO XML:")
    print("=" * 80)
    print(json.dumps(data, indent=2, ensure_ascii=False, default=str))
    print("=" * 80)
else:
    print("❌ Erro ao carregar XML")
