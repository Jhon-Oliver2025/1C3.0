#!/bin/bash
# Script de build robusto para Docker - 1Crypten

set -e

echo "🔧 Preparando ambiente de build..."

# Limpar cache e dependências antigas (conforme sugerido pelo Rollup)
echo "🧹 Limpando cache e node_modules completamente..."
rm -rf node_modules package-lock.json .npm .vite dist build || true
npm cache clean --force || true
echo "✅ Limpeza completa realizada"

# Configurar npm
echo "⚙️ Configurando npm..."
npm config set legacy-peer-deps true
npm config set engine-strict false

# Instalar dependências (incluindo devDependencies para build)
echo "📦 Instalando dependências..."
npm install --legacy-peer-deps
echo "✅ Dependências instaladas com sucesso"

# Verificar se Rollup foi instalado corretamente
echo "🔍 Verificando Rollup..."
if ! npm list rollup > /dev/null 2>&1; then
    echo "⚠️ Rollup não encontrado como dependência direta, mas deve estar disponível via Vite"
fi

# Build da aplicação
echo "🔨 Fazendo build..."
NODE_OPTIONS="--max-old-space-size=4096" npx vite build --mode production

echo "✅ Build concluído com sucesso!"
