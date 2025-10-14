"""
Sistema de Logging do Fiscalia
Configuração centralizada de logs usando Loguru
"""
import sys
from pathlib import Path
from loguru import logger
from .config import settings, BASE_DIR

# Remover handler padrão
logger.remove()

# Configurar diretório de logs
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# ==================== Console Handler ====================
# Log colorido no console para desenvolvimento
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=settings.log_level,
    colorize=True,
)

# ==================== File Handlers ====================
# Log geral - todos os níveis
logger.add(
    LOGS_DIR / "fiscalia_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
    rotation="00:00",  # Novo arquivo à meia-noite
    retention="30 days",  # Manter logs por 30 dias
    compression="zip",  # Comprimir logs antigos
    encoding="utf-8",
)

# Log de erros - apenas erros e críticos
logger.add(
    LOGS_DIR / "fiscalia_errors_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="ERROR",
    rotation="00:00",
    retention="90 days",  # Manter logs de erro por mais tempo
    compression="zip",
    encoding="utf-8",
)

# Log de processamento - específico para rastreamento de documentos
logger.add(
    LOGS_DIR / "processamento_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {extra[doc_id]} | {message}",
    level="INFO",
    rotation="00:00",
    retention="90 days",
    compression="zip",
    encoding="utf-8",
    filter=lambda record: "doc_id" in record["extra"],
)


def get_logger(name: str):
    """
    Retorna um logger configurado com o nome do módulo
    
    Args:
        name: Nome do módulo (geralmente __name__)
    
    Returns:
        Logger configurado
    
    Example:
        >>> from src.utils.logger import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Mensagem de log")
    """
    return logger.bind(module=name)


def log_document_processing(doc_id: str, message: str, level: str = "INFO"):
    """
    Log específico para processamento de documentos
    
    Args:
        doc_id: ID do documento sendo processado
        message: Mensagem a ser logada
        level: Nível do log (INFO, WARNING, ERROR)
    """
    doc_logger = logger.bind(doc_id=doc_id)
    
    if level == "INFO":
        doc_logger.info(message)
    elif level == "WARNING":
        doc_logger.warning(message)
    elif level == "ERROR":
        doc_logger.error(message)
    else:
        doc_logger.debug(message)


def log_crew_activity(crew_name: str, agent_name: str, task_name: str, message: str):
    """
    Log específico para atividades do CrewAI
    
    Args:
        crew_name: Nome da crew
        agent_name: Nome do agente
        task_name: Nome da task
        message: Mensagem a ser logada
    """
    logger.bind(
        crew=crew_name,
        agent=agent_name,
        task=task_name
    ).info(message)


# Exportar para facilitar importação
__all__ = [
    "logger",
    "get_logger",
    "log_document_processing",
    "log_crew_activity"
]
