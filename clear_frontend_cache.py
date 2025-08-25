#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para limpar cache do frontend e forçar rebuild - 1Crypten
Resolve problemas de cache que podem estar causando erros 503
"""

import os
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path

class FrontendCacheCleaner:
    """Limpador de cache do frontend"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.frontend_path = self.project_root / "front"
        
    def clear_node_modules(self) -> bool:
        """Remove node_modules para forçar reinstalação"""
        node_modules_path = self.frontend_path / "node_modules"
        
        if node_modules_path.exists():
            print("🗑️ Removendo node_modules...")
            try:
                shutil.rmtree(node_modules_path)
                print("   ✅ node_modules removido")
                return True
            except Exception as e:
                print(f"   ❌ Erro ao remover node_modules: {e}")
                return False
        else:
            print("   ℹ️ node_modules não encontrado")
            return True
    
    def clear_dist_build(self) -> bool:
        """Remove diretórios de build"""
        build_dirs = ['dist', 'build', '.vite']
        success = True
        
        for build_dir in build_dirs:
            build_path = self.frontend_path / build_dir
            if build_path.exists():
                print(f"🗑️ Removendo {build_dir}...")
                try:
                    shutil.rmtree(build_path)
                    print(f"   ✅ {build_dir} removido")
                except Exception as e:
                    print(f"   ❌ Erro ao remover {build_dir}: {e}")
                    success = False
            else:
                print(f"   ℹ️ {build_dir} não encontrado")
        
        return success
    
    def clear_package_lock(self) -> bool:
        """Remove package-lock.json para forçar nova resolução"""
        lock_files = ['package-lock.json', 'yarn.lock', 'pnpm-lock.yaml']
        
        for lock_file in lock_files:
            lock_path = self.frontend_path / lock_file
            if lock_path.exists():
                print(f"🗑️ Removendo {lock_file}...")
                try:
                    lock_path.unlink()
                    print(f"   ✅ {lock_file} removido")
                except Exception as e:
                    print(f"   ❌ Erro ao remover {lock_file}: {e}")
                    return False
        
        return True
    
    def reinstall_dependencies(self) -> bool:
        """Reinstala dependências do npm"""
        print("📦 Reinstalando dependências...")
        
        try:
            # Mudar para o diretório frontend
            os.chdir(self.frontend_path)
            
            # Instalar dependências
            result = subprocess.run(
                ['npm', 'install'], 
                capture_output=True, 
                text=True,
                timeout=300  # 5 minutos timeout
            )
            
            if result.returncode == 0:
                print("   ✅ Dependências instaladas com sucesso")
                return True
            else:
                print(f"   ❌ Erro na instalação: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("   ❌ Timeout na instalação de dependências")
            return False
        except Exception as e:
            print(f"   ❌ Erro ao instalar dependências: {e}")
            return False
        finally:
            # Voltar ao diretório original
            os.chdir(self.project_root)
    
    def build_frontend(self) -> bool:
        """Faz build do frontend"""
        print("🔨 Fazendo build do frontend...")
        
        try:
            # Mudar para o diretório frontend
            os.chdir(self.frontend_path)
            
            # Fazer build
            result = subprocess.run(
                ['npm', 'run', 'build'], 
                capture_output=True, 
                text=True,
                timeout=300  # 5 minutos timeout
            )
            
            if result.returncode == 0:
                print("   ✅ Build concluído com sucesso")
                return True
            else:
                print(f"   ❌ Erro no build: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("   ❌ Timeout no build")
            return False
        except Exception as e:
            print(f"   ❌ Erro ao fazer build: {e}")
            return False
        finally:
            # Voltar ao diretório original
            os.chdir(self.project_root)
    
    def clear_browser_cache_instructions(self):
        """Mostra instruções para limpar cache do browser"""
        print("\n🌐 INSTRUÇÕES PARA LIMPAR CACHE DO BROWSER:")
        print("="*60)
        print("\n📋 Chrome/Edge:")
        print("   1. Pressione Ctrl+Shift+Delete")
        print("   2. Selecione 'Todo o período'")
        print("   3. Marque 'Imagens e arquivos em cache'")
        print("   4. Clique em 'Limpar dados'")
        print("   5. Pressione Ctrl+F5 para hard refresh")
        
        print("\n📋 Firefox:")
        print("   1. Pressione Ctrl+Shift+Delete")
        print("   2. Selecione 'Tudo'")
        print("   3. Marque 'Cache'")
        print("   4. Clique em 'Limpar agora'")
        print("   5. Pressione Ctrl+F5 para hard refresh")
        
        print("\n📋 Alternativa rápida:")
        print("   1. Abra DevTools (F12)")
        print("   2. Clique com botão direito no botão refresh")
        print("   3. Selecione 'Esvaziar cache e recarregar forçadamente'")
    
    def run_complete_cleanup(self) -> bool:
        """Executa limpeza completa"""
        print("🧹 LIMPEZA COMPLETA DE CACHE FRONTEND - 1CRYPTEN")
        print("="*70)
        print(f"⏰ Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print()
        
        success = True
        
        # 1. Limpar cache de build
        print("📂 Limpando cache de build...")
        if not self.clear_dist_build():
            success = False
        
        # 2. Limpar node_modules
        print("\n📦 Limpando node_modules...")
        if not self.clear_node_modules():
            success = False
        
        # 3. Limpar package-lock
        print("\n🔒 Limpando arquivos de lock...")
        if not self.clear_package_lock():
            success = False
        
        # 4. Reinstalar dependências
        print("\n📥 Reinstalando dependências...")
        if not self.reinstall_dependencies():
            success = False
        
        # 5. Fazer novo build
        print("\n🔨 Fazendo novo build...")
        if not self.build_frontend():
            success = False
        
        # 6. Instruções para browser
        self.clear_browser_cache_instructions()
        
        # Resumo
        print("\n" + "="*70)
        print("📋 RESUMO DA LIMPEZA")
        print("="*70)
        
        if success:
            print("\n✅ Limpeza concluída com sucesso!")
            print("\n🎯 Próximos passos:")
            print("   1. Limpar cache do browser (instruções acima)")
            print("   2. Fazer hard refresh (Ctrl+F5)")
            print("   3. Testar a aplicação")
            print("   4. Verificar se erros 503 foram resolvidos")
        else:
            print("\n⚠️ Limpeza concluída com alguns erros")
            print("\n🔧 Tente:")
            print("   1. Executar novamente o script")
            print("   2. Verificar permissões de arquivo")
            print("   3. Fechar editores/IDEs que possam estar bloqueando")
        
        return success

def main():
    """Função principal"""
    cleaner = FrontendCacheCleaner()
    success = cleaner.run_complete_cleanup()
    
    if success:
        print("\n🎉 Cache limpo com sucesso!")
        return 0
    else:
        print("\n❌ Falha na limpeza de cache")
        return 1

if __name__ == '__main__':
    exit(main())