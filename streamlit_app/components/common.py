"""
Componentes comuns reutilizáveis
"""

import streamlit as st
from datetime import datetime


def show_header(title: str, subtitle: str = ""):
    """Exibe header padronizado"""
    st.markdown(f"""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="color: #1f77b4; font-size: 2.5rem; margin-bottom: 0.5rem;">
                📊 {title}
            </h1>
            {f'<p style="color: #666; font-size: 1.1rem;">{subtitle}</p>' if subtitle else ''}
        </div>
    """, unsafe_allow_html=True)


def show_metrics(metrics: dict):
    """
    Exibe métricas em colunas
    
    Args:
        metrics: dict com {label: (value, delta)}
    """
    cols = st.columns(len(metrics))
    
    for col, (label, data) in zip(cols, metrics.items()):
        with col:
            if isinstance(data, tuple):
                value, delta = data
                st.metric(label, value, delta)
            else:
                st.metric(label, data)


def show_error(message: str, details: str = ""):
    """Exibe mensagem de erro estilizada"""
    st.markdown(f"""
        <div style="background-color: #f8d7da; border-left: 5px solid #dc3545; 
                    padding: 1rem; border-radius: 5px; margin: 1rem 0;">
            <strong>❌ {message}</strong>
            {f'<br><small>{details}</small>' if details else ''}
        </div>
    """, unsafe_allow_html=True)


def show_success(message: str, details: str = ""):
    """Exibe mensagem de sucesso estilizada"""
    st.markdown(f"""
        <div style="background-color: #d4edda; border-left: 5px solid #28a745; 
                    padding: 1rem; border-radius: 5px; margin: 1rem 0;">
            <strong>✅ {message}</strong>
            {f'<br><small>{details}</small>' if details else ''}
        </div>
    """, unsafe_allow_html=True)


def show_info(message: str, details: str = ""):
    """Exibe mensagem informativa estilizada"""
    st.markdown(f"""
        <div style="background-color: #d1ecf1; border-left: 5px solid #17a2b8; 
                    padding: 1rem; border-radius: 5px; margin: 1rem 0;">
            <strong>ℹ️ {message}</strong>
            {f'<br><small>{details}</small>' if details else ''}
        </div>
    """, unsafe_allow_html=True)


def show_warning(message: str, details: str = ""):
    """Exibe mensagem de aviso estilizada"""
    st.markdown(f"""
        <div style="background-color: #fff3cd; border-left: 5px solid #ffc107; 
                    padding: 1rem; border-radius: 5px; margin: 1rem 0;">
            <strong>⚠️ {message}</strong>
            {f'<br><small>{details}</small>' if details else ''}
        </div>
    """, unsafe_allow_html=True)


def format_currency(value: float) -> str:
    """Formata valor monetário"""
    try:
        return f"R$ {float(value):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except:
        return "R$ 0,00"


def format_date(date_str: str) -> str:
    """Formata data para exibição"""
    try:
        if isinstance(date_str, str):
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            date_obj = date_str
        return date_obj.strftime('%d/%m/%Y %H:%M')
    except:
        return date_str


def show_sidebar_info():
    """Exibe informações na sidebar"""
    with st.sidebar:
        st.markdown("---")
        st.markdown("### ℹ️ Sistema")
        
        # Status do sistema
        from src.utils.config import get_settings
        settings = get_settings()
        
        st.info(f"""
        **Versão**: 1.0.0  
        **Ambiente**: {'🚀 Produção' if settings.is_production else '💻 Desenvolvimento'}  
        **LLM**: {settings.llm_provider or '❌ Não configurado'}  
        **Database**: {settings.db_type.upper()}
        """)
        
        st.markdown("---")
        st.markdown("### 🔧 Tecnologias")
        st.markdown("""
        - **CrewAI** 0.140.0
        - **Streamlit** 1.46.1
        - **Python** 3.13
        - **SQLite/PostgreSQL**
        """)
        
        st.markdown("---")
        st.caption(f"© 2025 Fiscalia | {datetime.now().strftime('%d/%m/%Y')}")
