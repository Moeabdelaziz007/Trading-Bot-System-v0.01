#!/bin/bash
set -e

# prepare_oracle_server.sh
# Purpose: Prepare a fresh Oracle Cloud ARM instance (Ubuntu or Oracle Linux) for Python/Docker deployment.
# Actions: Installs Docker/Compose, Configures Firewall (80, 443, 22).
# Usage: sudo ./prepare_oracle_server.sh

# Check for sudo
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (sudo)"
  exit 1
fi

echo ">> Starting Oracle Cloud Server Preparation..."

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    echo ">> Detected OS: $OS"
else
    echo ">> Unknown OS. This script supports Ubuntu and Oracle Linux."
    exit 1
fi

# ==========================================
# 1. Install Docker & Docker Compose
# ==========================================
echo ">> Installing Docker and Docker Compose..."

if [[ "$OS" == *"Ubuntu"* ]]; then
    # Ubuntu
    apt-get update -y
    apt-get install -y ca-certificates curl gnupg lsb-release

    # Add Docker GPG
    mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg

    # Set up repo
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

    apt-get update -y
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

elif [[ "$OS" == *"Oracle"* ]] || [[ "$OS" == *"Red Hat"* ]] || [[ "$OS" == *"CentOS"* ]]; then
    # Oracle Linux / RHEL / CentOS
    dnf config-manager --add-repo=https://download.docker.com/linux/centos/docker-ce.repo
    dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

    # Start Docker
    systemctl start docker
    systemctl enable docker

else
    echo ">> Unsupported OS for automatic Docker install. Please install Docker manually."
    exit 1
fi

# Verify Docker
echo ">> verifying Docker installation..."
docker --version
docker compose version

# ==========================================
# 2. Configure Firewall (80, 443, 22)
# ==========================================
echo ">> Configuring Firewall..."

if command -v ufw > /dev/null; then
    # UFW (Ubuntu default)
    echo ">> Configuring UFW..."
    ufw allow 22/tcp
    ufw allow 80/tcp
    ufw allow 443/tcp
    # Enable if not enabled, but be careful not to lock out via SSH.
    # We assume standard SSH port 22.
    echo "y" | ufw enable
    ufw reload
    ufw status

elif command -v firewall-cmd > /dev/null; then
    # Firewalld (Oracle Linux default)
    echo ">> Configuring Firewalld..."
    systemctl start firewalld
    systemctl enable firewalld

    firewall-cmd --permanent --add-port=22/tcp
    firewall-cmd --permanent --add-port=80/tcp
    firewall-cmd --permanent --add-port=443/tcp
    firewall-cmd --reload
    firewall-cmd --list-all

    # Note: Oracle Cloud often uses iptables directly on top of firewalld in some images
    # Ensure netfilter persistence if needed (usually handled by firewalld)

    # Also check if iptables is running and save rules just in case
    if command -v iptables-save > /dev/null; then
        iptables -I INPUT -p tcp --dport 80 -j ACCEPT
        iptables -I INPUT -p tcp --dport 443 -j ACCEPT
        iptables-save > /etc/iptables/rules.v4 2>/dev/null || true
    fi

else
    # Fallback to pure iptables
    echo ">> Configuring iptables (fallback)..."
    iptables -A INPUT -p tcp --dport 22 -j ACCEPT
    iptables -A INPUT -p tcp --dport 80 -j ACCEPT
    iptables -A INPUT -p tcp --dport 443 -j ACCEPT
    # Save not guaranteed without helper tools, but applies to runtime
fi

echo ">> Setup Complete! Docker installed and ports 80/443/22 opened."
echo ">> You may need to log out and log back in (or use 'newgrp docker') to use docker without sudo."
