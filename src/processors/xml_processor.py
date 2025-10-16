"""
Processador XML para Notas Fiscais Brasileiras (NFe/NFCe/CTe/MDF-e)
Extrai dados estruturados de arquivos XML conforme padrão SEFAZ
Versão corrigida para XMLs com e sem namespace
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import hashlib

from src.utils.logger import get_logger

logger = get_logger(__name__)


class XMLProcessor:
    """Processador de XML de Notas Fiscais brasileiras"""
    
    # Namespaces comuns em NFe
    NAMESPACES = {
        'nfe': 'http://www.portalfiscal.inf.br/nfe',
        'cte': 'http://www.portalfiscal.inf.br/cte',
        'mdfe': 'http://www.portalfiscal.inf.br/mdfe'
    }
    
    def __init__(self):
        """Inicializa o processador XML"""
        self.current_file: Optional[Path] = None
        self.xml_root: Optional[ET.Element] = None
        self.doc_type: Optional[str] = None
        
    def load_xml(self, file_path: Path) -> bool:
        """
        Carrega arquivo XML
        
        Args:
            file_path: Caminho do arquivo XML
            
        Returns:
            True se carregou com sucesso, False caso contrário
        """
        try:
            self.current_file = Path(file_path)
            
            # Parse do XML
            tree = ET.parse(file_path)
            self.xml_root = tree.getroot()
            
            # Detecta tipo de documento
            self.doc_type = self._detect_doc_type()
            
            logger.info(f"XML carregado: {file_path.name} (Tipo: {self.doc_type})")
            return True
            
        except ET.ParseError as e:
            logger.error(f"Erro ao parsear XML {file_path.name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro ao carregar XML {file_path.name}: {e}")
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
            return 'Desconhecido'
    
    def extract_data(self) -> Dict[str, Any]:
        """
        Extrai todos os dados relevantes do XML
        
        Returns:
            Dicionário com dados estruturados
        """
        if not self.xml_root:
            raise ValueError("Nenhum XML carregado. Use load_xml() primeiro.")
        
        data = {
            'tipo_documento': self.doc_type,
            'arquivo_hash': self.calculate_file_hash(),
            'metadados': self._extract_metadata(),
            'emitente': self._extract_emitente(),
            'destinatario': self._extract_destinatario(),
            'valores': self._extract_valores(),
            'impostos': self._extract_impostos(),
            'itens': self._extract_itens(),
            'transporte': self._extract_transporte(),
        }
        
        return data
    
    def calculate_file_hash(self) -> str:
        """
        Calcula hash MD5 do arquivo para detecção de duplicados
        
        Returns:
            Hash MD5 em hexadecimal
        """
        if not self.current_file or not self.current_file.exists():
            return ""
        
        md5_hash = hashlib.md5()
        with open(self.current_file, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
        
        return md5_hash.hexdigest()
    
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
            'cnpj': self._get_text('emit/CNPJ'),
            'cpf': self._get_text('emit/CPF'),
            'razao_social': self._get_text('emit/xNome'),
            'nome_fantasia': self._get_text('emit/xFant'),
            'inscricao_estadual': self._get_text('emit/IE'),
            'inscricao_municipal': self._get_text('emit/IM'),
            'cnae': self._get_text('emit/CNAE'),
            'regime_tributario': self._get_text('emit/CRT'),
            'endereco': {
                'logradouro': self._get_text('emit/enderEmit/xLgr'),
                'numero': self._get_text('emit/enderEmit/nro'),
                'complemento': self._get_text('emit/enderEmit/xCpl'),
                'bairro': self._get_text('emit/enderEmit/xBairro'),
                'municipio': self._get_text('emit/enderEmit/xMun'),
                'codigo_municipio': self._get_text('emit/enderEmit/cMun'),
                'uf': self._get_text('emit/enderEmit/UF'),
                'cep': self._get_text('emit/enderEmit/CEP'),
                'pais': self._get_text('emit/enderEmit/xPais'),
                'codigo_pais': self._get_text('emit/enderEmit/cPais'),
            }
        }
    
    def _extract_destinatario(self) -> Dict[str, Any]:
        """Extrai dados do destinatário"""
        return {
            'cnpj': self._get_text('dest/CNPJ'),
            'cpf': self._get_text('dest/CPF'),
            'razao_social': self._get_text('dest/xNome'),
            'inscricao_estadual': self._get_text('dest/IE'),
            'inscricao_municipal': self._get_text('dest/IM'),
            'email': self._get_text('dest/email'),
            'indicador_ie': self._get_text('dest/indIEDest'),
            'endereco': {
                'logradouro': self._get_text('dest/enderDest/xLgr'),
                'numero': self._get_text('dest/enderDest/nro'),
                'complemento': self._get_text('dest/enderDest/xCpl'),
                'bairro': self._get_text('dest/enderDest/xBairro'),
                'municipio': self._get_text('dest/enderDest/xMun'),
                'codigo_municipio': self._get_text('dest/enderDest/cMun'),
                'uf': self._get_text('dest/enderDest/UF'),
                'cep': self._get_text('dest/enderDest/CEP'),
                'pais': self._get_text('dest/enderDest/xPais'),
                'codigo_pais': self._get_text('dest/enderDest/cPais'),
            }
        }
    
    def _extract_valores(self) -> Dict[str, Any]:
        """Extrai valores totais da nota"""
        return {
            'valor_produtos': self._get_decimal('total/ICMSTot/vProd'),
            'valor_frete': self._get_decimal('total/ICMSTot/vFrete'),
            'valor_seguro': self._get_decimal('total/ICMSTot/vSeg'),
            'valor_desconto': self._get_decimal('total/ICMSTot/vDesc'),
            'valor_outros': self._get_decimal('total/ICMSTot/vOutro'),
            'valor_total': self._get_decimal('total/ICMSTot/vNF'),
            'valor_bc_icms': self._get_decimal('total/ICMSTot/vBC'),
            'valor_icms': self._get_decimal('total/ICMSTot/vICMS'),
            'valor_ipi': self._get_decimal('total/ICMSTot/vIPI'),
            'valor_pis': self._get_decimal('total/ICMSTot/vPIS'),
            'valor_cofins': self._get_decimal('total/ICMSTot/vCOFINS'),
        }
    
    def _extract_impostos(self) -> Dict[str, Any]:
        """Extrai detalhes dos impostos"""
        return {
            'icms': {
                'base_calculo': self._get_decimal('total/ICMSTot/vBC'),
                'valor': self._get_decimal('total/ICMSTot/vICMS'),
                'valor_st': self._get_decimal('total/ICMSTot/vST'),
                'base_st': self._get_decimal('total/ICMSTot/vBCST'),
            },
            'ipi': {
                'valor': self._get_decimal('total/ICMSTot/vIPI'),
            },
            'pis': {
                'valor': self._get_decimal('total/ICMSTot/vPIS'),
            },
            'cofins': {
                'valor': self._get_decimal('total/ICMSTot/vCOFINS'),
            },
            'tributos_aproximado': self._get_decimal('total/ICMSTot/vTotTrib'),
        }
    
    def _extract_itens(self) -> List[Dict[str, Any]]:
        """Extrai lista de itens da nota"""
        itens = []
        
        # Busca todos os elementos 'det' (itens)
        for det in self._find_all('det'):
            # Busca elemento prod dentro de det
            prod = None
            
            # Tenta sem namespace primeiro (mais comum)
            prod = det.find('prod')
            
            # Se não encontrou, tenta com namespace
            if prod is None:
                for prefix, uri in self.NAMESPACES.items():
                    prod = det.find(f'{{{uri}}}prod')
                    if prod is not None:
                        break
            
            if prod is None:
                continue
            
            # Extrai dados do produto
            def get_prod_text(tag: str, default: str = '') -> str:
                # Tenta sem namespace primeiro
                elem = prod.find(tag)
                if elem is not None and elem.text:
                    return elem.text
                
                # Tenta com namespace
                for prefix, uri in self.NAMESPACES.items():
                    elem = prod.find(f'{{{uri}}}{tag}')
                    if elem is not None and elem.text:
                        return elem.text
                
                return default
            
            def get_prod_decimal(tag: str, default: float = 0.0) -> float:
                text = get_prod_text(tag)
                try:
                    return float(text) if text else default
                except ValueError:
                    return default
            
            item = {
                'numero_item': det.get('nItem', ''),
                'produto': {
                    'codigo': get_prod_text('cProd'),
                    'ean': get_prod_text('cEAN'),
                    'descricao': get_prod_text('xProd'),
                    'ncm': get_prod_text('NCM'),
                    'cfop': get_prod_text('CFOP'),
                    'unidade': get_prod_text('uCom'),
                    'quantidade': get_prod_decimal('qCom'),
                    'valor_unitario': get_prod_decimal('vUnCom'),
                    'valor_total': get_prod_decimal('vProd'),
                },
                'impostos': {
                    'cfop': get_prod_text('CFOP'),
                    'icms_cst': '',
                    'ipi_cst': '',
                    'pis_cst': '',
                    'cofins_cst': '',
                }
            }
            itens.append(item)
        
        return itens
    
    def _extract_transporte(self) -> Dict[str, Any]:
        """Extrai dados de transporte"""
        return {
            'modalidade_frete': self._get_text('transp/modFrete'),
            'transportadora': {
                'cnpj': self._get_text('transp/transporta/CNPJ'),
                'cpf': self._get_text('transp/transporta/CPF'),
                'razao_social': self._get_text('transp/transporta/xNome'),
                'inscricao_estadual': self._get_text('transp/transporta/IE'),
                'endereco': self._get_text('transp/transporta/xEnder'),
                'municipio': self._get_text('transp/transporta/xMun'),
                'uf': self._get_text('transp/transporta/UF'),
            },
            'veiculo': {
                'placa': self._get_text('transp/veicTransp/placa'),
                'uf': self._get_text('transp/veicTransp/UF'),
            }
        }
    
    # Métodos auxiliares de navegação XML
    
    def _get_text(self, path: str, default: str = '', attr: Optional[str] = None) -> str:
        """Busca texto em caminho XML considerando namespaces"""
        if not self.xml_root:
            return default
        
        # Primeiro tenta sem namespace (mais comum em XMLs reais)
        element = self.xml_root.find(f'.//{path}')
        if element is not None:
            if attr:
                return element.get(attr, default)
            return element.text or default
        
        # Tenta com namespace NFe
        for prefix, uri in self.NAMESPACES.items():
            namespaced_path = '/'.join([f'{{{uri}}}{p}' if not p.startswith('{') else p 
                                       for p in path.split('/')])
            element = self.xml_root.find(f'.//{namespaced_path}')
            if element is not None:
                if attr:
                    return element.get(attr, default)
                return element.text or default
        
        return default
    
    def _get_text_from_element(self, element: ET.Element, path: str, default: str = '') -> str:
        """Busca texto relativo a um elemento específico"""
        if path.endswith('/*'):
            # Busca qualquer filho (para CST, CSOSN etc)
            parent_path = path.rstrip('/*')
            parent = element.find(f'.//{parent_path}')
            if parent is not None:
                for child in parent:
                    if child.text:
                        return child.text
            return default
        
        found = element.find(f'.//{path}')
        return found.text if found is not None and found.text else default
    
    def _get_decimal(self, path: str, default: float = 0.0) -> float:
        """Busca valor decimal"""
        text = self._get_text(path)
        try:
            return float(text) if text else default
        except ValueError:
            return default
    
    def _get_decimal_from_element(self, element: ET.Element, path: str, default: float = 0.0) -> float:
        """Busca valor decimal relativo a um elemento"""
        text = self._get_text_from_element(element, path)
        try:
            return float(text) if text else default
        except ValueError:
            return default
    
    def _find_all(self, tag: str) -> List[ET.Element]:
        """Busca todos elementos com tag especificada"""
        if not self.xml_root:
            return []
        
        # Primeiro tenta sem namespace (mais comum)
        results = self.xml_root.findall(f'.//{tag}')
        if results:
            return results
        
        # Se não encontrou, tenta com namespaces
        for prefix, uri in self.NAMESPACES.items():
            elements = self.xml_root.findall(f'.//{{{uri}}}{tag}')
            if elements:
                return elements
        
        return []
    
    @staticmethod
    def _parse_date(date_str: str) -> Optional[str]:
        """
        Converte data do formato XML para ISO
        Aceita: 2024-01-15T10:30:00-03:00 ou 2024-01-15
        """
        if not date_str:
            return None
        
        try:
            # Remove timezone se existir
            date_str = date_str.split('-03:00')[0].split('+')[0].split('T')[0]
            return date_str
        except Exception:
            return date_str
