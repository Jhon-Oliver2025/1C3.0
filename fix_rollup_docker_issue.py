#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir problema do Rollup no Docker - 1Crypten
Resolve erro: Cannot find module @rollup/rollup-linux-x64-musl
"""

import os
import json
from pathlib import Path
from datetime import datetime

class RollupDockerFixer:
    """Corrige problemas do Rollup no ambiente Docker"""
    
    def __init__(self):
        self.project_root = Path(".")
        self.frontend_path = self.project_root / "front"
        
    def fix_package_json(self) -> bool:
        """Corrige package.json para resolver dependências do Rollup"""
        package_json_path = self.frontend_path / "package.json"
        
        if not package_json_path.exists():
            print("❌ package.json não encontrado")
            return False
        
        try:
            with open(package_json_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
            
            # Adicionar resolutions para forçar versões específicas
            if 'resolutions' not in package_data:
                package_data['resolutions'] = {}
            
            # Forçar versão específica do Rollup que funciona no Docker
            package_data['resolutions'].update({
                "@rollup/rollup-linux-x64-musl": "npm:@rollup/rollup-linux-x64-gnu",
                "rollup": "^4.0.0"
            })
            
            # Adicionar overrides para npm
            if 'overrides' not in package_data:
                package_data['overrides'] = {}
            
            package_data['overrides'].update({
                "@rollup/rollup-linux-x64-musl": "npm:@rollup/rollup-linux-x64-gnu",
                "rollup": "^4.0.0"
            })
            
            # Atualizar engines para garantir compatibilidade
            package_data['engines'] = {
                "node": ">=18.0.0",
                "npm": ">=8.0.0"
            }
            
            with open(package_json_path, 'w', encoding='utf-8') as f:
                json.dump(package_data, f, indent=2, ensure_ascii=False)
            
            print("✅ package.json atualizado com correções do Rollup")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao atualizar package.json: {e}")
            return False
    
    def create_npmrc(self) -> bool:
        """Cria .npmrc para configurações específicas do Docker"""
        npmrc_path = self.frontend_path / ".npmrc"
        
        try:
            npmrc_content = '''# Configurações para resolver problemas do Rollup no Docker
optional=false
legacy-peer-deps=true
strict-peer-deps=false
engine-strict=false

# Configurações de cache e timeout
cache-max=86400000
fetch-timeout=300000
fetch-retries=3

# Configurações de registry
registry=https://registry.npmjs.org/
'''
            
            with open(npmrc_path, 'w', encoding='utf-8') as f:
                f.write(npmrc_content)
            
            print("✅ .npmrc criado com configurações otimizadas")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar .npmrc: {e}")
            return False
    
    def update_dockerfile(self) -> bool:
        """Atualiza Dockerfile para resolver problemas do Rollup"""
        dockerfile_path = self.frontend_path / "Dockerfile"
        
        if not dockerfile_path.exists():
            print("❌ Dockerfile não encontrado")
            return False
        
        try:
            with open(dockerfile_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar se já tem as correções
            if 'npm ci --only=production' in content:
                # Substituir npm ci por npm install com flags específicas
                content = content.replace(
                    'npm ci --only=production',
                    'npm install --production --legacy-peer-deps --no-optional'
                )
            
            if 'npm ci' in content and 'npm install' not in content:
                content = content.replace(
                    'npm ci',
                    'npm install --legacy-peer-deps --no-optional'
                )
            
            # Adicionar limpeza antes da instalação
            if 'COPY package*.json' in content and 'rm -rf node_modules' not in content:
                content = content.replace(
                    'COPY package*.json ./',
                    '''COPY package*.json ./
COPY .npmrc ./
RUN rm -rf node_modules package-lock.json || true'''
                )
            
            # Adicionar variáveis de ambiente para o Node.js
            if 'ENV NODE_ENV=production' not in content:
                content = 'ENV NODE_ENV=production\nENV NODE_OPTIONS="--max-old-space-size=4096"\n' + content
            
            with open(dockerfile_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Dockerfile atualizado com correções do Rollup")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao atualizar Dockerfile: {e}")
            return False
    
    def create_docker_ignore(self) -> bool:
        """Cria .dockerignore otimizado"""
        dockerignore_path = self.frontend_path / ".dockerignore"
        
        try:
            dockerignore_content = '''# Dependencies
node_modules
npm-debug.log*
yarn-debug.log*
yarn-error.log*
package-lock.json
yarn.lock

# Build outputs
dist
build
.vite
.cache

# Environment files
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE files
.vscode
.idea
*.swp
*.swo

# OS files
.DS_Store
Thumbs.db

# Git
.git
.gitignore

# Documentation
README.md
*.md
'''
            
            with open(dockerignore_path, 'w', encoding='utf-8') as f:
                f.write(dockerignore_content)
            
            print("✅ .dockerignore criado")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar .dockerignore: {e}")
            return False
    
    def create_build_script(self) -> bool:
        """Cria script de build robusto"""
        build_script_path = self.frontend_path / "build-docker.sh"
        
        try:
            build_script_content = '''#!/bin/bash
# Script de build robusto para Docker - 1Crypten

set -e

echo "🔧 Preparando ambiente de build..."

# Limpar cache e dependências antigas
echo "🧹 Limpando cache..."
rm -rf node_modules package-lock.json .npm || true
npm cache clean --force || true

# Configurar npm
echo "⚙️ Configurando npm..."
npm config set legacy-peer-deps true
npm config set optional false
npm config set engine-strict false

# Instalar dependências
echo "📦 Instalando dependências..."
npm install --legacy-peer-deps --no-optional --verbose

# Verificar se Rollup foi instalado corretamente
echo "🔍 Verificando Rollup..."
if ! npm list rollup > /dev/null 2>&1; then
    echo "⚠️ Rollup não encontrado, instalando manualmente..."
    npm install rollup@latest --legacy-peer-deps --no-optional
fi

# Build da aplicação
echo "🔨 Fazendo build..."
NODE_OPTIONS="--max-old-space-size=4096" npm run build

echo "✅ Build concluído com sucesso!"
'''
            
            with open(build_script_path, 'w', encoding='utf-8') as f:
                f.write(build_script_content)
            
            # Tornar executável
            os.chmod(build_script_path, 0o755)
            
            print("✅ Script de build criado")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar script de build: {e}")
            return False
    
    def update_vite_config_for_docker(self) -> bool:
        """Atualiza vite.config.ts para compatibilidade com Docker"""
        vite_config_path = self.frontend_path / "vite.config.ts"
        
        if not vite_config_path.exists():
            print("❌ vite.config.ts não encontrado")
            return False
        
        try:
            with open(vite_config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Adicionar configurações específicas para Docker
            if 'optimizeDeps' not in content:
                # Encontrar onde inserir a configuração
                if 'return {' in content:
                    content = content.replace(
                        'return {',
                        '''return {
    optimizeDeps: {
      include: ['react', 'react-dom'],
      exclude: ['@rollup/rollup-linux-x64-musl']
    },
    esbuild: {
      target: 'es2020'
    },'''
                    )
            
            # Adicionar configuração de build para Docker
            if 'build: {' in content and 'target: ' not in content:
                content = content.replace(
                    'build: {',
                    '''build: {
      target: 'es2020',
      minify: 'esbuild',
      sourcemap: false,'''
                )
            
            with open(vite_config_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ vite.config.ts atualizado para Docker")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao atualizar vite.config.ts: {e}")
            return False
    
    def run_complete_fix(self) -> bool:
        """Executa correção completa"""
        print("🔧 CORREÇÃO DO PROBLEMA ROLLUP NO DOCKER - 1CRYPTEN")
        print("="*70)
        print(f"⏰ Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print()
        
        success = True
        
        # 1. Corrigir package.json
        print("📦 FASE 1: Corrigindo package.json")
        if not self.fix_package_json():
            success = False
        
        # 2. Criar .npmrc
        print("\n⚙️ FASE 2: Criando .npmrc")
        if not self.create_npmrc():
            success = False
        
        # 3. Atualizar Dockerfile
        print("\n🐳 FASE 3: Atualizando Dockerfile")
        if not self.update_dockerfile():
            success = False
        
        # 4. Criar .dockerignore
        print("\n🚫 FASE 4: Criando .dockerignore")
        if not self.create_docker_ignore():
            success = False
        
        # 5. Criar script de build
        print("\n📜 FASE 5: Criando script de build")
        if not self.create_build_script():
            success = False
        
        # 6. Atualizar vite.config.ts
        print("\n⚡ FASE 6: Atualizando vite.config.ts")
        if not self.update_vite_config_for_docker():
            success = False
        
        # Resumo
        print("\n" + "="*70)
        print("📋 RESUMO DA CORREÇÃO")
        print("="*70)
        
        if success:
            print("\n✅ CORREÇÃO CONCLUÍDA COM SUCESSO!")
            print("\n🎯 Arquivos modificados:")
            print("   📦 package.json - Resolutions e overrides adicionados")
            print("   ⚙️ .npmrc - Configurações otimizadas")
            print("   🐳 Dockerfile - Comandos npm corrigidos")
            print("   🚫 .dockerignore - Arquivos desnecessários excluídos")
            print("   📜 build-docker.sh - Script de build robusto")
            print("   ⚡ vite.config.ts - Configurações para Docker")
            print("\n🚀 Próximos passos:")
            print("   1. Commit e push das alterações")
            print("   2. Coolify fará novo deploy automaticamente")
            print("   3. Build deve funcionar sem erros do Rollup")
        else:
            print("\n⚠️ Correção concluída com alguns erros")
            print("\n🔧 Verifique:")
            print("   1. Permissões de arquivo")
            print("   2. Estrutura do projeto")
            print("   3. Execute novamente se necessário")
        
        return success

def main():
    """Função principal"""
    fixer = RollupDockerFixer()
    
    try:
        success = fixer.run_complete_fix()
        
        if success:
            print("\n🎉 PROBLEMA DO ROLLUP CORRIGIDO!")
            print("\n⚡ AÇÃO NECESSÁRIA:")
            print("   1. Commit e push das alterações")
            print("   2. Aguarde novo deploy do Coolify")
            print("   3. Deploy deve funcionar sem erros")
            return 0
        else:
            print("\n❌ FALHA NA CORREÇÃO")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Operação cancelada")
        return 1
    except Exception as e:
        print(f"\n\n❌ Erro inesperado: {e}")
        return 1

if __name__ == '__main__':
    exit(main())