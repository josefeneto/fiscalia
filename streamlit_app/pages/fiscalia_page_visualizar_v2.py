"""
Fiscalia - Visualizar Banco de Dados (VERSÃO V9 - COM FILTRO DE PERÍODO)
Visualização das 2 tabelas: docs_para_erp e registo_resultados
Exportação CSV e XLSX
Filtros avançados + Filtro de Período
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO
import sqlite3
import os

# Adicionar src ao path
root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path))

from src.database.db_manager import DatabaseManager
from streamlit_app.components.common import show_header, show_success, show_error, show_info

# Configuração
st.set_page_config(
    page_title="Visualizar BD - Fiscalia",
    page_icon="📊",
    layout="wide"
)

# Header
show_header("Visualizar Banco de Dados", "Consulte, filtre e exporte os dados processados")

# ==================== FUNÇÕES AUXILIARES ====================

@st.cache_resource
def get_db():
    """Retorna instância do DatabaseManager (cached)"""
    return DatabaseManager()


def get_db_path():
    """
    Retorna caminho do banco de dados com múltiplas estratégias de busca
    """
    # Estratégia 1: Tentar via get_settings
    try:
        from src.utils.config import get_settings
        settings = get_settings()
        if settings and hasattr(settings, 'database_url') and settings.database_url:
            db_path = settings.database_url.replace('sqlite:///', '')
            if os.path.exists(db_path):
                return db_path
    except:
        pass
    
    # Estratégia 2: Procurar em locais comuns
    possible_paths = [
        root_path / 'data' / 'bd_fiscalia.db',
        root_path / 'bd_fiscalia.db',
        Path.cwd() / 'data' / 'bd_fiscalia.db',
        Path.cwd() / 'bd_fiscalia.db',
    ]
    
    for path in possible_paths:
        if path.exists():
            return str(path)
    
    # Estratégia 3: Procurar recursivamente
    for root, dirs, files in os.walk(root_path):
        if 'bd_fiscalia.db' in files:
            return os.path.join(root, 'bd_fiscalia.db')
    
    # Se não encontrar, retornar caminho padrão
    return str(root_path / 'data' / 'bd_fiscalia.db')


def load_docs_para_erp(data_inicio: str, data_fim: str) -> pd.DataFrame:
    """Carrega dados da tabela docs_para_erp com filtro de período"""
    try:
        db_path = get_db_path()
        
        if not os.path.exists(db_path):
            st.warning(f"⚠️ Banco de dados não encontrado em: {db_path}")
            return pd.DataFrame()
        
        conn = sqlite3.connect(db_path)
        
        # Query com filtro de período
        query = f"""
        SELECT * FROM docs_para_erp 
        WHERE date(time_stamp) BETWEEN '{data_inicio}' AND '{data_fim}'
        ORDER BY time_stamp DESC
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Converter colunas de data
        date_columns = ['time_stamp', 'data_emissao', 'data_saida_entrada']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        return df
            
    except Exception as e:
        st.error(f"❌ Erro ao carregar docs_para_erp: {e}")
        return pd.DataFrame()


def load_registo_resultados(data_inicio: str, data_fim: str) -> pd.DataFrame:
    """Carrega dados da tabela registo_resultados com filtro de período"""
    try:
        db_path = get_db_path()
        
        if not os.path.exists(db_path):
            st.warning(f"⚠️ Banco de dados não encontrado em: {db_path}")
            return pd.DataFrame()
        
        conn = sqlite3.connect(db_path)
        
        # Query com filtro de período
        query = f"""
        SELECT * FROM registo_resultados 
        WHERE date(time_stamp) BETWEEN '{data_inicio}' AND '{data_fim}'
        ORDER BY time_stamp DESC
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Converter coluna de data
        if 'time_stamp' in df.columns:
            df['time_stamp'] = pd.to_datetime(df['time_stamp'], errors='coerce')
        
        return df
            
    except Exception as e:
        st.error(f"❌ Erro ao carregar registo_resultados: {e}")
        return pd.DataFrame()


def to_excel(df: pd.DataFrame) -> bytes:
    """Converte DataFrame para Excel (bytes)"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Dados')
    return output.getvalue()


def format_currency(value) -> str:
    """Formata valor monetário"""
    try:
        if pd.isna(value):
            return "€ 0,00"
        return f"€ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "€ 0,00"


# ==================== FILTRO DE PERÍODO GLOBAL ====================

st.markdown("### 📅 Período de Análise")

col1, col2, col3 = st.columns([1, 1, 2])

# Default: mês corrente
hoje = datetime.now()
primeiro_dia_mes = datetime(hoje.year, hoje.month, 1)

with col1:
    data_inicio_global = st.date_input(
        "Data Início:",
        value=primeiro_dia_mes,
        key="data_inicio_visualizar"
    )

with col2:
    data_fim_global = st.date_input(
        "Data Fim:",
        value=hoje,
        key="data_fim_visualizar"
    )

