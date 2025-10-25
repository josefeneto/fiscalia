"""
Fiscalia - Consultas Inteligentes (VERSÃO COMPLETA V4)
SQL Direto + Linguagem Natural com processamento inteligente
Perguntas pré-definidas com seleção de período
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
import sqlite3
import os
from datetime import datetime, timedelta
import re

# Adicionar src ao path
root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path))

from src.database.db_manager import DatabaseManager
from streamlit_app.components.common import show_header, show_success, show_error, show_info

# Configuração
st.set_page_config(
    page_title="Consultas - Fiscalia",
    page_icon="💬",
    layout="wide"
)

# Header
show_header("Consultas Inteligentes", "Análises com SQL direto ou perguntas em linguagem natural")

# ==================== FUNÇÕES AUXILIARES ====================

def get_db_path():
    """Retorna caminho do banco de dados"""
    try:
        from src.utils.config import get_settings
        settings = get_settings()
        if settings and hasattr(settings, 'database_url') and settings.database_url:
            db_path = settings.database_url.replace('sqlite:///', '')
            if os.path.exists(db_path):
                return db_path
    except:
        pass
    
    possible_paths = [
        root_path / 'data' / 'bd_fiscalia.db',
        root_path / 'bd_fiscalia.db',
        Path.cwd() / 'data' / 'bd_fiscalia.db',
    ]
    
    for path in possible_paths:
        if path.exists():
            return str(path)
    
    for root, dirs, files in os.walk(root_path):
        if 'bd_fiscalia.db' in files:
            return os.path.join(root, 'bd_fiscalia.db')
    
    return str(root_path / 'data' / 'bd_fiscalia.db')


def executar_query(query: str) -> pd.DataFrame:
    """Executa query SQL e retorna DataFrame"""
    try:
        db_path = get_db_path()
        if not os.path.exists(db_path):
            st.error("❌ Banco de dados não encontrado")
            return pd.DataFrame()
        
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"❌ Erro ao executar consulta: {e}")
        return pd.DataFrame()


def format_currency(value) -> str:
    """Formata valor monetário"""
    try:
        if pd.isna(value):
            return "€ 0,00"
        return f"€ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "€ 0,00"


def processar_pergunta_natural(pergunta: str, data_inicio: str, data_fim: str) -> tuple:
    """
    Processa pergunta em linguagem natural e retorna (query_sql, resposta_texto)
    """
    pergunta_lower = pergunta.lower()
    
    # Filtro de período
    filtro_periodo = f"data_emissao BETWEEN '{data_inicio}' AND '{data_fim}'"
    
    # PERGUNTA 1: Quantas notas fiscais?
    if any(word in pergunta_lower for word in ['quantas notas', 'quantas nf', 'total de notas', 'número de notas']):
        query = f"""
        SELECT COUNT(*) as total_notas,
               SUM(valor_total) as valor_total
        FROM docs_para_erp
        WHERE {filtro_periodo}
        """
        df = executar_query(query)
        if not df.empty:
            total = int(df['total_notas'].iloc[0])
            valor = format_currency(df['valor_total'].iloc[0])
            resposta = f"📊 **Total de Notas Fiscais no período:** {total:,} notas\n\n💰 **Valor Total:** {valor}".replace(",", ".")
            return query, resposta, df
    
    # PERGUNTA 5: Total do valor bruto
    if any(word in pergunta_lower for word in ['total do valor', 'valor bruto', 'valor total', 'soma dos valores']):
        query = f"""
        SELECT 
            SUM(valor_total) as valor_bruto_total,
            AVG(valor_total) as valor_medio,
            COUNT(*) as quantidade_notas
        FROM docs_para_erp
        WHERE {filtro_periodo}
        """
        df = executar_query(query)
        if not df.empty:
            total = format_currency(df['valor_bruto_total'].iloc[0])
            medio = format_currency(df['valor_medio'].iloc[0])
            qtd = int(df['quantidade_notas'].iloc[0])
            resposta = f"💰 **Valor Bruto Total:** {total}\n\n📊 **Valor Médio por Nota:** {medio}\n\n📝 **Quantidade de Notas:** {qtd:,}".replace(",", ".")
            return query, resposta, df
    
    # PERGUNTA 6: Total de descontos
    if any(word in pergunta_lower for word in ['desconto', 'descontos']):
        query = f"""
        SELECT 
            SUM(valor_desconto) as total_desconto,
            AVG(valor_desconto) as media_desconto,
            COUNT(*) as notas_com_desconto
        FROM docs_para_erp
        WHERE {filtro_periodo} AND valor_desconto > 0
        """
        df = executar_query(query)
        if not df.empty:
            total = format_currency(df['total_desconto'].iloc[0])
            media = format_currency(df['media_desconto'].iloc[0])
            qtd = int(df['notas_com_desconto'].iloc[0])
            resposta = f"💸 **Total de Descontos:** {total}\n\n📊 **Média de Desconto:** {media}\n\n📝 **Notas com Desconto:** {qtd:,}".replace(",", ".")
            return query, resposta, df
    
    # PERGUNTA 7: Total de impostos
    if any(word in pergunta_lower for word in ['imposto', 'impostos', 'icms', 'ipi', 'pis', 'cofins']):
        query = f"""
        SELECT 
            SUM(valor_icms) as total_icms,
            SUM(valor_ipi) as total_ipi,
            SUM(valor_pis) as total_pis,
            SUM(valor_cofins) as total_cofins,
            SUM(valor_icms + valor_ipi + valor_pis + valor_cofins) as total_impostos
        FROM docs_para_erp
        WHERE {filtro_periodo}
        """
        df = executar_query(query)
        if not df.empty:
            icms = format_currency(df['total_icms'].iloc[0])
            ipi = format_currency(df['total_ipi'].iloc[0])
            pis = format_currency(df['total_pis'].iloc[0])
            cofins = format_currency(df['total_cofins'].iloc[0])
            total = format_currency(df['total_impostos'].iloc[0])
            resposta = f"💰 **Total de Impostos:** {total}\n\n📊 **Detalhamento:**\n- ICMS: {icms}\n- IPI: {ipi}\n- PIS: {pis}\n- COFINS: {cofins}"
            return query, resposta, df
    
    # PERGUNTA 8: Estatísticas de valores
    if any(word in pergunta_lower for word in ['média', 'mediana', 'máximo', 'mínimo', 'estatísticas']):
        query = f"""
        SELECT 
            AVG(valor_total) as media,
            MIN(valor_total) as minimo,
            MAX(valor_total) as maximo,
            COUNT(*) as total
        FROM docs_para_erp
        WHERE {filtro_periodo}
        """
        df = executar_query(query)
        if not df.empty:
            media = format_currency(df['media'].iloc[0])
            minimo = format_currency(df['minimo'].iloc[0])
            maximo = format_currency(df['maximo'].iloc[0])
            total = int(df['total'].iloc[0])
            resposta = f"📊 **Estatísticas de Valores:**\n\n- Média: {media}\n- Mínimo: {minimo}\n- Máximo: {maximo}\n- Total de Notas: {total:,}".replace(",", ".")
            return query, resposta, df
    
    # PERGUNTA 9-10: Por destinatário
    if any(word in pergunta_lower for word in ['destinatário', 'destinatarios', 'cliente', 'clientes', 'top destina']):
        query = f"""
        SELECT 
            razao_social_destinatario as 'Destinatário',
            COUNT(*) as 'Quantidade',
            SUM(valor_total) as valor_total,
            AVG(valor_total) as valor_medio
        FROM docs_para_erp
        WHERE {filtro_periodo}
        GROUP BY razao_social_destinatario
        ORDER BY valor_total DESC
        LIMIT 10
        """
        df = executar_query(query)
        if not df.empty:
            df['Valor Total'] = df['valor_total'].apply(format_currency)
            df['Valor Médio'] = df['valor_medio'].apply(format_currency)
            resposta = "📥 **Top 10 Destinatários por Valor Total:**"
            return query, resposta, df[['Destinatário', 'Quantidade', 'Valor Total', 'Valor Médio']]
    
    # PERGUNTA 11: Por UF
    if any(word in pergunta_lower for word in ['estado', 'uf', 'geografia', 'região']):
        query = f"""
        SELECT 
            uf_emitente as 'UF',
            COUNT(*) as 'Quantidade',
            SUM(valor_total) as valor_total
        FROM docs_para_erp
        WHERE {filtro_periodo}
        GROUP BY uf_emitente
        ORDER BY valor_total DESC
        """
        df = executar_query(query)
        if not df.empty:
            df['Valor Total'] = df['valor_total'].apply(format_currency)
            resposta = "🗺️ **Distribuição por Estado (UF):**"
            return query, resposta, df[['UF', 'Quantidade', 'Valor Total']]
    
    # PERGUNTA 12: Por município
    if any(word in pergunta_lower for word in ['município', 'municipio', 'cidade', 'cidades']):
        query = f"""
        SELECT 
            municipio_destinatario as 'Município',
            uf_destinatario as 'UF',
            COUNT(*) as 'Quantidade',
            SUM(valor_total) as valor_total
        FROM docs_para_erp
        WHERE {filtro_periodo}
        GROUP BY municipio_destinatario, uf_destinatario
        ORDER BY valor_total DESC
        LIMIT 20
        """
        df = executar_query(query)
        if not df.empty:
            df['Valor Total'] = df['valor_total'].apply(format_currency)
            resposta = "🏙️ **Top 20 Municípios por Valor Total:**"
            return query, resposta, df[['Município', 'UF', 'Quantidade', 'Valor Total']]
    
    # PERGUNTA 24: Distribuição temporal
    if any(word in pergunta_lower for word in ['tempo', 'temporal', 'mensal', 'diária', 'evolução', 'tendência']):
        query = f"""
        SELECT 
            strftime('%Y-%m-%d', data_emissao) as 'Data',
            COUNT(*) as 'Quantidade',
            SUM(valor_total) as valor_total
        FROM docs_para_erp
        WHERE {filtro_periodo}
        GROUP BY strftime('%Y-%m-%d', data_emissao)
        ORDER BY data_emissao
        """
        df = executar_query(query)
        if not df.empty:
            df['Valor Total'] = df['valor_total'].apply(format_currency)
            resposta = "📅 **Distribuição Temporal (por dia):**"
            return query, resposta, df[['Data', 'Quantidade', 'Valor Total']]
    
    # PERGUNTA 20: Duplicados
    if any(word in pergunta_lower for word in ['duplicado', 'duplicados', 'repetido', 'repetidos']):
        query = f"""
        SELECT 
            numero_nf as 'Número NF',
            serie as 'Série',
            COUNT(*) as 'Ocorrências'
        FROM docs_para_erp
        WHERE {filtro_periodo}
        GROUP BY numero_nf, serie
        HAVING COUNT(*) > 1
        """
        df = executar_query(query)
        if not df.empty:
            resposta = f"⚠️ **Notas Duplicadas Encontradas:** {len(df)} casos"
            return query, resposta, df
        else:
            resposta = "✅ **Nenhuma nota duplicada encontrada no período!**"
            return query, resposta, pd.DataFrame()
    
    # Fallback: Não reconheceu a pergunta
    return None, "❓ **Pergunta não reconhecida.** Por favor, reformule ou escolha uma das sugestões abaixo.", pd.DataFrame()


# ==================== TABS PRINCIPAIS ====================

tab1, tab2 = st.tabs(["🎯 Perguntas em Linguagem Natural", "💻 Consultas SQL Diretas"])

# ==================== TAB 1: LINGUAGEM NATURAL ====================

with tab1:
    st.markdown("### 🗣️ Faça Perguntas em Linguagem Natural")
    
    # Seleção de Período
    st.markdown("#### 📅 Período de Análise")
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        # Default: mês corrente
        hoje = datetime.now()
        primeiro_dia_mes = datetime(hoje.year, hoje.month, 1)
        data_inicio = st.date_input(
            "Data Início:",
            value=primeiro_dia_mes,
            key="data_inicio_ln"
        )
    
    with col2:
        data_fim = st.date_input(
            "Data Fim:",
            value=hoje,
            key="data_fim_ln"
        )
    
    with col3:
        st.info(f"📊 Período selecionado: {(data_fim - data_inicio).days} dias")
    
    st.markdown("---")
    
    # Perguntas Sugeridas
    with st.expander("💡 Perguntas Sugeridas (clique para usar)", expanded=True):
        st.markdown("""
        **Contagem / Dimensão:**
        - Quantas notas fiscais há no período?
        - Qual o total de registos?
        
        **Valores e Totais:**
        - Qual o total do valor bruto de todas as notas?
        - Qual o total de descontos?
        - Qual o total de impostos (ICMS, IPI, PIS, COFINS)?
        - Qual a média, mínimo e máximo dos valores?
        
        **Por Destinatário:**
        - Quais os top 10 destinatários por valor?
        - Quais os clientes com mais notas?
        
        **Geografia:**
        - Qual a distribuição por estado (UF)?
        - Quais os top 20 municípios por valor?
        
        **Tempo:**
        - Qual a evolução temporal das notas?
        - Qual a distribuição diária/mensal?
        
        **Integridade:**
        - Há notas duplicadas?
        - Há inconsistências nos dados?
        """)
        
        # Botões de exemplo
        st.markdown("**Clique para usar:**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Quantas notas?", key="ex1"):
                st.session_state.pergunta_ln = "Quantas notas fiscais há no período?"
            if st.button("💰 Valor total?", key="ex2"):
                st.session_state.pergunta_ln = "Qual o total do valor bruto?"
            if st.button("📥 Top destinatários?", key="ex3"):
                st.session_state.pergunta_ln = "Quais os top 10 destinatários?"
        
        with col2:
            if st.button("🗺️ Por estado?", key="ex4"):
                st.session_state.pergunta_ln = "Qual a distribuição por estado?"
            if st.button("💸 Descontos?", key="ex5"):
                st.session_state.pergunta_ln = "Qual o total de descontos?"
            if st.button("📈 Estatísticas?", key="ex6"):
                st.session_state.pergunta_ln = "Qual a média, mínimo e máximo?"
        
        with col3:
            if st.button("📅 Evolução temporal?", key="ex7"):
                st.session_state.pergunta_ln = "Qual a evolução temporal?"
            if st.button("🏙️ Por município?", key="ex8"):
                st.session_state.pergunta_ln = "Quais os top 20 municípios?"
            if st.button("⚠️ Duplicados?", key="ex9"):
                st.session_state.pergunta_ln = "Há notas duplicadas?"
    
    st.markdown("---")
    
    # Input da pergunta
    pergunta_natural = st.text_area(
        "✍️ Digite sua pergunta:",
        value=st.session_state.get('pergunta_ln', ''),
        placeholder="Ex: Quantas notas fiscais há no período? Qual o total de impostos?",
        height=100,
        key="pergunta_area"
    )
    
    if st.button("🚀 Processar Pergunta", type="primary", use_container_width=True, key="btn_ln"):
        if pergunta_natural:
            with st.spinner("🤔 Processando sua pergunta..."):
                query, resposta, df_resultado = processar_pergunta_natural(
                    pergunta_natural,
                    str(data_inicio),
                    str(data_fim)
                )
                
                if query:
                    st.markdown("---")
                    st.markdown("### 💬 Resposta")
                    st.markdown(resposta)
                    
                    # Mostrar DataFrame se houver
                    if not df_resultado.empty:
                        st.markdown("#### 📊 Dados Detalhados")
                        st.dataframe(df_resultado, use_container_width=True, hide_index=True, height=400)
                        
                        # Gráfico se for numérico
                        if len(df_resultado) > 1 and 'valor_total' in df_resultado.columns:
                            st.markdown("#### 📈 Visualização")
                            fig = px.bar(
                                df_resultado.head(15),
                                x=df_resultado.columns[0],
                                y='valor_total',
                                title='Distribuição de Valores'
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # Botão de exportação
                        csv = df_resultado.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Baixar Resultados (CSV)",
                            data=csv,
                            file_name=f"consulta_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                    
                    # Mostrar SQL usado (opcional)
                    with st.expander("🔍 Ver SQL Gerado"):
                        st.code(query, language="sql")
                else:
                    st.warning(resposta)
        else:
            st.warning("⚠️ Digite uma pergunta primeiro ou clique em uma sugestão")

# ==================== TAB 2: SQL DIRETO ====================

with tab2:
    st.markdown("### 💻 Execute Consultas SQL Diretas")
    
    st.info("💡 **Para usuários avançados:** Execute queries SQL customizadas diretamente no banco de dados.")
    
    # Exemplos SQL
    with st.expander("📚 Exemplos de SQL", expanded=False):
        st.markdown("""
        **Tabela Principal:** `docs_para_erp`
        
        **Colunas Disponíveis:**
        - `numero_nf`, `chave_acesso`, `serie`, `modelo`
        - `razao_social_emitente`, `cnpj_emitente`, `uf_emitente`, `municipio_emitente`
        - `razao_social_destinatario`, `cnpj_destinatario`, `uf_destinatario`, `municipio_destinatario`
        - `valor_total`, `valor_produtos`, `valor_frete`, `valor_desconto`
        - `valor_icms`, `valor_ipi`, `valor_pis`, `valor_cofins`
        - `data_emissao`, `data_saida_entrada`, `erp_processado`
        
        **Exemplos:**
        
        ```sql
        -- Documentos de São Paulo
        SELECT * FROM docs_para_erp 
        WHERE uf_emitente = 'SP' 
        LIMIT 50;
        
        -- Valores acima de 10.000
        SELECT numero_nf, razao_social_emitente, valor_total 
        FROM docs_para_erp 
        WHERE valor_total > 10000 
        ORDER BY valor_total DESC;
        
        -- Por período
        SELECT * FROM docs_para_erp 
        WHERE data_emissao BETWEEN '2024-01-01' AND '2024-12-31'
        ORDER BY data_emissao DESC;
        
        -- Agregação por UF
        SELECT uf_emitente, COUNT(*) as qtd, SUM(valor_total) as total
        FROM docs_para_erp 
        GROUP BY uf_emitente 
        ORDER BY total DESC;
        ```
        """)
    
    st.markdown("---")
    
    # Input SQL
    col1, col2 = st.columns([3, 1])
    
    with col1:
        consulta_sql = st.text_area(
            "Digite sua consulta SQL:",
            placeholder="SELECT * FROM docs_para_erp WHERE uf_emitente = 'SP' LIMIT 50",
            height=150,
            key="consulta_sql"
        )
    
    with col2:
        st.markdown("#### ⚙️ Opções")
        limite = st.number_input("Limite máximo:", min_value=10, max_value=1000, value=100, step=10)
        
        validar_sql = st.checkbox("Validar SQL", value=True, help="Verifica se é apenas SELECT")
    
    if st.button("🚀 Executar SQL", type="primary", use_container_width=True, key="btn_sql"):
        if consulta_sql:
            # Validação básica
            if validar_sql:
                if not consulta_sql.strip().upper().startswith('SELECT'):
                    st.error("❌ Apenas consultas SELECT são permitidas por segurança!")
                    st.stop()
            
            # Adicionar LIMIT se não tiver
            if 'LIMIT' not in consulta_sql.upper():
                consulta_sql += f" LIMIT {limite}"
            
            with st.spinner("⚙️ Executando SQL..."):
                df_result = executar_query(consulta_sql)
                
                if not df_result.empty:
                    st.success(f"✅ Consulta executada! {len(df_result)} registro(s) encontrado(s)")
                    
                    # Formatar colunas de valor
                    valor_cols = [col for col in df_result.columns if 'valor' in col.lower()]
                    for col in valor_cols:
                        if df_result[col].dtype in ['float64', 'int64']:
                            df_result[f'{col}_fmt'] = df_result[col].apply(format_currency)
                    
                    st.dataframe(df_result, use_container_width=True, hide_index=True, height=500)
                    
                    # Exportação
                    csv = df_result.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Baixar CSV",
                        data=csv,
                        file_name=f"sql_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("⚠️ Nenhum resultado encontrado")
        else:
            st.warning("⚠️ Digite uma consulta SQL primeiro")

# ==================== SIDEBAR ====================

with st.sidebar:
    st.header("💡 Guia de Uso")
    
    st.markdown("""
    **Linguagem Natural:**
    - ✅ Faça perguntas em português
    - ✅ Defina o período de análise
    - ✅ Use as sugestões fornecidas
    - ✅ Receba respostas contextualizadas
    
    **SQL Direto:**
    - ✅ Para usuários avançados
    - ✅ Controle total sobre queries
    - ✅ Apenas SELECT permitido
    - ✅ Exportação de resultados
    
    ---
    
    **Dicas:**
    - 📅 Sempre defina o período
    - 💡 Use perguntas claras
    - 📊 Exporte para análise externa
    - 🔍 Combine múltiplas consultas
    """)
    
    st.markdown("---")
    
    # Estatísticas rápidas
    st.markdown("**📊 Dados Disponíveis:**")
    query_stats = "SELECT COUNT(*) as total FROM docs_para_erp"
    df_stats = executar_query(query_stats)
    if not df_stats.empty:
        st.write(f"📝 {int(df_stats['total'].iloc[0]):,} documentos".replace(",", "."))

# ==================== FOOTER ====================

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>🗣️ <em>Perguntas em linguagem natural com processamento inteligente</em></p>
        <p>💻 <em>SQL direto para controle total das consultas</em></p>
        <p>📊 <em>Sempre defina o período de análise para resultados precisos</em></p>
    </div>
    """,
    unsafe_allow_html=True
)
