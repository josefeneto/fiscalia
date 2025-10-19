#!/bin/bash
# ============================================
# FISCALIA - Script de Inicialização Railway
# ============================================

set -e  # Para se houver erro

echo "🚀 FISCALIA - Iniciando..."

# ==================== VERIFICAR PORT ====================
if [ -z "$PORT" ]; then
    export PORT=8501
    echo "⚠️  PORT não definida, usando padrão: $PORT"
else
    echo "✅ PORT detectada: $PORT"
fi

# ==================== VERIFICAR AMBIENTE ====================
if [ ! -z "$RAILWAY_ENVIRONMENT" ]; then
    echo "🚂 Ambiente Railway: $RAILWAY_ENVIRONMENT"
    export ENVIRONMENT="production"
else
    echo "💻 Ambiente Local"
    export ENVIRONMENT="development"
fi

# ==================== VERIFICAR VOLUME ====================
if [ ! -z "$RAILWAY_VOLUME_MOUNT_PATH" ]; then
    echo "💾 Volume Railway montado em: $RAILWAY_VOLUME_MOUNT_PATH"
    DATA_DIR="$RAILWAY_VOLUME_MOUNT_PATH"
else
    echo "📁 Usando diretório local para dados"
    DATA_DIR="/data"
fi

# ==================== CRIAR DIRETÓRIOS ====================
echo "📁 Criando estrutura de diretórios..."
mkdir -p "$DATA_DIR/arquivos/entrados"
mkdir -p "$DATA_DIR/arquivos/processados"
mkdir -p "$DATA_DIR/arquivos/rejeitados"
mkdir -p "$DATA_DIR/temp"
mkdir -p "$DATA_DIR/database"
echo "✅ Diretórios criados/verificados"

# ==================== VERIFICAR API KEYS ====================
if [ -z "$GROQ_API_KEY" ] && [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ ERRO: Nenhuma API key configurada!"
    echo "   Configure GROQ_API_KEY ou OPENAI_API_KEY no Railway"
    exit 1
fi

if [ ! -z "$GROQ_API_KEY" ]; then
    echo "✅ Groq API key detectada"
fi

if [ ! -z "$OPENAI_API_KEY" ]; then
    echo "✅ OpenAI API key detectada"
fi

# ==================== VERIFICAR DATABASE ====================
if [ ! -z "$DATABASE_URL" ]; then
    echo "✅ PostgreSQL configurado"
else
    echo "ℹ️  Usando SQLite (PostgreSQL não configurado)"
fi

# ==================== DETECTAR FICHEIRO PRINCIPAL ====================
echo "🔍 Procurando ficheiro principal..."

# Fiscalia usa streamlit_app/app.py
if [ -f "streamlit_app/app.py" ]; then
    MAIN_FILE="streamlit_app/app.py"
    echo "✅ Ficheiro principal: $MAIN_FILE"
elif [ -f "app.py" ]; then
    MAIN_FILE="app.py"
    echo "✅ Ficheiro principal: $MAIN_FILE"
elif [ -f "main.py" ]; then
    MAIN_FILE="main.py"
    echo "✅ Ficheiro principal: $MAIN_FILE"
else
    echo "❌ ERRO: Ficheiro principal não encontrado!"
    echo ""
    echo "📂 Estrutura de diretórios:"
    ls -la
    echo ""
    echo "📂 Conteúdo de streamlit_app/ (se existir):"
    ls -la streamlit_app/ 2>/dev/null || echo "   (diretório não existe)"
    exit 1
fi

# ==================== INICIAR STREAMLIT ====================
echo ""
echo "======================================"
echo "🎯 Iniciando Streamlit na porta $PORT"
echo "======================================"
echo ""

exec streamlit run $MAIN_FILE \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.serverAddress=0.0.0.0 \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false \
    --logger.level=info
