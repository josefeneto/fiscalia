"""
Database Manager do Sistema Fiscalia
Gerencia conexões, sessões e operações do banco de dados
"""
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from datetime import datetime, date
from sqlalchemy import create_engine, func, and_, or_
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.pool import StaticPool

from .models import Base, RegistroResultado, DocumentoParaERP
from ..utils.config import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    """Gerenciador do banco de dados SQLite/PostgreSQL"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Inicializa o gerenciador do banco de dados
        
        Args:
            db_path: Caminho customizado do banco (opcional)
        """
        self.db_path = db_path or settings.get_database_path()
        self.engine = None
        self.SessionLocal = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Inicializa a engine e cria as tabelas"""
        try:
            # Configurar engine baseado no tipo de database
            if settings.db_type == "sqlite":
                # SQLite com configurações otimizadas
                self.engine = create_engine(
                    f"sqlite:///{self.db_path}",
                    connect_args={
                        "check_same_thread": False,  # Permitir multi-thread
                        "timeout": 30  # Timeout de 30 segundos
                    },
                    poolclass=StaticPool,  # Pool estático para SQLite
                    echo=False  # Desativar logs SQL
                )
                logger.info(f"SQLite database inicializado: {self.db_path}")
            
            elif settings.db_type == "postgresql":
                # PostgreSQL (para Railway)
                self.engine = create_engine(
                    settings.database_url,
                    pool_pre_ping=True,  # Verificar conexões
                    pool_size=5,
                    max_overflow=10,
                    echo=settings.environment == "development"
                )
                logger.info("PostgreSQL database conectado")
            
            # Criar SessionMaker
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine,
                expire_on_commit=False  # CRÍTICO: Não expirar objetos após commit
            )
            
            # Criar todas as tabelas
            Base.metadata.create_all(bind=self.engine)
            logger.info("Tabelas do banco de dados criadas/verificadas com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar database: {e}")
            raise
    
    @contextmanager
    def get_session(self) -> Session:
        """
        Context manager para sessões do banco de dados
        
        Yields:
            Session do SQLAlchemy
        
        Example:
            >>> with db_manager.get_session() as session:
            ...     result = session.query(DocumentoParaERP).first()
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
    
    # ==================== OPERAÇÕES - REGISTRO DE RESULTADOS ====================
    
    def adicionar_registro_resultado(
        self,
        path_nome_arquivo: str,
        resultado: str,
        causa: Optional[str] = None,
        tipo_arquivo: Optional[str] = None,
        tamanho_bytes: Optional[int] = None,
        hash_arquivo: Optional[str] = None
    ) -> RegistroResultado:
        """
        Adiciona um registro de resultado de processamento
        
        Args:
            path_nome_arquivo: Caminho completo do arquivo
            resultado: "Sucesso" ou "Insucesso"
            causa: Motivo do resultado
            tipo_arquivo: Tipo do arquivo (XML, PDF, etc)
            tamanho_bytes: Tamanho do arquivo
            hash_arquivo: Hash MD5 do arquivo
        
        Returns:
            RegistroResultado criado
        """
        session = self.SessionLocal()
        try:
            registro = RegistroResultado(
                path_nome_arquivo=path_nome_arquivo,
                resultado=resultado,
                causa=causa,
                tipo_arquivo=tipo_arquivo,
                tamanho_bytes=tamanho_bytes,
                hash_arquivo=hash_arquivo
            )
            session.add(registro)
            session.commit()
            session.refresh(registro)
            
            # Desanexar objeto da sessão para uso externo
            session.expunge(registro)
            
            logger.info(f"Registro de resultado adicionado: {resultado} - {path_nome_arquivo}")
            return registro
            
        except Exception as e:
            session.rollback()
            logger.error(f"Erro ao adicionar registro: {e}")
            raise
        finally:
            session.close()
    
    def buscar_registros_resultados(
        self,
        resultado: Optional[str] = None,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        limite: int = 100
    ) -> List[RegistroResultado]:
        """
        Busca registros de resultados com filtros
        
        Args:
            resultado: Filtrar por resultado (Sucesso/Insucesso)
            data_inicio: Data inicial
            data_fim: Data final
            limite: Número máximo de resultados
        
        Returns:
            Lista de RegistroResultado
        """
        with self.get_session() as session:
            query = session.query(RegistroResultado)
            
            if resultado:
                query = query.filter(RegistroResultado.resultado == resultado)
            
            if data_inicio:
                query = query.filter(RegistroResultado.time_stamp >= data_inicio)
            
            if data_fim:
                query = query.filter(RegistroResultado.time_stamp <= data_fim)
            
            query = query.order_by(RegistroResultado.time_stamp.desc())
            query = query.limit(limite)
            
            return query.all()
    
    def obter_estatisticas_processamento(self) -> Dict[str, Any]:
        """
        Obtém estatísticas gerais de processamento
        
        Returns:
            Dicionário com estatísticas
        """
        with self.get_session() as session:
            total = session.query(func.count(RegistroResultado.numero_sequencial)).scalar()
            sucesso = session.query(func.count(RegistroResultado.numero_sequencial))\
                .filter(RegistroResultado.resultado == "Sucesso").scalar()
            insucesso = session.query(func.count(RegistroResultado.numero_sequencial))\
                .filter(RegistroResultado.resultado == "Insucesso").scalar()
            
            return {
                'total_processamentos': total or 0,
                'total_sucesso': sucesso or 0,
                'total_insucesso': insucesso or 0,
                'taxa_sucesso': round((sucesso / total * 100) if total > 0 else 0, 2)
            }
    
    # ==================== OPERAÇÕES - DOCUMENTOS PARA ERP ====================
    
    def adicionar_documento(self, dados_documento: Dict[str, Any]) -> DocumentoParaERP:
        """
        Adiciona um documento fiscal processado
        
        Args:
            dados_documento: Dicionário com todos os dados do documento
        
        Returns:
            DocumentoParaERP criado
        
        Raises:
            IntegrityError: Se documento duplicado (mesmo hash ou chave)
        """
        session = self.SessionLocal()
        try:
            documento = DocumentoParaERP(**dados_documento)
            session.add(documento)
            session.commit()
            session.refresh(documento)
            
            # Desanexar objeto da sessão
            session.expunge(documento)
            
            logger.info(f"Documento adicionado: {documento.tipo_documento} - {documento.numero_nf}")
            return documento
            
        except Exception as e:
            session.rollback()
            logger.error(f"Erro ao adicionar documento: {e}")
            raise
        finally:
            session.close()
    
    def verificar_documento_duplicado(
        self,
        hash_arquivo: Optional[str] = None,
        chave_acesso: Optional[str] = None
    ) -> Optional[DocumentoParaERP]:
        """
        Verifica se documento já existe no banco
        
        Args:
            hash_arquivo: Hash MD5 do arquivo
            chave_acesso: Chave de acesso da NF
        
        Returns:
            DocumentoParaERP se encontrado, None caso contrário
        """
        with self.get_session() as session:
            query = session.query(DocumentoParaERP)
            
            conditions = []
            if hash_arquivo:
                conditions.append(DocumentoParaERP.hash_arquivo == hash_arquivo)
            if chave_acesso:
                conditions.append(DocumentoParaERP.chave_acesso == chave_acesso)
            
            if conditions:
                query = query.filter(or_(*conditions))
                return query.first()
            
            return None
    
    def buscar_documentos(
        self,
        tipo_documento: Optional[str] = None,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        emitente_cnpj: Optional[str] = None,
        destinatario_cnpj: Optional[str] = None,
        erp_processado: Optional[bool] = None,
        limite: int = 100,
        offset: int = 0
    ) -> List[DocumentoParaERP]:
        """
        Busca documentos com diversos filtros
        
        Args:
            tipo_documento: Tipo (NFe, NFCe, CTe, MDFe)
            data_inicio: Data inicial de emissão
            data_fim: Data final de emissão
            emitente_cnpj: CNPJ do emitente
            destinatario_cnpj: CNPJ do destinatário
            erp_processado: Filtrar por status ERP
            limite: Número máximo de resultados
            offset: Offset para paginação
        
        Returns:
            Lista de DocumentoParaERP
        """
        with self.get_session() as session:
            query = session.query(DocumentoParaERP)
            
            if tipo_documento:
                query = query.filter(DocumentoParaERP.tipo_documento == tipo_documento)
            
            if data_inicio:
                query = query.filter(DocumentoParaERP.data_emissao >= data_inicio)
            
            if data_fim:
                query = query.filter(DocumentoParaERP.data_emissao <= data_fim)
            
            if emitente_cnpj:
                query = query.filter(DocumentoParaERP.emitente_cnpj == emitente_cnpj)
            
            if destinatario_cnpj:
                query = query.filter(DocumentoParaERP.destinatario_cnpj == destinatario_cnpj)
            
            if erp_processado is not None:
                query = query.filter(DocumentoParaERP.erp_processado == erp_processado)
            
            query = query.order_by(DocumentoParaERP.data_emissao.desc())
            query = query.limit(limite).offset(offset)
            
            return query.all()
    
    def marcar_como_processado_erp(
        self,
        documento_id: int,
        usuario: Optional[str] = None,
        observacoes: Optional[str] = None
    ) -> bool:
        """
        Marca documento como processado no ERP
        
        Args:
            documento_id: ID do documento
            usuario: Usuário que processou
            observacoes: Observações sobre o processamento
        
        Returns:
            True se sucesso, False caso contrário
        """
        with self.get_session() as session:
            documento = session.query(DocumentoParaERP).filter(
                DocumentoParaERP.numero_sequencial == documento_id
            ).first()
            
            if documento:
                documento.erp_processado = True
                documento.erp_data_processamento = datetime.utcnow()
                documento.erp_usuario = usuario
                documento.erp_observacoes = observacoes
                
                logger.info(f"Documento {documento_id} marcado como processado no ERP")
                return True
            
            return False
    
    def obter_estatisticas_documentos(self) -> Dict[str, Any]:
        """
        Obtém estatísticas dos documentos fiscais
        
        Returns:
            Dicionário com estatísticas detalhadas
        """
        with self.get_session() as session:
            # Total de documentos
            total = session.query(func.count(DocumentoParaERP.numero_sequencial)).scalar()
            
            # Por tipo
            por_tipo = session.query(
                DocumentoParaERP.tipo_documento,
                func.count(DocumentoParaERP.numero_sequencial)
            ).group_by(DocumentoParaERP.tipo_documento).all()
            
            # Valores totais
            soma_valores = session.query(
                func.sum(DocumentoParaERP.valor_total),
                func.sum(DocumentoParaERP.valor_icms),
                func.sum(DocumentoParaERP.valor_ipi),
                func.sum(DocumentoParaERP.valor_pis),
                func.sum(DocumentoParaERP.valor_cofins)
            ).first()
            
            # Status ERP
            erp_processados = session.query(func.count(DocumentoParaERP.numero_sequencial))\
                .filter(DocumentoParaERP.erp_processado == True).scalar()
            erp_pendentes = session.query(func.count(DocumentoParaERP.numero_sequencial))\
                .filter(DocumentoParaERP.erp_processado == False).scalar()
            
            return {
                'total_documentos': total or 0,
                'por_tipo': {tipo: count for tipo, count in por_tipo},
                'valores': {
                    'total': float(soma_valores[0]) if soma_valores[0] else 0,
                    'icms': float(soma_valores[1]) if soma_valores[1] else 0,
                    'ipi': float(soma_valores[2]) if soma_valores[2] else 0,
                    'pis': float(soma_valores[3]) if soma_valores[3] else 0,
                    'cofins': float(soma_valores[4]) if soma_valores[4] else 0
                },
                'erp': {
                    'processados': erp_processados or 0,
                    'pendentes': erp_pendentes or 0
                }
            }
    
    # ==================== UTILIDADES ====================
    
    def limpar_tabelas(self, confirmar: bool = False):
        """
        CUIDADO: Remove todos os dados das tabelas
        
        Args:
            confirmar: Deve ser True para executar
        """
        if not confirmar:
            logger.warning("Tentativa de limpar tabelas sem confirmação")
            return False
        
        with self.get_session() as session:
            session.query(DocumentoParaERP).delete()
            session.query(RegistroResultado).delete()
            logger.warning("Todas as tabelas foram limpas!")
            return True
    
    def fechar(self):
        """Fecha todas as conexões do banco"""
        if self.engine:
            self.engine.dispose()
            logger.info("Conexões do banco de dados fechadas")


# Instância global do DatabaseManager
_db_manager = None

def get_db_manager() -> DatabaseManager:
    """
    Factory function para obter instância singleton do DatabaseManager
    
    Returns:
        DatabaseManager global
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


# Exportar para facilitar importação
__all__ = [
    "DatabaseManager",
    "get_db_manager",
    "RegistroResultado",
    "DocumentoParaERP"
]
