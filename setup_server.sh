#!/bin/bash

set -e

# ==============================
# CONFIGURATION
# ==============================

PROJECT_REPO="https://github.com/sidhant223/complianceAI.git"
PROJECT_DIR="/root/complianceAI"
MODEL_NAME="qwen2.5:7b"
APP_PORT="8000"

echo "======================================"
echo " ComplianceAI Server Setup Starting"
echo " Model: $MODEL_NAME"
echo "======================================"

echo "[1/11] Updating server..."
apt update && apt upgrade -y

echo "[2/11] Installing system packages..."
apt install -y python3 python3-pip python3-venv git curl unzip ufw

echo "[3/11] Installing Ollama..."
if ! command -v ollama >/dev/null 2>&1; then
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "Ollama already installed."
fi

echo "[4/11] Starting Ollama service..."
systemctl enable ollama || true
systemctl restart ollama || true
sleep 8

echo "[5/11] Checking Ollama API..."
if curl -s http://127.0.0.1:11434/api/tags >/dev/null; then
    echo "Ollama API is reachable."
else
    echo "Ollama service not reachable. Starting manually..."
    nohup ollama serve > /tmp/ollama.log 2>&1 &
    sleep 10
fi

echo "[6/11] Pulling Ollama model: $MODEL_NAME"
ollama pull "$MODEL_NAME"

echo "[7/11] Cloning or updating project..."
if [ ! -d "$PROJECT_DIR" ]; then
    git clone "$PROJECT_REPO" "$PROJECT_DIR"
else
    cd "$PROJECT_DIR"
    git pull || true
fi

cd "$PROJECT_DIR"

echo "[8/11] Creating Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "[9/11] Installing Python dependencies..."
pip install --upgrade pip

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    pip install fastapi uvicorn python-multipart requests reportlab pymupdf
fi

echo "[10/11] Setting Ollama model in src/ollama_client.py..."
if [ -f "src/ollama_client.py" ]; then
    sed -i "s/^DEFAULT_MODEL = .*/DEFAULT_MODEL = \"$MODEL_NAME\"/" src/ollama_client.py || true
else
    echo "WARNING: src/ollama_client.py not found."
fi

echo "[11/11] Creating FastAPI systemd service..."

cat > /etc/systemd/system/complianceai.service <<EOF
[Unit]
Description=ComplianceAI FastAPI Backend
After=network.target ollama.service

[Service]
User=root
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/.venv/bin/uvicorn app:app --host 0.0.0.0 --port $APP_PORT
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable complianceai
systemctl restart complianceai

echo "Configuring firewall..."
ufw allow 22
ufw allow $APP_PORT
ufw --force enable

echo "======================================"
echo " Setup Complete"
echo "======================================"
echo "Project directory: $PROJECT_DIR"
echo "Model: $MODEL_NAME"
echo "FastAPI Docs:"
echo "http://SERVER_IP:$APP_PORT/docs"
echo ""
echo "Useful commands:"
echo "systemctl status complianceai"
echo "journalctl -u complianceai -f"
echo "ollama list"
echo "ollama ps"
echo "curl http://127.0.0.1:11434/api/tags"
echo "======================================"