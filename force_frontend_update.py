#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para forçar atualização completa do frontend - 1Crypten
Resolve problemas persistentes de cache e versão antiga
"""

import os
import shutil
import subprocess
import time
import json
import hashlib
from datetime import datetime
from pathlib import Path

class FrontendForceUpdate:
    """Força atualização completa do frontend"""
    
    def __init__(self):
        self.project_root = Path(".")
        self.frontend_path = self.project_root / "front"
        self.timestamp = int(time.time())
        
    def generate_unique_hash(self) -> str:
        """Gera hash único baseado no timestamp"""
        content = f"{self.timestamp}-{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:8]
    
    def update_vite_config(self) -> bool:
        """Atualiza configuração do Vite para forçar novo build"""
        vite_config_path = self.frontend_path / "vite.config.ts"
        
        if not vite_config_path.exists():
            print("❌ vite.config.ts não encontrado")
            return False
        
        try:
            with open(vite_config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Adicionar configuração para forçar novo hash
            unique_hash = self.generate_unique_hash()
            
            # Procurar por build config existente
            if 'build:' in content:
                # Substituir configuração existente
                import re
                pattern = r'build:\s*{[^}]*}'
                new_build_config = f'''build: {{
    rollupOptions: {{
      output: {{
        entryFileNames: `assets/[name]-{unique_hash}.[hash].js`,
        chunkFileNames: `assets/[name]-{unique_hash}.[hash].js`,
        assetFileNames: `assets/[name]-{unique_hash}.[hash].[ext]`
      }}
    }}
  }}'''
                content = re.sub(pattern, new_build_config, content)
            else:
                # Adicionar nova configuração
                if 'export default defineConfig({' in content:
                    content = content.replace(
                        'export default defineConfig({',
                        f'''export default defineConfig({{
  build: {{
    rollupOptions: {{
      output: {{
        entryFileNames: `assets/[name]-{unique_hash}.[hash].js`,
        chunkFileNames: `assets/[name]-{unique_hash}.[hash].js`,
        assetFileNames: `assets/[name]-{unique_hash}.[hash].[ext]`
      }}
    }}
  }},'''
                    )
            
            with open(vite_config_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ vite.config.ts atualizado com hash: {unique_hash}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao atualizar vite.config.ts: {e}")
            return False
    
    def update_index_html(self) -> bool:
        """Atualiza index.html com meta tags únicas"""
        index_path = self.frontend_path / "index.html"
        
        if not index_path.exists():
            print("❌ index.html não encontrado")
            return False
        
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remover meta tags antigas de cache bust
            import re
            content = re.sub(r'<meta name="cache-bust"[^>]*>', '', content)
            content = re.sub(r'<meta name="build-time"[^>]*>', '', content)
            content = re.sub(r'<meta name="version"[^>]*>', '', content)
            
            # Adicionar novas meta tags
            unique_id = self.generate_unique_hash()
            new_meta_tags = f'''<meta name="cache-bust" content="{self.timestamp}">
    <meta name="build-time" content="{datetime.now().isoformat()}">
    <meta name="version" content="{unique_id}">
    <meta name="force-reload" content="true">'''
            
            if '<head>' in content:
                content = content.replace('<head>', f'<head>\n    {new_meta_tags}')
            
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ index.html atualizado com versão: {unique_id}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao atualizar index.html: {e}")
            return False
    
    def clean_all_cache(self) -> bool:
        """Remove todos os caches possíveis"""
        print("🧹 Limpando todos os caches...")
        
        cache_dirs = [
            self.frontend_path / "node_modules" / ".cache",
            self.frontend_path / ".vite",
            self.frontend_path / "dist",
            self.frontend_path / "build"
        ]
        
        success = True
        
        for cache_dir in cache_dirs:
            if cache_dir.exists():
                try:
                    shutil.rmtree(cache_dir)
                    print(f"   ✅ {cache_dir.name} removido")
                except Exception as e:
                    print(f"   ❌ Erro ao remover {cache_dir.name}: {e}")
                    success = False
            else:
                print(f"   ℹ️ {cache_dir.name} não encontrado")
        
        return success
    
    def reinstall_dependencies(self) -> bool:
        """Reinstala dependências do zero"""
        print("📦 Reinstalando dependências...")
        
        try:
            os.chdir(self.frontend_path)
            
            # Remover package-lock.json
            lock_file = Path("package-lock.json")
            if lock_file.exists():
                lock_file.unlink()
                print("   ✅ package-lock.json removido")
            
            # Instalar dependências
            result = subprocess.run(
                ['npm', 'install', '--force'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                print("   ✅ Dependências instaladas com sucesso")
                return True
            else:
                print(f"   ❌ Erro na instalação: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"   ❌ Erro ao instalar dependências: {e}")
            return False
        finally:
            os.chdir(self.project_root)
    
    def build_with_unique_hash(self) -> bool:
        """Faz build com hash único"""
        print("🔨 Fazendo build com hash único...")
        
        try:
            os.chdir(self.frontend_path)
            
            # Variáveis de ambiente para forçar novo build
            env = os.environ.copy()
            env['VITE_BUILD_TIME'] = str(self.timestamp)
            env['VITE_FORCE_REBUILD'] = 'true'
            env['VITE_CACHE_BUST'] = self.generate_unique_hash()
            
            result = subprocess.run(
                ['npm', 'run', 'build'],
                capture_output=True,
                text=True,
                env=env,
                timeout=300
            )
            
            if result.returncode == 0:
                print("   ✅ Build concluído com sucesso")
                
                # Verificar se novos arquivos foram gerados
                dist_path = Path("dist/assets")
                if dist_path.exists():
                    js_files = list(dist_path.glob("index-*.js"))
                    if js_files:
                        latest_file = max(js_files, key=lambda x: x.stat().st_mtime)
                        print(f"   📄 Novo arquivo JS: {latest_file.name}")
                        return True
                
                return True
            else:
                print(f"   ❌ Erro no build: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"   ❌ Erro ao fazer build: {e}")
            return False
        finally:
            os.chdir(self.project_root)
    
    def create_cache_bust_file(self) -> bool:
        """Cria arquivo para forçar atualização do CDN"""
        try:
            cache_bust_content = {
                'timestamp': self.timestamp,
                'version': self.generate_unique_hash(),
                'build_time': datetime.now().isoformat(),
                'force_update': True
            }
            
            # Salvar no frontend
            cache_file = self.frontend_path / "dist" / "cache-bust.json"
            cache_file.parent.mkdir(exist_ok=True)
            
            with open(cache_file, 'w') as f:
                json.dump(cache_bust_content, f, indent=2)
            
            # Salvar na raiz também
            with open("cache-bust.json", 'w') as f:
                json.dump(cache_bust_content, f, indent=2)
            
            print(f"✅ Arquivo cache-bust criado: {cache_bust_content['version']}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar cache-bust: {e}")
            return False
    
    def run_complete_update(self) -> bool:
        """Executa atualização completa"""
        print("🚀 ATUALIZAÇÃO FORÇADA DO FRONTEND - 1CRYPTEN")
        print("="*70)
        print(f"⏰ Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"🔢 Timestamp: {self.timestamp}")
        print()
        
        success = True
        
        # 1. Limpar todos os caches
        print("🧹 FASE 1: Limpeza completa")
        if not self.clean_all_cache():
            success = False
        
        # 2. Atualizar configurações
        print("\n⚙️ FASE 2: Atualização de configurações")
        if not self.update_vite_config():
            success = False
        if not self.update_index_html():
            success = False
        
        # 3. Reinstalar dependências
        print("\n📦 FASE 3: Reinstalação de dependências")
        if not self.reinstall_dependencies():
            success = False
        
        # 4. Build com hash único
        print("\n🔨 FASE 4: Build com hash único")
        if not self.build_with_unique_hash():
            success = False
        
        # 5. Criar arquivo cache-bust
        print("\n📄 FASE 5: Cache-bust")
        if not self.create_cache_bust_file():
            success = False
        
        # Resumo
        print("\n" + "="*70)
        print("📋 RESUMO DA ATUALIZAÇÃO")
        print("="*70)
        
        if success:
            print("\n✅ ATUALIZAÇÃO FORÇADA CONCLUÍDA COM SUCESSO!")
            print(f"\n🎯 Nova versão: {self.generate_unique_hash()}")
            print(f"🕐 Timestamp: {self.timestamp}")
            print("\n🚀 Próximos passos:")
            print("   1. Aguarde 2-3 minutos para deploy")
            print("   2. Acesse com timestamp: https://1crypten.space?t=" + str(self.timestamp))
            print("   3. Ou force refresh: Ctrl+Shift+R")
            print("   4. Verifique se vê novo arquivo JS (não index-DgCrHUEN.js)")
        else:
            print("\n⚠️ Atualização concluída com alguns erros")
            print("\n🔧 Tente:")
            print("   1. Verificar permissões de arquivo")
            print("   2. Fechar editores/IDEs")
            print("   3. Executar novamente")
        
        return success

def main():
    """Função principal"""
    updater = FrontendForceUpdate()
    
    try:
        success = updater.run_complete_update()
        
        if success:
            print("\n🎉 FRONTEND ATUALIZADO COM SUCESSO!")
            print("\n⚡ AÇÃO NECESSÁRIA:")
            print("   1. Aguarde 2-3 minutos")
            print("   2. Acesse: https://1crypten.space?t=" + str(updater.timestamp))
            print("   3. Verifique se os erros 503 sumiram")
            return 0
        else:
            print("\n❌ FALHA NA ATUALIZAÇÃO")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Operação cancelada")
        return 1
    except Exception as e:
        print(f"\n\n❌ Erro inesperado: {e}")
        return 1

if __name__ == '__main__':
    exit(main())