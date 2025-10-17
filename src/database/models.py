# src/database/models.py - ARQUIVO COMPLETO (sem alterações, mas segue completo)

"""
Modelos de dados SQLAlchemy para Fiscalia
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class DocParaERP(Base):
    """Tabela de documentos fiscais processados"""
    
    __tablename__ = 'docs_para_erp'
    
    # Campos de controle
    id = Column(Integer, primary_key=True, autoincrement=True)
    time_stamp = Column(DateTime, default=datetime.now, nullable=False)
    path_nome_arquivo = Column(String(500), nullable=False)
    erp_processado = Column(String(3), default='No', nullable=False)  # Yes/No
    
    # Dados da Nota Fiscal
    chave_acesso = Column(String(44), unique=True, nullable=False, index=True)
    numero_nf = Column(String(20), nullable=False)
    serie = Column(String(10))
    modelo = Column(String(10))
    natureza_operacao = Column(String(100))
    tipo_operacao = Column(String(1))  # 0=Entrada, 1=Saída
    data_emissao = Column(DateTime)
    data_saida_entrada = Column(DateTime)
    
    # Emitente
    cnpj_emitente = Column(String(14))
    cpf_emitente = Column(String(11))
    razao_social_emitente = Column(String(200))
    nome_fantasia_emitente = Column(String(200))
    ie_emitente = Column(String(20))
    uf_emitente = Column(String(2))
    municipio_emitente = Column(String(100))
    
    # Destinatário
    cnpj_destinatario = Column(String(14))
    cpf_destinatario = Column(String(11))
    razao_social_destinatario = Column(String(200))
    ie_destinatario = Column(String(20))
    uf_destinatario = Column(String(2))
    municipio_destinatario = Column(String(100))
    
    # Valores
    valor_total = Column(Float, default=0.0)
    valor_produtos = Column(Float, default=0.0)
    valor_frete = Column(Float, default=0.0)
    valor_seguro = Column(Float, default=0.0)
    valor_desconto = Column(Float, default=0.0)
    valor_outras_despesas = Column(Float, default=0.0)
    
    # Impostos
    base_calculo_icms = Column(Float, default=0.0)
    valor_icms = Column(Float, default=0.0)
    valor_ipi = Column(Float, default=0.0)
    valor_pis = Column(Float, default=0.0)
    valor_cofins = Column(Float, default=0.0)
    
    # Códigos Fiscais
    cfop = Column(String(10))
    
    # Informações Adicionais
    info_complementar = Column(Text)
    info_fisco = Column(Text)
    
    def __repr__(self):
        return f"<DocParaERP(nf={self.numero_nf}, valor={self.valor_total})>"


class RegistroResultado(Base):
    """Tabela de registro de resultados de processamento"""
    
    __tablename__ = 'registo_resultados'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    time_stamp = Column(DateTime, default=datetime.now, nullable=False, index=True)
    path_nome_arquivo = Column(String(500), nullable=False)
    resultado = Column(String(50), nullable=False)  # Sucesso, Insucesso
    causa = Column(String(500))  # Descrição do erro ou sucesso
    
    def __repr__(self):
        return f"<RegistroResultado(arquivo={self.path_nome_arquivo}, resultado={self.resultado})>"
