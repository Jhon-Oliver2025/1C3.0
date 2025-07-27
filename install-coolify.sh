#!/bin/bash
# Script de instalação do Coolify

echo "🐳 Instalando Coolify..."

# Baixar e executar instalador do Coolify
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash

# Aguardar inicialização
echo "⏳ Aguardando Coolify inicializar..."
sleep 30

# Verificar status
docker ps | grep coolify

echo "✅ Coolify instalado!"
echo "🌐 Acesse: http://91.99.219.101:8000"
echo "📧 Configure seu admin user na primeira execução"