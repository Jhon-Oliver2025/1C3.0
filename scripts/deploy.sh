#!/bin/bash

# Script de Deploy - 1Crypten
# Executa deploy completo em produção

set -e  # Parar em caso de erro

echo "🚀 Iniciando deploy do 1Crypten..."

# Verificar se está na branch main
if [ "$(git branch --show-current)" != "main" ]; then
    echo "❌ Deploy deve ser feito a partir da branch main"
    exit 1
fi

# Verificar se há mudanças não commitadas
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ Há mudanças não commitadas. Commit antes do deploy."
    exit 1
fi

# Pull das últimas mudanças
echo "📥 Atualizando código..."
git pull origin main

# Verificar se .env.production existe
if [ ! -f ".env.production" ]; then
    echo "❌ Arquivo .env.production não encontrado"
    echo "💡 Copie .env.production.template e configure as variáveis"
    exit 1
fi

# Parar containers existentes
echo "🛑 Parando containers..."
docker-compose -f docker-compose.production.yml down

# Build das imagens
echo "🔨 Construindo imagens..."
docker-compose -f docker-compose.production.yml build --no-cache

# Iniciar serviços
echo "🚀 Iniciando serviços..."
docker-compose -f docker-compose.production.yml up -d

# Aguardar serviços ficarem prontos
echo "⏳ Aguardando serviços..."
sleep 30

# Verificar saúde dos serviços
echo "🏥 Verificando saúde dos serviços..."
if curl -f http://localhost/health > /dev/null 2>&1; then
    echo "✅ Deploy concluído com sucesso!"
    echo "🌐 Aplicação disponível em: http://localhost"
else
    echo "❌ Falha no health check"
    echo "📋 Verificar logs: docker-compose -f docker-compose.production.yml logs"
    exit 1
fi

echo "🎉 Deploy finalizado!"
