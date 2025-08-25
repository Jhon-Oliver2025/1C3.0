#!/bin/bash
# Script de build robusto para Docker - 1Crypten

set -e

echo "🔧 Preparando ambiente de build..."

# Limpar cache e dependências antigas
echo "🧹 Limpando cache..."
rm -rf node_modules package-lock.json .npm || true
npm cache clean --force || true

# Configurar npm
echo "⚙️ Configurando npm..."
npm config set legacy-peer-deps true
npm config set optional false
npm config set engine-strict false

# Instalar dependências
echo "📦 Instalando dependências..."
npm install --legacy-peer-deps --no-optional --verbose

# Verificar se Rollup foi instalado corretamente
echo "🔍 Verificando Rollup..."
if ! npm list rollup > /dev/null 2>&1; then
    echo "⚠️ Rollup não encontrado, instalando manualmente..."
    npm install rollup@latest --legacy-peer-deps --no-optional
fi

# Build da aplicação
echo "🔨 Fazendo build..."
NODE_OPTIONS="--max-old-space-size=4096" npm run build

echo "✅ Build concluído com sucesso!"
