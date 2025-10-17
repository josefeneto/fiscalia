# teste_xml_raw.py
import xml.etree.ElementTree as ET
from pathlib import Path

xml_file = Path('arquivos/entrados/NFe00120954494003622218027814120519723516936553.xml')

tree = ET.parse(xml_file)
root = tree.getroot()

print(f"Root tag: {root.tag}")
print(f"Root attrib: {root.attrib}")

# Buscar infNFe
inf_nfe = root.find('.//infNFe')
if inf_nfe is not None:
    print(f"infNFe Id: {inf_nfe.get('Id')}")
else:
    print("❌ infNFe não encontrado")

# Buscar nNF
nnf = root.find('.//ide/nNF')
if nnf is not None:
    print(f"Número NF: {nnf.text}")
else:
    print("❌ nNF não encontrado")

# Buscar emit
emit = root.find('.//emit/xNome')
if emit is not None:
    print(f"Emitente: {emit.text}")
else:
    print("❌ emit não encontrado")
