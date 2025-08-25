# 🚨 Correção de Container em Produção - Erro 504

## 🎯 **PROBLEMA EM PRODUÇÃO IDENTIFICADO**

### ❌ **Erro Crítico:**
```
Error response from daemon: No such container: backend-mkskog4w8ccwk48gkwgk040g-164820202865
```

### 🔍 **Análise do Problema:**
- **Container backend** não encontrado em produção
- **ID específico** do container não existe
- **Serviço backend** provavelmente parado ou removido
- **Aplicação em produção** com falha crítica

## 🚀 **SOLUÇÕES PARA PRODUÇÃO**

### ⚡ **Solução Imediata (< 5 min)**

#### **1. Verificar Status dos Containers:**
```bash
# Conectar ao servidor de produção
ssh user@servidor-producao

# Verificar containers rodando
docker ps

# Verificar todos os containers (incluindo parados)
docker ps -a

# Verificar containers por nome
docker ps -a | grep backend
```

#### **2. Verificar Logs do Sistema:**
```bash
# Logs do Docker daemon
sudo journalctl -u docker.service --since "1 hour ago"

# Logs de containers parados
docker logs backend-mkskog4w8ccwk48gkwgk040g-164820202865 2>/dev/null || echo "Container não encontrado"

# Verificar eventos do Docker
docker events --since "1h" --filter container=backend
```

#### **3. Recriar Container Backend:**
```bash
# Opção A: Usar docker-compose (Recomendado)
cd /path/to/app
docker-compose down
docker-compose up -d backend

# Opção B: Recriar manualmente
docker run -d \
  --name backend-mkskog4w8ccwk48gkwgk040g-164820202865 \
  --restart unless-stopped \
  -p 5000:5000 \
  -e NODE_ENV=production \
  your-backend-image:latest

# Opção C: Usar imagem específica
docker pull your-registry/backend:latest
docker run -d \
  --name backend-new \
  --restart unless-stopped \
  -p 5000:5000 \
  your-registry/backend:latest
```

### 🔧 **Solução Completa (Deploy Novo)**

#### **1. Deploy via Docker Compose:**
```bash
# Navegar para diretório da aplicação
cd /opt/app  # ou caminho correto

# Parar todos os containers
docker-compose down

# Atualizar imagens
docker-compose pull

# Recriar e iniciar containers
docker-compose up -d

# Verificar status
docker-compose ps
```

#### **2. Deploy via Coolify (Se usando):**
```bash
# Verificar status no Coolify
curl -X GET "https://coolify.domain.com/api/applications/status" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Trigger redeploy
curl -X POST "https://coolify.domain.com/api/applications/deploy" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"application_id": "your-app-id"}'
```

#### **3. Deploy Manual com GitHub:**
```bash
# Atualizar código
git pull origin main

# Rebuild da imagem
docker build -t backend:latest ./back

# Parar container antigo
docker stop backend-mkskog4w8ccwk48gkwgk040g-164820202865 2>/dev/null || true
docker rm backend-mkskog4w8ccwk48gkwgk040g-164820202865 2>/dev/null || true

# Iniciar novo container
docker run -d \
  --name backend-production \
  --restart unless-stopped \
  -p 5000:5000 \
  -e FLASK_ENV=production \
  -e DATABASE_URL="$DATABASE_URL" \
  -e JWT_SECRET="$JWT_SECRET" \
  backend:latest
```

## 🔍 **DIAGNÓSTICO AVANÇADO**

### 📊 **Script de Verificação Completa:**
```bash
#!/bin/bash
# production_diagnostic.sh

echo "🔍 Diagnóstico de Produção - $(date)"
echo "==========================================="

# 1. Verificar Docker
echo "\n📦 Status do Docker:"
docker version 2>/dev/null || echo "❌ Docker não disponível"
docker info 2>/dev/null | grep "Containers:" || echo "❌ Docker daemon não rodando"

# 2. Verificar containers
echo "\n🐳 Containers Ativos:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 3. Verificar containers parados
echo "\n⏹️ Containers Parados:"
docker ps -a --filter "status=exited" --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"

# 4. Verificar imagens
echo "\n🖼️ Imagens Disponíveis:"
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"

# 5. Verificar recursos
echo "\n💾 Recursos do Sistema:"
df -h | grep -E "(Filesystem|/dev/)"
free -h

# 6. Verificar portas
echo "\n🌐 Portas em Uso:"
netstat -tlnp | grep -E ":(80|443|5000|3000)"

# 7. Verificar logs recentes
echo "\n📋 Logs Recentes do Docker:"
sudo journalctl -u docker.service --since "30 minutes ago" --no-pager | tail -10

# 8. Verificar docker-compose
if [ -f "docker-compose.yml" ] || [ -f "docker-compose.production.yml" ]; then
    echo "\n📄 Docker Compose Status:"
    docker-compose ps 2>/dev/null || echo "❌ Docker Compose não disponível"
fi

echo "\n✅ Diagnóstico concluído!"
```

