"""
Configurações do Sistema Fiscalia
Gerencia todas as variáveis de ambiente e configurações da aplicação
"""
import os
from pathlib import Path
from typing import Literal
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Carregar variáveis de ambiente
load_dotenv()

# Diretório base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Configurações da aplicação usando Pydantic"""
    
    # ==================== LLM Configuration ====================
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = os.getenv("GROQ_MODEL", "groq/llama-3.3-70b-versatile")
    
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    llm_provider: Literal["groq", "openai"] = os.getenv("LLM_PROVIDER", "groq")
    
    # ==================== Database Configuration ====================
    db_type: Literal["sqlite", "postgresql"] = os.getenv("DB_TYPE", "sqlite")
    sqlite_db_path: str = os.getenv("SQLITE_DB_PATH", "data/bd_fiscalia.db")
    database_url: str = os.getenv("DATABASE_URL", "")
    railway_volume_mount_path: str = os.getenv("RAILWAY_VOLUME_MOUNT_PATH", "/data")
    
    # ==================== Paths Configuration ====================
    arquivos_base_path: Path = Path(os.getenv("ARQUIVOS_BASE_PATH", "arquivos"))
    arquivos_entrados: Path = Path(os.getenv("ARQUIVOS_ENTRADOS", "arquivos/entrados"))
    arquivos_processados: Path = Path(os.getenv("ARQUIVOS_PROCESSADOS", "arquivos/processados"))
    arquivos_rejeitados: Path = Path(os.getenv("ARQUIVOS_REJEITADOS", "arquivos/rejeitados"))
    
    # ==================== Application Configuration ====================
    environment: Literal["development", "production"] = os.getenv("ENVIRONMENT", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    streamlit_server_port: int = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))
    streamlit_server_address: str = os.getenv("STREAMLIT_SERVER_ADDRESS", "localhost")
    
    # ==================== Processing Configuration ====================
    max_files_per_batch: int = int(os.getenv("MAX_FILES_PER_BATCH", "100"))
    max_file_size_mb: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    processing_timeout: int = int(os.getenv("PROCESSING_TIMEOUT", "300"))
    
    # ==================== Security ====================
    secret_key: str = os.getenv("SECRET_KEY", "change-this-in-production")
    
    # ==================== CrewAI Configuration ====================
    crewai_verbose: bool = os.getenv("CREWAI_VERBOSE", "True").lower() == "true"
    crewai_memory: bool = os.getenv("CREWAI_MEMORY", "True").lower() == "true"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def get_database_path(self) -> str:
        """Retorna o caminho correto do database baseado no ambiente"""
        if self.environment == "production" and self.railway_volume_mount_path:
            # Em produção no Railway, usar volume montado
            return f"{self.railway_volume_mount_path}/bd_fiscalia.db"
        else:
            # Em desenvolvimento, usar caminho local
            db_path = BASE_DIR / self.sqlite_db_path
            # Criar diretório data se não existir
            db_path.parent.mkdir(parents=True, exist_ok=True)
            return str(db_path)
    
    def get_llm_config(self) -> dict:
        """Retorna configuração do LLM baseado no provider selecionado"""
        if self.llm_provider == "groq":
            return {
                "api_key": self.groq_api_key,
                "model": self.groq_model,
                "provider": "groq"
            }
        else:
            return {
                "api_key": self.openai_api_key,
                "model": self.openai_model,
                "provider": "openai"
            }
    
    def ensure_directories(self):
        """Garante que todos os diretórios necessários existem"""
        directories = [
            self.arquivos_entrados,
            self.arquivos_processados,
            self.arquivos_rejeitados,
            BASE_DIR / "data",
            BASE_DIR / "logs"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            # Criar arquivo .gitkeep para manter diretório no Git
            gitkeep = directory / ".gitkeep"
            if not gitkeep.exists():
                gitkeep.touch()
    
    def validate_config(self) -> tuple[bool, list[str]]:
        """Valida se as configurações essenciais estão presentes"""
        errors = []
        
        # Validar API keys
        if self.llm_provider == "groq" and not self.groq_api_key:
            errors.append("GROQ_API_KEY não configurada")
        
        if self.llm_provider == "openai" and not self.openai_api_key:
            errors.append("OPENAI_API_KEY não configurada")
        
        # Validar paths
        if not self.arquivos_base_path.exists():
            errors.append(f"Diretório base de arquivos não existe: {self.arquivos_base_path}")
        
        return len(errors) == 0, errors


# Instância global de configurações
settings = Settings()

# Garantir que os diretórios existem ao importar
settings.ensure_directories()


def get_settings() -> Settings:
    """Factory function para obter instância de configurações"""
    return settings


# Exportar para facilitar importação
__all__ = ["settings", "get_settings", "Settings", "BASE_DIR"]
