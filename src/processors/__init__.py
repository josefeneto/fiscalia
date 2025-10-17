# src/processors/__init__.py - ARQUIVO COMPLETO CORRIGIDO

"""
Módulo de processadores de documentos fiscais
"""

from processors.xml_processor import XMLProcessor
from processors.validator import NFValidator
from processors.file_handler import FileHandler
from processors.nfe_processor import NFeProcessor

__all__ = [
    'XMLProcessor',
    'NFValidator',
    'FileHandler',
    'NFeProcessor'
]
