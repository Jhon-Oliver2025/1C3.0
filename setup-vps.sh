#!/bin/bash
# Script de configuração inicial do VPS Hetzner
# Para Ubuntu 22.04 LTS

echo "🚀 Iniciando configuração do VPS para Ecossistema Crypto..."

# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências essenciais
sudo apt install -y curl wget git htop nano ufw fail2ban

# Configurar firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

echo "✅ Configuração básica do VPS concluída!"
echo "🔄 Reinicie o sistema: sudo reboot"