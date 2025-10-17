# src/database/__init__.py - ARQUIVO COMPLETO CORRIGIDO

"""
Módulo de banco de dados para Fiscalia
"""

from database.models import Base, DocParaERP, RegistroResultado
from database.db_manager import DatabaseManager, get_db_manager, initialize_database

__all__ = [
    'Base',
    'DocParaERP',
    'RegistroResultado',
    'DatabaseManager',
    'get_db_manager',
    'initialize_database'
]
