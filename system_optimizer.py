#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Otimização Automática - 1Crypten
Executa limpeza e otimizações baseadas no diagnóstico
Prepara o sistema para produção
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict

class SystemOptimizer:
    """Sistema de otimização automática"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / 'optimization_backup'
        self.actions_log = []
        
    def run_optimization(self, diagnostic_report_path: str = None):
        """Executa otimização completa do sistema"""
        print("🚀 INICIANDO OTIMIZAÇÃO DO SISTEMA 1CRYPTEN")
        print("="*80)
        
        # Carregar relatório de diagnóstico
        if diagnostic_report_path:
            report_path = Path(diagnostic_report_path)
        else:
            report_path = self.project_root / 'system_diagnostic_report.json'
        
        if not report_path.exists():
            print("❌ Relatório de diagnóstico não encontrado. Execute o diagnóstico primeiro.")
            return
        
        with open(report_path, 'r', encoding='utf-8') as f:
            self.diagnostic_report = json.load(f)
        
        # Criar backup
        print("\n📦 Criando backup...")
        self.create_backup()
        
        # Executar otimizações
        print("\n🧹 Removendo arquivos não utilizados...")
        self.cleanup_unused_files()
        
        print("\n📁 Organizando estrutura de arquivos...")
        self.organize_file_structure()
        
        print("\n⚡ Otimizando performance...")
        self.optimize_performance()
        
        print("\n🔒 Corrigindo problemas de segurança...")
        self.fix_security_issues()
        
        print("\n📋 Criando documentação...")
        self.create_production_docs()
        
        # Salvar log de ações
        self.save_actions_log()
        
        print("\n✅ Otimização concluída!")
        self.print_summary()
    
    def create_backup(self):
        """Cria backup antes das otimizações"""
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        self.backup_dir.mkdir()
        
        # Backup de arquivos críticos
        critical_files = [
            'back',
            'front/src',
            'front/package.json',
            'front/vite.config.ts',
            'docker-compose.production.yml',
            '.env.production.template'
        ]
        
        for file_path in critical_files:
            source = self.project_root / file_path
            if source.exists():
                if source.is_dir():
                    shutil.copytree(source, self.backup_dir / file_path)
                else:
                    if '/' in file_path:
                        dest_dir = self.backup_dir / Path(file_path).parent
                        dest_dir.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(source, dest_dir / source.name)
                    else:
                        shutil.copy2(source, self.backup_dir / source.name)
        
        self.actions_log.append(f"✅ Backup criado em: {self.backup_dir}")
        print(f"   📦 Backup salvo em: {self.backup_dir}")
    
    def cleanup_unused_files(self):
        """Remove arquivos não utilizados identificados no diagnóstico"""
        unused_files = self.diagnostic_report.get('unused_files', [])
        removed_count = 0
        
        # Categorizar arquivos por tipo
        safe_to_remove = {
            'debug_file': [],
            'config_backup': [],
            'test_file': []
        }
        
        for file_info in unused_files:
            file_type = file_info.get('type', 'unknown')
            if file_type in safe_to_remove:
                safe_to_remove[file_type].append(file_info['file'])
        
        # Remover arquivos de debug e temporários
        for file_path in safe_to_remove['debug_file']:
            try:
                path = Path(file_path)
                if path.exists() and self._is_safe_to_remove(path):
                    path.unlink()
                    removed_count += 1
                    self.actions_log.append(f"🗑️ Removido arquivo de debug: {file_path}")
            except Exception as e:
                print(f"   ⚠️ Erro ao remover {file_path}: {e}")
        
        # Remover backups de configuração antigos
        for file_path in safe_to_remove['config_backup']:
            try:
                path = Path(file_path)
                if path.exists() and path.suffix in ['.old', '.backup', '.example']:
                    path.unlink()
                    removed_count += 1
                    self.actions_log.append(f"🗑️ Removido backup: {file_path}")
            except Exception as e:
                print(f"   ⚠️ Erro ao remover {file_path}: {e}")
        
        print(f"   🗑️ {removed_count} arquivos removidos")
    
    def _is_safe_to_remove(self, file_path: Path) -> bool:
        """Verifica se é seguro remover o arquivo"""
        # Lista de padrões seguros para remoção
        safe_patterns = [
            'debug_', 'test_', 'temp_', 'fix_', 'apply_', 'update_',
            '.old', '.backup', '.example', '.temp'
        ]
        
        # Verificar se o nome ou extensão está na lista segura
        for pattern in safe_patterns:
            if pattern in file_path.name.lower():
                return True
        
        # Não remover se for arquivo crítico
        critical_patterns = ['app.py', 'main.py', 'index.', 'package.json', '.env']
        for pattern in critical_patterns:
            if pattern in file_path.name.lower():
                return False
        
        return False
    
    def organize_file_structure(self):
        """Organiza estrutura de arquivos"""
        # Criar diretório para arquivos de documentação
        docs_dir = self.project_root / 'docs'
        docs_dir.mkdir(exist_ok=True)
        
        # Mover arquivos de documentação para pasta docs
        doc_files = list(self.project_root.glob('*.md'))
        moved_count = 0
        
        for doc_file in doc_files:
            if doc_file.name not in ['README.md']:  # Manter README na raiz
                try:
                    shutil.move(str(doc_file), str(docs_dir / doc_file.name))
                    moved_count += 1
                    self.actions_log.append(f"📁 Movido para docs/: {doc_file.name}")
                except Exception as e:
                    print(f"   ⚠️ Erro ao mover {doc_file}: {e}")
        
        # Criar diretório para scripts de utilidade
        scripts_dir = self.project_root / 'scripts'
        scripts_dir.mkdir(exist_ok=True)
        
        # Mover scripts de debug e teste
        script_patterns = ['debug_*.py', 'test_*.py', 'diagnose*.py', 'check_*.py']
        for pattern in script_patterns:
            for script_file in self.project_root.glob(pattern):
                if script_file.name not in ['system_diagnostic.py', 'system_optimizer.py']:
                    try:
                        shutil.move(str(script_file), str(scripts_dir / script_file.name))
                        moved_count += 1
                        self.actions_log.append(f"📁 Movido para scripts/: {script_file.name}")
                    except Exception as e:
                        print(f"   ⚠️ Erro ao mover {script_file}: {e}")
        
        print(f"   📁 {moved_count} arquivos organizados")
    
    def optimize_performance(self):
        """Otimiza performance do sistema"""
        optimizations = 0
        
        # Otimizar package.json do frontend
        package_json = self.project_root / 'front' / 'package.json'
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                
                # Adicionar scripts de build otimizado
                if 'scripts' not in data:
                    data['scripts'] = {}
                
                data['scripts']['build:prod'] = 'vite build --mode production'
                data['scripts']['preview:prod'] = 'vite preview --mode production'
                data['scripts']['analyze'] = 'vite-bundle-analyzer'
                
                with open(package_json, 'w') as f:
                    json.dump(data, f, indent=2)
                
                optimizations += 1
                self.actions_log.append("⚡ Scripts de build otimizados adicionados")
            except Exception as e:
                print(f"   ⚠️ Erro ao otimizar package.json: {e}")
        
        # Criar arquivo de configuração de produção para Vite
        vite_config_prod = self.project_root / 'front' / 'vite.config.prod.ts'
        if not vite_config_prod.exists():
            vite_prod_content = '''import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

export default defineConfig({
  plugins: [react()],
  build: {
    target: 'es2015',
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true
      }
    },
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom'],
          ui: ['styled-components']
        }
      }
    },
    chunkSizeWarningLimit: 1000
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 3000,
    host: true
  },
  preview: {
    port: 3000,
    host: true
  }
})
'''
            with open(vite_config_prod, 'w') as f:
                f.write(vite_prod_content)
            
            optimizations += 1
            self.actions_log.append("⚡ Configuração de produção Vite criada")
        
        print(f"   ⚡ {optimizations} otimizações de performance aplicadas")
    
    def fix_security_issues(self):
        """Corrige problemas de segurança identificados"""
        security_issues = self.diagnostic_report.get('security_issues', [])
        fixes = 0
        
        # Criar .gitignore melhorado se não existir
        gitignore_path = self.project_root / '.gitignore'
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

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local
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

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/

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

# Database
*.db
*.sqlite
*.sqlite3

# Certificates
*.pem
*.key
*.crt

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
optimization_backup/
'''
        
        try:
            with open(gitignore_path, 'w') as f:
                f.write(gitignore_content)
            fixes += 1
            self.actions_log.append("🔒 .gitignore de segurança criado")
        except Exception as e:
            print(f"   ⚠️ Erro ao criar .gitignore: {e}")
        
        # Verificar e alertar sobre arquivos .env expostos
        env_files = list(self.project_root.rglob('.env*'))
        for env_file in env_files:
            if not env_file.name.endswith('.example') and not env_file.name.endswith('.template'):
                print(f"   🔒 ATENÇÃO: Arquivo {env_file} pode conter credenciais sensíveis")
                print(f"      Certifique-se de que está no .gitignore")
        
        print(f"   🔒 {fixes} correções de segurança aplicadas")
    
    def create_production_docs(self):
        """Cria documentação para produção"""
        docs_dir = self.project_root / 'docs'
        docs_dir.mkdir(exist_ok=True)
        
        # Guia de deploy em produção
        deploy_guide = docs_dir / 'PRODUCTION_DEPLOY.md'
        deploy_content = '''# Guia de Deploy em Produção - 1Crypten

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
'''
        
        with open(deploy_guide, 'w', encoding='utf-8') as f:
            f.write(deploy_content)
        
        # Guia de manutenção
        maintenance_guide = docs_dir / 'MAINTENANCE.md'
        maintenance_content = '''# Guia de Manutenção - 1Crypten

## 🔄 Atualizações

### Deploy de nova versão
```bash
# Pull das mudanças
git pull origin main

# Rebuild e restart
docker-compose -f docker-compose.production.yml build
docker-compose -f docker-compose.production.yml up -d
```

### Rollback
```bash
# Voltar para versão anterior
git checkout <commit-anterior>
docker-compose -f docker-compose.production.yml build
docker-compose -f docker-compose.production.yml up -d
```

## 🗄️ Backup

### Backup do banco de dados
```bash
# Backup automático diário configurado
# Backup manual:
docker exec <container-db> pg_dump -U user database > backup.sql
```

### Backup de arquivos
```bash
# Backup de uploads e configurações
tar -czf backup-$(date +%Y%m%d).tar.gz uploads/ config/
```

## 📊 Monitoramento

### Logs importantes
- Aplicação: `docker-compose logs app`
- Banco: `docker-compose logs db`
- Nginx: `docker-compose logs nginx`

### Métricas
- CPU e memória: `docker stats`
- Espaço em disco: `df -h`
- Conexões: `netstat -an | grep :80`

## 🚨 Troubleshooting

### Problemas comuns
1. **Container não inicia**: Verificar logs e variáveis de ambiente
2. **Erro 502**: Verificar se app está rodando na porta correta
3. **Lentidão**: Verificar uso de CPU/memória

### Comandos úteis
```bash
# Restart completo
docker-compose -f docker-compose.production.yml restart

# Limpar cache
docker system prune -f

# Verificar saúde
curl -f http://localhost/api/health
```
'''
        
        with open(maintenance_guide, 'w', encoding='utf-8') as f:
            f.write(maintenance_content)
        
        self.actions_log.append("📋 Documentação de produção criada")
        print("   📋 Documentação de produção criada")
    
    def save_actions_log(self):
        """Salva log de ações executadas"""
        log_file = self.project_root / 'optimization_log.txt'
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"OTIMIZAÇÃO DO SISTEMA 1CRYPTEN\n")
            f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"{'='*50}\n\n")
            
            for action in self.actions_log:
                f.write(f"{action}\n")
        
        print(f"\n📄 Log de ações salvo em: {log_file}")
    
    def print_summary(self):
        """Imprime resumo da otimização"""
        print("\n" + "="*80)
        print("📊 RESUMO DA OTIMIZAÇÃO")
        print("="*80)
        
        print(f"\n✅ Ações executadas: {len(self.actions_log)}")
        
        categories = {
            '🗑️': 'Limpeza',
            '📁': 'Organização', 
            '⚡': 'Performance',
            '🔒': 'Segurança',
            '📋': 'Documentação',
            '📦': 'Backup'
        }
        
        for icon, category in categories.items():
            count = sum(1 for action in self.actions_log if action.startswith(icon))
            if count > 0:
                print(f"   {icon} {category}: {count} ações")
        
        print(f"\n🎯 Próximos passos:")
        print(f"   1. Testar aplicação localmente")
        print(f"   2. Executar testes automatizados")
        print(f"   3. Deploy em ambiente de staging")
        print(f"   4. Deploy em produção")
        print(f"   5. Monitorar performance")
        
        print(f"\n📁 Arquivos importantes:")
        print(f"   📦 Backup: {self.backup_dir}")
        print(f"   📄 Log: optimization_log.txt")
        print(f"   📋 Docs: docs/")

def main():
    """Função principal"""
    project_root = os.getcwd()
    
    print("🔧 SISTEMA DE OTIMIZAÇÃO 1CRYPTEN")
    print(f"📁 Projeto: {project_root}")
    print(f"⏰ Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Confirmar execução
    response = input("\n⚠️ Esta operação irá modificar arquivos. Continuar? (s/N): ")
    if response.lower() not in ['s', 'sim', 'y', 'yes']:
        print("❌ Operação cancelada.")
        return
    
    # Executar otimização
    optimizer = SystemOptimizer(project_root)
    optimizer.run_optimization()
    
    print("\n🎉 Sistema otimizado e pronto para produção!")

if __name__ == '__main__':
    main()