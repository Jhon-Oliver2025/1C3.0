#!/bin/bash

# Script de Deploy para VPS - 1Crypten
# Criado em: 06/08/2025
# Uso: ./deploy-vps.sh

echo "🚀 Iniciando deploy do 1Crypten no VPS..."
echo "================================================"

# Função para verificar se o comando foi executado com sucesso
check_status() {
    if [ $? -eq 0 ]; then
        echo "✅ $1 - Sucesso"
    else
        echo "❌ $1 - Falhou"
        exit 1
    fi
}

# 1. Verificar se o Docker está rodando
echo "📋 Verificando Docker..."
docker --version
check_status "Verificação do Docker"

# 2. Parar containers antigos (se existirem)
echo "🛑 Parando containers antigos..."
docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
check_status "Parada de containers antigos"

# 3. Limpar imagens antigas (opcional)
echo "🧹 Limpando imagens antigas..."
docker system prune -f
check_status "Limpeza do sistema Docker"

# 4. Build das novas imagens
echo "🔨 Construindo imagens..."
docker-compose -f docker-compose.prod.yml build --no-cache
check_status "Build das imagens"

# 5. Subir os containers
echo "🚀 Iniciando containers..."
docker-compose -f docker-compose.prod.yml up -d
check_status "Inicialização dos containers"

# 6. Aguardar containers ficarem prontos
echo "⏳ Aguardando containers ficarem prontos..."
sleep 30

# 7. Verificar status dos containers
echo "📊 Verificando status dos containers..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 8. Verificar logs do nginx
echo "📝 Verificando logs do nginx..."
docker logs crypto-nginx --tail 10

# 9. Verificar logs do frontend
echo "📝 Verificando logs do frontend..."
docker logs crypto-frontend --tail 10

# 10. Verificar logs do backend
echo "📝 Verificando logs do backend..."
docker logs crypto-backend --tail 10

# 11. Teste de conectividade
echo "🔍 Testando conectividade..."
echo "Frontend:"
curl -s -o /dev/null -w "%{http_code}" http://localhost/dashboard
echo ""
echo "API Health:"
curl -s http://localhost/api/health
echo ""

# 12. Informações finais
echo "================================================"
echo "✅ Deploy concluído!"
echo "🌐 Frontend: http://localhost/dashboard"
echo "🔧 API: http://localhost/api/health"
echo "📊 Monitoramento: docker logs crypto-nginx -f"
echo "================================================"

# 13. Mostrar comandos úteis
echo "📋 Comandos úteis:"
echo "  - Ver logs: docker logs <container-name> -f"
echo "  - Reiniciar: docker-compose -f docker-compose.prod.yml restart"
echo "  - Parar tudo: docker-compose -f docker-compose.prod.yml down"
echo "  - Status: docker ps"
echo "================================================"