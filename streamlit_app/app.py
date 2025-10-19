"""
Fiscalia - Dashboard Principal
Sistema de Processamento de NFe com CrewAI
"""

import streamlit as st
import sys
from pathlib import Path

# Adicionar src ao path
root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path))

from src.utils.config import get_settings, validate_settings
from src.database.db_manager import DatabaseManager
from streamlit_app.components.common import (
    show_header,
    show_metrics,
    show_sidebar_info,
    format_currency
)

# ==================== CONFIGURAÇÃO ====================
st.set_page_config(
    page_title="Fiscalia - Processamento de NFe",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/josefeneto/fiscalia',
        'Report a bug': 'https://github.com/josefeneto/fiscalia/issues',
        'About': 'Fiscalia v1.0.0 - Sistema Inteligente de Processamento de NFe'
    }
)

# ==================== CSS CUSTOMIZADO ====================
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        color: #1f77b4;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stButton>button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# ==================== FUNÇÕES ====================

@st.cache_resource
def get_db():
    """Inicializa conexão com banco de dados"""
    try:
        return DatabaseManager()
    except Exception as e:
        st.error(f"❌ Erro ao conectar ao banco: {str(e)}")
        return None


def get_estatisticas_gerais(db):
    """Obtém estatísticas gerais do sistema"""
    try:
        stats = db.get_statistics()
        return stats
    except Exception as e:
        st.error(f"Erro ao buscar estatísticas: {str(e)}")
        return None


# ==================== VALIDAÇÃO ====================
if not validate_settings():
    st.error("⚠️ Configuração incompleta! Verifique o arquivo .env")
    st.stop()

settings = get_settings()

# ==================== SIDEBAR ====================
show_sidebar_info()

# ==================== HEADER ====================
show_header(
    "Fiscalia",
    "Sistema Inteligente de Processamento de Notas Fiscais Eletrônicas"
)

# ==================== INFO BOX ====================
st.markdown("""
    <div style="background-color: #e7f3ff; border-left: 5px solid #1f77b4; 
                padding: 1rem; border-radius: 5px; margin: 1rem 0;">
        <strong>👋 Bem-vindo ao Fiscalia!</strong><br>
        Sistema de processamento automático de Notas Fiscais Eletrônicas (NFe) 
        usando Inteligência Artificial Multi-Agente com CrewAI.
    </div>
""", unsafe_allow_html=True)

# ==================== CONECTAR AO BANCO ====================
db = get_db()

if not db:
    st.error("❌ Não foi possível conectar ao banco de dados.")
    st.info("💡 Verifique se o banco está configurado corretamente.")
    st.stop()

# ==================== MÉTRICAS PRINCIPAIS ====================
st.markdown("### 📊 Visão Geral do Sistema")

stats = get_estatisticas_gerais(db)

if stats:
    # Linha 1: Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📝 NFes Processadas",
            value=f"{stats['total_documentos']:,}",
            help="Total de notas fiscais no sistema"
        )
    
    with col2:
        valor_total = stats['valor_total'] or 0
        st.metric(
            label="💰 Valor Total",
            value=format_currency(valor_total),
            help="Soma de todas as notas fiscais"
        )
    
    with col3:
        st.metric(
            label="✅ Processadas ERP",
            value=f"{stats['documentos_processados_erp']:,}",
            help="Notas já integradas ao ERP"
        )
    
    with col4:
        st.metric(
            label="⏳ Pendentes ERP",
            value=f"{stats['documentos_pendentes_erp']:,}",
            help="Notas aguardando integração"
        )
    
    # Progress bar
    if stats['total_documentos'] > 0:
        percentual = (stats['documentos_processados_erp'] / stats['total_documentos']) * 100
        st.progress(percentual / 100, text=f"Processamento ERP: {percentual:.1f}%")

else:
    st.warning("⚠️ Ainda não há dados processados no sistema.")
    st.info("💡 Use a página **📤 Upload** para começar a processar notas fiscais!")

st.markdown("---")

# ==================== FUNCIONALIDADES ====================
st.markdown("### 🚀 Funcionalidades Principais")

col1, col2 = st.columns(2)

