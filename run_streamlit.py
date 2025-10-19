"""
Script para rodar Streamlit com browser automático
"""

import subprocess
import sys
import webbrowser
import time
from pathlib import Path

def main():
    print("=" * 70)
    print("🚀 Iniciando Fiscalia - Sistema de Processamento de NFe")
    print("=" * 70)
    
    app_path = Path(__file__).parent / "streamlit_app" / "app.py"
    print(f"\n📂 App: {app_path}")
    
    print("\n🌐 Servidor Streamlit iniciando...")
    print("   → Acesse: http://localhost:8501")
    print("\⚠️  Pressione Ctrl+C para encerrar\n")
    print("=" * 70)
    
    # NOVO: Abrir browser automaticamente após 2 segundos
    def open_browser():
        time.sleep(2)
        webbrowser.open('http://localhost:8501')
    
    import threading
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Rodar Streamlit
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        str(app_path),
        "--server.port=8501",
        "--server.address=localhost"
    ])

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("✅ Servidor Streamlit encerrado com sucesso!")
        print("=" * 70)
