#!/bin/bash
# run.sh — стартиране на DEX Trading Platform
# Работи с .env, Python виртуално окръжение и multi-module backend

set -e  # Спира при първата грешка
set -o pipefail

echo "==============================="
echo "DEX Trading Platform Startup"
echo "==============================="

# ----------------------------
# 1. Зареждане на .env
# ----------------------------
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Please copy .env.example to .env and fill in keys."
    exit 1
fi
export $(grep -v '^#' .env | xargs)
echo "✅ Loaded environment variables from .env"

# ----------------------------
# 2. Създаване / активиране на виртуално Python окръжение
# ----------------------------
VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "⚡ Creating virtual environment..."
    python3 -m venv $VENV_DIR
fi

source $VENV_DIR/bin/activate
echo "✅ Virtual environment activated"

# ----------------------------
# 3. Инсталиране на зависимости
# ----------------------------
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"

# ----------------------------
# 4. Създаване на директории за данни и логове
# ----------------------------
mkdir -p data logs
echo "✅ Data and log directories created"

# ----------------------------
# 5. Стартиране на Core Engine
# ----------------------------
echo "🚀 Starting Core Engine..."
nohup python core/main.py > logs/core.log 2>&1 &

# ----------------------------
# 6. Стартиране на Shadow / Research Engine (по избор)
# ----------------------------
if [ "$SHADOW_TRADING" = "true" ]; then
    echo "🔬 Starting Shadow/Research Engine..."
    nohup python research/shadow_engine.py > logs/research.log 2>&1 &
fi

# ----------------------------
# 7. Стартиране на Monitoring / Prometheus (ако е включено)
# ----------------------------
if [ "$PROMETHEUS_ENABLED" = "true" ]; then
    echo "📊 Starting Prometheus metrics server on port $PROMETHEUS_PORT..."
    nohup python monitoring/prometheus_server.py > logs/prometheus.log 2>&1 &
fi

# ----------------------------
# 8. Финално съобщение
# ----------------------------
echo "==============================="
echo "✅ All modules launched successfully!"
echo "✅ Logs: logs/"
echo "Use 'ps aux | grep python' to see running processes."
echo "==============================="
