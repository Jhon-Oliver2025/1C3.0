#!/bin/bash

# Script de Rollback - 1Crypten
# Reverte para versão anterior

set -e

echo "🔄 Iniciando rollback..."

# Verificar se há commit anterior
if [ -z "$1" ]; then
    echo "❌ Especifique o commit para rollback: ./rollback.sh <commit-hash>"
    exit 1
fi

COMMIT_HASH=$1

# Verificar se o commit existe
if ! git cat-file -e "$COMMIT_HASH" 2>/dev/null; then
    echo "❌ Commit $COMMIT_HASH não encontrado"
    exit 1
fi

# Fazer checkout do commit
echo "📥 Revertendo para commit $COMMIT_HASH..."
git checkout "$COMMIT_HASH"

# Rebuild e restart
echo "🔨 Reconstruindo aplicação..."
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml build --no-cache
docker-compose -f docker-compose.production.yml up -d

# Verificar saúde
sleep 30
if curl -f http://localhost/health > /dev/null 2>&1; then
    echo "✅ Rollback concluído com sucesso!"
else
    echo "❌ Falha no rollback"
    exit 1
fi

echo "🎉 Rollback finalizado!"
