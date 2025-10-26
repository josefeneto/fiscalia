"""
Fiscalia - Página de Upload de XMLs (VERSÃO FINAL V7 - CORRIGIDA)
Usa DatabaseManager corretamente (cria BD automaticamente)
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import zipfile
import io

# Adicionar src ao path de forma robusta
current_file = Path(__file__).resolve()
root_path = current_file.parent.parent.parent
src_path = root_path / 'src'

# Adicionar ambos ao path se não existirem
for path in [str(root_path), str(src_path)]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Importar
try:
    from src.processors.nfe_processor import NFeProcessor
    from src.database.db_manager import DatabaseManager
    from src.utils.config import get_settings
    from streamlit_app.components.common import show_header, show_success, show_error, show_info
except ImportError as e:
    st.error(f"❌ Erro ao importar módulos: {e}")
    st.stop()

# Configuração
st.set_page_config(page_title="Upload - Fiscalia", page_icon="📤", layout="wide")

# Header
show_header("Upload de Notas Fiscais", "Carregar arquivos XML (individual ou ZIP)")

# ==================== FUNÇÕES AUXILIARES ====================

@st.cache_resource
def get_db():
    """Retorna instância do DatabaseManager (cria BD automaticamente)"""
    return DatabaseManager()


def registrar_resultado_bd(arquivo_nome: str, resultado: str, causa: str = None):
    """
    Registra resultado na tabela registo_resultados usando DatabaseManager
    """
    try:
        db = get_db()
        
        resultado_data = {
            'time_stamp': datetime.now(),
            'path_nome_arquivo': str(Path("upload") / arquivo_nome),
            'resultado': resultado,
            'causa': causa
        }
        
        db.add_resultado(resultado_data)
        
    except Exception as e:
        st.warning(f"⚠️ Erro ao registrar resultado: {e}")


def validate_xml_structure(content: bytes) -> tuple:
    """
    Valida estrutura XML
    Retorna: (is_valid: bool, message: str, root: Element or None)
    """
    try:
        import xml.etree.ElementTree as ET
        
        xml_str = content.decode('utf-8', errors='ignore')
        root = ET.fromstring(xml_str)
        
        if len(xml_str) < 100:
            return (False, 'XML muito pequeno (possivelmente corrompido)', None)
        
        if not root.tag:
            return (False, 'XML sem tag raiz', None)
        
        return (True, 'XML válido', root)
        
    except ET.ParseError as e:
        return (False, f'XML mal formado: {str(e)}', None)
    except UnicodeDecodeError:
        return (False, 'Encoding inválido (não é UTF-8)', None)
    except Exception as e:
        return (False, f'Erro ao validar XML: {str(e)}', None)


def extract_chave_acesso_from_root(root) -> str:
    """Extrai chave de acesso de um elemento XML já parseado"""
    try:
        for elem in root.iter():
            if 'chNFe' in elem.tag or 'chave' in elem.tag.lower():
                if elem.text and len(elem.text) == 44:
                    return elem.text
        
        for elem in root.iter():
            if 'Id' in elem.attrib:
                id_val = elem.attrib['Id']
                if 'NFe' in id_val:
                    chave = id_val.replace('NFe', '')
                    if len(chave) == 44 and chave.isdigit():
                        return chave
        
        return None
    except:
        return None


def check_duplicate_by_chave(chave_acesso: str) -> tuple:
    """
    Verifica se chave já existe na BD usando DatabaseManager
    Retorna: (is_duplicate: bool, existing_file: str)
    """
    if not chave_acesso:
        return (False, None)
    
    try:
        db = get_db()
        doc = db.get_documento_by_chave(chave_acesso)
        
        if doc:
            existing_file = Path(doc.path_nome_arquivo).name if doc.path_nome_arquivo else "desconhecido"
            return (True, existing_file)
        return (False, None)
    except Exception as e:
        st.warning(f"⚠️ Erro ao verificar duplicado: {e}")
        return (False, None)


def extract_xml_from_zip(zip_file) -> list:
    """Extrai XMLs de um ZIP - retorna [(filename, content)]"""
    xml_files = []
    
    try:
        with zipfile.ZipFile(io.BytesIO(zip_file.read())) as z:
            for filename in z.namelist():
                if filename.startswith('__MACOSX') or filename.startswith('.'):
                    continue
                if filename.lower().endswith('.xml'):
                    content = z.read(filename)
                    xml_files.append((filename, content))
        return xml_files
    except zipfile.BadZipFile:
        st.error("❌ Ficheiro ZIP inválido ou corrompido")
        return []
    except Exception as e:
        st.error(f"❌ Erro ao extrair ZIP: {e}")
        return []


# ==================== INFO SOBRE TIPOS SUPORTADOS ====================

with st.expander("ℹ️ Tipos de Documentos Suportados"):
    st.markdown("""
    **Atualmente (MVP):**
    - ✅ **NFe Brasil** (Formato XML padrão)
    
    **Em Breve:**
    - 🔜 NFe Portugal
    - 🔜 SAF-T
    """)

st.write("---")

# ==================== TABS DE UPLOAD ====================

tab1, tab2 = st.tabs(["📄 Upload de Ficheiros XML", "📦 Upload de ZIP"])

# ==================== TAB 1: Upload Individual ====================

with tab1:
    st.subheader("📄 Upload de Ficheiros XML")
    
    st.info("💡 Selecione até 20 ficheiros XML. Sistema deteta duplicados automaticamente.")
    
    uploaded_files = st.file_uploader(
        "Selecione ficheiros NFe (XML)",
        type=["xml"],
        accept_multiple_files=True,
        help="Máximo 20 ficheiros",
        key="xml_uploader"
    )
    
    if uploaded_files and len(uploaded_files) > 20:
        st.error(f"❌ Limite de 20 ficheiros excedido! Selecionou {len(uploaded_files)}.")
        st.info("💡 Use upload ZIP para lotes maiores")
        uploaded_files = None
    
    if uploaded_files:
        st.success(f"✅ **{len(uploaded_files)} ficheiro(s)** carregado(s)")
        
        with st.expander("📋 Ver lista de ficheiros"):
            for i, file in enumerate(uploaded_files, 1):
                size_mb = len(file.getvalue()) / (1024 * 1024)
                st.write(f"{i}. **{file.name}** ({size_mb:.2f} MB)")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            process_btn = st.button("🚀 Processar", type="primary", width="stretch", key="btn_xml")
        
        if process_btn:
            st.write("---")
            st.subheader("🔄 Processamento em Curso")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            processor = NFeProcessor()
            resultados = []
            
            for idx, file in enumerate(uploaded_files):
                status_text.text(f"Processando {idx+1}/{len(uploaded_files)}: {file.name}")
                
                content = file.read()
                
                # 1. Validar XML
                is_valid, validation_msg, root = validate_xml_structure(content)
                
                if not is_valid:
                    registrar_resultado_bd(file.name, 'ERRO', validation_msg)
                    
                    resultados.append({
                        'arquivo': file.name,
                        'status': 'erro',
                        'message': f'❌ {validation_msg}',
                        'chave': None
                    })
                    file.seek(0)
                    continue
                
                # 2. Extrair chave
                chave = extract_chave_acesso_from_root(root)
                
                if not chave:
                    registrar_resultado_bd(file.name, 'ERRO', 'Chave de acesso NFe não encontrada')
                    
                    resultados.append({
                        'arquivo': file.name,
                        'status': 'erro',
                        'message': '❌ Chave de acesso NFe não encontrada',
                        'chave': None
                    })
                    file.seek(0)
                    continue
                
                # 3. Verificar duplicado
                is_dup, existing_file = check_duplicate_by_chave(chave)
                
                if is_dup:
                    registrar_resultado_bd(
                        file.name, 
                        'ERRO', 
                        f'Duplicado - Chave já processada em: {existing_file}'
                    )
                    
                    resultados.append({
                        'arquivo': file.name,
                        'status': 'duplicado',
                        'message': f'Chave já processada no ficheiro: {existing_file}',
                        'chave': chave
                    })
                    file.seek(0)
                    continue
                
                # 4. Processar
                try:
                    file.seek(0)
                    resultado = processor.process_uploaded_file(file, file.name)
                    
                    if resultado.get('success'):
                        resultados.append({
                            'arquivo': file.name,
                            'status': 'sucesso',
                            'message': 'Processado com sucesso',
                            'chave': chave
                        })
                    else:
                        msg_erro = resultado.get('message', 'Erro desconhecido')
                        registrar_resultado_bd(file.name, 'ERRO', msg_erro)
                        
                        resultados.append({
                            'arquivo': file.name,
                            'status': 'erro',
                            'message': msg_erro,
                            'chave': chave
                        })
                except Exception as e:
                    registrar_resultado_bd(file.name, 'ERRO', str(e))
                    
                    resultados.append({
                        'arquivo': file.name,
                        'status': 'erro',
                        'message': str(e),
                        'chave': chave
                    })
                
                file.seek(0)
                progress_bar.progress((idx + 1) / len(uploaded_files))
            
            progress_bar.empty()
            status_text.empty()
            
            # Resultados
            st.write("---")
            st.subheader("📊 Resultados")
            
            total = len(resultados)
            sucessos = sum(1 for r in resultados if r['status'] == 'sucesso')
            duplicados = sum(1 for r in resultados if r['status'] == 'duplicado')
            erros = sum(1 for r in resultados if r['status'] == 'erro')
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total", total)
            col2.metric("✅ Sucesso", sucessos)
            col3.metric("⚠️ Duplicados", duplicados)
            col4.metric("❌ Erros", erros)
            
            st.write("### 📋 Detalhes")
            
            for res in resultados:
                icon = "✅" if res['status'] == 'sucesso' else ("⚠️" if res['status'] == 'duplicado' else "❌")
                expanded = res['status'] == 'erro'
                
                with st.expander(f"{icon} {res['arquivo']}", expanded=expanded):
                    if res['status'] == 'sucesso':
                        show_success("Processado com sucesso!")
                        if res['chave']:
                            st.caption(f"Chave: {res['chave']}")
                    elif res['status'] == 'duplicado':
                        st.warning("⚠️ Ficheiro duplicado")
                        st.info(res['message'])
                    else:
                        show_error("Erro", res['message'])
            
            if sucessos == total:
                st.success(f"🎉 Todos os {total} ficheiros processados!")
            elif sucessos > 0:
                st.warning(f"⚠️ {sucessos} de {total} processados.")


# ==================== TAB 2: Upload ZIP ====================

with tab2:
    st.subheader("📦 Upload de Ficheiro ZIP")
    
    st.info("💡 ZIP pode conter até 50 ficheiros XML")
    
    zip_file = st.file_uploader(
        "Selecione ZIP",
        type=["zip"],
        key="zip_uploader"
    )
    
    if zip_file:
        xml_files = extract_xml_from_zip(zip_file)
        
        if xml_files:
            st.success(f"✅ ZIP com **{len(xml_files)} ficheiro(s) XML**")
            
            with st.expander("📋 Conteúdo"):
                for i, (filename, content) in enumerate(xml_files, 1):
                    st.write(f"{i}. {filename} ({len(content)/1024:.1f} KB)")
            
            col1, col2 = st.columns([3, 1])
            
            with col2:
                process_zip_btn = st.button("🚀 Processar ZIP", type="primary", width="stretch", key="btn_zip")
            
            if process_zip_btn:
                if len(xml_files) > 50:
                    st.error(f"❌ ZIP contém {len(xml_files)} ficheiros. Limite: 50")
                else:
                    st.write("---")
                    st.subheader("🔄 Processamento em Curso")
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    processor = NFeProcessor()
                    resultados = []
                    
                    for idx, (filename, content) in enumerate(xml_files):
                        status_text.text(f"Processando {idx+1}/{len(xml_files)}: {filename}")
                        
                        # Processar igual ao tab1
                        is_valid, validation_msg, root = validate_xml_structure(content)
                        
                        if not is_valid:
                            registrar_resultado_bd(filename, 'ERRO', validation_msg)
                            resultados.append({
                                'arquivo': filename,
                                'status': 'erro',
                                'message': f'❌ {validation_msg}',
                                'chave': None
                            })
                            continue
                        
                        chave = extract_chave_acesso_from_root(root)
                        
                        if not chave:
                            registrar_resultado_bd(filename, 'ERRO', 'Chave não encontrada')
                            resultados.append({
                                'arquivo': filename,
                                'status': 'erro',
                                'message': '❌ Chave não encontrada',
                                'chave': None
                            })
                            continue
                        
                        is_dup, existing_file = check_duplicate_by_chave(chave)
                        
                        if is_dup:
                            registrar_resultado_bd(
                                filename,
                                'ERRO',
                                f'Duplicado - já processado em: {existing_file}'
                            )
                            resultados.append({
                                'arquivo': filename,
                                'status': 'duplicado',
                                'message': f'Já processado em: {existing_file}',
                                'chave': chave
                            })
                            continue
                        
                        try:
                            class FakeFile:
                                def __init__(self, name, content):
                                    self.name = name
                                    self._content = content
                                    self._pos = 0
                                def read(self, size=-1):
                                    if size == -1:
                                        result = self._content[self._pos:]
                                        self._pos = len(self._content)
                                    else:
                                        result = self._content[self._pos:self._pos + size]
                                        self._pos += size
                                    return result
                                def seek(self, pos, whence=0):
                                    if whence == 0:
                                        self._pos = pos
                                    elif whence == 1:
                                        self._pos += pos
                                    elif whence == 2:
                                        self._pos = len(self._content) + pos
                                    return self._pos
                                def tell(self):
                                    return self._pos
                                def getvalue(self):
                                    return self._content
                                def getbuffer(self):
                                    return memoryview(self._content)
                                @property
                                def size(self):
                                    return len(self._content)
                            
                            fake_file = FakeFile(filename, content)
                            resultado = processor.process_uploaded_file(fake_file, filename)
                            
                            if resultado.get('success'):
                                resultados.append({
                                    'arquivo': filename,
                                    'status': 'sucesso',
                                    'message': 'Processado',
                                    'chave': chave
                                })
                            else:
                                msg_erro = resultado.get('message', 'Erro')
                                registrar_resultado_bd(filename, 'ERRO', msg_erro)
                                resultados.append({
                                    'arquivo': filename,
                                    'status': 'erro',
                                    'message': msg_erro,
                                    'chave': chave
                                })
                        except Exception as e:
                            registrar_resultado_bd(filename, 'ERRO', str(e))
                            resultados.append({
                                'arquivo': filename,
                                'status': 'erro',
                                'message': str(e),
                                'chave': chave
                            })
                        
                        progress_bar.progress((idx + 1) / len(xml_files))
                    
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Resultados
                    st.write("---")
                    st.subheader("📊 Resultados")
                    
                    total = len(resultados)
                    sucessos = sum(1 for r in resultados if r['status'] == 'sucesso')
                    duplicados = sum(1 for r in resultados if r['status'] == 'duplicado')
                    erros = sum(1 for r in resultados if r['status'] == 'erro')
                    
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Total", total)
                    col2.metric("✅ Sucesso", sucessos)
                    col3.metric("⚠️ Duplicados", duplicados)
                    col4.metric("❌ Erros", erros)
                    
                    st.write("### 📋 Detalhes")
                    
                    for res in resultados:
                        icon = "✅" if res['status'] == 'sucesso' else ("⚠️" if res['status'] == 'duplicado' else "❌")
                        expanded = res['status'] == 'erro'
                        
                        with st.expander(f"{icon} {res['arquivo']}", expanded=expanded):
                            if res['status'] == 'sucesso':
                                show_success("Processado!")
                            elif res['status'] == 'duplicado':
                                st.warning("⚠️ Duplicado")
                                st.info(res['message'])
                            else:
                                show_error("Erro", res['message'])


# ==================== SIDEBAR ====================

with st.sidebar:
    st.header("ℹ️ Informação")
    st.write("**Limites:**")
    st.write("- Ficheiros XML: 20")
    st.write("- ZIP: 50 ficheiros")
    st.write("---")
    st.write("**Deteção:**")
    st.write("✅ Por chave de acesso")
    st.write("✅ Validação XML")
    st.write("✅ Registo completo na BD")
    st.write("---")
    st.write("**BD Automática:**")
    st.write("✅ Criada automaticamente")
    st.write("✅ Sem configuração manual")
