#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corretor de Produção - 1Crypten
Corrige automaticamente os problemas identificados na validação
Prepara o sistema para deploy em produção
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime

class ProductionFixer:
    """Corretor automático para problemas de produção"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.fixes_applied = []
        
    def run_fixes(self):
        """Executa todas as correções necessárias"""
        print("🔧 CORRETOR DE PRODUÇÃO - 1CRYPTEN")
        print("="*80)
        
        print("\n📦 Corrigindo package.json...")
        self.fix_package_json()
        
        print("\n🐳 Corrigindo Docker Compose...")
        self.fix_docker_compose()
        
        print("\n🔒 Melhorando .gitignore...")
        self.fix_gitignore()
        
        print("\n⚡ Otimizando configurações...")
        self.optimize_configs()
        
        print("\n📋 Criando scripts de deploy...")
        self.create_deploy_scripts()
        
        self.print_summary()
    
    def fix_package_json(self):
        """Corrige package.json do frontend"""
        package_json_path = self.project_root / 'front' / 'package.json'
        
        if not package_json_path.exists():
            print("   ⚠️ package.json não encontrado")
            return
        
        try:
            with open(package_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Adicionar scripts essenciais
            if 'scripts' not in data:
                data['scripts'] = {}
            
            scripts_to_add = {
                'start': 'vite preview --host 0.0.0.0 --port 3000',
                'build': 'vite build',
                'build:prod': 'vite build --mode production',
                'preview': 'vite preview',
                'preview:prod': 'vite preview --mode production --host 0.0.0.0',
                'lint': 'eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0',
                'type-check': 'tsc --noEmit'
            }
            
            added_scripts = []
            for script_name, script_command in scripts_to_add.items():
                if script_name not in data['scripts']:
                    data['scripts'][script_name] = script_command
                    added_scripts.append(script_name)
            
            # Salvar package.json atualizado
            with open(package_json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            if added_scripts:
                self.fixes_applied.append(f"✅ Scripts adicionados ao package.json: {', '.join(added_scripts)}")
                print(f"   ✅ Scripts adicionados: {', '.join(added_scripts)}")
            else:
                print("   ✅ package.json já está correto")
                
        except Exception as e:
            print(f"   ❌ Erro ao corrigir package.json: {e}")
    
    def fix_docker_compose(self):
        """Corrige docker-compose.production.yml"""
        docker_compose_path = self.project_root / 'docker-compose.production.yml'
        
        # Criar docker-compose.production.yml se não existir
        if not docker_compose_path.exists():
            docker_compose_content = '''version: '3.8'

services:
  app:
    build:
      context: ./back
      dockerfile: Dockerfile
    container_name: 1crypten-backend
    restart: unless-stopped
    environment:
      - FLASK_ENV=production
      - PYTHONPATH=/app
    env_file:
      - .env.production
    ports:
      - "5000:5000"
    volumes:
      - ./back:/app
      - /app/__pycache__
    networks:
      - 1crypten-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  frontend:
    build:
      context: ./front
      dockerfile: Dockerfile
    container_name: 1crypten-frontend
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    networks:
      - 1crypten-network
    depends_on:
      - app

  nginx:
    image: nginx:alpine
    container_name: 1crypten-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.prod.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    networks:
      - 1crypten-network
    depends_on:
      - app
      - frontend

networks:
  1crypten-network:
    driver: bridge

volumes:
  postgres_data:
'''
            
            with open(docker_compose_path, 'w', encoding='utf-8') as f:
                f.write(docker_compose_content)
            
            self.fixes_applied.append("✅ docker-compose.production.yml criado")
            print("   ✅ docker-compose.production.yml criado")
        else:
            print("   ✅ docker-compose.production.yml já existe")
        
        # Criar Dockerfile para o frontend se não existir
        frontend_dockerfile = self.project_root / 'front' / 'Dockerfile'
        if not frontend_dockerfile.exists():
            dockerfile_content = '''# Build stage
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build application
RUN npm run build:prod

# Production stage
FROM node:18-alpine as production

WORKDIR /app

# Install serve globally
RUN npm install -g serve

# Copy built application
COPY --from=build /app/dist ./dist

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/ || exit 1

# Start application
CMD ["serve", "-s", "dist", "-l", "3000"]
'''
            
            with open(frontend_dockerfile, 'w', encoding='utf-8') as f:
                f.write(dockerfile_content)
            
            self.fixes_applied.append("✅ Dockerfile do frontend criado")
            print("   ✅ Dockerfile do frontend criado")
    
    def fix_gitignore(self):
        """Melhora o .gitignore"""
        gitignore_path = self.project_root / '.gitignore'
        
        # Conteúdo completo do .gitignore
        gitignore_content = '''# Dependencies
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
PIPFILE.lock

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local
.env.production
.env.n8n
.venv
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
lerna-debug.log*

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/
*.lcov

# nyc test coverage
.nyc_output

# Grunt intermediate storage
.grunt

# Bower dependency directory
bower_components

# node-waf configuration
.lock-wscript

# Compiled binary addons
build/Release

# Dependency directories
jspm_packages/

# TypeScript cache
*.tsbuildinfo

# Optional npm cache directory
.npm

# Optional eslint cache
.eslintcache

# Microbundle cache
.rpt2_cache/
.rts2_cache_cjs/
.rts2_cache_es/
.rts2_cache_umd/

# Optional REPL history
.node_repl_history

# Output of 'npm pack'
*.tgz

# Yarn Integrity file
.yarn-integrity

# parcel-bundler cache
.cache
.parcel-cache

# Next.js build output
.next

# Nuxt.js build / generate output
.nuxt
dist

# Gatsby files
.cache/
public

# Storybook build outputs
.out
.storybook-out

# Temporary folders
tmp/
temp/

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Backup files
*.backup
*.old
*.temp
*.bak

# Database
*.db
*.sqlite
*.sqlite3

# Certificates
*.pem
*.key
*.crt
*.p12
*.pfx

# Docker
.dockerignore

# Build outputs
build/
dist/
out/

# Cache
.cache/
.parcel-cache/
.next/
.nuxt/

# Diagnostic reports
system_diagnostic_report.json
production_validation_report.json
optimization_backup/
optimization_log.txt

# Test files
test_*.py
*_test.py
debug_*.py
diagnose*.py
check_*.py

# HTML debug files
*.html
!index.html
!public/*.html

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
Pipfile.lock

# PEP 582
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/
'''
        
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        
        self.fixes_applied.append("✅ .gitignore atualizado com padrões de segurança")
        print("   ✅ .gitignore atualizado")
    
    def optimize_configs(self):
        """Otimiza configurações para produção"""
        # Criar .env.production.template se não existir
        env_template_path = self.project_root / '.env.production.template'
        if not env_template_path.exists():
            env_template_content = '''# Configurações de Produção - 1Crypten
# Copie este arquivo para .env.production e configure as variáveis

# Flask
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-super-secret-key-here

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-key

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/1crypten

# API Keys
BINANCE_API_KEY=your-binance-api-key
BINANCE_SECRET_KEY=your-binance-secret-key

# Telegram
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-telegram-chat-id

# Mercado Pago
MERCADO_PAGO_ACCESS_TOKEN=your-mercado-pago-token
MERCADO_PAGO_PUBLIC_KEY=your-mercado-pago-public-key

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Security
JWT_SECRET_KEY=your-jwt-secret-key
CORS_ORIGINS=https://yourdomain.com

# Performance
WORKERS=4
THREADS=2
TIMEOUT=120

# Monitoring
LOG_LEVEL=INFO
SENTRY_DSN=your-sentry-dsn
'''
            
            with open(env_template_path, 'w', encoding='utf-8') as f:
                f.write(env_template_content)
            
            self.fixes_applied.append("✅ Template de produção .env criado")
            print("   ✅ .env.production.template criado")
        
        # Criar configuração nginx para produção
        nginx_dir = self.project_root / 'nginx'
        nginx_dir.mkdir(exist_ok=True)
        
        nginx_prod_config = nginx_dir / 'nginx.prod.conf'
        if not nginx_prod_config.exists():
            nginx_content = '''events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    
    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;
    
    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;
    
    # Upstream backend
    upstream backend {
        server app:5000;
    }
    
    # Upstream frontend
    upstream frontend {
        server frontend:3000;
    }
    
    server {
        listen 80;
        server_name _;
        
        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
        add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https:; media-src 'self'; object-src 'none'; child-src 'none'; frame-ancestors 'self'; form-action 'self'; base-uri 'self';" always;
        
        # API routes
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }
        
        # Login rate limiting
        location /api/auth/login {
            limit_req zone=login burst=5 nodelay;
            
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Frontend routes
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Handle client-side routing
            try_files $uri $uri/ /index.html;
        }
        
        # Static files caching
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
            proxy_pass http://frontend;
        }
        
        # Health check
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
'''
            
            with open(nginx_prod_config, 'w', encoding='utf-8') as f:
                f.write(nginx_content)
            
            self.fixes_applied.append("✅ Configuração Nginx para produção criada")
            print("   ✅ nginx.prod.conf criado")
    
    def create_deploy_scripts(self):
        """Cria scripts de deploy automatizado"""
        scripts_dir = self.project_root / 'scripts'
        scripts_dir.mkdir(exist_ok=True)
        
        # Script de deploy
        deploy_script = scripts_dir / 'deploy.sh'
        deploy_content = '''#!/bin/bash

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
'''
        
        with open(deploy_script, 'w', encoding='utf-8') as f:
            f.write(deploy_content)
        
        # Tornar executável (no Linux/Mac)
        try:
            os.chmod(deploy_script, 0o755)
        except:
            pass
        
        # Script de rollback
        rollback_script = scripts_dir / 'rollback.sh'
        rollback_content = '''#!/bin/bash

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
'''
        
        with open(rollback_script, 'w', encoding='utf-8') as f:
            f.write(rollback_content)
        
        try:
            os.chmod(rollback_script, 0o755)
        except:
            pass
        
        self.fixes_applied.append("✅ Scripts de deploy criados")
        print("   ✅ Scripts de deploy e rollback criados")
    
    def print_summary(self):
        """Imprime resumo das correções"""
        print("\n" + "="*80)
        print("📊 RESUMO DAS CORREÇÕES APLICADAS")
        print("="*80)
        
        print(f"\n✅ Total de correções aplicadas: {len(self.fixes_applied)}")
        
        for fix in self.fixes_applied:
            print(f"   {fix}")
        
        print(f"\n🎯 Próximos passos:")
        print(f"   1. Configure o arquivo .env.production")
        print(f"   2. Execute: python production_validator.py")
        print(f"   3. Se tudo estiver OK, execute: ./scripts/deploy.sh")
        print(f"   4. Monitore os logs: docker-compose logs -f")
        
        print(f"\n📁 Arquivos importantes criados:")
        print(f"   📄 .env.production.template")
        print(f"   🐳 docker-compose.production.yml")
        print(f"   🌐 nginx/nginx.prod.conf")
        print(f"   🚀 scripts/deploy.sh")
        print(f"   🔄 scripts/rollback.sh")
        
        print(f"\n🎉 Sistema corrigido e pronto para validação!")

def main():
    """Função principal"""
    project_root = os.getcwd()
    
    print("🔧 CORRETOR DE PRODUÇÃO 1CRYPTEN")
    print(f"📁 Projeto: {project_root}")
    print(f"⏰ Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Executar correções
    fixer = ProductionFixer(project_root)
    fixer.run_fixes()

if __name__ == '__main__':
    main()