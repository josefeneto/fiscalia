"""
Fiscalia - Estatísticas
"""

import streamlit as st
import sys
from pathlib import Path

# Adicionar src ao path
root_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_path))

from src.database.db_manager import DatabaseManager
from streamlit_app.components import show_header, format_currency

# Configuração
st.set_page_config(page_title="Estatísticas - Fiscalia", page_icon="📈", layout="wide")

# Header
show_header("Estatísticas e Análises", "Dashboard analítico com insights")

# Conectar ao banco
@st.cache_resource
def get_db():
    return DatabaseManager()

db = get_db()

# Buscar estatísticas
st.markdown("### 📊 Visão Geral")

try:
    stats = db.get_statistics()
    
    if stats:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📝 Total NFes", f"{stats['total_documentos']:,}")
        
        with col2:
            st.metric("💰 Valor Total", format_currency(stats['valor_total']))
        
        with col3:
            st.metric("✅ Processadas ERP", f"{stats['documentos_processados_erp']:,}")
        
        with col4:
            st.metric("⏳ Pendentes ERP", f"{stats['documentos_pendentes_erp']:,}")
        
        st.markdown("---")
        st.markdown("### 📈 Gráficos e Análises")
        st.info("🚧 Gráficos detalhados em desenvolvimento...")
        
    else:
        st.warning("⚠️ Sem dados para exibir.")
        
except Exception as e:
    st.error(f"❌ Erro: {str(e)}")
