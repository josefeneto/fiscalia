"""
Módulo de processadores de Notas Fiscais
Extração, validação e gerenciamento de arquivos
"""

from src.processors.xml_processor import XMLProcessor
from src.processors.validator import NFValidator, ValidationError
from src.processors.file_handler import FileHandler
from src.processors.nfe_processor import NFeProcessor, ProcessingResult

__all__ = [
    'XMLProcessor',
    'NFValidator',
    'ValidationError',
    'FileHandler',
    'NFeProcessor',
    'ProcessingResult',
]
