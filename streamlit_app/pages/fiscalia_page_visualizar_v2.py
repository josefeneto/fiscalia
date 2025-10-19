"""
Fiscalia - Visualizar Banco de Dados
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd

# Adicionar src ao path
root_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_path))

from src.database.db_manager import DatabaseManager
from streamlit_app.components import show_header, format_currency

# Configuração
st.set_page_config(page_title="Visualizar BD - Fiscalia", page_icon="📊", layout="wide")

# Header
show_header("Visualizar Banco de Dados", "Consulte e explore os dados processados")

# Conectar ao banco
@st.cache_resource
def get_db():
    return DatabaseManager()

db = get_db()

# Buscar dados
st.markdown("### 📋 Notas Fiscais Processadas")

try:
    documentos = db.get_recent_documents(100)
    
    if documentos:
        st.success(f"✅ Encontradas {len(documentos)} NFe(s)")
        
        # Preparar dados para tabela
        data = []
        for doc in documentos:
            data.append({
                'Número': doc.numero_nf,
                'Emitente': doc.razao_social_emitente,
                'Destinatário': doc.razao_social_destinatario,
                'Valor': format_currency(doc.valor_total),
                'Data': doc.data_emissao.strftime('%d/%m/%Y') if doc.data_emissao else 'N/A',
                'UF': doc.uf_emitente,
                'ERP': '✅' if doc.erp_processado == 'Yes' else '⏳'
            })
        
        df = pd.DataFrame(data)
        
        # Exibir tabela
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Exportar
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Exportar CSV",
            data=csv,
            file_name="fiscalia_export.csv",
            mime="text/csv"
        )
    else:
        st.warning("⚠️ Nenhuma NFe encontrada.")
        st.info("💡 Use a página **📤 Upload** para processar arquivos XML.")
        
except Exception as e:
    st.error(f"❌ Erro ao buscar dados: {str(e)}")
