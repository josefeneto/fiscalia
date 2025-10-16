"""
Gerenciador de banco de dados SQLite para o sistema Fiscalia
Versão corrigida com métodos para Etapa 3
"""

from contextlib import contextmanager
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from src.database.models import Base, DocParaERP, RegistroResultado
from src.utils.config import get_settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    """Gerenciador do banco de dados SQLite"""
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Inicializa o gerenciador de banco de dados
        
        Args:
            db_path: Caminho customizado para o banco (opcional)
        """
        self.settings = get_settings()
        
        # Define caminho do banco
        if db_path:
            self.db_path = Path(db_path)
        else:
            self.db_path = Path(self.settings.SQLITE_DB_PATH)
        
        # Garante que diretório existe
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Cria engine e sessão
        self.engine = None
        self.SessionLocal = None
        
        self._initialize_database()
    
    def _initialize_database(self):
        """Inicializa conexão com banco de dados e cria tabelas"""
        try:
            # URL do banco
            db_url = f"sqlite:///{self.db_path}"
            
            # Cria engine
            self.engine = create_engine(
                db_url,
                echo=False,
                connect_args={"check_same_thread": False}
            )
            
            # Cria sessionmaker
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine,
                expire_on_commit=False  # IMPORTANTE: mantém objetos acessíveis após commit
            )
            
            # Cria todas as tabelas
            Base.metadata.create_all(bind=self.engine)
            
            logger.info(f"SQLite database inicializado: {self.db_path}")
            logger.info("Tabelas do banco de dados criadas/verificadas com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar banco de dados: {e}")
            raise
    
    @contextmanager
    def _get_session(self) -> Session:
        """
        Context manager para sessões do banco
        
        Yields:
            Session do SQLAlchemy
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Erro na sessão do banco: {e}")
            raise
        finally:
            session.close()
    
    # ========================================================================
    # OPERAÇÕES: DocParaERP
    # ========================================================================
    
    def add_doc_para_erp(self, doc_data: dict) -> DocParaERP:
        """
        Adiciona documento para processamento ERP
        
        Args:
            doc_data: Dicionário com dados do documento
            
        Returns:
            Objeto DocParaERP criado
        """
        doc = DocParaERP(**doc_data)
        
        with self._get_session() as session:
            session.add(doc)
            session.commit()
            session.refresh(doc)
            
            logger.info(f"Documento adicionado: {doc.numero} - {doc.emitente_razao_social}")
            return doc
    
    def get_doc_para_erp_by_id(self, doc_id: int) -> Optional[DocParaERP]:
        """
        Busca documento por ID
        
        Args:
            doc_id: ID do documento
            
        Returns:
            Objeto DocParaERP ou None
        """
        with self._get_session() as session:
            doc = session.query(DocParaERP).filter(DocParaERP.id == doc_id).first()
            return doc
    
    def get_doc_para_erp_by_chave(self, chave_acesso: str) -> Optional[DocParaERP]:
        """
        Busca documento por chave de acesso
        
        Args:
            chave_acesso: Chave de acesso da NFe
            
        Returns:
            Objeto DocParaERP ou None
        """
        with self._get_session() as session:
            doc = session.query(DocParaERP).filter(
                DocParaERP.chave_acesso == chave_acesso
            ).first()
            return doc
    
    def get_all_docs_para_erp(self, limit: Optional[int] = None) -> List[DocParaERP]:
        """
        Retorna todos os documentos
        
        Args:
            limit: Limite de registros (opcional)
            
        Returns:
            Lista de DocParaERP
        """
        with self._get_session() as session:
            query = session.query(DocParaERP).order_by(DocParaERP.data_emissao.desc())
            
            if limit:
                query = query.limit(limit)
            
            docs = query.all()
            return docs
    
    def get_docs_pendentes_erp(self) -> List[DocParaERP]:
        """
        Retorna documentos ainda não processados no ERP
        
        Returns:
            Lista de DocParaERP pendentes
        """
        with self._get_session() as session:
            docs = session.query(DocParaERP).filter(
                DocParaERP.erp_processado == 'No'
            ).order_by(DocParaERP.data_emissao).all()
            
            return docs
    
    def update_doc_erp_processado(self, doc_id: int) -> bool:
        """
        Marca documento como processado no ERP
        
        Args:
            doc_id: ID do documento
            
        Returns:
            True se atualizado com sucesso
        """
        with self._get_session() as session:
            doc = session.query(DocParaERP).filter(DocParaERP.id == doc_id).first()
            
            if doc:
                doc.erp_processado = 'Yes'
                session.commit()
                logger.info(f"Documento {doc_id} marcado como processado no ERP")
                return True
            
            return False
    
    def delete_doc_para_erp(self, doc_id: int) -> bool:
        """
        Remove documento (use com cuidado!)
        
        Args:
            doc_id: ID do documento
            
        Returns:
            True se removido com sucesso
        """
        with self._get_session() as session:
            doc = session.query(DocParaERP).filter(DocParaERP.id == doc_id).first()
            
            if doc:
                session.delete(doc)
                session.commit()
                logger.warning(f"Documento {doc_id} removido do banco")
                return True
            
            return False
    
    def check_duplicate_by_hash(self, arquivo_hash: str) -> bool:
        """
        Verifica se arquivo já foi processado pelo hash
        
        Args:
            arquivo_hash: Hash MD5 do arquivo
            
        Returns:
            True se já existe, False caso contrário
        """
        with self._get_session() as session:
            exists = session.query(DocParaERP).filter(
                DocParaERP.arquivo_hash == arquivo_hash
            ).first() is not None
            
            return exists
    
    # ========================================================================
    # OPERAÇÕES: RegistroResultado
    # ========================================================================
    
    def add_registro_resultado(
        self, 
        arquivo_path: str,
        arquivo_hash: str,
        resultado: str,
        causa: str
    ) -> RegistroResultado:
        """
        Adiciona registro de resultado de processamento
        
        Args:
            arquivo_path: Caminho do arquivo
            arquivo_hash: Hash MD5 do arquivo
            resultado: "Sucesso" ou "Insucesso"
            causa: Descrição do resultado
            
        Returns:
            Objeto RegistroResultado criado
        """
        registro = RegistroResultado(
            arquivo_path=arquivo_path,
            arquivo_hash=arquivo_hash,
            resultado=resultado,
            causa=causa
        )
        
        with self._get_session() as session:
            session.add(registro)
            session.commit()
            session.refresh(registro)
            
            logger.info(f"Registro de resultado adicionado: {resultado}")
            return registro
    
    def get_registro_resultado_by_id(self, registro_id: int) -> Optional[RegistroResultado]:
        """
        Busca registro por ID
        
        Args:
            registro_id: ID do registro
            
        Returns:
            Objeto RegistroResultado ou None
        """
        with self._get_session() as session:
            registro = session.query(RegistroResultado).filter(
                RegistroResultado.id == registro_id
            ).first()
            return registro
    
    def get_all_registros_resultado(self, limit: Optional[int] = None) -> List[RegistroResultado]:
        """
        Retorna todos os registros de resultado
        
        Args:
            limit: Limite de registros (opcional)
            
        Returns:
            Lista de RegistroResultado
        """
        with self._get_session() as session:
            query = session.query(RegistroResultado).order_by(
                RegistroResultado.timestamp.desc()
            )
            
            if limit:
                query = query.limit(limit)
            
            registros = query.all()
            return registros
    
    def get_registros_por_resultado(self, resultado: str) -> List[RegistroResultado]:
        """
        Busca registros por resultado (Sucesso/Insucesso)
        
        Args:
            resultado: "Sucesso" ou "Insucesso"
            
        Returns:
            Lista de RegistroResultado
        """
        with self._get_session() as session:
            registros = session.query(RegistroResultado).filter(
                RegistroResultado.resultado == resultado
            ).order_by(RegistroResultado.timestamp.desc()).all()
            
            return registros
    
    def delete_registro_resultado(self, registro_id: int) -> bool:
        """
        Remove registro (use com cuidado!)
        
        Args:
            registro_id: ID do registro
            
        Returns:
            True se removido com sucesso
        """
        with self._get_session() as session:
            registro = session.query(RegistroResultado).filter(
                RegistroResultado.id == registro_id
            ).first()
            
            if registro:
                session.delete(registro)
                session.commit()
                logger.warning(f"Registro {registro_id} removido do banco")
                return True
            
            return False
    
    # ========================================================================
    # ESTATÍSTICAS E CONSULTAS
    # ========================================================================
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do banco de dados
        
        Returns:
            Dicionário com estatísticas
        """
        with self._get_session() as session:
            # Contagem de documentos
            total_docs = session.query(DocParaERP).count()
            docs_processados_erp = session.query(DocParaERP).filter(
                DocParaERP.erp_processado == 'Yes'
            ).count()
            docs_pendentes_erp = total_docs - docs_processados_erp
            
            # Contagem de registros de resultado
            total_registros = session.query(RegistroResultado).count()
            sucesso = session.query(RegistroResultado).filter(
                RegistroResultado.resultado == 'Sucesso'
            ).count()
            insucesso = session.query(RegistroResultado).filter(
                RegistroResultado.resultado == 'Insucesso'
            ).count()
            
            # Valores totais (opcional - pode ser lento com muitos registros)
            soma_valores = session.query(
                func.sum(DocParaERP.valor_total)
            ).scalar() or 0.0
            
            return {
                'total_docs_para_erp': total_docs,
                'docs_processados_erp': docs_processados_erp,
                'docs_pendentes_erp': docs_pendentes_erp,
                'total_registros_resultado': total_registros,
                'sucesso': sucesso,
                'insucesso': insucesso,
                'soma_valores_total': float(soma_valores)
            }
    
    def get_docs_por_periodo(
        self, 
        data_inicio: str, 
        data_fim: str
    ) -> List[DocParaERP]:
        """
        Busca documentos por período
        
        Args:
            data_inicio: Data início (YYYY-MM-DD)
            data_fim: Data fim (YYYY-MM-DD)
            
        Returns:
            Lista de DocParaERP
        """
        with self._get_session() as session:
            docs = session.query(DocParaERP).filter(
                DocParaERP.data_emissao >= data_inicio,
                DocParaERP.data_emissao <= data_fim
            ).order_by(DocParaERP.data_emissao).all()
            
            return docs
    
    def get_docs_por_emitente(self, cnpj_emitente: str) -> List[DocParaERP]:
        """
        Busca documentos por CNPJ do emitente
        
        Args:
            cnpj_emitente: CNPJ do emitente
            
        Returns:
            Lista de DocParaERP
        """
        with self._get_session() as session:
            docs = session.query(DocParaERP).filter(
                DocParaERP.emitente_cnpj == cnpj_emitente
            ).order_by(DocParaERP.data_emissao.desc()).all()
            
            return docs
    
    # ========================================================================
    # UTILIDADES
    # ========================================================================
    
    def clear_all_data(self) -> bool:
        """
        CUIDADO: Remove TODOS os dados do banco (mantém estrutura)
        
        Returns:
            True se executado com sucesso
        """
        try:
            with self._get_session() as session:
                session.query(DocParaERP).delete()
                session.query(RegistroResultado).delete()
                session.commit()
                
                logger.warning("TODOS os dados foram removidos do banco!")
                return True
                
        except Exception as e:
            logger.error(f"Erro ao limpar dados: {e}")
            return False
    
    def backup_database(self, backup_path: Path) -> bool:
        """
        Cria backup do banco de dados
        
        Args:
            backup_path: Caminho para o arquivo de backup
            
        Returns:
            True se backup criado com sucesso
        """
        try:
            import shutil
            
            backup_path = Path(backup_path)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(self.db_path, backup_path)
            
            logger.info(f"Backup criado: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar backup: {e}")
            return False
    
    def get_table_info(self) -> Dict[str, int]:
        """
        Retorna informações sobre as tabelas
        
        Returns:
            Dicionário com contagem de registros por tabela
        """
        with self._get_session() as session:
            return {
                'docs_para_erp': session.query(DocParaERP).count(),
                'registros_resultado': session.query(RegistroResultado).count()
            }
    
    def close(self):
        """Fecha conexão com banco de dados"""
        if self.engine:
            self.engine.dispose()
            logger.info("Conexão com banco de dados fechada")
    
    def __repr__(self) -> str:
        """Representação em string"""
        return f"DatabaseManager(db_path='{self.db_path}')"
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# ========================================================================
# FUNÇÕES AUXILIARES
# ========================================================================

def get_db_manager() -> DatabaseManager:
    """
    Factory function para obter instância do DatabaseManager
    
    Returns:
        Instância de DatabaseManager
    """
    return DatabaseManager()


def initialize_database(db_path: Optional[Path] = None) -> DatabaseManager:
    """
    Inicializa banco de dados (alias para get_db_manager)
    
    Args:
        db_path: Caminho customizado para o banco (opcional)
        
    Returns:
        Instância de DatabaseManager
    """
    return DatabaseManager(db_path=db_path)