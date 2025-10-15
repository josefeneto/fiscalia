"""
Modelos de Dados do Sistema Fiscalia
Define as tabelas do banco de dados usando SQLAlchemy ORM
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, 
    Boolean, Numeric, Date, JSON, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class RegistroResultado(Base):
    """
    Tabela de registro de processamento de arquivos
    Armazena resultado de cada tentativa de processamento
    """
    __tablename__ = "registo_resultados"
    
    # Colunas
    numero_sequencial = Column(Integer, primary_key=True, autoincrement=True)
    time_stamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    path_nome_arquivo = Column(Text, nullable=False)
    resultado = Column(String(50), nullable=False, index=True)  # Sucesso/Insucesso
    causa = Column(Text)  # Motivo do resultado
    tipo_arquivo = Column(String(20))  # XML, PDF, CSV, etc
    tamanho_bytes = Column(Integer)  # Tamanho do arquivo
    hash_arquivo = Column(String(64))  # Hash MD5 para detectar duplicados
    
    # Índices compostos para queries comuns
    __table_args__ = (
        Index('idx_resultado_timestamp', 'resultado', 'time_stamp'),
        Index('idx_hash_arquivo', 'hash_arquivo'),
    )
    
    def __repr__(self):
        return f"<RegistroResultado(id={self.numero_sequencial}, resultado={self.resultado}, arquivo={self.path_nome_arquivo})>"
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'numero_sequencial': self.numero_sequencial,
            'time_stamp': self.time_stamp.isoformat() if self.time_stamp else None,
            'path_nome_arquivo': self.path_nome_arquivo,
            'resultado': self.resultado,
            'causa': self.causa,
            'tipo_arquivo': self.tipo_arquivo,
            'tamanho_bytes': self.tamanho_bytes,
            'hash_arquivo': self.hash_arquivo
        }


class DocumentoParaERP(Base):
    """
    Tabela de documentos fiscais processados
    Armazena dados extraídos para posterior integração com ERP
    """
    __tablename__ = "docs_para_ERP"
    
    # Identificação e controle
    numero_sequencial = Column(Integer, primary_key=True, autoincrement=True)
    time_stamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    path_nome_arquivo = Column(Text, nullable=False)
    hash_arquivo = Column(String(64), unique=True, nullable=False)  # Prevenir duplicados
    
    # Tipo de documento
    tipo_documento = Column(String(20), nullable=False, index=True)  # NFe, NFCe, CTe, MDFe
    modelo = Column(String(10))  # 55, 65, 57, 58
    
    # Dados principais da NF
    chave_acesso = Column(String(44), unique=True, index=True)  # Chave de 44 dígitos
    numero_nf = Column(String(20), nullable=False, index=True)
    serie = Column(String(10))
    data_emissao = Column(Date, nullable=False, index=True)
    data_saida_entrada = Column(Date)
    tipo_operacao = Column(String(1))  # 0=Entrada, 1=Saída
    
    # Emitente
    emitente_cnpj = Column(String(14), index=True)
    emitente_cpf = Column(String(11))
    emitente_nome = Column(String(200), nullable=False)
    emitente_nome_fantasia = Column(String(200))
    emitente_ie = Column(String(20))  # Inscrição Estadual
    emitente_uf = Column(String(2))
    emitente_municipio = Column(String(100))
    
    # Destinatário
    destinatario_cnpj = Column(String(14), index=True)
    destinatario_cpf = Column(String(11))
    destinatario_nome = Column(String(200), nullable=False)
    destinatario_nome_fantasia = Column(String(200))
    destinatario_ie = Column(String(20))
    destinatario_uf = Column(String(2))
    destinatario_municipio = Column(String(100))
    
    # Valores totais
    valor_total = Column(Numeric(15, 2), nullable=False)
    valor_produtos = Column(Numeric(15, 2))
    valor_servicos = Column(Numeric(15, 2))
    valor_frete = Column(Numeric(15, 2))
    valor_seguro = Column(Numeric(15, 2))
    valor_desconto = Column(Numeric(15, 2))
    valor_outras_despesas = Column(Numeric(15, 2))
    
    # Impostos
    valor_icms = Column(Numeric(15, 2))
    valor_icms_st = Column(Numeric(15, 2))  # Substituição Tributária
    valor_ipi = Column(Numeric(15, 2))
    valor_pis = Column(Numeric(15, 2))
    valor_cofins = Column(Numeric(15, 2))
    valor_ii = Column(Numeric(15, 2))  # Imposto de Importação
    
    # Informações fiscais
    cfop = Column(String(10), index=True)  # CFOP principal
    natureza_operacao = Column(String(200))
    finalidade_emissao = Column(String(1))  # 1=Normal, 2=Complementar, 3=Ajuste, 4=Devolução
    
    # Dados XML completos
    items_json = Column(JSON)  # Array de itens da NF
    impostos_detalhados_json = Column(JSON)  # Detalhamento de impostos
    transporte_json = Column(JSON)  # Dados de transporte
    pagamento_json = Column(JSON)  # Formas de pagamento
    xml_completo = Column(Text)  # XML original completo (opcional)
    
    # Informações adicionais
    informacoes_complementares = Column(Text)
    informacoes_fisco = Column(Text)
    
    # Protocolo e autorização
    protocolo_autorizacao = Column(String(50))
    data_autorizacao = Column(DateTime)
    
    # Controle ERP
    erp_processado = Column(Boolean, default=False, nullable=False, index=True)
    erp_data_processamento = Column(DateTime)
    erp_usuario = Column(String(100))
    erp_observacoes = Column(Text)
    
    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Índices compostos para queries comuns
    __table_args__ = (
        Index('idx_emitente_data', 'emitente_cnpj', 'data_emissao'),
        Index('idx_destinatario_data', 'destinatario_cnpj', 'data_emissao'),
        Index('idx_tipo_data', 'tipo_documento', 'data_emissao'),
        Index('idx_erp_processado', 'erp_processado', 'data_emissao'),
        Index('idx_chave_acesso', 'chave_acesso'),
    )
    
    def __repr__(self):
        return f"<DocumentoParaERP(id={self.numero_sequencial}, tipo={self.tipo_documento}, numero={self.numero_nf}, valor={self.valor_total})>"
    
    def to_dict(self, include_xml=False):
        """
        Converte o objeto para dicionário
        
        Args:
            include_xml: Se True, inclui o XML completo (pode ser grande)
        """
        data = {
            'numero_sequencial': self.numero_sequencial,
            'time_stamp': self.time_stamp.isoformat() if self.time_stamp else None,
            'path_nome_arquivo': self.path_nome_arquivo,
            'tipo_documento': self.tipo_documento,
            'modelo': self.modelo,
            'chave_acesso': self.chave_acesso,
            'numero_nf': self.numero_nf,
            'serie': self.serie,
            'data_emissao': self.data_emissao.isoformat() if self.data_emissao else None,
            'data_saida_entrada': self.data_saida_entrada.isoformat() if self.data_saida_entrada else None,
            'tipo_operacao': self.tipo_operacao,
            'emitente': {
                'cnpj': self.emitente_cnpj,
                'cpf': self.emitente_cpf,
                'nome': self.emitente_nome,
                'nome_fantasia': self.emitente_nome_fantasia,
                'ie': self.emitente_ie,
                'uf': self.emitente_uf,
                'municipio': self.emitente_municipio
            },
            'destinatario': {
                'cnpj': self.destinatario_cnpj,
                'cpf': self.destinatario_cpf,
                'nome': self.destinatario_nome,
                'nome_fantasia': self.destinatario_nome_fantasia,
                'ie': self.destinatario_ie,
                'uf': self.destinatario_uf,
                'municipio': self.destinatario_municipio
            },
            'valores': {
                'total': float(self.valor_total) if self.valor_total else 0,
                'produtos': float(self.valor_produtos) if self.valor_produtos else 0,
                'servicos': float(self.valor_servicos) if self.valor_servicos else 0,
                'frete': float(self.valor_frete) if self.valor_frete else 0,
                'seguro': float(self.valor_seguro) if self.valor_seguro else 0,
                'desconto': float(self.valor_desconto) if self.valor_desconto else 0,
                'outras_despesas': float(self.valor_outras_despesas) if self.valor_outras_despesas else 0
            },
            'impostos': {
                'icms': float(self.valor_icms) if self.valor_icms else 0,
                'icms_st': float(self.valor_icms_st) if self.valor_icms_st else 0,
                'ipi': float(self.valor_ipi) if self.valor_ipi else 0,
                'pis': float(self.valor_pis) if self.valor_pis else 0,
                'cofins': float(self.valor_cofins) if self.valor_cofins else 0,
                'ii': float(self.valor_ii) if self.valor_ii else 0
            },
            'fiscal': {
                'cfop': self.cfop,
                'natureza_operacao': self.natureza_operacao,
                'finalidade_emissao': self.finalidade_emissao
            },
            'items': self.items_json,
            'impostos_detalhados': self.impostos_detalhados_json,
            'transporte': self.transporte_json,
            'pagamento': self.pagamento_json,
            'informacoes_complementares': self.informacoes_complementares,
            'informacoes_fisco': self.informacoes_fisco,
            'protocolo_autorizacao': self.protocolo_autorizacao,
            'data_autorizacao': self.data_autorizacao.isoformat() if self.data_autorizacao else None,
            'erp_processado': self.erp_processado,
            'erp_data_processamento': self.erp_data_processamento.isoformat() if self.erp_data_processamento else None,
            'erp_usuario': self.erp_usuario,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_xml:
            data['xml_completo'] = self.xml_completo
        
        return data
    
    def get_total_impostos(self):
        """Calcula o total de impostos"""
        total = 0
        if self.valor_icms:
            total += float(self.valor_icms)
        if self.valor_icms_st:
            total += float(self.valor_icms_st)
        if self.valor_ipi:
            total += float(self.valor_ipi)
        if self.valor_pis:
            total += float(self.valor_pis)
        if self.valor_cofins:
            total += float(self.valor_cofins)
        if self.valor_ii:
            total += float(self.valor_ii)
        return total
