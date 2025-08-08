#!/bin/bash

# Script de health check para Coolify
# Verifica se todos os serviços estão funcionando

echo "Verificando health da aplicação..."

# Verificar se o Nginx está respondendo
if curl -f http://localhost:80/api/health > /dev/null 2>&1; then
    echo "✅ Nginx e API estão funcionando"
else
    echo "❌ Nginx ou API não estão respondendo"
    exit 1
fi

# Verificar se o backend está respondendo diretamente
if curl -f http://localhost:5000/api/health > /dev/null 2>&1; then
    echo "✅ Backend está funcionando"
else
    echo "❌ Backend não está respondendo"
    exit 1
fi

# Verificar se o PostgreSQL está acessível
if pg_isready -h localhost -p 5432 -U postgres > /dev/null 2>&1; then
    echo "✅ PostgreSQL está funcionando"
else
    echo "❌ PostgreSQL não está acessível"
    exit 1
fi

# Verificar se o Redis está acessível
if redis-cli -h localhost -p 6379 ping > /dev/null 2>&1; then
    echo "✅ Redis está funcionando"
else
    echo "❌ Redis não está acessível"
    exit 1
fi

echo "✅ Todos os serviços estão funcionando corretamente!"
exit 0