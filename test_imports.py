# test_imports.py - CRIAR NA RAIZ (teste simples)

"""Teste mínimo de imports"""

import sys
from pathlib import Path

# Adicionar src ao path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

print(f"✓ Python path configurado: {src_path}\n")

# Teste 1: Utils
try:
    from utils.config import get_settings
    print("✅ utils.config importado")
    settings = get_settings()
    print(f"   Database: {settings.database_path}")
except Exception as e:
    print(f"❌ Erro em utils.config: {e}")
    import traceback
    traceback.print_exc()

# Teste 2: Logger
try:
    from utils.logger import setup_logger
    print("✅ utils.logger importado")
    logger = setup_logger("test")
    print("   Logger criado")
except Exception as e:
    print(f"❌ Erro em utils.logger: {e}")
    import traceback
    traceback.print_exc()

# Teste 3: Database
try:
    from database.db_manager import DatabaseManager
    print("✅ database.db_manager importado")
    db = DatabaseManager()
    print(f"   Total docs: {db.count_documents()}")
except Exception as e:
    print(f"❌ Erro em database: {e}")
    import traceback
    traceback.print_exc()

# Teste 4: LLM Config
try:
    from utils.llm_config import verify_llm_connection
    print("✅ utils.llm_config importado")
    verify_llm_connection()
except Exception as e:
    print(f"❌ Erro em llm_config: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Teste de imports concluído!")
