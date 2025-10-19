"""
Fiscalia - Consultas Inteligentes
"""

import streamlit as st
import sys
from pathlib import Path

# Adicionar src ao path
root_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_path))

from src.database.db_manager import DatabaseManager
from streamlit_app.components import show_header

# Configuração
st.set_page_config(page_title="Consultas - Fiscalia", page_icon="💬", layout="wide")

# Header
show_header("Consultas Inteligentes", "Faça perguntas aos agentes de IA")

# Info sobre agentes
with st.expander("🤖 Sobre os Agentes de IA", expanded=False):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 📋 Coordinator Agent
        - Orquestra processamento
        - Gerencia workflow
        - Distribui tarefas
        """)
    
    with col2:
        st.markdown("""
        ### 🔍 Auditor Agent
        - Análise fiscal
        - Detecta anomalias
        - Verifica consistência
        """)
    
    with col3:
        st.markdown("""
        ### 📊 Analyst Agent
        - Business Intelligence
        - Gera insights
        - Análises estatísticas
        """)

st.markdown("---")

# Consultas pré-definidas
st.markdown("### 🎯 Consultas Pré-Definidas")

col1, col2 = st.columns(2)

with col1:
    if st.button("📊 Resumo Geral", use_container_width=True):
        st.info("🚧 Integração CrewAI em desenvolvimento...")

with col2:
    if st.button("🗺️ Análise por Estado", use_container_width=True):
        st.info("🚧 Integração CrewAI em desenvolvimento...")

st.markdown("---")

# Consulta personalizada
st.markdown("### ✍️ Consulta Personalizada")

consulta = st.text_area(
    "Descreva sua pergunta:",
    placeholder="Ex: Qual o total de ICMS por estado?",
    height=100
)

if st.button("🚀 Executar Consulta", type="primary", use_container_width=True):
    if consulta:
        st.info("🚧 Consultas personalizadas em desenvolvimento...")
    else:
        st.warning("⚠️ Digite uma consulta primeiro")

st.markdown("---")
st.info("💡 **Próxima versão**: Integração completa com agentes CrewAI para análises avançadas!")
