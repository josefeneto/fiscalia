"""
Script de teste para validar configuração do ambiente
Execute: python test_setup.py
"""
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.config import settings, BASE_DIR
from src.utils.logger import get_logger

logger = get_logger(__name__)


def test_environment():
    """Testa configuração do ambiente"""
    print("\n" + "="*60)
    print("🔍 FISCALIA - Teste de Configuração do Ambiente")
    print("="*60 + "\n")
    
    # Testar configurações
    print("📋 Configurações Carregadas:")
    print(f"   • Ambiente: {settings.environment}")
    print(f"   • LLM Provider: {settings.llm_provider}")
    print(f"   • Modelo: {settings.groq_model if settings.llm_provider == 'groq' else settings.openai_model}")
    print(f"   • Database: {settings.db_type}")
    print(f"   • Log Level: {settings.log_level}")
    
    # Testar paths
    print(f"\n📁 Diretórios:")
    print(f"   • Base: {BASE_DIR}")
    print(f"   • Entrados: {settings.arquivos_entrados}")
    print(f"   • Processados: {settings.arquivos_processados}")
    print(f"   • Rejeitados: {settings.arquivos_rejeitados}")
    print(f"   • Database: {settings.get_database_path()}")
    
    # Validar configuração
    print(f"\n✅ Validação:")
    is_valid, errors = settings.validate_config()
    
    if is_valid:
        print("   ✓ Todas as configurações estão corretas!")
    else:
        print("   ✗ Erros encontrados:")
        for error in errors:
            print(f"     - {error}")
    
    # Testar diretórios
    print(f"\n📂 Verificação de Diretórios:")
    directories = [
        settings.arquivos_entrados,
        settings.arquivos_processados,
        settings.arquivos_rejeitados,
        BASE_DIR / "data",
        BASE_DIR / "logs"
    ]
    
    for directory in directories:
        exists = directory.exists()
        status = "✓" if exists else "✗"
        print(f"   {status} {directory}")
    
    # Testar logger
    print(f"\n📝 Teste de Logger:")
    try:
        logger.info("Teste de log INFO - OK")
        logger.warning("Teste de log WARNING - OK")
        logger.error("Teste de log ERROR - OK")
        print("   ✓ Sistema de logging funcionando!")
    except Exception as e:
        print(f"   ✗ Erro no sistema de logging: {e}")
    
    # Testar imports principais
    print(f"\n📦 Teste de Importações:")
    try:
        import crewai
        print(f"   ✓ CrewAI {crewai.__version__}")
    except ImportError as e:
        print(f"   ✗ CrewAI: {e}")
    
    try:
        import streamlit
        print(f"   ✓ Streamlit {streamlit.__version__}")
    except ImportError as e:
        print(f"   ✗ Streamlit: {e}")
    
    try:
        import sqlalchemy
        print(f"   ✓ SQLAlchemy {sqlalchemy.__version__}")
    except ImportError as e:
        print(f"   ✗ SQLAlchemy: {e}")
    
    try:
        import lxml
        print(f"   ✓ lxml {lxml.__version__}")
    except ImportError as e:
        print(f"   ✗ lxml: {e}")
    
    # Testar LLM (sem fazer chamada real)
    print(f"\n🤖 Configuração LLM:")
    llm_config = settings.get_llm_config()
    api_key = llm_config['api_key']
    if api_key and len(api_key) > 10:
        masked_key = api_key[:8] + "..." + api_key[-4:]
        print(f"   ✓ API Key configurada: {masked_key}")
        print(f"   ✓ Provider: {llm_config['provider']}")
        print(f"   ✓ Modelo: {llm_config['model']}")
    else:
        print(f"   ✗ API Key não configurada para {llm_config['provider']}")
    
    print("\n" + "="*60)
    if is_valid:
        print("✅ Ambiente configurado corretamente!")
    else:
        print("⚠️  Corrija os erros acima antes de continuar")
    print("="*60 + "\n")
    
    return is_valid


if __name__ == "__main__":
    success = test_environment()
    sys.exit(0 if success else 1)
