#!/bin/bash
# 一键部署脚本 Deploy Script
set -e

APP_NAME="novel-writing-workbench"
INSTALL_DIR="/opt/${APP_NAME}"
DATA_DIR="/var/lib/workbench/data"
SERVICE_FILE="deploy/workbench.service"

echo "🚀 部署 ${APP_NAME} v3.0"

# 1. Create directories
sudo mkdir -p "${INSTALL_DIR}" "${DATA_DIR}/chapters"

# 2. Copy files
sudo cp -r server.py static/ tools/ "${INSTALL_DIR}/"
sudo cp deploy/nginx.conf /etc/nginx/sites-available/${APP_NAME}.conf 2>/dev/null || true

# 3. Install Python dependencies
pip3 install fastapi uvicorn --quiet

# 4. Install systemd service
sudo cp "${SERVICE_FILE}" /etc/systemd/system/${APP_NAME}.service
sudo systemctl daemon-reload
sudo systemctl enable ${APP_NAME}
sudo systemctl restart ${APP_NAME}

# 5. (Optional) Link modules from novel-creation-omnibus
if [ -d "/home/agentuser/.hermes/skills/novel-creation-omnibus/references/modules" ]; then
    ln -sf "/home/agentuser/.hermes/skills/novel-creation-omnibus/references/modules" "${INSTALL_DIR}/modules"
    echo "📚 Modules linked"
fi

echo ""
echo "✅ 部署完成!"
echo "   运行: sudo systemctl status ${APP_NAME}"
echo "   访问: http://localhost:8080"
echo "   日志: sudo journalctl -u ${APP_NAME} -f"
