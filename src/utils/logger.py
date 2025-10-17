# src/utils/logger.py - ARQUIVO COMPLETO CORRIGIDO

"""
Sistema de logging para Fiscalia
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


def setup_logger(
    name: str,
    level: Optional[str] = None,
    log_file: Optional[Path] = None
) -> logging.Logger:
    """
    Configura e retorna um logger
    
    Args:
        name: Nome do logger
        level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Arquivo para salvar logs (opcional)
    
    Returns:
        Logger configurado
    """
    
    # Obter configurações apenas se disponível
    try:
        from utils.config import get_settings
        settings = get_settings()
        log_level = level or settings.log_level
        default_log_file = settings.log_file
    except:
        # Fallback se config não disponível
        log_level = level or "INFO"
        default_log_file = None
    
    # Criar logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Evitar duplicação de handlers
    if logger.handlers:
        return logger
    
    # Formato do log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para arquivo (se especificado)
    file_to_use = log_file or default_log_file
    if file_to_use:
        file_to_use = Path(file_to_use)
        file_to_use.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(file_to_use, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# Logger padrão do módulo (criado sem dependência de config)
default_logger = setup_logger('fiscalia')


if __name__ == "__main__":
    """Teste standalone"""
    print("=== Teste de Logger ===\n")
    
    logger = setup_logger("test", level="DEBUG")
    
    logger.debug("Mensagem de debug")
    logger.info("Mensagem de info")
    logger.warning("Mensagem de warning")
    logger.error("Mensagem de erro")
    
    print("\n✅ Logger funcionando!")
