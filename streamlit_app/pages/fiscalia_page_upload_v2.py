"""
Fiscalia - Página de Upload de XMLs (VERSÃO FINAL)
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

# Adicionar src ao path
root_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_path))

from src.processors.nfe_processor import NFeProcessor
from src.utils.config import get_settings
from streamlit_app.components.common import show_header, show_success, show_error, show_info

# Configuração
st.set_page_config(page_title="Upload - Fiscalia", page_icon="📤", layout="wide")

# ==================== SESSION STATE ====================
if 'arquivos_processados' not in st.session_state:
    st.session_state.arquivos_processados = set()

if 'ultimo_modo' not in st.session_state:
    st.session_state.ultimo_modo = None

# Header
show_header("Upload de Arquivos XML", "Carregue arquivos XML de Notas Fiscais Eletrônicas")

# Configuração de pastas
settings = get_settings()

st.markdown("### ⚙️ Configuração de Pastas")

col1, col2 = st.columns([3, 1])

with col1:
    pasta_info = f"""
    📁 **Pasta Base**: `{settings.pasta_base}`
    - 📥 Entrados: `{settings.pasta_entrados}`
    - ✅ Processados: `{settings.pasta_processados}`
    - ❌ Rejeitados: `{settings.pasta_rejeitados}`
    """
    st.info(pasta_info)

with col2:
    if st.button("🔄 Limpar Estado", use_container_width=True, help="Limpa histórico da sessão"):
        st.session_state.arquivos_processados = set()
        st.session_state.ultimo_modo = None
        show_success("Estado limpo! Pronto para novo processamento.")
        st.rerun()

st.markdown("---")

# Modos de upload
st.markdown("### 📥 Escolha o Modo de Processamento")

modo = st.radio(
    "Selecione uma opção:",
    ["📤 Upload Manual (Arrastar/Selecionar)", 
     "📂 Processar Pasta /entrados (Batch)"],
    help="Upload manual: processa imediatamente. Batch: processa todos da pasta.",
    key="modo_upload"
)

# Detectar mudança de modo
if st.session_state.ultimo_modo and st.session_state.ultimo_modo != modo:
    st.session_state.arquivos_processados = set()
    show_info("Modo alterado. Estado limpo automaticamente.")

st.session_state.ultimo_modo = modo

st.markdown("---")

# ==================== MODO 1: Upload Manual ====================
if modo == "📤 Upload Manual (Arrastar/Selecionar)":
    st.markdown("### 📤 Upload de Arquivos XML")
    
    uploaded_files = st.file_uploader(
        "Arraste arquivos XML ou clique para selecionar",
        type=['xml'],
        accept_multiple_files=True,
        help="Você pode selecionar múltiplos arquivos XML",
        key="file_uploader"
    )
    
    if uploaded_files:
        # Filtrar arquivos já processados NESTA SESSÃO
        novos_arquivos = [
            f for f in uploaded_files 
            if f.name not in st.session_state.arquivos_processados
        ]
        
        if not novos_arquivos:
            st.warning("⚠️ Todos os arquivos selecionados já foram processados nesta sessão.")
            st.info("💡 Use o botão 'Limpar Estado' para reprocessar ou selecione novos arquivos.")
        else:
            show_success(f"{len(novos_arquivos)} arquivo(s) NOVO(S) carregado(s)")
            
            if len(uploaded_files) > len(novos_arquivos):
                st.warning(f"⚠️ {len(uploaded_files) - len(novos_arquivos)} arquivo(s) já processado(s) nesta sessão - ignorados")
            
            # Mostrar apenas NOVOS arquivos
            with st.expander("📋 Arquivos NOVOS a Processar", expanded=True):
                for file in novos_arquivos:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.text(f"📄 {file.name}")
                    with col2:
                        st.text(f"{file.size / 1024:.1f} KB")
            
            st.markdown("---")
            
            # Botão processar
            if st.button("🚀 Processar Arquivos NOVOS", type="primary", use_container_width=True):
                
                with st.spinner('Processando arquivos...'):
                    processor = NFeProcessor()
                    resultados = []
                    
                    # Barra de progresso
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for idx, uploaded_file in enumerate(novos_arquivos):
                        status_text.text(f"Processando {idx+1}/{len(novos_arquivos)}: {uploaded_file.name}")
                        
                        # Processar
                        resultado = processor.process_uploaded_file(uploaded_file, uploaded_file.name)
                        
                        resultados.append({
                            'arquivo': uploaded_file.name,
                            'resultado': resultado
                        })
                        
                        # Marcar como processado NESTA SESSÃO
                        st.session_state.arquivos_processados.add(uploaded_file.name)
                        
                        # Atualizar progresso
                        progress_bar.progress((idx + 1) / len(novos_arquivos))
                    
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Mostrar resultados
                    st.markdown("### 📊 Resultados do Processamento")
                    
                    sucessos = sum(1 for r in resultados if r['resultado'].get('success'))
                    duplicados = sum(1 for r in resultados if r['resultado'].get('duplicado'))
                    erros = len(resultados) - sucessos - duplicados
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total", len(resultados))
                    with col2:
                        st.metric("✅ Sucessos", sucessos)
                    with col3:
                        st.metric("⚠️ Duplicados", duplicados)
                    with col4:
                        st.metric("❌ Erros", erros)
                    
                    # Detalhes
                    for resultado in resultados:
                        res = resultado['resultado']
                        
                        if res.get('duplicado'):
                            icon = "⚠️"
                            expanded = False
                        elif res.get('success'):
                            icon = "✅"
                            expanded = False
                        else:
                            icon = "❌"
                            expanded = True
                        
                        with st.expander(f"{icon} {resultado['arquivo']}", expanded=expanded):
                            if res.get('success'):
                                show_success("Processado com sucesso!", "Movido para: /processados")
                            elif res.get('duplicado'):
                                st.warning(f"⚠️ Arquivo duplicado: {res.get('message')}")
                                st.info("💡 Este arquivo já existe no banco de dados")
                            else:
                                show_error("Erro no processamento", res.get('message', 'Erro desconhecido'))

# ==================== MODO 2: Batch ====================
else:
    st.markdown("### 📂 Processamento em Lote (Batch)")
    
    # Inicializar processor
    processor = NFeProcessor()
    
    # Usar método inteligente que filtra duplicados
    arquivos_novos = processor.file_handler.get_arquivos_entrados()
    
    if arquivos_novos:
        # CORREÇÃO: Removido "XML" da mensagem
        show_info(f"Encontrados {len(arquivos_novos)} arquivo(s) na pasta /entrados")
        
        with st.expander("📋 Arquivos Encontrados", expanded=True):
            for arquivo in arquivos_novos:
                col1, col2 = st.columns([3, 1])
                with col1:
                    # Mostrar ícone baseado na extensão
                    ext = arquivo.suffix.lower()
                    if ext == '.xml':
                        icon = "📄"
                    else:
                        icon = "⚠️"
                    st.text(f"{icon} {arquivo.name}")
                with col2:
                    st.text(ext)
        
        st.markdown("---")
        
        if st.button("🚀 Processar Arquivos", type="primary", use_container_width=True):
            with st.spinner('Processando arquivos em lote...'):
                resultado_batch = processor.process_batch()
                
                if resultado_batch['success']:
                    st.markdown("### 📊 Resultados do Processamento")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total", resultado_batch['total'])
                    with col2:
                        st.metric("✅ Sucessos", resultado_batch['processados'])
                    with col3:
                        st.metric("❌ Erros", resultado_batch['erros'])
                    
                    # Detalhes
                    if 'resultados' in resultado_batch:
                        for resultado in resultado_batch['resultados']:
                            arquivo_nome = Path(resultado.get('file', 'desconhecido')).name
                            
                            icon = "✅" if resultado.get('success') else "❌"
                            expanded = not resultado.get('success')
                            
                            with st.expander(f"{icon} {arquivo_nome}", expanded=expanded):
                                if resultado.get('success'):
                                    show_success("Processado com sucesso!")
                                else:
                                    show_error("Erro no processamento", resultado.get('message', 'Erro desconhecido'))
                    
                    show_success("✅ Processamento em lote concluído!")
    
    else:
        st.warning("⚠️ Nenhum arquivo encontrado na pasta /entrados")
        st.info("💡 A pasta está vazia ou todos os arquivos já foram processados")

# ==================== STATUS DA SESSÃO ====================
if st.session_state.arquivos_processados:
    with st.expander("📊 Status da Sessão Atual", expanded=False):
        st.markdown(f"""
        **Arquivos processados nesta sessão:** {len(st.session_state.arquivos_processados)}
        
        **Arquivos:**
        """)
        for arquivo in sorted(st.session_state.arquivos_processados):
            st.text(f"✅ {arquivo}")

# Informações adicionais
st.markdown("---")
st.markdown("### ℹ️ Informações")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    #### 📝 Formatos Suportados
    - ✅ **XML** - Notas Fiscais Eletrônicas (NFe)
    - ⏳ PDF - Em desenvolvimento
    - ⏳ Imagens - Em desenvolvimento
    
    #### 🔍 Proteções Anti-Duplicação
    - Verifica duplicados no banco de dados
    - Bloqueia reprocessamento na sessão
    - Evita salvar arquivos duplicados
    - Mantém histórico no BD
    """)

with col2:
    st.markdown("""
    #### 📊 Após Processamento
    - Dados salvos no banco
    - Disponíveis para análise
    - Prontos para integração ERP
    - Arquivos movidos automaticamente
    
    #### 🤖 Validações Automáticas
    - Extensão do arquivo
    - Estrutura XML válida
    - Chave de acesso NFe
    - Duplicados no banco
    """)
