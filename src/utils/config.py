"""
Configurações do sistema Fiscalia
Gerencia variáveis de ambiente e configurações globais
"""

from pathlib import Path
from typing import Optional
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações do sistema carregadas do arquivo .env"""
    
    # ========================================================================
    # LLM Configuration
    # ========================================================================
    
    # Provider selection
    LLM_PROVIDER: str = "groq"  # groq ou openai
    
    # Groq settings
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "groq/llama-3.3-70b-versatile"
    
    # OpenAI settings
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # ========================================================================
    # Database Configuration
    # ========================================================================
    
    # Database type
    DB_TYPE: str = "sqlite"  # sqlite ou postgresql
    
    # SQLite settings
    SQLITE_DB_PATH: str = "data/bd_fiscalia.db"
    
    # PostgreSQL settings (para uso futuro no Railway)
    POSTGRES_HOST: Optional[str] = None
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    
    # ========================================================================
    # Application Configuration
    # ========================================================================
    
    # Logging
    LOG_LEVEL: str = "WARNING"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FILE: str = "fiscalia.log"
    
    # Paths
    BASE_PATH: str = "."
    ARQUIVOS_PATH: str = "arquivos"
    DATA_PATH: str = "data"
    
    # Railway volume mount (para persistência no Railway)
    RAILWAY_VOLUME_MOUNT_PATH: Optional[str] = None
    
    # ========================================================================
    # Processing Configuration
    # ========================================================================
    
    # Limites de processamento
    MAX_FILE_SIZE_MB: int = 10
    BATCH_SIZE: int = 100
    
    # Timeouts
    PROCESSING_TIMEOUT_SECONDS: int = 300
    
    # ========================================================================
    # Pydantic Configuration
    # ========================================================================
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignora variáveis extras no .env
    )
    
    # ========================================================================
    # Computed Properties
    # ========================================================================
    
    @property
    def database_url(self) -> str:
        """
        Retorna URL de conexão do banco de dados
        
        Returns:
            String de conexão SQLAlchemy
        """
        if self.DB_TYPE == "sqlite":
            # Ajusta path se estiver no Railway
            if self.RAILWAY_VOLUME_MOUNT_PATH:
                db_path = Path(self.RAILWAY_VOLUME_MOUNT_PATH) / "bd_fiscalia.db"
            else:
                db_path = Path(self.SQLITE_DB_PATH)
            
            return f"sqlite:///{db_path}"
        
        elif self.DB_TYPE == "postgresql":
            if not all([self.POSTGRES_HOST, self.POSTGRES_USER, 
                       self.POSTGRES_PASSWORD, self.POSTGRES_DB]):
                raise ValueError("PostgreSQL configurado mas variáveis incompletas")
            
            return (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        
        else:
            raise ValueError(f"DB_TYPE não suportado: {self.DB_TYPE}")
    
    @property
    def llm_config(self) -> dict:
        """
        Retorna configuração da LLM baseada no provider
        
        Returns:
            Dicionário com configuração da LLM
        """
        if self.LLM_PROVIDER == "groq":
            return {
                "provider": "groq",
                "api_key": self.GROQ_API_KEY,
                "model": self.GROQ_MODEL,
            }
        elif self.LLM_PROVIDER == "openai":
            return {
                "provider": "openai",
                "api_key": self.OPENAI_API_KEY,
                "model": self.OPENAI_MODEL,
            }
        else:
            raise ValueError(f"LLM_PROVIDER não suportado: {self.LLM_PROVIDER}")
    
    def get_full_path(self, relative_path: str) -> Path:
        """
        Retorna caminho completo baseado no BASE_PATH
        
        Args:
            relative_path: Caminho relativo
            
        Returns:
            Path absoluto
        """
        return Path(self.BASE_PATH) / relative_path
    
    def validate_llm_config(self) -> bool:
        """
        Valida se configuração da LLM está completa
        
        Returns:
            True se configuração válida
        """
        if self.LLM_PROVIDER == "groq":
            return bool(self.GROQ_API_KEY)
        elif self.LLM_PROVIDER == "openai":
            return bool(self.OPENAI_API_KEY)
        return False


@lru_cache()
def get_settings() -> Settings:
    """
    Retorna instância única de Settings (cached)
    
    Returns:
        Instância de Settings
    """
    return Settings()


# ========================================================================
# Funções auxiliares
# ========================================================================

def get_database_path() -> Path:
    """
    Retorna caminho do banco de dados SQLite
    
    Returns:
        Path do banco de dados
    """
    settings = get_settings()
    
    if settings.RAILWAY_VOLUME_MOUNT_PATH:
        return Path(settings.RAILWAY_VOLUME_MOUNT_PATH) / "bd_fiscalia.db"
    else:
        return Path(settings.SQLITE_DB_PATH)


def get_arquivos_path() -> Path:
    """
    Retorna caminho da pasta de arquivos
    
    Returns:
        Path da pasta arquivos
    """
    settings = get_settings()
    return Path(settings.ARQUIVOS_PATH)


def is_railway_environment() -> bool:
    """
    Verifica se está rodando no Railway
    
    Returns:
        True se no Railway
    """
    settings = get_settings()
    return settings.RAILWAY_VOLUME_MOUNT_PATH is not None


# ========================================================================
# Exportações
# ========================================================================

__all__ = [
    'Settings',
    'get_settings',
    'get_database_path',
    'get_arquivos_path',
    'is_railway_environment',
]
