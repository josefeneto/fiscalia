# src/processors/__init__.py - ARQUIVO COMPLETO CORRIGIDO

"""
Módulo de processadores de documentos fiscais
"""

from .xml_processor import XMLProcessor
from .validator import NFValidator
from .file_handler import FileHandler
from .nfe_processor import NFeProcessor

__all__ = [
    'XMLProcessor',
    'NFValidator',
    'FileHandler',
    'NFeProcessor'
]
