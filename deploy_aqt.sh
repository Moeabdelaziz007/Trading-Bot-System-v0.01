#!/bin/bash

# AQT Oracle Deployment Script
echo "🚀 Starting AQT MCP Server Deployment..."

# 1. Install Dependencies
sudo apt update && sudo apt install -y python3-pip python3-venv git

# 2. Setup Directory
mkdir -p ~/aqt-mcp
cd ~/aqt-mcp

# 3. Create Python Venv
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# 4. Install Python Libs
pip install fastmcp uvicorn websockets cryptography

# 5. Setup Server File (mcp_server.py)
# Check if we are running from the repo and copy the file
if [ -f "$(pwd)/../../connector/mcp_server.py" ]; then
    echo "Using repo version of mcp_server.py"
    cp "$(pwd)/../../connector/mcp_server.py" mcp_server.py
elif [ -f "mcp_server.py" ]; then
    echo "Using existing mcp_server.py"
else
    echo "⚠️ Warning: Source mcp_server.py not found. Creating placeholder."
    cat <<EOPY > mcp_server.py
from mcp.server.fastmcp import FastMCP
import uvicorn
import os

mcp = FastMCP("AlphaQuanTopology (AQT)")

@mcp.tool()
def get_status() -> dict:
    return {"status": "AQT Cloud Engine Online", "location": "Oracle Cloud", "warning": "Placeholder Server"}

if __name__ == "__main__":
    mcp.run(transport="sse", sse_path="/mcp", host="0.0.0.0", port=8766)
EOPY
fi

# 6. Install Cloudflare Tunnel
if ! command -v cloudflared &> /dev/null; then
    curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
    sudo dpkg -i cloudflared.deb
    rm cloudflared.deb
fi

# 7. Create Systemd Service
sudo bash -c 'cat <<EOS > /etc/systemd/system/aqt-mcp.service
[Unit]
Description=AQT MCP Server
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/aqt-mcp
ExecStart=/home/ubuntu/aqt-mcp/venv/bin/python /home/ubuntu/aqt-mcp/mcp_server.py
Restart=always
Environment=PYTHONUNBUFFERED=1
Environment=MCP_PORT=8766
Environment=MCP_HOST=0.0.0.0

[Install]
WantedBy=multi-user.target
EOS'

# 8. Start MCP Service
sudo systemctl daemon-reload
sudo systemctl enable aqt-mcp
sudo systemctl restart aqt-mcp

echo "✅ MCP Deployment Complete (Local Port 8766)"
echo "⚠️ NEXT STEP MANUALLY: Run 'sudo cloudflared tunnel login' then create your tunnel."
