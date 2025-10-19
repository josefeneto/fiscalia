# ==================================================
# FISCALIA - Dockerfile Otimizado para Railway
# ==================================================

FROM python:3.11-slim

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
# (gcc/g++ necessários para compilar lxml e outras libs)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro (cache de Docker layers)
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Copiar e dar permissão ao script de start
RUN chmod +x start.sh

# Criar estrutura de diretórios
RUN mkdir -p \
    arquivos/entrados \
    arquivos/processados \
    arquivos/rejeitados \
    data/database \
    temp

# Expor porta padrão (Railway sobrescreve via $PORT)
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8501}/_stcore/health || exit 1

# Comando de inicialização
CMD ["./start.sh"]
