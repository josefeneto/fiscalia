"""
Fiscalia - Página Inicial
Sistema de Gestão e Análise de Documentos Fiscais
"""

import streamlit as st
from pathlib import Path
import sys

# Adicionar src ao path
root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path))

# Configuração da página
st.set_page_config(
    page_title="Fiscalia - Home",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Header
st.title("🏠 Fiscalia")
st.markdown("### Sistema de Gestão e Análise de Documentos Fiscais")
st.markdown("---")

# Informações principais
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📤 Upload")
    st.markdown("""
    - Upload de XMLs individuais
    - Upload múltiplo (até 20 arquivos)
    - Upload de arquivo ZIP
    - Processamento automático
    """)

with col2:
    st.markdown("### 📊 Visualização")
    st.markdown("""
    - Dados de todas as notas fiscais
    - Filtros por período
    - Exportação para CSV/Excel
    - Pesquisa avançada
    """)

with col3:
    st.markdown("### 📈 Análise")
    st.markdown("""
    - Estatísticas detalhadas
    - Gráficos interativos
    - Consultas inteligentes
    - Relatórios customizados
    """)

st.markdown("---")

# Guia Rápido
st.markdown("## 🎯 Como Começar")

st.markdown("### 📝 Guia Rápido")

with st.expander("**1️⃣ Fazer Upload de XMLs**", expanded=True):
    st.markdown("""
    #### 📤 Página de Upload
    
    Você pode fazer upload de 3 formas diferentes:
    
    **Opção 1: Arquivo Individual**
    - Clique em "Browse files"
    - Selecione **1 arquivo XML**
    - Clique em "Processar Arquivos"
    
    **Opção 2: Múltiplos Arquivos (até 20)**
    - Clique em "Browse files"
    - Selecione **múltiplos XMLs** (Ctrl+Click ou Shift+Click)
    - Máximo: 20 arquivos por vez
    - Clique em "Processar Arquivos"
    
    **Opção 3: Arquivo ZIP (até 50 XMLs)**
    - Compacte seus XMLs em um arquivo **.zip**
    - Máximo: 50 arquivos dentro do ZIP
    - Faça upload do ZIP
    - Todos os XMLs serão extraídos e processados automaticamente
    
    #### ✅ Após o Upload:
    - XMLs são validados automaticamente
    - Dados extraídos e salvos no banco de dados
    - Arquivos movidos para pasta "processados"
    - Relatório de sucesso/erro exibido
    """)

with st.expander("**2️⃣ Visualizar Dados**"):
    st.markdown("""
    #### 📊 Página Visualizar
    
    **Filtros Disponíveis:**
    - 📅 **Período:** Selecione data início e fim
      - Padrão: 01/01/2025 até hoje (ano corrente)
    - 🔍 **Pesquisa:** Busque por qualquer campo
    
    **Tabelas Disponíveis:**
    - 📄 **Documentos:** Todas as notas fiscais processadas
    - 📋 **Registro de Resultados:** Histórico de processamento
    
    **Ações:**
    - 📥 Exportar para CSV
    - 📥 Exportar para Excel
    - 🔄 Atualizar dados
    - 👁️ Ver detalhes de cada nota
    """)

with st.expander("**3️⃣ Analisar Estatísticas**"):
    st.markdown("""
    #### 📈 Página Estatísticas
    
    **Filtro de Período:**
    - 📅 Selecione o período para análise
    - Padrão: Todo o ano corrente
    
    **Análises Disponíveis:**
    
    1. **📊 Por Estado (UF)**
       - Top 10 estados por quantidade
       - Top 10 estados por valor total
    
    2. **📅 Evolução Temporal**
       - Gráfico de linha mostrando documentos por mês
       - Tendências ao longo do tempo
    
    3. **⚙️ Status ERP**
       - Documentos processados vs pendentes
       - Gráfico de pizza
    
    4. **💰 Distribuição de Valores**
       - Histograma de valores
       - Faixas de valor (até 1k, 1k-5k, 5k-10k, etc.)
    
    **Métricas Exibidas:**
    - 📊 Total de documentos
    - 💰 Valor total
    - 📈 Valor médio
    - 📉 Valor mínimo e máximo
    """)

with st.expander("**4️⃣ Fazer Consultas Inteligentes**"):
    st.markdown("""
    #### 💬 Página Consultas
    
    **3 Formas de Consultar:**
    
    **1. Botões Rápidos (9 opções):**
    - 📊 Quantas notas?
    - 💰 Valor total?
    - 📥 Top destinatários?
    - 📤 Top emitentes?
    - 🗺️ Por estado?
    - 🏙️ Por município?
    - 💸 Descontos?
    - 📈 Estatísticas?
    - ⚠️ Duplicados?
    
    **2. Linguagem Natural:**
    - Digite sua pergunta em português
    - Exemplos:
      - "Qual o total de notas em 2025?"
      - "Quais os top 10 fornecedores?"
      - "Há notas duplicadas?"
      - "Qual a média de valores?"
    
    **3. SQL Direto:**
    - Escreva consultas SQL customizadas
    - Acesso direto ao banco de dados
    - Para usuários avançados
    
    **Recursos:**
    - 📅 Filtro de período integrado
    - 📊 Gráficos automáticos quando relevante
    - 📥 Exportar resultados
    - 💡 Sugestões de perguntas
    """)

st.markdown("---")

# Dicas e Informações
st.markdown("## 💡 Dicas Importantes")

col1, col2 = st.columns(2)

with col1:
    st.info("""
    **📅 Período Padrão:**
    - Todas as páginas iniciam com período: **01/01/2025 até hoje**
    - Você pode alterar para qualquer período desejado
    - Dados são filtrados automaticamente
    """)
    
    st.success("""
    **✅ Processamento:**
    - XMLs são validados automaticamente
    - Duplicados são detectados
    - Arquivos movidos para pasta "processados"
    - Histórico completo mantido no banco
    """)

with col2:
    st.warning("""
    **⚠️ Limites:**
    - Upload individual: 1 arquivo por vez
    - Upload múltiplo: até 20 arquivos
    - ZIP: até 50 arquivos dentro do ZIP
    - Tamanho máximo por arquivo: conforme config
    """)
    
    st.info("""
    **🔍 Consultas:**
    - Botões rápidos para perguntas comuns
    - Linguagem natural em português
    - SQL avançado disponível
    - Resultados exportáveis
    """)

st.markdown("---")

# Recursos Principais
st.markdown("## 🚀 Recursos Principais")

features = [
    ("📤", "Upload Flexível", "Arquivo individual, múltiplos (até 20) ou ZIP completo"),
    ("🔍", "Validação Automática", "XMLs validados e verificados antes do processamento"),
    ("💾", "Banco de Dados", "SQLite com histórico completo de operações"),
    ("📊", "Visualização", "Tabelas interativas com filtros e pesquisa"),
    ("📈", "Estatísticas", "Gráficos e análises detalhadas por período"),
    ("💬", "Consultas", "Linguagem natural, botões rápidos ou SQL direto"),
    ("📥", "Exportação", "CSV e Excel para análise externa"),
    ("🔄", "Atualização", "Dados sempre atualizados e sincronizados"),
]

cols = st.columns(4)
for i, (icon, title, desc) in enumerate(features):
    with cols[i % 4]:
        st.markdown(f"### {icon} {title}")
        st.caption(desc)

st.markdown("---")

# Footer
st.markdown("### 📞 Suporte")
st.markdown("""
**Precisa de ajuda?**
- 📚 Consulte os guias em cada página
- 💡 Use os botões de exemplo nas consultas
- 🔍 Explore as funcionalidades gradualmente
- ⚙️ Ajuste os períodos conforme necessário
""")

st.markdown("---")
st.caption("Fiscalia - Sistema de Gestão de Documentos Fiscais | Versão 2.0")
