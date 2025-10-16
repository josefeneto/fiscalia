"""
Modelos de dados SQLAlchemy para o sistema Fiscalia
Define estrutura das tabelas do banco de dados
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, Float, DateTime, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Classe base para todos os modelos"""
    pass


class DocParaERP(Base):
    """
    Tabela para armazenar documentos fiscais para processamento ERP
    Armazena dados extraídos de XMLs de Notas Fiscais
    """
    __tablename__ = 'docs_para_erp'
    
    # Chave primária
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Timestamp e controle
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    arquivo_path: Mapped[str] = mapped_column(String(500))
    arquivo_hash: Mapped[str] = mapped_column(String(32), unique=True, index=True)  # MD5 hash
    
    # Metadados do documento
    tipo_documento: Mapped[str] = mapped_column(String(20))  # NFe, NFCe, CTe, MDFe
    chave_acesso: Mapped[Optional[str]] = mapped_column(String(44), index=True)  # Removido unique=True
    numero: Mapped[Optional[str]] = mapped_column(String(20))
    serie: Mapped[Optional[str]] = mapped_column(String(10))
    data_emissao: Mapped[Optional[str]] = mapped_column(String(10))  # YYYY-MM-DD
    modelo: Mapped[Optional[str]] = mapped_column(String(2))
    natureza_operacao: Mapped[Optional[str]] = mapped_column(String(200))
    tipo_operacao: Mapped[Optional[str]] = mapped_column(String(1))  # 0=Entrada, 1=Saída
    
    # Emitente
    emitente_cnpj: Mapped[Optional[str]] = mapped_column(String(14))
    emitente_cpf: Mapped[Optional[str]] = mapped_column(String(11))
    emitente_razao_social: Mapped[Optional[str]] = mapped_column(String(200))
    emitente_ie: Mapped[Optional[str]] = mapped_column(String(20))
    
    # Destinatário
    destinatario_cnpj: Mapped[Optional[str]] = mapped_column(String(14))
    destinatario_cpf: Mapped[Optional[str]] = mapped_column(String(11))
    destinatario_razao_social: Mapped[Optional[str]] = mapped_column(String(200))
    
    # Valores
    valor_total: Mapped[Optional[float]] = mapped_column(Float, default=0.0)
    valor_produtos: Mapped[Optional[float]] = mapped_column(Float, default=0.0)
    valor_desconto: Mapped[Optional[float]] = mapped_column(Float, default=0.0)
    
    # Impostos
    valor_icms: Mapped[Optional[float]] = mapped_column(Float, default=0.0)
    valor_ipi: Mapped[Optional[float]] = mapped_column(Float, default=0.0)
    valor_pis: Mapped[Optional[float]] = mapped_column(Float, default=0.0)
    valor_cofins: Mapped[Optional[float]] = mapped_column(Float, default=0.0)
    
    # Status ERP
    erp_processado: Mapped[str] = mapped_column(String(3), default='No')  # Yes/No
    
    def __repr__(self) -> str:
        return f"<DocParaERP(id={self.id}, numero={self.numero}, emitente={self.emitente_razao_social})>"


class RegistroResultado(Base):
    """
    Tabela para registrar resultados de processamento de arquivos
    Log de todas as operações (sucesso/insucesso)
    """
    __tablename__ = 'registo_resultados'
    
    # Chave primária
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Timestamp
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, index=True)
    
    # Informações do arquivo
    arquivo_path: Mapped[str] = mapped_column(String(500))
    arquivo_hash: Mapped[str] = mapped_column(String(32), index=True)  # MD5 hash
    
    # Resultado
    resultado: Mapped[str] = mapped_column(String(20), index=True)  # Sucesso/Insucesso
    causa: Mapped[Optional[str]] = mapped_column(Text)  # Detalhes do resultado
    
    def __repr__(self) -> str:
        return f"<RegistroResultado(id={self.id}, resultado={self.resultado}, timestamp={self.timestamp})>"
