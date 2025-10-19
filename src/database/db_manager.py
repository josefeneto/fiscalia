# src/database/db_manager.py - ARQUIVO COMPLETO CORRIGIDO

"""
Gerenciador do banco de dados SQLite
"""

import os
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError

from .models import Base, DocParaERP, RegistroResultado
from ..utils.config import get_settings
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class DatabaseManager:
    """Gerenciador do banco de dados SQLite"""
    
    _instance = None
    _engine = None
    _SessionLocal = None
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Inicializa conexão com banco de dados"""
        if self._engine is None:
            settings = get_settings()
            db_path = Path(settings.database_path)
            
            # Criar diretório se não existir
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Criar engine
            database_url = f"sqlite:///{db_path}"
            self._engine = create_engine(
                database_url,
                echo=False,
                connect_args={"check_same_thread": False}
            )
            
            # Criar tabelas
            Base.metadata.create_all(bind=self._engine)
            
            # Criar SessionLocal
            self._SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine
            )
            
            logger.info(f"Database inicializado: {db_path}")
    
    def get_session(self) -> Session:
        """Retorna uma nova sessão do banco de dados"""
        return self._SessionLocal()
    
    def add_documento(self, doc_data: dict) -> Optional[int]:
        """
        Adiciona documento à tabela docs_para_erp
        
        Args:
            doc_data: Dicionário com dados do documento
            
        Returns:
            ID do documento inserido ou None se erro
        """
        session = self.get_session()
        try:
            doc = DocParaERP(**doc_data)
            session.add(doc)
            session.commit()
            session.refresh(doc)
            logger.info(f"Documento adicionado: Número {doc.numero_nf}")
            return doc.id
        except IntegrityError as e:
            session.rollback()
            logger.error(f"Documento duplicado: {e}")
            return None
        except Exception as e:
            session.rollback()
            logger.error(f"Erro ao adicionar documento: {e}")
            return None
        finally:
            session.close()
    
    def add_resultado(self, resultado_data: dict) -> Optional[int]:
        """
        Adiciona resultado de processamento
        
        Args:
            resultado_data: Dicionário com dados do resultado
            
        Returns:
            ID do resultado inserido ou None se erro
        """
        session = self.get_session()
        try:
            resultado = RegistroResultado(**resultado_data)
            session.add(resultado)
            session.commit()
            session.refresh(resultado)
            logger.info(f"Resultado registrado: {resultado.resultado}")
            return resultado.id
        except Exception as e:
            session.rollback()
            logger.error(f"Erro ao registrar resultado: {e}")
            return None
        finally:
            session.close()
    
    def check_documento_existe(self, chave_acesso: str) -> bool:
        """
        Verifica se documento já existe no banco
        
        Args:
            chave_acesso: Chave de acesso da nota fiscal
            
        Returns:
            True se existe, False caso contrário
        """
        session = self.get_session()
        try:
            existe = session.query(DocParaERP).filter(
                DocParaERP.chave_acesso == chave_acesso
            ).first() is not None
            return existe
        finally:
            session.close()
    
    def get_documento_by_chave(self, chave_acesso: str) -> Optional[DocParaERP]:
        """
        Busca documento por chave de acesso
        
        Args:
            chave_acesso: Chave de acesso da nota fiscal
            
        Returns:
            Objeto DocParaERP ou None
        """
        session = self.get_session()
        try:
            return session.query(DocParaERP).filter(
                DocParaERP.chave_acesso == chave_acesso
            ).first()
        finally:
            session.close()
    
    def get_recent_documents(self, limit: int = 10) -> List[DocParaERP]:
        """
        Retorna documentos mais recentes
        
        Args:
            limit: Número máximo de documentos
            
        Returns:
            Lista de objetos DocParaERP
        """
        session = self.get_session()
        try:
            return session.query(DocParaERP).order_by(
                DocParaERP.time_stamp.desc()
            ).limit(limit).all()
        finally:
            session.close()
    
    def get_recent_results(self, limit: int = 10) -> List[RegistroResultado]:
        """
        Retorna resultados mais recentes
        
        Args:
            limit: Número máximo de resultados
            
        Returns:
            Lista de objetos RegistroResultado
        """
        session = self.get_session()
        try:
            return session.query(RegistroResultado).order_by(
                RegistroResultado.time_stamp.desc()
            ).limit(limit).all()
        finally:
            session.close()
    
    def count_documents(self) -> int:
        """Retorna número total de documentos"""
        session = self.get_session()
        try:
            return session.query(DocParaERP).count()
        finally:
            session.close()
    
    def count_results(self) -> int:
        """Retorna número total de resultados"""
        session = self.get_session()
        try:
            return session.query(RegistroResultado).count()
        finally:
            session.close()
    
    def get_statistics(self) -> dict:
        """
        Retorna estatísticas do banco de dados
        
        Returns:
            Dicionário com estatísticas
        """
        session = self.get_session()
        try:
            stats = {
                'total_documentos': session.query(DocParaERP).count(),
                'total_resultados': session.query(RegistroResultado).count(),
                'valor_total': session.query(
                    func.sum(DocParaERP.valor_total)
                ).scalar() or 0.0,
                'documentos_processados_erp': session.query(DocParaERP).filter(
                    DocParaERP.erp_processado == 'Yes'
                ).count(),
                'documentos_pendentes_erp': session.query(DocParaERP).filter(
                    DocParaERP.erp_processado == 'No'
                ).count(),
            }
            return stats
        finally:
            session.close()


# Instância global (singleton)
_db_manager = None


def get_db_manager() -> DatabaseManager:
    """Retorna instância global do DatabaseManager"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def initialize_database():
    """Inicializa o banco de dados (cria tabelas se necessário)"""
    db = get_db_manager()
    logger.info("Database inicializado com sucesso")
    return db


if __name__ == "__main__":
    # Teste básico
    print("Testando DatabaseManager...")
    db = initialize_database()
    print(f"Total de documentos: {db.count_documents()}")
    print(f"Total de resultados: {db.count_results()}")
    print("✅ DatabaseManager funcionando!")