with col3:
    dias_selecionados = (data_fim_global - data_inicio_global).days
    st.info(f"📊 Período selecionado: {dias_selecionados} dias")

st.markdown("---")

# ==================== SELEÇÃO DE TABELA ====================

st.markdown("### 🗂️ Selecione a Tabela")

tab_opcoes = ["📄 Documentos para ERP", "📋 Registo de Resultados"]
selected_tab = st.radio(
    "Escolha qual tabela visualizar:",
    tab_opcoes,
    horizontal=True,
    label_visibility="collapsed"
)

st.markdown("---")

# ==================== TABELA: DOCS_PARA_ERP ====================

if selected_tab == "📄 Documentos para ERP":
    st.subheader("📄 Documentos para ERP")
    
    with st.spinner("🔄 Carregando dados..."):
        df = load_docs_para_erp(str(data_inicio_global), str(data_fim_global))
    
    if df.empty:
        show_info("Nenhum documento encontrado no período selecionado.", "💡 Ajuste as datas ou use a página **📤 Upload** para processar ficheiros.")
    else:
        # ==================== ESTATÍSTICAS ====================
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📝 Total Documentos", f"{len(df):,}")
        
        with col2:
            total_valor = df['valor_total'].sum() if 'valor_total' in df.columns else 0
            st.metric("💰 Valor Total", format_currency(total_valor))
        
        with col3:
            processados = len(df[df['erp_processado'] == 'Yes']) if 'erp_processado' in df.columns else 0
            st.metric("✅ Processados ERP", f"{processados:,}")
        
        with col4:
            pendentes = len(df[df['erp_processado'] != 'Yes']) if 'erp_processado' in df.columns else 0
            st.metric("⏳ Pendentes ERP", f"{pendentes:,}")
        
        st.markdown("---")
        
        # ==================== FILTROS ADICIONAIS ====================
        with st.expander("🔍 Filtros Adicionais", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            df_filtered = df.copy()
            
            # Filtro: Emitente
            with col1:
                if 'razao_social_emitente' in df.columns:
                    emitentes = ['Todos'] + sorted(df['razao_social_emitente'].dropna().unique().tolist())
                    emitente_filtro = st.selectbox("Emitente", emitentes)
                    if emitente_filtro != 'Todos':
                        df_filtered = df_filtered[df_filtered['razao_social_emitente'] == emitente_filtro]
            
            # Filtro: Destinatário
            with col2:
                if 'razao_social_destinatario' in df.columns:
                    destinatarios = ['Todos'] + sorted(df['razao_social_destinatario'].dropna().unique().tolist())
                    dest_filtro = st.selectbox("Destinatário", destinatarios)
                    if dest_filtro != 'Todos':
                        df_filtered = df_filtered[df_filtered['razao_social_destinatario'] == dest_filtro]
            
            # Filtro: Status ERP
            with col3:
                if 'erp_processado' in df.columns:
                    status_erp = st.selectbox("Status ERP", ['Todos', 'Yes', 'No'])
                    if status_erp != 'Todos':
                        df_filtered = df_filtered[df_filtered['erp_processado'] == status_erp]
            
            if len(df_filtered) != len(df):
                st.info(f"🔍 Filtros aplicados: {len(df_filtered)} de {len(df)} registos")
            
            df = df_filtered
        
        # ==================== TABELA ====================
        st.markdown("### 📊 Dados")
        
        # Selecionar colunas principais para exibição
        display_cols = [
            'numero_nf', 'chave_acesso', 'razao_social_emitente', 
            'razao_social_destinatario', 'valor_total', 'data_emissao',
            'uf_emitente', 'erp_processado', 'time_stamp'
        ]
        
        # Filtrar apenas colunas que existem
        display_cols = [col for col in display_cols if col in df.columns]
        
        df_display = df[display_cols].copy() if display_cols else df.copy()
        
        # Formatar datas
        for col in ['time_stamp', 'data_emissao', 'data_saida_entrada']:
            if col in df_display.columns and pd.api.types.is_datetime64_any_dtype(df_display[col]):
                df_display[col] = df_display[col].dt.strftime('%d/%m/%Y %H:%M')
        
        # Formatar valores monetários
        if 'valor_total' in df_display.columns:
            df_display['valor_total'] = df_display['valor_total'].apply(format_currency)
        
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        # ==================== EXPORTAÇÃO ====================
        st.markdown("---")
        st.markdown("### 📥 Exportar Dados")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        with col1:
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📄 Baixar CSV",
                data=csv_data,
                file_name=f"docs_erp_{timestamp}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            excel_data = to_excel(df)
            st.download_button(
                label="📊 Baixar XLSX",
                data=excel_data,
                file_name=f"docs_erp_{timestamp}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col3:
            st.info(f"✅ {len(df):,} registos prontos para exportação")

# ==================== TABELA: REGISTO_RESULTADOS ====================

else:  # "📋 Registo de Resultados"
    st.subheader("📋 Registo de Resultados")
    
    with st.spinner("🔄 Carregando dados..."):
        df = load_registo_resultados(str(data_inicio_global), str(data_fim_global))
    
    if df.empty:
        show_info("Nenhum registo encontrado no período selecionado.", "💡 Ajuste as datas ou verifique se há processamentos neste período.")
    else:
        # ==================== ESTATÍSTICAS ====================
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📝 Total Registos", f"{len(df):,}")
        
        with col2:
            # A coluna é "resultado", não "status"
            if 'resultado' in df.columns:
                sucessos = len(df[df['resultado'] == 'SUCESSO'])
                st.metric("✅ Sucessos", f"{sucessos:,}")
            else:
                st.metric("✅ Sucessos", "N/A")
        
        with col3:
            if 'resultado' in df.columns:
                erros = len(df[df['resultado'] == 'ERRO'])
                st.metric("❌ Erros", f"{erros:,}")
            else:
                st.metric("❌ Erros", "N/A")
        
        with col4:
            # Contar arquivos únicos
            if 'path_nome_arquivo' in df.columns:
                arquivos = df['path_nome_arquivo'].nunique()
                st.metric("📁 Arquivos", f"{arquivos:,}")
            else:
                st.metric("📁 Arquivos", "N/A")
        
        st.markdown("---")
        
        # ==================== FILTROS ADICIONAIS ====================
        with st.expander("🔍 Filtros Adicionais", expanded=False):
            col1, col2 = st.columns(2)
            
            df_filtered = df.copy()
            
            # Filtro: Resultado
            with col1:
                if 'resultado' in df.columns:
                    resultados = ['Todos'] + sorted(df['resultado'].dropna().unique().tolist())
                    resultado_filtro = st.selectbox("Resultado", resultados)
                    if resultado_filtro != 'Todos':
                        df_filtered = df_filtered[df_filtered['resultado'] == resultado_filtro]
            
            # Filtro: Causa (para erros)
            with col2:
                if 'causa' in df.columns:
                    causas = ['Todos'] + sorted(df['causa'].dropna().unique().tolist())
                    causa_filtro = st.selectbox("Causa", causas)
                    if causa_filtro != 'Todos':
                        df_filtered = df_filtered[df_filtered['causa'] == causa_filtro]
            
            if len(df_filtered) != len(df):
                st.info(f"🔍 Filtros aplicados: {len(df_filtered)} de {len(df)} registos")
            
            df = df_filtered
        
        # ==================== TABELA ====================
        st.markdown("### 📊 Dados")
        
        # Preparar DataFrame para exibição
        df_display = df.copy()
        
        # Formatar datas
        if 'time_stamp' in df_display.columns and pd.api.types.is_datetime64_any_dtype(df_display['time_stamp']):
            df_display['time_stamp'] = df_display['time_stamp'].dt.strftime('%d/%m/%Y %H:%M')
        
        # Simplificar path para mostrar só o nome do arquivo
        if 'path_nome_arquivo' in df_display.columns:
            df_display['arquivo'] = df_display['path_nome_arquivo'].apply(lambda x: Path(x).name if x else '')
            # Reorganizar colunas
            cols = ['time_stamp', 'arquivo', 'resultado', 'causa']
            cols = [c for c in cols if c in df_display.columns]
            df_display = df_display[cols]
        
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        # ==================== EXPORTAÇÃO ====================
        st.markdown("---")
        st.markdown("### 📥 Exportar Dados")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        with col1:
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📄 Baixar CSV",
                data=csv_data,
                file_name=f"registo_resultados_{timestamp}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            excel_data = to_excel(df)
            st.download_button(
                label="📊 Baixar XLSX",
                data=excel_data,
                file_name=f"registo_resultados_{timestamp}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col3:
            st.info(f"✅ {len(df):,} registos prontos para exportação")

# ==================== SIDEBAR ====================

with st.sidebar:
    st.header("ℹ️ Informação")
    st.markdown("""
    **Filtro de Período:**
    - 📅 Filtra por data de upload (time_stamp)
    - 🔄 Default: mês corrente
    - ⚡ Aplicado automaticamente
    
    ---
    
    **Tabelas Disponíveis:**
    - 📄 **Documentos para ERP**: Dados extraídos das NFe
    - 📋 **Registo de Resultados**: Histórico de processamentos
    
    ---
    
    **Exportação:**
    - 📄 CSV: Formato universal (texto)
    - 📊 XLSX: Excel com formatação
    
    ---
    
    **Filtros Adicionais:**
    - Use o expander "🔍 Filtros Adicionais"
    - Combine com o filtro de período
    - Refine sua visualização
    """)
    
    # Botão para limpar cache
    if st.button("🔄 Atualizar Dados", use_container_width=True):
        st.rerun()

# ==================== FOOTER ====================

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>📅 <em>Use o filtro de período para visualizar dados específicos</em></p>
        <p>📊 Filtros adicionais disponíveis para refinar a visualização</p>
        <p>📥 Exporte para CSV ou XLSX para análise externa</p>
    </div>
    """,
    unsafe_allow_html=True
)
