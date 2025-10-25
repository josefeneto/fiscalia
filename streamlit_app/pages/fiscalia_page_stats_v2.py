"""
Fiscalia - Estatísticas e Análises (VERSÃO V5 - CORRIGIDA)
Usa DatabaseManager corretamente (cria BD automaticamente)
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from sqlalchemy import text

# Adicionar src ao path
root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path))

from src.database.db_manager import DatabaseManager
from streamlit_app.components.common import show_header, show_info

# Configuração
st.set_page_config(
    page_title="Estatísticas - Fiscalia",
    page_icon="📈",
    layout="wide"
)

# Header
show_header("Estatísticas e Análises", "Dashboard analítico com insights e visualizações")

# ==================== FUNÇÕES AUXILIARES ====================

@st.cache_resource
def get_db():
    """Retorna instância do DatabaseManager (cria BD automaticamente)"""
    return DatabaseManager()


def load_stats_data(data_inicio: str, data_fim: str) -> pd.DataFrame:
    """Carrega dados para estatísticas com filtro de período"""
    try:
        db = get_db()
        session = db.get_session()
        
        query = text(f"""
        SELECT * FROM docs_para_erp 
        WHERE date(time_stamp) BETWEEN '{data_inicio}' AND '{data_fim}'
        ORDER BY time_stamp DESC
        """)
        
        df = pd.read_sql_query(query, session.bind)
        session.close()
        
        # Converter datas
        date_columns = ['time_stamp', 'data_emissao', 'data_saida_entrada']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")
        return pd.DataFrame()


def format_currency(value) -> str:
    """Formata valor monetário"""
    try:
        if pd.isna(value):
            return "€ 0,00"
        return f"€ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "€ 0,00"


def format_number(value) -> str:
    """Formata número com separadores"""
    try:
        return f"{int(value):,}".replace(",", ".")
    except:
        return "0"


# ==================== FILTRO DE PERÍODO ====================

st.markdown("### 📅 Período de Análise")

col1, col2, col3 = st.columns([1, 1, 2])

hoje = datetime.now()
primeiro_dia_mes = datetime(hoje.year, hoje.month, 1)

with col1:
    data_inicio = st.date_input(
        "Data Início:",
        value=primeiro_dia_mes,
        key="data_inicio_stats"
    )

with col2:
    data_fim = st.date_input(
        "Data Fim:",
        value=hoje,
        key="data_fim_stats"
    )

with col3:
    dias_selecionados = (data_fim - data_inicio).days
    st.info(f"📊 Período selecionado: {dias_selecionados} dias")

st.markdown("---")

# ==================== CARREGAR DADOS ====================

with st.spinner("🔄 Carregando dados..."):
    df = load_stats_data(str(data_inicio), str(data_fim))

if df.empty:
    show_info("Nenhum dado encontrado no período selecionado.", "💡 Ajuste as datas ou use a página **📤 Upload**.")
    st.stop()

# ==================== KPIs PRINCIPAIS ====================

st.markdown("### 📊 Indicadores Principais")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_docs = len(df)
    st.metric("📝 Total Documentos", format_number(total_docs))

with col2:
    total_valor = df['valor_total'].sum() if 'valor_total' in df.columns else 0
    st.metric("💰 Valor Total", format_currency(total_valor))

with col3:
    if 'valor_total' in df.columns and total_docs > 0:
        valor_medio = df['valor_total'].mean()
        st.metric("📊 Valor Médio", format_currency(valor_medio))
    else:
        st.metric("📊 Valor Médio", "€ 0,00")

with col4:
    if 'erp_processado' in df.columns:
        processados = len(df[df['erp_processado'] == 'Yes'])
        percentual = (processados / total_docs * 100) if total_docs > 0 else 0
        st.metric("✅ Processados ERP", f"{processados}", f"{percentual:.1f}%")
    else:
        st.metric("✅ Processados ERP", "0")

with col5:
    if 'uf_emitente' in df.columns:
        ufs = df['uf_emitente'].nunique()
        st.metric("🗺️ Estados", format_number(ufs))
    else:
        st.metric("🗺️ Estados", "0")

st.markdown("---")

# ==================== GRÁFICOS - LINHA 1 ====================

st.markdown("### 📈 Análises Visuais")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🗺️ Documentos por Estado")
    
    if 'uf_emitente' in df.columns:
        df_uf = df['uf_emitente'].value_counts().reset_index()
        df_uf.columns = ['UF', 'Quantidade']
        
        fig_uf = px.bar(
            df_uf.head(10),
            x='UF',
            y='Quantidade',
            title='Top 10 Estados',
            color='Quantidade',
            color_continuous_scale='Blues'
        )
        fig_uf.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_uf, use_container_width=True)
    else:
        st.info("📊 Dados de UF não disponíveis")

with col2:
    st.markdown("#### 💰 Valor Total por Estado")
    
    if 'uf_emitente' in df.columns and 'valor_total' in df.columns:
        df_uf_valor = df.groupby('uf_emitente')['valor_total'].sum().reset_index()
        df_uf_valor.columns = ['UF', 'Valor Total']
        df_uf_valor = df_uf_valor.sort_values('Valor Total', ascending=False)
        
        fig_valor = px.bar(
            df_uf_valor.head(10),
            x='UF',
            y='Valor Total',
            title='Top 10 Estados por Valor',
            color='Valor Total',
            color_continuous_scale='Greens'
        )
        fig_valor.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_valor, use_container_width=True)
    else:
        st.info("📊 Dados de valor não disponíveis")

# ==================== GRÁFICOS - LINHA 2 ====================

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 📅 Evolução no Tempo")
    
    if 'data_emissao' in df.columns:
        df_temp = df.copy()
        # Remover valores nulos e garantir formato datetime
        df_temp = df_temp[df_temp['data_emissao'].notna()].copy()
        
        if len(df_temp) > 0:
            # Criar coluna mês/ano formatada
            df_temp['mes_ano'] = df_temp['data_emissao'].dt.strftime('%Y-%m')
            df_temp_grouped = df_temp.groupby('mes_ano').size().reset_index(name='Quantidade')
            
            # Ordenar por data
            df_temp_grouped = df_temp_grouped.sort_values('mes_ano')
            
            # Converter para formato legível (MMM/AAAA)
            df_temp_grouped['mes_ano_label'] = pd.to_datetime(df_temp_grouped['mes_ano']).dt.strftime('%b/%Y')
            
            fig_tempo = px.line(
                df_temp_grouped,
                x='mes_ano_label',
                y='Quantidade',
                title='Documentos por Mês',
                markers=True
            )
            fig_tempo.update_layout(
                height=400,
                xaxis_title='Mês/Ano',
                yaxis_title='Quantidade'
            )
            fig_tempo.update_xaxes(tickangle=-45)
            st.plotly_chart(fig_tempo, use_container_width=True)
        else:
            st.info("📊 Sem dados com datas válidas")
    else:
        st.info("📊 Dados de data não disponíveis")

with col2:
    st.markdown("#### ⚙️ Status de Processamento ERP")
    
    if 'erp_processado' in df.columns:
        df_erp = df['erp_processado'].value_counts().reset_index()
        df_erp.columns = ['Status', 'Quantidade']
        df_erp['Status'] = df_erp['Status'].map({'Yes': 'Processado', 'No': 'Pendente'})
        
        fig_erp = px.pie(
            df_erp,
            values='Quantidade',
            names='Status',
            title='Status de Processamento',
            color='Status',
            color_discrete_map={'Processado': '#28a745', 'Pendente': '#ffc107'}
        )
        fig_erp.update_layout(height=400)
        st.plotly_chart(fig_erp, use_container_width=True)
    else:
        st.info("📊 Dados de status ERP não disponíveis")

st.markdown("---")

# ==================== TABELAS DE TOP ====================

st.markdown("### 🏆 Rankings (por Valor Total)")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 📤 Top 10 Emitentes")
    
    if 'razao_social_emitente' in df.columns and 'valor_total' in df.columns:
        df_emit = df.groupby('razao_social_emitente').agg({
            'valor_total': 'sum',
            'numero_nf': 'count'
        }).reset_index()
        
        df_emit.columns = ['Emitente', 'Valor Total (€)', 'Qtd Docs']
        df_emit = df_emit.sort_values('Valor Total (€)', ascending=False).head(10)
        
        df_emit['Valor Total'] = df_emit['Valor Total (€)'].apply(format_currency)
        df_emit = df_emit[['Emitente', 'Valor Total', 'Qtd Docs']]
        
        st.dataframe(df_emit, use_container_width=True, hide_index=True, height=400)
    else:
        st.info("📊 Dados de emitentes não disponíveis")

with col2:
    st.markdown("#### 📥 Top 10 Destinatários")
    
    if 'razao_social_destinatario' in df.columns and 'valor_total' in df.columns:
        df_dest = df.groupby('razao_social_destinatario').agg({
            'valor_total': 'sum',
            'numero_nf': 'count'
        }).reset_index()
        
        df_dest.columns = ['Destinatário', 'Valor Total (€)', 'Qtd Docs']
        df_dest = df_dest.sort_values('Valor Total (€)', ascending=False).head(10)
        
        df_dest['Valor Total'] = df_dest['Valor Total (€)'].apply(format_currency)
        df_dest = df_dest[['Destinatário', 'Valor Total', 'Qtd Docs']]
        
        st.dataframe(df_dest, use_container_width=True, hide_index=True, height=400)
    else:
        st.info("📊 Dados de destinatários não disponíveis")

st.markdown("---")

# ==================== ANÁLISE DE VALORES ====================

if 'valor_total' in df.columns:
    st.markdown("### 💰 Análise Financeira")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 📊 Distribuição de Valores")
        
        fig_hist = px.histogram(
            df,
            x='valor_total',
            nbins=30,
            title='Distribuição de Valores'
        )
        fig_hist.update_layout(height=300)
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        st.markdown("#### 📈 Estatísticas")
        
        stats_valores = df['valor_total'].describe()
        
        st.metric("Mínimo", format_currency(stats_valores['min']))
        st.metric("Máximo", format_currency(stats_valores['max']))
        st.metric("Mediana", format_currency(stats_valores['50%']))
        st.metric("Desvio Padrão", format_currency(stats_valores['std']))
    
    with col3:
        st.markdown("#### 🎯 Faixas de Valor")
        
        bins = [0, 1000, 5000, 10000, 50000, float('inf')]
        labels = ['0-1k', '1k-5k', '5k-10k', '10k-50k', '50k+']
        df['faixa_valor'] = pd.cut(df['valor_total'], bins=bins, labels=labels)
        
        df_faixas = df['faixa_valor'].value_counts().reset_index()
        df_faixas.columns = ['Faixa', 'Quantidade']
        
        fig_faixas = px.bar(
            df_faixas,
            x='Faixa',
            y='Quantidade',
            title='Documentos por Faixa'
        )
        fig_faixas.update_layout(height=300)
        st.plotly_chart(fig_faixas, use_container_width=True)

# ==================== SIDEBAR ====================

with st.sidebar:
    st.header("📋 Resumo Estatístico")
    
    st.markdown("**Período Analisado:**")
    st.write(f"📅 {data_inicio.strftime('%d/%m/%Y')} até {data_fim.strftime('%d/%m/%Y')}")
    
    st.markdown("---")
    
    st.markdown("**Documentos:**")
    st.write(f"📝 Total: {format_number(len(df))}")
    
    if 'erp_processado' in df.columns:
        proc = len(df[df['erp_processado'] == 'Yes'])
        pend = len(df[df['erp_processado'] == 'No'])
        st.write(f"✅ Processados: {format_number(proc)}")
        st.write(f"⏳ Pendentes: {format_number(pend)}")
    
    st.markdown("---")
    
    if 'valor_total' in df.columns:
        st.markdown("**Valores:**")
        st.write(f"💰 Total: {format_currency(df['valor_total'].sum())}")
        st.write(f"📊 Médio: {format_currency(df['valor_total'].mean())}")
    
    st.markdown("---")
    
    if st.button("🔄 Atualizar Dados", use_container_width=True):
        st.rerun()

# ==================== FOOTER ====================

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>📅 <em>Selecione o período para análises específicas</em></p>
        <p>🏆 <em>Rankings ordenados por valor total</em></p>
    </div>
    """,
    unsafe_allow_html=True
)
