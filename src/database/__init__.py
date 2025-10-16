"""
Módulo de banco de dados do sistema Fiscalia
Gerenciamento de dados com SQLite e SQLAlchemy
"""

from src.database.models import Base, DocParaERP, RegistroResultado
from src.database.db_manager import DatabaseManager, get_db_manager, initialize_database

__all__ = [
    'Base',
    'DocParaERP',
    'RegistroResultado',
    'DatabaseManager',
    'get_db_manager',
    'initialize_database',
]