### 🚨 **Verificação de Saúde da Aplicação:**
```bash
#!/bin/bash
# health_check.sh

BASE_URL="https://1crypten.space"  # Ajustar para seu domínio

echo "🏥 Verificação de Saúde da Aplicação"
echo "====================================="

# Testar endpoints críticos
endpoints=(
    "/api/status"
    "/api/btc-signals/confirmed"
    "/manifest.json"
    "/"
)

for endpoint in "${endpoints[@]}"; do
    echo -n "Testando $endpoint: "
    
    response=$(curl -s -o /dev/null -w "%{http_code}:%{time_total}" "$BASE_URL$endpoint" --max-time 30)
    http_code=$(echo $response | cut -d: -f1)
    time_total=$(echo $response | cut -d: -f2)
    
    if [ "$http_code" = "200" ]; then
        echo "✅ OK (${time_total}s)"
    elif [ "$http_code" = "504" ]; then
        echo "🚨 TIMEOUT (Gateway Timeout)"
    else
        echo "❌ ERRO ($http_code)"
    fi
done

echo "\n📊 Resumo da Verificação:"
echo "Timestamp: $(date)"
echo "Servidor: $(hostname)"
echo "Uptime: $(uptime -p)"
```

## 🛠️ **CORREÇÕES ESPECÍFICAS POR CENÁRIO**

### 🔄 **Cenário 1: Container Parou Inesperadamente**
```bash
# Verificar por que parou
docker logs backend-mkskog4w8ccwk48gkwgk040g-164820202865

# Verificar eventos
docker events --filter container=backend-mkskog4w8ccwk48gkwgk040g-164820202865 --since 24h

# Reiniciar com logs
docker start backend-mkskog4w8ccwk48gkwgk040g-164820202865
docker logs -f backend-mkskog4w8ccwk48gkwgk040g-164820202865
```

### 🗑️ **Cenário 2: Container Foi Removido**
```bash
# Verificar imagem base
docker images | grep backend

# Recriar a partir da imagem
docker run -d \
  --name backend-mkskog4w8ccwk48gkwgk040g-164820202865 \
  --restart unless-stopped \
  -p 5000:5000 \
  $(docker images --format "{{.Repository}}:{{.Tag}}" | grep backend | head -1)
```

### 🔄 **Cenário 3: Deploy Falhou**
```bash
# Rollback para versão anterior
docker tag backend:latest backend:backup
docker pull your-registry/backend:previous
docker tag your-registry/backend:previous backend:latest

# Recriar container
docker-compose down
docker-compose up -d
```

### 🌐 **Cenário 4: Problema de Rede**
```bash
# Verificar redes Docker
docker network ls

# Recriar rede se necessário
docker network prune -f
docker-compose down
docker-compose up -d

# Verificar conectividade
docker exec backend-container ping database-container
```

## 📋 **CHECKLIST DE RECUPERAÇÃO**

### ✅ **Passos Obrigatórios:**
- [ ] **Conectar ao servidor** de produção
- [ ] **Verificar status** dos containers
- [ ] **Analisar logs** de erro
- [ ] **Identificar causa** da falha
- [ ] **Executar correção** apropriada
- [ ] **Verificar funcionamento** da aplicação
- [ ] **Monitorar estabilidade** por 30 minutos
- [ ] **Documentar incidente** para prevenção

### 🔧 **Comandos de Emergência:**
```bash
# Restart completo da aplicação
docker-compose down && docker-compose up -d

# Verificação rápida de saúde
curl -I https://1crypten.space/api/status

# Logs em tempo real
docker-compose logs -f backend

# Limpeza de emergência
docker system prune -f
docker volume prune -f
```

## 🚨 **PREVENÇÃO DE FUTUROS PROBLEMAS**

### 📊 **Monitoramento Contínuo:**
```bash
# Crontab para verificação automática
# Adicionar ao crontab: crontab -e
*/5 * * * * /opt/scripts/health_check.sh >> /var/log/health_check.log 2>&1
*/15 * * * * docker stats --no-stream >> /var/log/docker_stats.log
0 2 * * * docker system prune -f >> /var/log/docker_cleanup.log 2>&1
```

### 🔄 **Auto-Restart Policy:**
```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    image: backend:latest
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/status"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
        window: 120s
```

### 📱 **Alertas Automáticos:**
```bash
#!/bin/bash
# alert_system.sh

# Verificar se backend está rodando
if ! docker ps | grep -q backend; then
    # Enviar alerta (Slack, Discord, Email)
    curl -X POST -H 'Content-type: application/json' \
        --data '{"text":"🚨 PRODUÇÃO: Backend container não encontrado!"}' \
        YOUR_SLACK_WEBHOOK_URL
    
    # Tentar restart automático
    docker-compose up -d backend
fi
```

## 🎯 **SOLUÇÃO RECOMENDADA PARA AGORA**

### ⚡ **Ação Imediata:**
```bash
# 1. Conectar ao servidor
ssh user@servidor-producao

# 2. Verificar situação
docker ps -a | grep backend

# 3. Solução rápida
cd /path/to/app
docker-compose down
docker-compose pull
docker-compose up -d

# 4. Verificar funcionamento
curl -I https://1crypten.space/api/status

# 5. Monitorar logs
docker-compose logs -f backend
```

### 📞 **Se Precisar de Ajuda:**
1. **Executar script** de diagnóstico
2. **Coletar logs** de erro
3. **Verificar recursos** do servidor
4. **Contactar suporte** com informações coletadas

---

## 🔑 **RESUMO EXECUTIVO**

### 🚨 **Problema:**
Container backend não encontrado em produção (ID: backend-mkskog4w8ccwk48gkwgk040g-164820202865)

### ⚡ **Solução Rápida:**
```bash
docker-compose down && docker-compose up -d
```

### 🔍 **Verificação:**
```bash
curl -I https://1crypten.space/api/status
```

### 📊 **Monitoramento:**
```bash
docker-compose logs -f backend
```

**💡 Execute os comandos acima no servidor de produção para resolver o problema imediatamente!**