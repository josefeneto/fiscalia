"""
NFe Processor - Processador Principal (VERSÃO FINAL)
Usa BD para controle de duplicados
"""

from pathlib import Path
from typing import Dict, Any
import hashlib
from datetime import datetime

from src.processors.xml_processor import XMLProcessor
from src.processors.validator import NFValidator
from src.processors.file_handler import FileHandler
from src.database.db_manager import DatabaseManager
from src.utils.logger import setup_logger
from src.utils.config import get_settings

logger = setup_logger(__name__)


class NFeProcessor:
    """Processador principal de Notas Fiscais Eletrônicas"""
    
    def __init__(self):
        """Inicializa o processador"""
        self.xml_processor = XMLProcessor()
        self.validator = NFValidator()
        self.db = DatabaseManager()
        self.file_handler = FileHandler()
        
        # IMPORTANTE: Injetar DB no FileHandler
        self.file_handler.set_db_manager(self.db)
        
        self.settings = get_settings()
        logger.info("NFeProcessor inicializado")
    
    def _parse_date_to_datetime(self, date_str: str) -> datetime:
        """Converte string de data para objeto datetime"""
        if not date_str:
            return None
        
        try:
            if isinstance(date_str, datetime):
                return date_str
            
            return datetime.strptime(date_str, '%Y-%m-%d')
        except Exception as e:
            logger.warning(f"Erro ao converter data '{date_str}': {e}")
            return None
    
    def _calcular_hash(self, arquivo_path: Path) -> str:
        """Calcula hash MD5 do arquivo"""
        try:
            with open(arquivo_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            logger.error(f"Erro ao calcular hash: {e}")
            return ""
    
    def _verificar_duplicado_antes_salvar(self, conteudo_bytes: bytes) -> tuple[bool, str]:
        """Verifica se arquivo já existe antes de salvar"""
        try:
            hash_arquivo = hashlib.md5(conteudo_bytes).hexdigest()
            
            temp_dir = Path(self.settings.pasta_base) / "temp"
            temp_dir.mkdir(exist_ok=True)
            
            temp_path = temp_dir / f"temp_{hash_arquivo}.xml"
            temp_path.write_bytes(conteudo_bytes)
            
            try:
                if self.xml_processor.load_xml(temp_path):
                    dados = self.xml_processor.extract_data()
                    chave_acesso = dados.get('metadata', {}).get('chave_acesso', '')
                    
                    if chave_acesso and self.db.check_documento_existe(chave_acesso):
                        logger.warning(f"Arquivo duplicado detectado ANTES de salvar: {chave_acesso}")
                        return True, chave_acesso
                    
                    return False, chave_acesso
                else:
                    return False, ""
                
            finally:
                if temp_path.exists():
                    temp_path.unlink()
                    
        except Exception as e:
            logger.error(f"Erro ao verificar duplicado: {e}")
            return False, ""
    
    def _extrair_dados_do_xml(self, arquivo_path: Path) -> Dict[str, Any]:
        """Extrai dados do XML e converte para formato do banco"""
        try:
            if not self.xml_processor.load_xml(arquivo_path):
                logger.error(f"Falha ao carregar XML: {arquivo_path.name}")
                return {}
            
            data = self.xml_processor.extract_data()
            
            if not data:
                logger.error(f"Falha ao extrair dados do XML: {arquivo_path.name}")
                return {}
            
            metadata = data.get('metadata', {})
            emitente = data.get('emitente', {})
            destinatario = data.get('destinatario', {})
            valores = data.get('valores', {})
            
            data_emissao_str = metadata.get('data_emissao')
            data_saida_str = metadata.get('data_saida')
            
            dados_db = {
                'chave_acesso': metadata.get('chave_acesso', ''),
                'numero_nf': metadata.get('numero', ''),
                'serie': metadata.get('serie', ''),
                'modelo': metadata.get('modelo', ''),
                'natureza_operacao': metadata.get('natureza_operacao', ''),
                'tipo_operacao': metadata.get('tipo_operacao', ''),
                'data_emissao': self._parse_date_to_datetime(data_emissao_str),
                'data_saida_entrada': self._parse_date_to_datetime(data_saida_str),
                'cnpj_emitente': emitente.get('CNPJ', ''),
                'cpf_emitente': emitente.get('CPF', ''),
                'razao_social_emitente': emitente.get('xNome', ''),
                'nome_fantasia_emitente': emitente.get('xFant', ''),
                'ie_emitente': emitente.get('IE', ''),
                'uf_emitente': emitente.get('enderEmit', {}).get('UF', ''),
                'municipio_emitente': emitente.get('enderEmit', {}).get('xMun', ''),
                'cnpj_destinatario': destinatario.get('CNPJ', ''),
                'cpf_destinatario': destinatario.get('CPF', ''),
                'razao_social_destinatario': destinatario.get('xNome', ''),
                'ie_destinatario': destinatario.get('IE', ''),
                'uf_destinatario': destinatario.get('enderDest', {}).get('UF', ''),
                'municipio_destinatario': destinatario.get('enderDest', {}).get('xMun', ''),
                'valor_total': valores.get('vNF', 0.0),
                'valor_produtos': valores.get('vProd', 0.0),
                'valor_frete': valores.get('vFrete', 0.0),
                'valor_seguro': valores.get('vSeg', 0.0),
                'valor_desconto': valores.get('vDesc', 0.0),
                'valor_outras_despesas': valores.get('vOutro', 0.0),
                'base_calculo_icms': valores.get('vBC', 0.0),
                'valor_icms': valores.get('vICMS', 0.0),
                'valor_ipi': valores.get('vIPI', 0.0),
                'valor_pis': valores.get('vPIS', 0.0),
                'valor_cofins': valores.get('vCOFINS', 0.0),
                'path_nome_arquivo': str(arquivo_path),
                'erp_processado': 'No',
            }
            
            return dados_db
            
        except Exception as e:
            logger.error(f"Erro ao extrair dados do XML {arquivo_path.name}: {e}")
            return {}
    
    def process_file(self, arquivo_path: Path) -> Dict[str, Any]:
        """Processa um arquivo XML de NFe"""
        try:
            logger.info(f"Processando arquivo: {arquivo_path.name}")
            
            if not arquivo_path.exists():
                return {
                    'success': False,
                    'message': 'Arquivo não encontrado',
                    'file': str(arquivo_path)
                }
            
            # Validar extensão
            if not self.file_handler.validar_extensao(arquivo_path):
                self.file_handler.processar_arquivo_invalido(arquivo_path)
                
                self.db.add_resultado({
                    'path_nome_arquivo': str(arquivo_path),
                    'resultado': 'Insucesso',
                    'causa': 'Extensão inválida'
                })
                
                return {
                    'success': False,
                    'message': 'Extensão inválida',
                    'file': str(arquivo_path)
                }
            
            # Extrair dados
            dados = self._extrair_dados_do_xml(arquivo_path)
            
            if not dados or not dados.get('chave_acesso'):
                self.file_handler.move_to_rejeitados(arquivo_path, "XML inválido")
                
                self.db.add_resultado({
                    'path_nome_arquivo': str(arquivo_path),
                    'resultado': 'Insucesso',
                    'causa': 'XML inválido ou sem chave de acesso'
                })
                
                return {
                    'success': False,
                    'message': 'XML inválido ou sem chave de acesso',
                    'file': str(arquivo_path)
                }
            
            # Verificar duplicado
            chave_acesso = dados['chave_acesso']
            if self.db.check_documento_existe(chave_acesso):
                logger.warning(f"Documento duplicado: {chave_acesso}")
                
                self.file_handler.move_to_rejeitados(arquivo_path, "Documento duplicado")
                
                self.db.add_resultado({
                    'path_nome_arquivo': str(arquivo_path),
                    'resultado': 'Insucesso',
                    'causa': f'Documento duplicado: {chave_acesso}'
                })
                
                return {
                    'success': False,
                    'message': f'Documento duplicado: {chave_acesso}',
                    'file': str(arquivo_path),
                    'chave_acesso': chave_acesso
                }
            
            logger.info("✅ Validação desabilitada temporariamente")
            
            # Adicionar ao banco
            doc_id = self.db.add_documento(dados)
            
            if doc_id:
                self.file_handler.move_to_processados(arquivo_path)
                
                self.db.add_resultado({
                    'path_nome_arquivo': str(arquivo_path),
                    'resultado': 'Sucesso',
                    'causa': f"NFe {dados.get('numero_nf')} processada com sucesso"
                })
                
                logger.info(f"Arquivo processado com sucesso: {arquivo_path.name}")
                
                return {
                    'success': True,
                    'message': 'Arquivo processado com sucesso',
                    'file': str(arquivo_path),
                    'dados': dados
                }
            else:
                self.file_handler.move_to_rejeitados(arquivo_path, "Erro no banco de dados")
                
                self.db.add_resultado({
                    'path_nome_arquivo': str(arquivo_path),
                    'resultado': 'Insucesso',
                    'causa': f"Erro ao processar {arquivo_path.name}"
                })
                
                return {
                    'success': False,
                    'message': 'Erro ao adicionar ao banco de dados',
                    'file': str(arquivo_path)
                }
                
        except Exception as e:
            logger.error(f"Erro ao processar arquivo {arquivo_path.name}: {str(e)}")
            
            try:
                self.file_handler.move_to_rejeitados(arquivo_path, f"Erro: {str(e)}")
                
                self.db.add_resultado({
                    'path_nome_arquivo': str(arquivo_path),
                    'resultado': 'Insucesso',
                    'causa': f"Erro no processamento: {str(e)}"
                })
            except:
                pass
            
            return {
                'success': False,
                'message': f'Erro no processamento: {str(e)}',
                'file': str(arquivo_path)
            }
    
    def process_uploaded_file(self, uploaded_file, nome_arquivo: str) -> Dict[str, Any]:
        """Processa arquivo do Streamlit file_uploader"""
        try:
            conteudo = uploaded_file.getbuffer().tobytes()
            
            is_duplicado, chave_acesso = self._verificar_duplicado_antes_salvar(conteudo)
            
            if is_duplicado:
                logger.warning(f"Upload bloqueado - arquivo duplicado: {nome_arquivo}")
                return {
                    'success': False,
                    'message': f'Arquivo já existe no banco: {chave_acesso}',
                    'file': nome_arquivo,
                    'chave_acesso': chave_acesso,
                    'duplicado': True
                }
            
            temp_path = Path(self.settings.pasta_entrados) / nome_arquivo
            temp_path.write_bytes(conteudo)
            
            return self.process_file(temp_path)
            
        except Exception as e:
            logger.error(f"Erro ao processar upload: {e}")
            return {
                'success': False,
                'message': f'Erro no upload: {str(e)}',
                'file': nome_arquivo
            }
    
    def process_batch(self) -> Dict[str, Any]:
        """Processa todos os arquivos da pasta entrados"""
        try:
            arquivos = self.file_handler.get_arquivos_entrados()
            
            if not arquivos:
                logger.info("Nenhum arquivo novo para processar")
                return {
                    'success': True,
                    'message': 'Nenhum arquivo novo',
                    'total': 0,
                    'processados': 0,
                    'erros': 0
                }
            
            resultados = []
            sucessos = 0
            erros = 0
            
            for arquivo in arquivos:
                resultado = self.process_file(arquivo)
                resultados.append(resultado)
                
                if resultado['success']:
                    sucessos += 1
                else:
                    erros += 1
            
            return {
                'success': True,
                'message': 'Processamento em lote concluído',
                'total': len(arquivos),
                'processados': sucessos,
                'erros': erros,
                'resultados': resultados
            }
            
        except Exception as e:
            logger.error(f"Erro no processamento em lote: {e}")
            return {
                'success': False,
                'message': f'Erro no batch: {str(e)}'
            }
