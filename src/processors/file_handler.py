"""
File Handler - Movimentação e Gestão de Arquivos
USA BANCO DE DADOS com query EXATA
"""

import shutil
from pathlib import Path
import os

from src.utils.logger import setup_logger
from src.utils.config import get_settings

logger = setup_logger(__name__)


class FileHandler:
    """Gerenciador de movimentação de arquivos"""
    
    def __init__(self, db_manager=None):
        """
        Inicializa o File Handler
        
        Args:
            db_manager: Instância do DatabaseManager (opcional)
        """
        self.settings = get_settings()
        self.pasta_entrados = Path(self.settings.pasta_entrados)
        self.pasta_processados = Path(self.settings.pasta_processados)
        self.pasta_rejeitados = Path(self.settings.pasta_rejeitados)
        
        self.db = db_manager
        
        logger.info("FileHandler inicializado")
    
    def set_db_manager(self, db_manager):
        """Define o DatabaseManager"""
        self.db = db_manager
    
    def _arquivo_ja_processado(self, nome_arquivo: str) -> bool:
        """
        Verifica se arquivo já foi processado no BANCO DE DADOS
        Busca EXATA pelo nome do arquivo
        """
        if not self.db:
            logger.warning("DatabaseManager não configurado")
            return False
        
        try:
            from src.database.models import RegistroResultado
            
            session = self.db.get_session()
            try:
                # CRÍTICO: Busca por arquivos que TERMINAM com o nome
                # porque path_nome_arquivo tem o caminho completo
                existe = session.query(RegistroResultado).filter(
                    RegistroResultado.path_nome_arquivo.like(f'%{nome_arquivo}')
                ).first() is not None
                
                if existe:
                    logger.debug(f"Arquivo {nome_arquivo} encontrado no BD")
                
                return existe
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Erro ao verificar arquivo processado: {e}")
            return False
    
    def move_to_processados(self, arquivo_path: Path) -> bool:
        """Move arquivo para pasta processados"""
        try:
            nome_arquivo = arquivo_path.name
            destino = self.pasta_processados / nome_arquivo
            
            if destino.exists():
                logger.warning(f"Arquivo já existe em /processados - substituindo")
                os.remove(destino)
            
            if not arquivo_path.exists():
                logger.error(f"Arquivo não existe para mover: {arquivo_path}")
                return False
            
            shutil.move(str(arquivo_path), str(destino))
            
            logger.info(f"Arquivo movido: {nome_arquivo} → processados/")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao mover para processados: {e}")
            return False
    
    def move_to_rejeitados(self, arquivo_path: Path, motivo: str = "Validação falhou") -> bool:
        """Move arquivo para pasta rejeitados"""
        try:
            nome_arquivo = arquivo_path.name
            destino = self.pasta_rejeitados / nome_arquivo
            
            if destino.exists():
                logger.warning(f"Arquivo já existe em /rejeitados - substituindo")
                os.remove(destino)
            
            if not arquivo_path.exists():
                logger.error(f"Arquivo não existe para mover: {arquivo_path}")
                return False
            
            shutil.move(str(arquivo_path), str(destino))
            
            logger.info(f"Arquivo movido: {nome_arquivo} → rejeitados/ (Motivo: {motivo})")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao mover para rejeitados: {e}")
            return False
    
    def validar_extensao(self, arquivo_path: Path) -> bool:
        """Valida se arquivo tem extensão permitida"""
        extensoes_validas = {'.xml'}
        extensao = arquivo_path.suffix.lower()
        
        if extensao not in extensoes_validas:
            logger.warning(f"Extensão inválida: {extensao} - Arquivo: {arquivo_path.name}")
            return False
        
        return True
    
    def processar_arquivo_invalido(self, arquivo_path: Path) -> bool:
        """Processa arquivo com extensão inválida"""
        try:
            nome_arquivo = arquivo_path.name
            
            if not arquivo_path.exists():
                logger.error(f"Arquivo não existe: {arquivo_path}")
                return False
            
            destino = self.pasta_rejeitados / nome_arquivo
            
            if destino.exists():
                logger.warning(f"Arquivo já existe em /rejeitados - substituindo")
                os.remove(destino)
            
            shutil.move(str(arquivo_path), str(destino))
            logger.info(f"Arquivo movido: {nome_arquivo} → rejeitados/ (Extensão inválida)")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao processar arquivo inválido: {e}")
            return False
    
    def get_arquivos_entrados(self) -> list[Path]:
        """
        Lista TODOS os arquivos na pasta entrados
        FILTRA usando BANCO DE DADOS
        """
        try:
            # Busca TODOS os arquivos
            todos_arquivos = [
                f for f in self.pasta_entrados.iterdir() 
                if f.is_file() and f.name != '.gitkeep'
            ]
            
            # Filtrar apenas arquivos NÃO processados
            arquivos_novos = []
            for arquivo in todos_arquivos:
                if not self._arquivo_ja_processado(arquivo.name):
                    arquivos_novos.append(arquivo)
                else:
                    logger.info(f"Arquivo {arquivo.name} já foi processado (registro no BD) - SERÁ PROCESSADO NOVAMENTE para garantir registro correto")
                    # MUDANÇA: Não pula, processa novamente para garantir que vai para rejeitados
                    arquivos_novos.append(arquivo)
            
            return arquivos_novos
            
        except Exception as e:
            logger.error(f"Erro ao listar arquivos entrados: {e}")
            return []
