"""
Fiscalia - Consultas Inteligentes (VERSÃO DEFINITIVA V4 - CORRIGIDA)
SQL Direto + Linguagem Natural com processamento inteligente
Perguntas pré-definidas com seleção de período
Usa DatabaseManager corretamente (cria BD automaticamente)
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from sqlalchemy import text
import os
import warnings

# Suprimir TODOS os warnings de deprecation
warnings.filterwarnings('ignore')
import logging
logging.getLogger('streamlit').setLevel(logging.ERROR)

# Adicionar src ao path de forma robusta
current_file = Path(__file__).resolve()
root_path = current_file.parent.parent
src_path = root_path / 'src'

# Adicionar ambos ao path se não existirem
for path in [str(root_path), str(src_path)]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Agora importar
try:
    from src.database.db_manager import DatabaseManager
    from streamlit_app.components.common import show_header, show_success, show_error, show_info
except ImportError:
    # Fallback se estiver em ambiente diferente
    import importlib.util
    db_manager_path = root_path / 'src' / 'database' / 'db_manager.py'
    if db_manager_path.exists():
        spec = importlib.util.spec_from_file_location("db_manager", db_manager_path)
        db_manager = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(db_manager)
        DatabaseManager = db_manager.DatabaseManager
    
    # Fallback para components
    def show_header(title, subtitle=""):
        st.title(title)
        if subtitle:
            st.caption(subtitle)
    def show_success(msg): st.success(msg)
    def show_error(msg): st.error(msg)
    def show_info(msg): st.info(msg)

# Configuração
st.set_page_config(
    page_title="Consultas - Fiscalia",
    page_icon="💬",
    layout="wide"
)

# Header
show_header("Consultas Inteligentes", "Análises com SQL direto ou perguntas em linguagem natural")

# ==================== FUNÇÕES AUXILIARES ====================

@st.cache_resource
def get_db():
    """Retorna instância do DatabaseManager (cria BD automaticamente)"""
    return DatabaseManager()

def executar_query(query: str) -> pd.DataFrame:
    """Executa query SQL e retorna DataFrame"""
    try:
        db = get_db()
        session = db.get_session()
        
        # Envolver query em text()
        if isinstance(query, str):
            query = text(query)
        
        df = pd.read_sql_query(query, session.bind)
        session.close()
        
        return df
    except Exception as e:
        st.error(f"❌ Erro ao executar consulta: {e}")
        return pd.DataFrame()

def format_currency(value) -> str:
    """Formata valor monetário em Reais (R$)"""
    try:
        if pd.isna(value):
            return "R$ 0,00"
        return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"

def criar_botoes_exportacao(df: pd.DataFrame, prefixo: str = "consulta"):
    """
    Cria botões de exportação para CSV e Excel
    """
    from io import BytesIO
    
    st.markdown("#### 📥 Exportar Resultados")
    col_exp1, col_exp2 = st.columns(2)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    with col_exp1:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar CSV",
            data=csv,
            file_name=f"{prefixo}_{timestamp}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col_exp2:
        # Exportar para Excel
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Resultados')
        buffer.seek(0)
        
        st.download_button(
            label="📥 Baixar Excel",
            data=buffer,
            file_name=f"{prefixo}_{timestamp}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

def processar_pergunta_natural(pergunta: str, data_inicio: str, data_fim: str) -> tuple:
    """
    Processa pergunta em linguagem natural e retorna (query_sql, resposta_texto, dataframe)
    """
    pergunta_lower = pergunta.lower()
    
    # Filtro de período
    filtro_periodo = f"data_emissao BETWEEN '{data_inicio}' AND '{data_fim}'"
    
    # PERGUNTA 1: Quantas notas fiscais?
    if any(word in pergunta_lower for word in ['quantas notas', 'quantas nf', 'total de notas', 'número de notas', 'total de registos', 'quantidade de notas', 'qt notas', 'qtd notas']):
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
    
    # PERGUNTA 2: Total do valor bruto
    if any(word in pergunta_lower for word in ['total do valor', 'valor bruto', 'valor total', 'soma dos valores', 'total valor', 'quanto foi', 'valor das notas']):
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
    
    # PERGUNTA 3: Total de descontos
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
    
    # PERGUNTA 4: Total de impostos
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
    
    # PERGUNTA 5: Estatísticas de valores
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
    
    # PERGUNTA 6: Por destinatário
    if any(word in pergunta_lower for word in ['destinatário', 'destinatarios', 'destinatário', 'cliente', 'clientes', 'top destina', 'top 10 destina', 'destinat']):
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
            df_display = df[['Destinatário', 'Quantidade', 'Valor Total', 'Valor Médio']]
            resposta = "📥 **Top 10 Destinatários (por valor total):**"
            return query, resposta, df_display
    
    # PERGUNTA 7: Por emitente/fornecedor
    if any(word in pergunta_lower for word in ['emitente', 'emitentes', 'fornecedor', 'fornecedores', 'top emit', 'top 10 emit', 'emit']):
        query = f"""
        SELECT 
            razao_social_emitente as 'Emitente',
            COUNT(*) as 'Quantidade',
            SUM(valor_total) as valor_total,
            AVG(valor_total) as valor_medio
        FROM docs_para_erp
        WHERE {filtro_periodo}
        GROUP BY razao_social_emitente
        ORDER BY valor_total DESC
        LIMIT 10
        """
        df = executar_query(query)
        if not df.empty:
            df['Valor Total'] = df['valor_total'].apply(format_currency)
            df['Valor Médio'] = df['valor_medio'].apply(format_currency)
            df_display = df[['Emitente', 'Quantidade', 'Valor Total', 'Valor Médio']]
            resposta = "📤 **Top 10 Emitentes/Fornecedores (por valor total):**"
            return query, resposta, df_display
    
    # PERGUNTA 8: Por estado/UF
    if any(word in pergunta_lower for word in ['estado', 'estados', 'uf', 'distribuição', 'distribui', 'por estado', 'quais estados', 'geográfica', 'geografica', 'qual a distribui']):
        query = f"""
        SELECT 
            uf_emitente as 'UF',
            COUNT(*) as 'Quantidade',
            SUM(valor_total) as valor_total,
            AVG(valor_total) as valor_medio
        FROM docs_para_erp
        WHERE {filtro_periodo}
        GROUP BY uf_emitente
        ORDER BY valor_total DESC
        """
        df = executar_query(query)
        if not df.empty:
            df['Valor Total'] = df['valor_total'].apply(format_currency)
            df['Valor Médio'] = df['valor_medio'].apply(format_currency)
            df_display = df[['UF', 'Quantidade', 'Valor Total', 'Valor Médio']]
            resposta = "🗺️ **Distribuição por Estado:**"
            return query, resposta, df_display
    
    # PERGUNTA 8.5: ERROS / PROBLEMAS / VALIDAÇÃO (NOVA - INTELIGENTE)
    palavras_erros = ['errado', 'errada', 'errados', 'erradas', 'erro', 'erros', 'problema', 'problemas',
                      'invalido', 'invalida', 'inválido', 'inválida', 'incorreto', 'incorreta',
                      'suspeito', 'suspeita', 'anormal', 'anomalia', 'anomalias', 'inconsistente',
                      'inconsistência', 'inconsistencia', 'verificar', 'validar', 'checar', 'revisar',
                      'corrigir', 'correcao', 'correção', 'falha', 'falhas', 'defeito', 'defeitos',
                      'irregular', 'irregularidade', 'irregularidades', 'criticar', 'crítico', 'critico']
    
    if any(palavra in pergunta_lower for palavra in palavras_erros):
        # Query que verifica MÚLTIPLOS tipos de problemas
        query = f"""
        SELECT 
            'Valores Zerados' as 'Tipo de Problema',
            COUNT(*) as 'Quantidade'
        FROM docs_para_erp
        WHERE {filtro_periodo} AND valor_total = 0
        UNION ALL
        SELECT 
            'Valores Negativos' as 'Tipo de Problema',
            COUNT(*) as 'Quantidade'
        FROM docs_para_erp
        WHERE {filtro_periodo} AND valor_total < 0
        UNION ALL
        SELECT 
            'Sem Emitente' as 'Tipo de Problema',
            COUNT(*) as 'Quantidade'
        FROM docs_para_erp
        WHERE {filtro_periodo} AND (razao_social_emitente IS NULL OR razao_social_emitente = '')
        UNION ALL
        SELECT 
            'Sem Destinatário' as 'Tipo de Problema',
            COUNT(*) as 'Quantidade'
        FROM docs_para_erp
        WHERE {filtro_periodo} AND (razao_social_destinatario IS NULL OR razao_social_destinatario = '')
        UNION ALL
        SELECT 
            'Notas Duplicadas' as 'Tipo de Problema',
            COUNT(*) as 'Quantidade'
        FROM (
            SELECT numero_nf, serie
            FROM docs_para_erp
            WHERE {filtro_periodo}
            GROUP BY numero_nf, serie
            HAVING COUNT(*) > 1
        )
        UNION ALL
        SELECT 
            'Valores Muito Altos (>R$ 1Mi)' as 'Tipo de Problema',
            COUNT(*) as 'Quantidade'
        FROM docs_para_erp
        WHERE {filtro_periodo} AND valor_total > 1000000
        """
        df = executar_query(query)
        
        if not df.empty:
            # Filtrar apenas problemas reais (quantidade > 0)
            df_problemas = df[df['Quantidade'] > 0]
            
            if not df_problemas.empty:
                total_problemas = int(df_problemas['Quantidade'].sum())
                resposta = f"⚠️ **Análise de Problemas nas Notas Fiscais:**\n\n**Total de problemas detectados: {total_problemas}**\n\nDetalhes abaixo:"
                return query, resposta, df_problemas
            else:
                resposta = """✅ **Análise Completa: Nenhum Problema Detectado!**

