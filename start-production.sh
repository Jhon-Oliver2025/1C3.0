#!/bin/bash
# Script de inicialização para produção
# Inicia frontend primeiro, depois backend

echo "🚀 Iniciando sistema em produção..."
echo "📍 Domínio: 1crypten.space"

# Função para verificar se um serviço está rodando
check_service() {
    local service_name=$1
    local max_attempts=30
    local attempt=1
    
    echo "⏳ Aguardando $service_name..."
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose ps $service_name | grep -q "Up"; then
            echo "✅ $service_name está rodando!"
            return 0
        fi
        echo "⏳ Tentativa $attempt/$max_attempts - Aguardando $service_name..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ Erro: $service_name não iniciou corretamente"
    return 1
}

# Parar serviços existentes
echo "🛑 Parando serviços existentes..."
docker-compose down

# Limpar containers órfãos
echo "🧹 Limpando containers órfãos..."
docker-compose down --remove-orphans

# Verificar se arquivo .env existe
if [ ! -f ".env" ]; then
    echo "❌ Erro: Arquivo .env não encontrado!"
    echo "📝 Copie .env.example para .env e configure as variáveis"
    exit 1
fi

# Criar diretórios necessários
echo "📁 Criando diretórios necessários..."
mkdir -p back/data
mkdir -p nginx/ssl
chmod 755 back/data

# Iniciar banco de dados e Redis primeiro
echo "🗄️ Iniciando banco de dados e Redis..."
docker-compose up -d postgres redis

# Aguardar banco de dados
check_service "postgres"
check_service "redis"

# Aguardar um pouco mais para garantir que o banco está pronto
echo "⏳ Aguardando inicialização completa do banco..."
sleep 10

# Iniciar backend
echo "🔧 Iniciando backend..."
docker-compose up -d backend

# Verificar se backend está rodando
check_service "backend"

# Aguardar backend estar completamente pronto
echo "⏳ Aguardando backend estar pronto..."
sleep 15

# Testar endpoint do backend
echo "🔍 Testando backend..."
for i in {1..10}; do
    if curl -f http://localhost:5000/health >/dev/null 2>&1; then
        echo "✅ Backend respondendo corretamente!"
        break
    fi
    echo "⏳ Tentativa $i/10 - Aguardando backend..."
    sleep 3
done

# Iniciar frontend
echo "🎨 Iniciando frontend..."
docker-compose up -d frontend

# Verificar se frontend está rodando
check_service "frontend"

# Aguardar frontend estar pronto
echo "⏳ Aguardando frontend estar pronto..."
sleep 10

# Iniciar Nginx
echo "🌐 Iniciando Nginx..."
docker-compose up -d nginx

# Verificar se Nginx está rodando
check_service "nginx"

# Status final
echo "\n📊 Status dos serviços:"
docker-compose ps

echo "\n🎉 Sistema iniciado com sucesso!"
echo "🌐 Frontend: https://1crypten.space"
echo "🔧 Backend API: https://api.1crypten.space"
echo "\n📋 Para monitorar logs:"
echo "   docker-compose logs -f"
echo "\n🛑 Para parar:"
echo "   docker-compose down"