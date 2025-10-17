"""
Gerenciador de Arquivos de Notas Fiscais
Move arquivos entre pastas, calcula hash, verifica duplicados
"""

import shutil
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime
import hashlib

from utils.config import get_settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class FileHandler:
    """Gerenciador de arquivos do sistema"""
    
    # Extensões suportadas
    SUPPORTED_EXTENSIONS = {'.xml', '.pdf', '.png', '.jpg', '.jpeg'}
    
    def __init__(self, base_path: Optional[Path] = None):
        """
        Inicializa o gerenciador de arquivos
        
        Args:
            base_path: Caminho base (padrão: arquivos/)
        """
        if base_path is None:
            base_path = Path('arquivos')
        
        self.base_path = Path(base_path)
        self.entrados_path = self.base_path / 'entrados'
        self.processados_path = self.base_path / 'processados'
        self.rejeitados_path = self.base_path / 'rejeitados'
        
        # Cria estrutura de pastas se não existir
        self._ensure_folders()
    
    def _ensure_folders(self):
        """Garante que as pastas necessárias existem"""
        for folder in [self.entrados_path, self.processados_path, self.rejeitados_path]:
            folder.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Pasta verificada: {folder}")
    
    def set_base_path(self, new_path: Path):
        """
        Altera o caminho base das pastas
        
        Args:
            new_path: Novo caminho base
        """
        self.base_path = Path(new_path)
        self.entrados_path = self.base_path / 'entrados'
        self.processados_path = self.base_path / 'processados'
        self.rejeitados_path = self.base_path / 'rejeitados'
        self._ensure_folders()
        logger.info(f"Caminho base alterado para: {new_path}")
    
    def get_pending_files(self) -> list[Path]:
        """
        Lista arquivos pendentes na pasta entrados/
        
        Returns:
            Lista de Path com arquivos pendentes
        """
        files = []
        for ext in self.SUPPORTED_EXTENSIONS:
            files.extend(self.entrados_path.glob(f'*{ext}'))
        
        logger.info(f"Encontrados {len(files)} arquivo(s) pendente(s)")
        return sorted(files)
    
    def is_supported_file(self, file_path: Path) -> bool:
        """
        Verifica se arquivo tem extensão suportada
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            True se extensão suportada
        """
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS
    
    def get_file_type(self, file_path: Path) -> str:
        """
        Identifica tipo do arquivo pela extensão
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Tipo: 'xml', 'pdf', 'imagem', 'desconhecido'
        """
        ext = file_path.suffix.lower()
        
        if ext == '.xml':
            return 'xml'
        elif ext == '.pdf':
            return 'pdf'
        elif ext in {'.png', '.jpg', '.jpeg'}:
            return 'imagem'
        else:
            return 'desconhecido'
    
    def calculate_hash(self, file_path: Path) -> str:
        """
        Calcula hash MD5 do arquivo
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Hash MD5 em hexadecimal
        """
        if not file_path.exists():
            logger.error(f"Arquivo não encontrado: {file_path}")
            return ""
        
        try:
            md5_hash = hashlib.md5()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    md5_hash.update(chunk)
            
            hash_value = md5_hash.hexdigest()
            logger.debug(f"Hash calculado para {file_path.name}: {hash_value}")
            return hash_value
            
        except Exception as e:
            logger.error(f"Erro ao calcular hash de {file_path.name}: {e}")
            return ""
    
    def move_to_processed(self, file_path: Path) -> Tuple[bool, Optional[Path]]:
        """
        Move arquivo para pasta processados/
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Tupla (sucesso, novo_path)
        """
        return self._move_file(file_path, self.processados_path)
    
    def move_to_rejected(self, file_path: Path) -> Tuple[bool, Optional[Path]]:
        """
        Move arquivo para pasta rejeitados/
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Tupla (sucesso, novo_path)
        """
        return self._move_file(file_path, self.rejeitados_path)
    
    def _move_file(self, file_path: Path, destination_folder: Path) -> Tuple[bool, Optional[Path]]:
        """
        Move arquivo para pasta de destino, evitando sobrescrever
        
        Args:
            file_path: Arquivo origem
            destination_folder: Pasta destino
            
        Returns:
            Tupla (sucesso, novo_path)
        """
        if not file_path.exists():
            logger.error(f"Arquivo não encontrado: {file_path}")
            return False, None
        
        try:
            # Garante que pasta destino existe
            destination_folder.mkdir(parents=True, exist_ok=True)
            
            # Nome destino com timestamp se já existir
            dest_path = destination_folder / file_path.name
            
            if dest_path.exists():
                # Adiciona timestamp para evitar sobrescrever
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                stem = file_path.stem
                suffix = file_path.suffix
                dest_path = destination_folder / f"{stem}_{timestamp}{suffix}"
            
            # Move o arquivo
            shutil.move(str(file_path), str(dest_path))
            logger.info(f"Arquivo movido: {file_path.name} → {destination_folder.name}/")
            
            return True, dest_path
            
        except Exception as e:
            logger.error(f"Erro ao mover arquivo {file_path.name}: {e}")
            return False, None
    
    def copy_to_entrados(self, source_path: Path) -> Tuple[bool, Optional[Path]]:
        """
        Copia arquivo para pasta entrados/ (usado no upload Streamlit)
        
        Args:
            source_path: Arquivo origem
            
        Returns:
            Tupla (sucesso, novo_path)
        """
        if not source_path.exists():
            logger.error(f"Arquivo não encontrado: {source_path}")
            return False, None
        
        try:
            # Nome destino
            dest_path = self.entrados_path / source_path.name
            
            # Se já existe, adiciona timestamp
            if dest_path.exists():
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                stem = source_path.stem
                suffix = source_path.suffix
                dest_path = self.entrados_path / f"{stem}_{timestamp}{suffix}"
            
            # Copia o arquivo
            shutil.copy2(str(source_path), str(dest_path))
            logger.info(f"Arquivo copiado para entrados/: {source_path.name}")
            
            return True, dest_path
            
        except Exception as e:
            logger.error(f"Erro ao copiar arquivo {source_path.name}: {e}")
            return False, None
    
    def get_stats(self) -> dict:
        """
        Retorna estatísticas das pastas
        
        Returns:
            Dicionário com contagem de arquivos
        """
        def count_files(folder: Path) -> int:
            return sum(1 for f in folder.iterdir() if f.is_file())
        
        return {
            'entrados': count_files(self.entrados_path),
            'processados': count_files(self.processados_path),
            'rejeitados': count_files(self.rejeitados_path),
            'base_path': str(self.base_path.absolute())
        }
    
    def validate_file_structure(self, file_path: Path) -> Tuple[bool, str]:
        """
        Valida estrutura básica do arquivo
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Tupla (é_válido, mensagem)
        """
        if not file_path.exists():
            return False, "Arquivo não encontrado"
        
        if not file_path.is_file():
            return False, "Caminho não é um arquivo"
        
        if file_path.stat().st_size == 0:
            return False, "Arquivo vazio"
        
        if not self.is_supported_file(file_path):
            return False, f"Extensão não suportada: {file_path.suffix}"
        
        # Validação específica por tipo
        file_type = self.get_file_type(file_path)
        
        if file_type == 'xml':
            # Verifica se é XML válido (básico)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(100)
                    if not content.strip().startswith('<?xml'):
                        return False, "Arquivo não parece ser um XML válido"
            except UnicodeDecodeError:
                return False, "Arquivo XML com encoding inválido"
            except Exception as e:
                return False, f"Erro ao ler arquivo: {str(e)}"
        
        return True, "Arquivo válido"
