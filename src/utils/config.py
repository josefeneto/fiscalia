# src/utils/config.py - ARQUIVO COMPLETO CORRIGIDO

"""
Configurações do sistema Fiscalia
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from dotenv import load_dotenv

# Carregar .env
load_dotenv()


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Paths
    project_root: Path = Path(__file__).parent.parent.parent
    data_dir: Path = project_root / "data"
    arquivos_dir: Path = project_root / "arquivos"
    
    # Database
    database_path: Path = data_dir / "bd_fiscalia.db"
    
    # Pastas de arquivos
    pasta_entrados: Path = arquivos_dir / "entrados"
    pasta_processados: Path = arquivos_dir / "processados"
    pasta_rejeitados: Path = arquivos_dir / "rejeitados"
    
    # LLM Configuration
    llm_provider: str = "groq"
    groq_api_key: Optional[str] = None
    groq_model: str = "groq/llama-3.3-70b-versatile"
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[Path] = None
    
    # Configuração do Pydantic v2
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # ← IMPORTANTE: Ignora campos extras do .env
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Carregar de variáveis de ambiente (sobrescreve defaults)
        self.llm_provider = os.getenv("LLM_PROVIDER", "groq").lower()
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.groq_model = os.getenv("GROQ_MODEL", "groq/llama-3.3-70b-versatile")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        
        # Criar diretórios se não existirem
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.arquivos_dir.mkdir(parents=True, exist_ok=True)
        self.pasta_entrados.mkdir(parents=True, exist_ok=True)
        self.pasta_processados.mkdir(parents=True, exist_ok=True)
        self.pasta_rejeitados.mkdir(parents=True, exist_ok=True)


# Singleton
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Retorna instância única das configurações"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


if __name__ == "__main__":
    """Teste standalone"""
    print("=== Teste de Configurações ===\n")
    
    settings = get_settings()
    
    print(f"✓ Project Root: {settings.project_root}")
    print(f"✓ Data Dir: {settings.data_dir}")
    print(f"✓ Database: {settings.database_path}")
    print(f"✓ Arquivos Dir: {settings.arquivos_dir}")
    print(f"✓ Pasta Entrados: {settings.pasta_entrados}")
    print(f"✓ Pasta Processados: {settings.pasta_processados}")
    print(f"✓ Pasta Rejeitados: {settings.pasta_rejeitados}")
    print(f"\n✓ LLM Provider: {settings.llm_provider}")
    print(f"✓ Groq Model: {settings.groq_model}")
    print(f"✓ OpenAI Model: {settings.openai_model}")
    
    print("\n✅ Configurações carregadas com sucesso!")