with col1:
    with st.container():
        st.markdown("""
        #### 📤 Processamento de NFe
        - ✅ Upload de arquivos XML individuais
        - ✅ Processamento em lote (batch)
        - ✅ Validação automática de dados
        - ✅ Detecção de duplicatas
        - ✅ Movimentação inteligente de arquivos
        
        #### 🤖 Inteligência Artificial
        - **Coordinator Agent**: Orquestra processamento
        - **Auditor Agent**: Análise fiscal e conformidade
        - **Analyst Agent**: Business Intelligence
        """)

with col2:
    with st.container():
        st.markdown("""
        #### 📊 Análises e Relatórios
        - 📈 Dashboard interativo em tempo real
        - 🗺️ Análises geográficas por estado
        - 🏢 Rankings de emitentes
        - 🔍 Detecção de anomalias
        - 💼 Consolidados fiscais e tributários
        
        #### 💬 Consultas Inteligentes
        - Perguntas em linguagem natural
        - Insights automáticos dos agentes AI
        - Relatórios executivos personalizados
        """)

st.markdown("---")

# ==================== QUICK START ====================
st.markdown("### 🎯 Como Começar")

with st.expander("📝 Guia Rápido", expanded=False):
    st.markdown("""
    #### 1️⃣ Upload de XMLs
    Vá para a página **📤 Upload** no menu lateral e:
    - Arraste ou selecione arquivos XML de NFe
    - Ou deposite arquivos na pasta `/entrados` para processamento em lote
    - Clique em "Processar Arquivos"
    
    #### 2️⃣ Visualizar Dados
    Acesse **📊 Visualizar BD** para:
    - Ver todas as NFes processadas
    - Filtrar por emitente, data, estado, etc.
    - Examinar detalhes completos de cada nota
    
    #### 3️⃣ Análises Estatísticas
    Explore **📈 Estatísticas** para:
    - Gráficos interativos de valores e volumes
    - Análises por estado e emitente
    - Identificação de padrões e tendências
    
    #### 4️⃣ Consultas com IA
    Use **💬 Consultas** para:
    - Fazer perguntas sobre seus dados
    - Obter insights dos agentes de IA
    - Gerar relatórios executivos automáticos
    """)

st.markdown("---")

# ==================== ÚLTIMAS NFes ====================
st.markdown("### 📋 Últimas NFes Processadas")

try:
    ultimas = db.get_recent_documents(5)
    
    if ultimas:
        import pandas as pd
        
        # Preparar dados
        data = []
        for doc in ultimas:
            data.append({
                'Número': doc.numero_nf,
                'Emitente': doc.razao_social_emitente,
                'Destinatário': doc.razao_social_destinatario,
                'Valor': format_currency(doc.valor_total),
                'Data': doc.data_emissao.strftime('%d/%m/%Y') if doc.data_emissao else 'N/A',
                'ERP': '✅' if doc.erp_processado == 'Yes' else '⏳'
            })
        
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma NFe processada ainda. Comece fazendo upload de arquivos XML!")
        
except Exception as e:
    st.error(f"Erro ao carregar últimas NFes: {str(e)}")

st.markdown("---")

# ==================== SISTEMA INFO ====================
with st.expander("ℹ️ Informações do Sistema", expanded=False):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🔧 Configuração Atual**")
        st.code(f"""
Ambiente: {settings.is_production and 'Produção' or 'Desenvolvimento'}
LLM Provider: {settings.llm_provider}
Modelo: {settings.llm_model}
Database: {settings.db_type.upper()}
        """)
    
    with col2:
        st.markdown("**📊 Limites de Processamento**")
        st.code(f"""
Max arquivos/batch: {settings.max_files_per_batch}
Max tamanho arquivo: {settings.max_file_size_mb} MB
Timeout processamento: {settings.processing_timeout}s
        """)

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #999; padding: 2rem 0;">
        <p><strong>Fiscalia</strong> © 2025 | Desenvolvido com ❤️ usando CrewAI e Streamlit</p>
        <p style="font-size: 0.9rem;">Sistema de Processamento Inteligente de NFe | v1.0.0</p>
    </div>
""", unsafe_allow_html=True)
