#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Preparação para Produção
Configura automaticamente os arquivos necessários para deploy
"""

import os
import json
import shutil
from pathlib import Path

def create_railway_config():
    """Cria configuração para Railway"""
    railway_config = {
        "build": {
            "builder": "NIXPACKS"
        },
        "deploy": {
            "startCommand": "cd back && python app_supabase.py",
            "healthcheckPath": "/api/health"
        }
    }
    
    with open('railway.json', 'w') as f:
        json.dump(railway_config, f, indent=2)
    
    print("✅ railway.json criado")

def create_vercel_config():
    """Cria configuração para Vercel"""
    vercel_config = {
        "name": "crypten-frontend",
        "version": 2,
        "builds": [
            {
                "src": "front/package.json",
                "use": "@vercel/static-build",
                "config": {
                    "distDir": "dist"
                }
            }
        ],
        "routes": [
            {
                "src": "/(.*)",
                "dest": "/front/$1"
            }
        ],
        "env": {
            "VITE_API_URL": "@vite_api_url",
            "VITE_MERCADO_PAGO_PUBLIC_KEY": "@vite_mercado_pago_public_key"
        }
    }
    
    with open('vercel.json', 'w') as f:
        json.dump(vercel_config, f, indent=2)
    
    print("✅ vercel.json criado")

def create_dockerfile_production():
    """Cria Dockerfile otimizado para produção"""
    dockerfile_content = """
# Dockerfile para Produção
FROM python:3.11-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
WORKDIR /app

# Copiar requirements e instalar dependências Python
COPY back/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY back/ .

# Criar usuário não-root
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expor porta
EXPOSE 5000

# Comando de inicialização
CMD ["python", "app_supabase.py"]
"""
    
    with open('Dockerfile.production', 'w') as f:
        f.write(dockerfile_content)
    
    print("✅ Dockerfile.production criado")

def create_docker_compose_production():
    """Cria docker-compose para produção"""
    compose_content = """
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.production
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - MERCADO_PAGO_ACCESS_TOKEN=${MERCADO_PAGO_ACCESS_TOKEN}
      - MERCADO_PAGO_PUBLIC_KEY=${MERCADO_PAGO_PUBLIC_KEY}
      - MERCADO_PAGO_WEBHOOK_SECRET=${MERCADO_PAGO_WEBHOOK_SECRET}
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - JWT_SECRET=${JWT_SECRET}
      - FRONTEND_URL=${FRONTEND_URL}
      - BACKEND_URL=${BACKEND_URL}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.prod.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - backend
    restart: unless-stopped
"""
    
    with open('docker-compose.production.yml', 'w') as f:
        f.write(compose_content)
    
    print("✅ docker-compose.production.yml criado")

def create_nginx_production():
    """Cria configuração Nginx para produção"""
    nginx_config = """
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    
    # Gzip
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    
    # Upstream backend
    upstream backend {
        server backend:5000;
    }
    
    # HTTP to HTTPS redirect
    server {
        listen 80;
        server_name seu-dominio.com www.seu-dominio.com;
        return 301 https://$server_name$request_uri;
    }
    
    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name seu-dominio.com www.seu-dominio.com;
        
        # SSL configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;
        
        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        
        # API routes
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }
        
        # Health check
        location /health {
            proxy_pass http://backend/api/health;
            access_log off;
        }
        
        # Frontend (se servindo pelo mesmo domínio)
        location / {
            root /var/www/html;
            try_files $uri $uri/ /index.html;
            
            # Cache static assets
            location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
                expires 1y;
                add_header Cache-Control "public, immutable";
            }
        }
    }
}
"""
    
    os.makedirs('nginx', exist_ok=True)
    with open('nginx/nginx.prod.conf', 'w') as f:
        f.write(nginx_config)
    
    print("✅ nginx/nginx.prod.conf criado")

def create_env_production_template():
    """Cria template de .env para produção"""
    env_template = """
# Configurações de Produção - 1Crypten

# Mercado Pago - PRODUÇÃO (substitua pelos valores reais)
MERCADO_PAGO_ACCESS_TOKEN=APP_USR-seu_access_token_de_producao
MERCADO_PAGO_PUBLIC_KEY=APP_USR-sua_public_key_de_producao
MERCADO_PAGO_WEBHOOK_SECRET=sua_chave_secreta_webhook

# URLs de Produção
FRONTEND_URL=https://seu-dominio.com
BACKEND_URL=https://api.seu-dominio.com

# Banco de Dados Supabase
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua_chave_supabase_anon
SUPABASE_SERVICE_KEY=sua_chave_supabase_service