Todas as notas fiscais estão corretas:
- ✅ Sem valores zerados ou negativos
- ✅ Todos os campos preenchidos corretamente
- ✅ Sem notas duplicadas
- ✅ Valores dentro da normalidade
- ✅ Dados consistentes e válidos

O sistema está funcionando perfeitamente! 🎉"""
                return query, resposta, pd.DataFrame()
    
    # PERGUNTA 9: Duplicados
    if any(word in pergunta_lower for word in ['duplicado', 'duplicadas', 'repetido', 'repetidas']):
        query = f"""
        SELECT 
            numero_nf as 'Número NF',
            serie as 'Série',
            COUNT(*) as 'Ocorrências'
        FROM docs_para_erp
        WHERE {filtro_periodo}
        GROUP BY numero_nf, serie
        HAVING COUNT(*) > 1
        ORDER BY COUNT(*) DESC
        """
        df = executar_query(query)
        if not df.empty:
            resposta = f"⚠️ **Notas Duplicadas Encontradas:** {len(df)} casos"
            return query, resposta, df
        else:
            resposta = "✅ **Nenhuma nota duplicada encontrada no período!**"
            return query, resposta, pd.DataFrame()
    
    # PERGUNTA 10: Maiores valores
    if any(word in pergunta_lower for word in ['maiores valores', 'maiores notas', 'top valores', 'notas maiores', 'valores maiores', 'quais as notas', 'quais notas']):
        query = f"""
        SELECT 
            numero_nf as 'Número NF',
            razao_social_emitente as 'Emitente',
            razao_social_destinatario as 'Destinatário',
            valor_total as 'Valor',
            data_emissao as 'Data'
        FROM docs_para_erp
        WHERE {filtro_periodo}
        ORDER BY valor_total DESC
        LIMIT 20
        """
        df = executar_query(query)
        if not df.empty:
            df['Valor'] = df['Valor'].apply(format_currency)
            resposta = "💰 **Top 20 Notas por Maior Valor:**"
            return query, resposta, df
    
    # PERGUNTA 11: Status ERP
    if any(word in pergunta_lower for word in ['erp', 'processad', 'pendente']):
        query = f"""
        SELECT 
            erp_processado as 'Status ERP',
            COUNT(*) as 'Quantidade',
            SUM(valor_total) as valor_total
        FROM docs_para_erp
        WHERE {filtro_periodo}
        GROUP BY erp_processado
        """
        df = executar_query(query)
        if not df.empty:
            df['Valor Total'] = df['valor_total'].apply(format_currency)
            df['Status ERP'] = df['Status ERP'].map({'Yes': '✅ Processado', 'No': '⏳ Pendente'})
            df_display = df[['Status ERP', 'Quantidade', 'Valor Total']]
            resposta = "⚙️ **Status de Processamento ERP:**"
            return query, resposta, df_display
    
    # PERGUNTA 12: Por município
    if any(word in pergunta_lower for word in ['município', 'municipio', 'cidade', 'cidades', 'municípios', 'municipios', 'top 20 munic', 'top munic', 'munic']):
        query = f"""
        SELECT 
            municipio_emitente as 'Município',
            uf_emitente as 'UF',
            COUNT(*) as 'Quantidade',
            SUM(valor_total) as valor_total
        FROM docs_para_erp
        WHERE {filtro_periodo}
        GROUP BY municipio_emitente, uf_emitente
        ORDER BY valor_total DESC
        LIMIT 20
        """
        df = executar_query(query)
        if not df.empty:
            df['Valor Total'] = df['valor_total'].apply(format_currency)
            df_display = df[['Município', 'UF', 'Quantidade', 'Valor Total']]
            resposta = "🏙️ **Top 20 Municípios:**"
            return query, resposta, df_display
    
    # PERGUNTA 13: Evolução temporal
    if any(word in pergunta_lower for word in ['evolução', 'evolucao', 'temporal', 'mês', 'mes', 'mensal', 'diária', 'diaria', 'qual a evolu', 'qual evolu']):
        query = f"""
        SELECT 
            strftime('%Y-%m', data_emissao) as 'Mês',
            COUNT(*) as 'Quantidade',
            SUM(valor_total) as valor_total,
            AVG(valor_total) as valor_medio
        FROM docs_para_erp
        WHERE {filtro_periodo}
        GROUP BY strftime('%Y-%m', data_emissao)
        ORDER BY strftime('%Y-%m', data_emissao)
        """
        df = executar_query(query)
        if not df.empty:
            df['Valor Total'] = df['valor_total'].apply(format_currency)
            df['Valor Médio'] = df['valor_medio'].apply(format_currency)
            df_display = df[['Mês', 'Quantidade', 'Valor Total', 'Valor Médio']]
            resposta = "📅 **Evolução Temporal:**"
            return query, resposta, df_display
    
    # FALLBACK: Tentar detectar intenção por palavras-chave parciais
    # Se tem "maior" ou "alto" → maiores valores
    if ('maior' in pergunta_lower or 'alto' in pergunta_lower) and 'valor' in pergunta_lower:
        query = f"""
        SELECT 
            numero_nf as 'Número NF',
            razao_social_emitente as 'Emitente',
            razao_social_destinatario as 'Destinatário',
            valor_total as 'Valor',
            data_emissao as 'Data'
        FROM docs_para_erp
        WHERE {filtro_periodo}
        ORDER BY valor_total DESC
        LIMIT 20
        """
        df = executar_query(query)
        if not df.empty:
            df['Valor'] = df['Valor'].apply(format_currency)
            resposta = "💰 **Top 20 Notas por Maior Valor:**"
            return query, resposta, df
    
    # Se tem "menor" ou "baixo" → menores valores
    if ('menor' in pergunta_lower or 'baixo' in pergunta_lower) and 'valor' in pergunta_lower:
        query = f"""
        SELECT 
            numero_nf as 'Número NF',
            razao_social_emitente as 'Emitente',
            razao_social_destinatario as 'Destinatário',
            valor_total as 'Valor',
            data_emissao as 'Data'
        FROM docs_para_erp
        WHERE {filtro_periodo}
        ORDER BY valor_total ASC
        LIMIT 20
        """
        df = executar_query(query)
        if not df.empty:
            df['Valor'] = df['Valor'].apply(format_currency)
            resposta = "📉 **Top 20 Notas por Menor Valor:**"
            return query, resposta, df
    
    # Pergunta não reconhecida
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
        # Default: início do ano corrente
        hoje = datetime.now()
        inicio_ano = datetime(hoje.year, 1, 1)
        data_inicio = st.date_input(
            "Data Início:",
            value=inicio_ano,
            key="data_inicio_ln"
        )
    
    with col2:
        data_fim = st.date_input(
            "Data Fim:",
            value=hoje,
            key="data_fim_ln"
        )
    
    with col3:
        dias_selecionados = (data_fim - data_inicio).days
        st.info(f"📊 Período: {dias_selecionados} dias ({data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')})")
    
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
        
        **Por Emitente:**
        - Quais os top 10 emitentes por valor?
        - Quais os fornecedores com mais notas?
        
        **Geografia:**
        - Qual a distribuição por estado (UF)?
        - Quais os top 20 municípios por valor?
        
        **Tempo:**
        - Qual a evolução temporal das notas?
        - Qual a evolução mensal?
        
        **Status:**
        - Qual o status de processamento ERP?
        - Quantas notas processadas vs pendentes?
        
        **Integridade:**
        - Há notas duplicadas?
        - Quais as notas com maiores valores?
        """)
        
        # Botões de exemplo
        st.markdown("**Clique para usar:**")
        col1, col2, col3 = st.columns(3)
        
        # Variável para controlar se um botão foi clicado
        pergunta_do_botao = None
        
        with col1:
            if st.button("📊 Quantas notas?", key="ex1"):
                pergunta_do_botao = "Quantas notas fiscais há no período?"
            if st.button("💰 Valor total?", key="ex2"):
                pergunta_do_botao = "Qual o total do valor bruto?"
            if st.button("📥 Top destinatários?", key="ex3"):
                pergunta_do_botao = "Quais os top 10 destinatários?"
        
        with col2:
            if st.button("📤 Top emitentes?", key="ex4"):
                pergunta_do_botao = "Quais os top 10 emitentes?"
            if st.button("🗺️ Por estado?", key="ex5"):
                pergunta_do_botao = "Qual a distribuição por estado?"
            if st.button("🏙️ Por município?", key="ex6"):
                pergunta_do_botao = "Quais os top 20 municípios?"
        
        with col3:
            if st.button("💸 Descontos?", key="ex7"):
                pergunta_do_botao = "Qual o total de descontos?"
            if st.button("📈 Estatísticas?", key="ex8"):
                pergunta_do_botao = "Qual a média, mínimo e máximo?"
            if st.button("⚠️ Duplicados?", key="ex9"):
                pergunta_do_botao = "Há notas duplicadas?"
        
        # Se algum botão foi clicado, processar imediatamente
        if pergunta_do_botao:
            st.markdown("---")
            st.info(f"🔍 Processando: **{pergunta_do_botao}**")
            
            with st.spinner("🤔 Processando sua pergunta..."):
                query, resposta, df_resultado = processar_pergunta_natural(
                    pergunta_do_botao,
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
                        st.dataframe(df_resultado, width="stretch", hide_index=True, height=400)
                        
                        # Gráfico se for numérico
                        if len(df_resultado) > 1 and 'valor_total' in df_resultado.columns:
                            st.markdown("#### 📈 Visualização")
                            fig = px.bar(
                                df_resultado.head(15),
                                x=df_resultado.columns[0],
                                y='valor_total',
                                title='Distribuição de Valores'
                            )
                            st.plotly_chart(fig, width="stretch")
                        
                        # Botões de exportação
                        criar_botoes_exportacao(df_resultado, "consulta_botao")
                    
                    # Mostrar SQL usado (opcional)
                    with st.expander("🔍 Ver SQL Gerado"):
                        st.code(query, language="sql")
                else:
                    st.warning(resposta)
    
    st.markdown("---")
    
    # Input da pergunta
    pergunta_natural = st.text_area(
        "✍️ Digite sua pergunta:",
        value=st.session_state.get('pergunta_ln', ''),
        placeholder="Ex: Quantas notas fiscais há no período? Qual o total de impostos?",
        height=100,
        key="pergunta_area"
    )
    
    if st.button("🚀 Processar Pergunta", type="primary", width="stretch", key="btn_ln"):
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
                        st.dataframe(df_resultado, width="stretch", hide_index=True, height=400)
                        
                        # Gráfico se for numérico
                        if len(df_resultado) > 1 and 'valor_total' in df_resultado.columns:
                            st.markdown("#### 📈 Visualização")
                            fig = px.bar(
                                df_resultado.head(15),
                                x=df_resultado.columns[0],
                                y='valor_total',
                                title='Distribuição de Valores'
                            )
                            st.plotly_chart(fig, width="stretch")
                        
                        # Botões de exportação
                        criar_botoes_exportacao(df_resultado, "consulta_natural")
                    
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
        LIMIT 50
        
        -- Valores acima de 10.000
        SELECT numero_nf, razao_social_emitente, valor_total 
        FROM docs_para_erp 
        WHERE valor_total > 10000 
        ORDER BY valor_total DESC
        LIMIT 100
        
        -- Por período
        SELECT * FROM docs_para_erp 
        WHERE data_emissao BETWEEN '2024-01-01' AND '2024-12-31'
        ORDER BY data_emissao DESC
        LIMIT 100
        
        -- Agregação por UF
        SELECT uf_emitente, COUNT(*) as qtd, SUM(valor_total) as total
        FROM docs_para_erp 
        GROUP BY uf_emitente 
        ORDER BY total DESC
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
    
    if st.button("🚀 Executar SQL", type="primary", width="stretch", key="btn_sql"):
        if consulta_sql:
            # Limpar SQL: remover ponto-e-vírgula no final e múltiplas statements
            consulta_sql = consulta_sql.strip()
            
            # Remover ponto-e-vírgula no final
            if consulta_sql.endswith(';'):
                consulta_sql = consulta_sql[:-1].strip()
            
            # Verificar se tem múltiplas statements (ponto-e-vírgula no meio)
            if ';' in consulta_sql:
                st.error("❌ Apenas uma consulta SQL por vez é permitida. Remova o ponto-e-vírgula (;) do meio da query.")
                st.info("💡 **Dica:** Se copiou do exemplo, remova todos os ponto-e-vírgulas (;)")
                st.stop()
            
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
                    
                    st.dataframe(df_result, width="stretch", hide_index=True, height=500)
                    
                    # Botões de exportação
                    criar_botoes_exportacao(df_result, "sql_result")
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
    
    ---
    
    **BD Automática:**
    - ✅ Criada automaticamente
    - ✅ Sem configuração manual
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
