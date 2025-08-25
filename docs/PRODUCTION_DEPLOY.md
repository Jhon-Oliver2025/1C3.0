# Guia de Deploy em Produção - 1Crypten

## 📋 Pré-requisitos

- Docker e Docker Compose instalados
- Domínio configurado
- Certificados SSL
- Variáveis de ambiente configuradas

## 🚀 Deploy

### 1. Preparar ambiente
```bash
# Clonar repositório
git clone https://github.com/seu-usuario/1C3.0.git
cd 1C3.0

# Configurar variáveis de ambiente
cp .env.production.template .env.production
# Editar .env.production com suas credenciais
```

### 2. Build e Deploy
```bash
# Build da aplicação
docker-compose -f docker-compose.production.yml build

# Iniciar serviços
docker-compose -f docker-compose.production.yml up -d
```

### 3. Verificar saúde
```bash
# Verificar containers
docker-compose -f docker-compose.production.yml ps

# Verificar logs
docker-compose -f docker-compose.production.yml logs -f
```

## 🔧 Monitoramento

- Health check: `https://seu-dominio.com/api/health`
- Logs: `docker-compose logs -f`
- Métricas: Dashboard interno

## 🔒 Segurança

- Todas as credenciais em variáveis de ambiente
- HTTPS obrigatório
- Rate limiting ativo
- Logs de auditoria

## 📊 Performance

- CDN configurado
- Cache otimizado
- Compressão gzip
- Bundle splitting
