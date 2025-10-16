"""
Processador Principal de Notas Fiscais
Coordena XML, validação, banco de dados e movimentação de arquivos
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.processors.xml_processor import XMLProcessor
from src.processors.validator import NFValidator
from src.processors.file_handler import FileHandler
from src.database.db_manager import DatabaseManager
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ProcessingResult:
    """Resultado do processamento de um arquivo"""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.success = False
        self.message = ""
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.data: Optional[Dict[str, Any]] = None
        self.hash: str = ""
        self.processing_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'file_name': self.file_path.name,
            'success': self.success,
            'message': self.message,
            'errors': self.errors,
            'warnings': self.warnings,
            'hash': self.hash,
            'processing_time': f"{self.processing_time:.2f}s"
        }


class NFeProcessor:
    """Processador principal do sistema Fiscalia"""
    
    def __init__(self, base_path: Optional[Path] = None):
        """
        Inicializa processador
        
        Args:
            base_path: Caminho base para arquivos (padrão: arquivos/)
        """
        self.file_handler = FileHandler(base_path)
        self.xml_processor = XMLProcessor()
        self.validator = NFValidator()
        self.db_manager = DatabaseManager()
        
        logger.info("NFeProcessor inicializado")
    
    def process_single_file(self, file_path: Path) -> ProcessingResult:
        """
        Processa um único arquivo
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            ProcessingResult com detalhes do processamento
        """
        start_time = datetime.now()
        result = ProcessingResult(file_path)
        
        try:
            logger.info(f"Processando: {file_path.name}")
            
            # 1. Valida estrutura do arquivo
            is_valid, msg = self.file_handler.validate_file_structure(file_path)
            if not is_valid:
                result.success = False
                result.message = msg
                result.errors.append(msg)
                self._save_result_and_move(result, rejected=True)
                return result
            
            # 2. Calcula hash para detecção de duplicados
            result.hash = self.file_handler.calculate_hash(file_path)
            
            if self._is_duplicate(result.hash):
                result.success = False
                result.message = "Arquivo duplicado"
                result.errors.append("Este arquivo já foi processado anteriormente")
                self._save_result_and_move(result, rejected=True)
                return result
            
            # 3. Identifica tipo e processa
            file_type = self.file_handler.get_file_type(file_path)
            
            if file_type != 'xml':
                result.success = False
                result.message = f"Tipo de arquivo ainda não suportado: {file_type}"
                result.errors.append(result.message)
                self._save_result_and_move(result, rejected=True)
                return result
            
            # 4. Processa XML
            if not self.xml_processor.load_xml(file_path):
                result.success = False
                result.message = "Erro ao carregar XML"
                result.errors.append("XML inválido ou corrompido")
                self._save_result_and_move(result, rejected=True)
                return result
            
            # 5. Extrai dados
            try:
                data = self.xml_processor.extract_data()
                result.data = data
            except Exception as e:
                result.success = False
                result.message = f"Erro na extração de dados: {str(e)}"
                result.errors.append(result.message)
                self._save_result_and_move(result, rejected=True)
                return result
            
            # 6. Valida dados extraídos
            is_valid = self.validator.validate(data, strict=False)
            validation_report = self.validator.get_validation_report()
            
            result.errors.extend(validation_report['errors'])
            result.warnings.extend(validation_report['warnings'])
            
            if not is_valid:
                result.success = False
                result.message = "Dados inválidos"
                self._save_result_and_move(result, rejected=True)
                return result
            
            # 7. Salva no banco de dados
            try:
                self._save_to_database(file_path, data, result.hash)
                result.success = True
                result.message = "Processado com sucesso"
                
                if result.warnings:
                    result.message += f" (com {len(result.warnings)} aviso(s))"
                
                self._save_result_and_move(result, rejected=False)
                
            except Exception as e:
                logger.error(f"Erro ao salvar no banco: {e}")
                result.success = False
                result.message = f"Erro ao salvar no banco: {str(e)}"
                result.errors.append(result.message)
                self._save_result_and_move(result, rejected=True)
            
        except Exception as e:
            logger.error(f"Erro inesperado ao processar {file_path.name}: {e}")
            result.success = False
            result.message = f"Erro inesperado: {str(e)}"
            result.errors.append(result.message)
            self._save_result_and_move(result, rejected=True)
        
        finally:
            result.processing_time = (datetime.now() - start_time).total_seconds()
        
        return result
    
    def process_batch(self) -> List[ProcessingResult]:
        """
        Processa todos os arquivos pendentes em batch
        
        Returns:
            Lista de ProcessingResult
        """
        pending_files = self.file_handler.get_pending_files()
        
        if not pending_files:
            logger.info("Nenhum arquivo pendente para processar")
            return []
        
        logger.info(f"Iniciando processamento em batch de {len(pending_files)} arquivo(s)")
        
        results = []
        for file_path in pending_files:
            result = self.process_single_file(file_path)
            results.append(result)
        
        # Estatísticas
        success_count = sum(1 for r in results if r.success)
        failed_count = len(results) - success_count
        
        logger.info(
            f"Batch concluído: {success_count} sucesso(s), "
            f"{failed_count} falha(s)"
        )
        
        return results
    
    def _is_duplicate(self, file_hash: str) -> bool:
        """Verifica se arquivo já foi processado (por hash)"""
        try:
            return self.db_manager.check_duplicate_by_hash(file_hash)
        except Exception as e:
            logger.error(f"Erro ao verificar duplicado: {e}")
            return False
    
    def _save_to_database(self, file_path: Path, data: Dict[str, Any], file_hash: str):
        """Salva dados no banco"""
        # Prepara dados para o banco
        metadata = data.get('metadados', {})
        emitente = data.get('emitente', {})
        destinatario = data.get('destinatario', {})
        valores = data.get('valores', {})
        impostos = data.get('impostos', {})
        
        doc_data = {
            'arquivo_hash': file_hash,
            'arquivo_path': str(file_path),
            
            # Metadados
            'tipo_documento': data.get('tipo_documento', ''),
            'chave_acesso': metadata.get('chave_acesso', ''),
            'numero': metadata.get('numero', ''),
            'serie': metadata.get('serie', ''),
            'data_emissao': metadata.get('data_emissao'),
            'modelo': metadata.get('modelo', ''),
            'natureza_operacao': metadata.get('natureza_operacao', ''),
            'tipo_operacao': metadata.get('tipo_operacao', ''),
            
            # Emitente
            'emitente_cnpj': emitente.get('cnpj', ''),
            'emitente_cpf': emitente.get('cpf', ''),
            'emitente_razao_social': emitente.get('razao_social', ''),
            'emitente_ie': emitente.get('inscricao_estadual', ''),
            
            # Destinatário
            'destinatario_cnpj': destinatario.get('cnpj', ''),
            'destinatario_cpf': destinatario.get('cpf', ''),
            'destinatario_razao_social': destinatario.get('razao_social', ''),
            
            # Valores
            'valor_total': valores.get('valor_total', 0.0),
            'valor_produtos': valores.get('valor_produtos', 0.0),
            'valor_desconto': valores.get('valor_desconto', 0.0),
            
            # Impostos
            'valor_icms': impostos.get('icms', {}).get('valor', 0.0),
            'valor_ipi': impostos.get('ipi', {}).get('valor', 0.0),
            'valor_pis': impostos.get('pis', {}).get('valor', 0.0),
            'valor_cofins': impostos.get('cofins', {}).get('valor', 0.0),
            
            # Status
            'erp_processado': 'No',
        }
        
        self.db_manager.add_doc_para_erp(doc_data)
    
    def _save_result_and_move(self, result: ProcessingResult, rejected: bool):
        """Salva resultado no banco e move arquivo"""
        # Determina resultado
        if result.success:
            resultado_str = "Sucesso"
            causa = result.message
        else:
            resultado_str = "Insucesso"
            causa = "; ".join(result.errors) if result.errors else result.message
        
        # Salva log no banco
        try:
            self.db_manager.add_registro_resultado(
                arquivo_path=str(result.file_path),
                arquivo_hash=result.hash,
                resultado=resultado_str,
                causa=causa
            )
        except Exception as e:
            logger.error(f"Erro ao salvar resultado no banco: {e}")
        
        # Move arquivo
        if rejected:
            success, new_path = self.file_handler.move_to_rejected(result.file_path)
        else:
            success, new_path = self.file_handler.move_to_processed(result.file_path)
        
        if not success:
            logger.error(f"Erro ao mover arquivo: {result.file_path.name}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do sistema
        
        Returns:
            Dicionário com estatísticas
        """
        file_stats = self.file_handler.get_stats()
        db_stats = self.db_manager.get_statistics()
        
        return {
            'arquivos': file_stats,
            'banco_dados': db_stats,
            'timestamp': datetime.now().isoformat()
        }
    
    def set_base_path(self, new_path: Path):
        """Altera caminho base dos arquivos"""
        self.file_handler.set_base_path(new_path)
