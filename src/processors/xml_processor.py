"""
Processador de arquivos XML de documentos fiscais
Suporta NFe, NFCe, CTe e MDFe
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib

from utils.logger import setup_logger

logger = setup_logger(__name__)


class XMLProcessor:
    """Processador genérico de XMLs fiscais"""
    
    def __init__(self):
        """Inicializa o processador XML"""
        self.current_file: Optional[Path] = None
        self.xml_root: Optional[ET.Element] = None
        self.root: Optional[ET.Element] = None  # Alias para compatibilidade
        self.tree: Optional[ET.ElementTree] = None
        self.doc_type: Optional[str] = None
        self.ns: Dict[str, str] = {}  # Namespace (vazio por padrão)
    
    def load_xml(self, file_path: Path) -> bool:
        """
        Carrega arquivo XML
        
        Args:
            file_path: Caminho do arquivo XML
            
        Returns:
            True se carregou com sucesso, False caso contrário
        """
        try:
            self.current_file = file_path
            self.tree = ET.parse(file_path)
            self.xml_root = self.tree.getroot()
            self.root = self.xml_root  # Alias para compatibilidade
            
            # Detectar namespace (se houver)
            if self.root.tag.startswith('{'):
                # Tem namespace
                ns_match = self.root.tag[1:].split('}')[0]
                self.ns = {'ns': ns_match}
            else:
                # Sem namespace
                self.ns = {}
            
            # Detectar tipo de documento
            self.doc_type = self._detect_doc_type()
            
            logger.info(f"XML carregado: {file_path.name} (Tipo: {self.doc_type})")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao carregar XML {file_path}: {e}")
            return False
    
    def _detect_doc_type(self) -> str:
        """
        Detecta tipo de documento fiscal
        
        Returns:
            Tipo do documento (NFe, NFCe, CTe, MDFe)
        """
        root_tag = self.xml_root.tag.lower()
        
        if 'nfe' in root_tag or 'nfeproc' in root_tag:
            # Verifica se é NFCe (modelo 65) ou NFe (modelo 55)
            modelo = self._get_text('ide/mod', '55')
            return 'NFCe' if modelo == '65' else 'NFe'
        elif 'cte' in root_tag:
            return 'CTe'
        elif 'mdfe' in root_tag:
            return 'MDFe'
        else:
            return 'Unknown'
    
    def extract_data(self) -> Dict[str, Any]:
        """
        Extrai dados do XML carregado
        
        Returns:
            Dicionário com dados estruturados do documento
        """
        if self.xml_root is None:
            logger.error("Nenhum XML carregado")
            return {}
        
        try:
            data = {
                'metadata': self._extract_metadata(),
                'emitente': self._extract_emitente(),
                'destinatario': self._extract_destinatario(),
                'valores': self._extract_valores(),
                'impostos': self._extract_impostos(),
                'itens': self._extract_itens(),
                'transporte': self._extract_transporte(),
                'file_hash': self.calculate_file_hash()
            }
            
            return data
            
        except Exception as e:
            logger.error(f"Erro ao extrair dados: {e}")
            return {}
    
    def calculate_file_hash(self) -> str:
        """Calcula hash SHA256 do arquivo"""
        if not self.current_file or not self.current_file.exists():
            return ''
        
        try:
            with open(self.current_file, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            logger.error(f"Erro ao calcular hash: {e}")
            return ''
    
    def _extract_metadata(self) -> Dict[str, Any]:
        """Extrai metadados do documento"""
        # Tenta extrair chave de acesso de várias formas
        chave = self._get_text('protNFe/infProt/chNFe')
        if not chave:
            chave = self._get_text('infNFe', attr='Id', default='')
            if chave:
                chave = chave.replace('NFe', '')
        
        return {
            'chave_acesso': chave,
            'numero': self._get_text('ide/nNF'),
            'serie': self._get_text('ide/serie'),
            'data_emissao': self._parse_date(self._get_text('ide/dhEmi') or self._get_text('ide/dEmi')),
            'data_saida': self._parse_date(self._get_text('ide/dhSaiEnt') or self._get_text('ide/dSaiEnt')),
            'modelo': self._get_text('ide/mod'),
            'natureza_operacao': self._get_text('ide/natOp'),
            'tipo_operacao': self._get_text('ide/tpNF'),  # 0=Entrada, 1=Saída
            'finalidade': self._get_text('ide/finNFe'),
            'versao': self._get_text('infNFe', attr='versao'),
        }
    
    def _extract_emitente(self) -> Dict[str, Any]:
        """Extrai dados do emitente"""
        return {
            'CNPJ': self._get_text('emit/CNPJ'),
            'CPF': self._get_text('emit/CPF'),
            'xNome': self._get_text('emit/xNome'),
            'xFant': self._get_text('emit/xFant'),
            'IE': self._get_text('emit/IE'),
            'IEST': self._get_text('emit/IEST'),
            'IM': self._get_text('emit/IM'),
            'CNAE': self._get_text('emit/CNAE'),
            'CRT': self._get_text('emit/CRT'),
            'enderEmit': {
                'xLgr': self._get_text('emit/enderEmit/xLgr'),
                'nro': self._get_text('emit/enderEmit/nro'),
                'xCpl': self._get_text('emit/enderEmit/xCpl'),
                'xBairro': self._get_text('emit/enderEmit/xBairro'),
                'cMun': self._get_text('emit/enderEmit/cMun'),
                'xMun': self._get_text('emit/enderEmit/xMun'),
                'UF': self._get_text('emit/enderEmit/UF'),
                'CEP': self._get_text('emit/enderEmit/CEP'),
                'cPais': self._get_text('emit/enderEmit/cPais'),
                'xPais': self._get_text('emit/enderEmit/xPais'),
                'fone': self._get_text('emit/enderEmit/fone'),
            }
        }
    
    def _extract_destinatario(self) -> Dict[str, Any]:
        """Extrai dados do destinatário"""
        return {
            'CNPJ': self._get_text('dest/CNPJ'),
            'CPF': self._get_text('dest/CPF'),
            'idEstrangeiro': self._get_text('dest/idEstrangeiro'),
            'xNome': self._get_text('dest/xNome'),
            'IE': self._get_text('dest/IE'),
            'ISUF': self._get_text('dest/ISUF'),
            'IM': self._get_text('dest/IM'),
            'email': self._get_text('dest/email'),
            'enderDest': {
                'xLgr': self._get_text('dest/enderDest/xLgr'),
                'nro': self._get_text('dest/enderDest/nro'),
                'xCpl': self._get_text('dest/enderDest/xCpl'),
                'xBairro': self._get_text('dest/enderDest/xBairro'),
                'cMun': self._get_text('dest/enderDest/cMun'),
                'xMun': self._get_text('dest/enderDest/xMun'),
                'UF': self._get_text('dest/enderDest/UF'),
                'CEP': self._get_text('dest/enderDest/CEP'),
                'cPais': self._get_text('dest/enderDest/cPais'),
                'xPais': self._get_text('dest/enderDest/xPais'),
                'fone': self._get_text('dest/enderDest/fone'),
            }
        }
    
    def _extract_valores(self) -> Dict[str, Any]:
        """Extrai valores totais"""
        return {
            'vBC': self._get_decimal('total/ICMSTot/vBC'),
            'vICMS': self._get_decimal('total/ICMSTot/vICMS'),
            'vICMSDeson': self._get_decimal('total/ICMSTot/vICMSDeson'),
            'vFCP': self._get_decimal('total/ICMSTot/vFCP'),
            'vBCST': self._get_decimal('total/ICMSTot/vBCST'),
            'vST': self._get_decimal('total/ICMSTot/vST'),
            'vFCPST': self._get_decimal('total/ICMSTot/vFCPST'),
            'vFCPSTRet': self._get_decimal('total/ICMSTot/vFCPSTRet'),
            'vProd': self._get_decimal('total/ICMSTot/vProd'),
            'vFrete': self._get_decimal('total/ICMSTot/vFrete'),
            'vSeg': self._get_decimal('total/ICMSTot/vSeg'),
            'vDesc': self._get_decimal('total/ICMSTot/vDesc'),
            'vII': self._get_decimal('total/ICMSTot/vII'),
            'vIPI': self._get_decimal('total/ICMSTot/vIPI'),
            'vIPIDevol': self._get_decimal('total/ICMSTot/vIPIDevol'),
            'vPIS': self._get_decimal('total/ICMSTot/vPIS'),
            'vCOFINS': self._get_decimal('total/ICMSTot/vCOFINS'),
            'vOutro': self._get_decimal('total/ICMSTot/vOutro'),
            'vNF': self._get_decimal('total/ICMSTot/vNF'),
            'vTotTrib': self._get_decimal('total/ICMSTot/vTotTrib'),
        }
    
    def _extract_impostos(self) -> Dict[str, Any]:
        """Extrai resumo de impostos"""
        valores = self._extract_valores()
        
        return {
            'ICMS': valores.get('vICMS', 0.0),
            'IPI': valores.get('vIPI', 0.0),
            'PIS': valores.get('vPIS', 0.0),
            'COFINS': valores.get('vCOFINS', 0.0),
            'total': (
                valores.get('vICMS', 0.0) +
                valores.get('vIPI', 0.0) +
                valores.get('vPIS', 0.0) +
                valores.get('vCOFINS', 0.0)
            )
        }
    
    def _extract_itens(self) -> List[Dict[str, Any]]:
        """Extrai itens/produtos da nota"""
        itens = []
        
        # Buscar todos os elementos 'det'
        det_elements = self._find_all('det')
        
        for det in det_elements:
            def get_prod_text(tag: str, default: str = '') -> str:
                """Helper para buscar texto dentro de prod"""
                elem = det.find(f'.//prod/{tag}')
                return elem.text if elem is not None and elem.text else default
            
            def get_prod_decimal(tag: str, default: float = 0.0) -> float:
                """Helper para buscar decimal dentro de prod"""
                text = get_prod_text(tag)
                try:
                    return float(text) if text else default
                except (ValueError, TypeError):
                    return default
            
            item = {
                'nItem': det.get('nItem', ''),
                'cProd': get_prod_text('cProd'),
                'cEAN': get_prod_text('cEAN'),
                'xProd': get_prod_text('xProd'),
                'NCM': get_prod_text('NCM'),
                'CEST': get_prod_text('CEST'),
                'CFOP': get_prod_text('CFOP'),
                'uCom': get_prod_text('uCom'),
                'qCom': get_prod_decimal('qCom'),
                'vUnCom': get_prod_decimal('vUnCom'),
                'vProd': get_prod_decimal('vProd'),
                'cEANTrib': get_prod_text('cEANTrib'),
                'uTrib': get_prod_text('uTrib'),
                'qTrib': get_prod_decimal('qTrib'),
                'vUnTrib': get_prod_decimal('vUnTrib'),
                'vFrete': get_prod_decimal('vFrete'),
                'vSeg': get_prod_decimal('vSeg'),
                'vDesc': get_prod_decimal('vDesc'),
                'vOutro': get_prod_decimal('vOutro'),
            }
            
            itens.append(item)
        
        return itens
    
    def _extract_transporte(self) -> Dict[str, Any]:
        """Extrai informações de transporte"""
        return {
            'modFrete': self._get_text('transp/modFrete'),
            'transporta': {
                'CNPJ': self._get_text('transp/transporta/CNPJ'),
                'CPF': self._get_text('transp/transporta/CPF'),
                'xNome': self._get_text('transp/transporta/xNome'),
                'IE': self._get_text('transp/transporta/IE'),
                'xEnder': self._get_text('transp/transporta/xEnder'),
                'xMun': self._get_text('transp/transporta/xMun'),
                'UF': self._get_text('transp/transporta/UF'),
            },
            'veicTransp': {
                'placa': self._get_text('transp/veicTransp/placa'),
                'UF': self._get_text('transp/veicTransp/UF'),
                'RNTC': self._get_text('transp/veicTransp/RNTC'),
            }
        }
    
    def _get_text(self, path: str, default: str = '', attr: Optional[str] = None) -> str:
        """
        Extrai texto de elemento XML
        
        Args:
            path: Caminho XPath do elemento
            default: Valor padrão se não encontrado
            attr: Nome do atributo (opcional)
        
        Returns:
            Texto do elemento ou valor do atributo
        """
        try:
            # Se tiver namespace, ajusta o path
            if self.ns:
                # Adiciona ns: antes de cada tag no path
                ns_path = '/'.join([f"ns:{tag}" if tag else '' for tag in path.split('/')])
                element = self.root.find(f'.//{ns_path}', self.ns)
            else:
                # Sem namespace - busca direta
                element = self.root.find(f'.//{path}')
            
            if element is not None:
                if attr:
                    return element.get(attr, default)
                return element.text or default
            
            return default
        except Exception as e:
            logger.warning(f"Erro ao extrair {path}: {e}")
            return default
    
    def _get_text_from_element(self, element: ET.Element, path: str, default: str = '') -> str:
        """Extrai texto de sub-elemento"""
        try:
            if self.ns:
                ns_path = '/'.join([f"ns:{tag}" if tag else '' for tag in path.split('/')])
                sub_elem = element.find(f'.//{ns_path}', self.ns)
            else:
                sub_elem = element.find(f'.//{path}')
            
            return sub_elem.text if sub_elem is not None and sub_elem.text else default
        except:
            return default
    
    def _get_decimal(self, path: str, default: float = 0.0) -> float:
        """Extrai valor decimal"""
        text = self._get_text(path)
        try:
            return float(text) if text else default
        except (ValueError, TypeError):
            return default
    
    def _get_decimal_from_element(self, element: ET.Element, path: str, default: float = 0.0) -> float:
        """Extrai decimal de sub-elemento"""
        text = self._get_text_from_element(element, path)
        try:
            return float(text) if text else default
        except (ValueError, TypeError):
            return default
    
    def _find_all(self, tag: str) -> List[ET.Element]:
        """Busca todos elementos com determinada tag"""
        try:
            if self.ns:
                return self.root.findall(f'.//ns:{tag}', self.ns)
            else:
                return self.root.findall(f'.//{tag}')
        except:
            return []
    
    @staticmethod
    def _parse_date(date_str: str) -> Optional[str]:
        """
        Converte string de data para formato padrão
        
        Args:
            date_str: Data em formato ISO ou brasileiro
            
        Returns:
            Data em formato YYYY-MM-DD ou None
        """
        if not date_str:
            return None
        
        try:
            # Remove timezone e hora se existir
            date_str = date_str.split('T')[0].split(' ')[0]
            
            # Tenta parsear diferentes formatos
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%Y%m%d']:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            return date_str  # Retorna original se não conseguir parsear
            
        except Exception as e:
            logger.warning(f"Erro ao parsear data {date_str}: {e}")
            return None


if __name__ == "__main__":
    """Teste standalone"""
    print("=== Teste XML Processor ===\n")
    
    # Teste com arquivo de exemplo
    test_file = Path("arquivos/entrados/NFe00120954494003622218027814120519723516936553.xml")
    
    if test_file.exists():
        processor = XMLProcessor()
        
        if processor.load_xml(test_file):
            print(f"✅ XML carregado: {processor.doc_type}\n")
            
            data = processor.extract_data()
            
            print("Metadados:")
            print(f"  Chave: {data['metadata'].get('chave_acesso')}")
            print(f"  Número: {data['metadata'].get('numero')}")
            print(f"  Data: {data['metadata'].get('data_emissao')}")
            
            print("\nEmitente:")
            print(f"  Nome: {data['emitente'].get('xNome')}")
            print(f"  CNPJ: {data['emitente'].get('CNPJ')}")
            
            print("\nValores:")
            print(f"  Total NF: R$ {data['valores'].get('vNF', 0):,.2f}")
            print(f"  Total Impostos: R$ {data['impostos'].get('total', 0):,.2f}")
            
            print(f"\nItens: {len(data['itens'])}")
            
        else:
            print("❌ Erro ao carregar XML")
    else:
        print(f"❌ Arquivo não encontrado: {test_file}")
