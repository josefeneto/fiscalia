"""
Configurações do Sistema Fiscalia
Usa valores padrão inteligentes - usuário só configura o essencial
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar .env se existir (desenvolvimento local)
load_dotenv()


class Settings:
    """Configurações centralizadas com defaults inteligentes"""
    
    def __init__(self):
        # ==================== DETECÇÃO AUTOMÁTICA DE AMBIENTE ====================
        self.is_railway = os.getenv('RAILWAY_ENVIRONMENT') is not None
        self.is_production = self.is_railway or os.getenv('ENVIRONMENT') == 'production'
        
        # ==================== LLM APIs (OBRIGATÓRIO) ====================
        # Usuário deve configurar PELO MENOS uma destas
        self.groq_api_key = os.getenv('GROQ_API_KEY', '')
        self.openai_api_key = os.getenv('OPENAI_API_KEY', '')
        
        # Provider padrão: usa o que estiver configurado
        if self.openai_api_key:
            self.llm_provider = 'openai'
            self.llm_model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        elif self.groq_api_key:
            self.llm_provider = 'groq'
            self.llm_model = os.getenv('GROQ_MODEL', 'groq/llama-3.3-70b-versatile')
        else:
            self.llm_provider = None
            self.llm_model = None
        
        # ==================== DATABASE (AUTO-DETECTA) ====================
        # Railway: usa PostgreSQL se DATABASE_URL estiver definida
        # Local: usa SQLite sempre
        self.database_url = os.getenv('DATABASE_URL')
        
        if self.database_url:
            # PostgreSQL (Railway ou explícito)
            self.db_type = 'postgresql'
        else:
            # SQLite (padrão)
            self.db_type = 'sqlite'
            
            # Path do SQLite
            if self.is_railway:
                # Railway: usar volume montado
                volume_path = os.getenv('RAILWAY_VOLUME_MOUNT_PATH', '/data')
                self.database_path = Path(volume_path) / 'bd_fiscalia.db'
            else:
                # Local: pasta data/
                self.database_path = Path('data') / 'bd_fiscalia.db'
                self.database_path.parent.mkdir(parents=True, exist_ok=True)
        
        # ==================== PATHS DE ARQUIVOS (AUTO-CONFIGURA) ====================
        # Railway: usar volume se disponível
        if self.is_railway:
            volume_path = os.getenv('RAILWAY_VOLUME_MOUNT_PATH', '/data')
            base_path = Path(volume_path) / 'arquivos'
        else:
            base_path = Path('arquivos')
        
        # Criar estrutura de pastas
        self.pasta_base = base_path
        self.pasta_entrados = base_path / 'entrados'
        self.pasta_processados = base_path / 'processados'
        self.pasta_rejeitados = base_path / 'rejeitados'
        
        # Criar pastas se não existirem
        for pasta in [self.pasta_entrados, self.pasta_processados, self.pasta_rejeitados]:
            pasta.mkdir(parents=True, exist_ok=True)
        
        # ==================== PROCESSAMENTO (DEFAULTS) ====================
        self.max_files_per_batch = int(os.getenv('MAX_FILES_PER_BATCH', '100'))
        self.max_file_size_mb = int(os.getenv('MAX_FILE_SIZE_MB', '50'))
        self.processing_timeout = int(os.getenv('PROCESSING_TIMEOUT', '600'))
        
        # ==================== STREAMLIT (DEFAULTS) ====================
        self.streamlit_port = int(os.getenv('STREAMLIT_SERVER_PORT', '8501'))
        self.streamlit_address = os.getenv('STREAMLIT_SERVER_ADDRESS', 
                                           '0.0.0.0' if self.is_production else 'localhost')
        
        # ==================== LOGGING (AUTO) ====================
        self.log_level = os.getenv('LOG_LEVEL', 
                                   'INFO' if self.is_production else 'DEBUG')
        
        # ==================== CREWAI (DEFAULTS) ====================
        self.crewai_verbose = os.getenv('CREWAI_VERBOSE', 'False').lower() == 'true'
        
        # Desabilitar telemetria do CrewAI
        os.environ['CREWAI_TELEMETRY_OPT_OUT'] = 'true'
    
    def validate(self) -> tuple[bool, str]:
        """
        Valida configuração mínima
        
        Returns:
            (is_valid, error_message)
        """
        errors = []
        
        # Verificar se tem pelo menos uma API key
        if not self.groq_api_key and not self.openai_api_key:
            errors.append(
                "⚠️  Nenhuma API key configurada!\n"
                "   Configure GROQ_API_KEY ou OPENAI_API_KEY"
            )
        
        # Avisos (não bloqueiam)
        warnings = []
        
        if self.is_railway and not self.database_url:
            warnings.append(
                "💡 Dica: Configure DATABASE_URL para usar PostgreSQL no Railway\n"
                "   (usando SQLite que não persiste entre deploys)"
            )
        
        if errors:
            return False, "\n".join(errors)
        
        if warnings:
            print("\n".join(warnings))
        
        return True, ""
    
    def get_summary(self) -> str:
        """Retorna resumo da configuração atual"""
        return f"""
╔════════════════════════════════════════════════════════════╗
║           CONFIGURAÇÃO DO SISTEMA FISCALIA                 ║
╚════════════════════════════════════════════════════════════╝

🌍 Ambiente: {'Railway/Produção' if self.is_railway else 'Desenvolvimento Local'}

🤖 LLM Provider: {self.llm_provider or '❌ NÃO CONFIGURADO'}
   Modelo: {self.llm_model or 'N/A'}

💾 Database: {self.db_type.upper()}
   {'URL: ' + self.database_url[:50] + '...' if self.database_url else 'Path: ' + str(self.database_path)}

📁 Arquivos Base: {self.pasta_base}

📊 Processamento:
   - Max arquivos/batch: {self.max_files_per_batch}
   - Max tamanho: {self.max_file_size_mb} MB
   - Timeout: {self.processing_timeout}s

🌐 Streamlit: {self.streamlit_address}:{self.streamlit_port}

═══════════════════════════════════════════════════════════
"""


# Singleton global
_settings = None


def get_settings() -> Settings:
    """Retorna instância única das configurações"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def validate_settings() -> bool:
    """
    Valida configurações e retorna True se OK
    Imprime erros se houver problemas
    """
    settings = get_settings()
    is_valid, error_msg = settings.validate()
    
    if not is_valid:
        print("\n❌ ERRO DE CONFIGURAÇÃO:")
        print(error_msg)
        print("\n💡 Como corrigir:")
        print("   1. Crie um arquivo .env na raiz do projeto")
        print("   2. Adicione pelo menos uma das seguintes linhas:")
        print("      GROQ_API_KEY=sua_chave_aqui")
        print("      OPENAI_API_KEY=sua_chave_aqui")
        return False
    
    return True


# Para facilitar imports
__all__ = ['Settings', 'get_settings', 'validate_settings']


if __name__ == "__main__":
    # Teste da configuração
    settings = get_settings()
    print(settings.get_summary())
    
    is_valid, msg = settings.validate()
    if not is_valid:
        print("\n❌ ERROS:")
        print(msg)
    else:
        print("✅ Configuração válida!")