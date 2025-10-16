"""
Sistema de logging do Fiscalia
Configura logs para console e arquivo
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from src.utils.config import get_settings


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None
) -> None:
    """
    Configura sistema de logging
    
    Args:
        log_level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Caminho do arquivo de log
    """
    settings = get_settings()
    
    # Define nível de log
    if log_level is None:
        log_level = settings.LOG_LEVEL
    
    # Define arquivo de log
    if log_file is None:
        log_file = settings.LOG_FILE
    
    # Converte string para nível
    numeric_level = getattr(logging, log_level.upper(), logging.WARNING)
    
    # Cria diretório de logs se não existir
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configuração do formato
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Remove handlers existentes
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Configura logging básico
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            # Handler para arquivo
            logging.FileHandler(log_file, encoding='utf-8'),
            # Handler para console
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Silencia logs muito verbosos de bibliotecas externas
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    

def get_logger(name: str) -> logging.Logger:
    """
    Retorna logger configurado para um módulo
    
    Args:
        name: Nome do módulo (geralmente __name__)
        
    Returns:
        Logger configurado
    """
    # Garante que logging está configurado
    if not logging.getLogger().handlers:
        setup_logging()
    
    return logging.getLogger(name)


def set_log_level(level: str) -> None:
    """
    Altera nível de log em runtime
    
    Args:
        level: Novo nível (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    numeric_level = getattr(logging, level.upper(), logging.WARNING)
    logging.getLogger().setLevel(numeric_level)
    
    # Atualiza todos os handlers
    for handler in logging.getLogger().handlers:
        handler.setLevel(numeric_level)


def get_log_file_path() -> Path:
    """
    Retorna caminho do arquivo de log
    
    Returns:
        Path do arquivo de log
    """
    settings = get_settings()
    return Path(settings.LOG_FILE)


# ========================================================================
# Inicialização automática
# ========================================================================

# Configura logging na importação do módulo
setup_logging()


# ========================================================================
# Exportações
# ========================================================================

__all__ = [
    'setup_logging',
    'get_logger',
    'set_log_level',
    'get_log_file_path',
]