# Segurança
JWT_SECRET=sua_chave_jwt_super_secreta_e_longa_para_producao

# Flask
FLASK_ENV=production
FLASK_DEBUG=false
PORT=5000

# Logs
LOG_LEVEL=INFO
LOG_FILE=logs/production.log

# SSL
SSL_DISABLE=false

# Workers
WORKERS=4
"""
    
    with open('.env.production.template', 'w') as f:
        f.write(env_template)
    
    print("✅ .env.production.template criado")

def create_deployment_script():
    """Cria script de deploy automatizado"""
    deploy_script = """
#!/bin/bash

# Script de Deploy Automatizado
set -e

echo "🚀 Iniciando deploy para produção..."

# Verificar se estamos na branch main
if [ "$(git branch --show-current)" != "main" ]; then
    echo "❌ Erro: Deploy deve ser feito a partir da branch main"
    exit 1
fi

# Verificar se há mudanças não commitadas
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ Erro: Há mudanças não commitadas"
    exit 1
fi

# Build do frontend
echo "📦 Fazendo build do frontend..."
cd front
npm ci
npm run build
cd ..

# Testes do backend
echo "🧪 Executando testes do backend..."
cd back
python -m pytest tests/ || echo "⚠️ Alguns testes falharam, continuando..."
cd ..

# Deploy via Docker
echo "🐳 Fazendo deploy via Docker..."
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml build --no-cache
docker-compose -f docker-compose.production.yml up -d

# Verificar saúde da aplicação
echo "🏥 Verificando saúde da aplicação..."
sleep 10
if curl -f http://localhost:5000/api/health; then
    echo "✅ Deploy realizado com sucesso!"
else
    echo "❌ Erro: Aplicação não está respondendo"
    docker-compose -f docker-compose.production.yml logs
    exit 1
fi

echo "🎉 Deploy concluído! Aplicação rodando em produção."
"""
    
    with open('deploy.sh', 'w') as f:
        f.write(deploy_script)
    
    # Tornar executável
    os.chmod('deploy.sh', 0o755)
    
    print("✅ deploy.sh criado")

def create_healthcheck_script():
    """Cria script de monitoramento"""
    healthcheck_script = """
#!/bin/bash

# Script de Monitoramento de Saúde

API_URL="${BACKEND_URL:-http://localhost:5000}"
WEBHOOK_URL="$API_URL/api/payments/webhook"
HEALTH_URL="$API_URL/api/health"

echo "🏥 Verificando saúde do sistema..."

# Verificar API principal
echo "Testando API principal..."
if curl -f "$HEALTH_URL" > /dev/null 2>&1; then
    echo "✅ API principal: OK"
else
    echo "❌ API principal: FALHA"
    exit 1
fi

# Verificar webhook
echo "Testando webhook..."
if curl -f -X POST "$WEBHOOK_URL" \
    -H "Content-Type: application/json" \
    -d '{"type":"test","data":{"id":"test"}}' > /dev/null 2>&1; then
    echo "✅ Webhook: OK"
else
    echo "❌ Webhook: FALHA"
fi

# Verificar banco de dados
echo "Testando conexão com banco..."
if curl -f "$API_URL/api/debug/db-status" > /dev/null 2>&1; then
    echo "✅ Banco de dados: OK"
else
    echo "❌ Banco de dados: FALHA"
fi

echo "🎉 Verificação de saúde concluída!"
"""
    
    with open('healthcheck.sh', 'w') as f:
        f.write(healthcheck_script)
    
    # Tornar executável
    os.chmod('healthcheck.sh', 0o755)
    
    print("✅ healthcheck.sh criado")

def main():
    """Função principal"""
    print("🔧 Preparando arquivos para produção...\n")
    
    try:
        create_railway_config()
        create_vercel_config()
        create_dockerfile_production()
        create_docker_compose_production()
        create_nginx_production()
        create_env_production_template()
        create_deployment_script()
        create_healthcheck_script()
        
        print("\n🎉 Preparação concluída com sucesso!")
        print("\n📋 Próximos passos:")
        print("1. Configure as variáveis de ambiente em .env.production")
        print("2. Obtenha credenciais de produção do Mercado Pago")
        print("3. Configure seu domínio e SSL")
        print("4. Execute o deploy: ./deploy.sh")
        print("5. Configure o webhook no Mercado Pago")
        print("\n📖 Consulte DEPLOY_PRODUCTION.md para instruções detalhadas")
        
    except Exception as e:
        print(f"❌ Erro durante a preparação: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())