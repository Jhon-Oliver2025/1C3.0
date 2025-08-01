#!/bin/bash
# Script de monitoramento do sistema

echo "📊 Status do Sistema - 1crypten.space"
echo "======================================"

# Status dos containers
echo "\n🐳 Status dos Containers:"
docker-compose ps

# Uso de recursos
echo "\n💾 Uso de Recursos:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

# Verificar conectividade
echo "\n🌐 Teste de Conectividade:"
echo -n "Frontend (1crypten.space): "
if curl -s -o /dev/null -w "%{http_code}" https://1crypten.space | grep -q "200\|301\|302"; then
    echo "✅ OK"
else
    echo "❌ ERRO"
fi

echo -n "Backend API (api.1crypten.space): "
if curl -s -o /dev/null -w "%{http_code}" https://api.1crypten.space/health | grep -q "200"; then
    echo "✅ OK"
else
    echo "❌ ERRO"
fi

# Logs recentes
echo "\n📝 Logs Recentes (últimas 10 linhas):"
echo "--- Backend ---"
docker-compose logs --tail=5 backend
echo "\n--- Frontend ---"
docker-compose logs --tail=5 frontend