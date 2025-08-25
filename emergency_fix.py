#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de correção emergencial - 1Crypten
Resolve problemas de cache e força atualização imediata
"""

import os
import shutil
import subprocess
import time
import json
from datetime import datetime
from pathlib import Path

def emergency_fix():
    """Correção emergencial completa"""
    print("🚨 CORREÇÃO EMERGENCIAL - 1CRYPTEN")
    print("="*50)
    print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    # 1. Forçar rebuild com timestamp único
    print("🔨 Forçando rebuild com timestamp único...")
    
    # Navegar para frontend
    frontend_path = Path("front")
    if not frontend_path.exists():
        print("❌ Diretório frontend não encontrado!")
        return False
    
    os.chdir(frontend_path)
    
    # Adicionar timestamp ao build
    timestamp = int(time.time())
    
    # Modificar index.html para forçar cache bust
    index_path = Path("index.html")
    if index_path.exists():
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Adicionar meta tag para cache bust
        cache_bust = f'<meta name="cache-bust" content="{timestamp}">'    
        if '<head>' in content and cache_bust not in content:
            content = content.replace('<head>', f'<head>\n    {cache_bust}')
            
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"   ✅ Cache bust adicionado: {timestamp}")
    
    # Fazer build com variável de ambiente única
    env = os.environ.copy()
    env['VITE_BUILD_TIME'] = str(timestamp)
    env['VITE_CACHE_BUST'] = str(timestamp)
    
    print("🔄 Fazendo novo build...")
    try:
        result = subprocess.run(
            ['npm', 'run', 'build'],
            capture_output=True,
            text=True,
            env=env,
            timeout=120
        )
        
        if result.returncode == 0:
            print("   ✅ Build concluído com sucesso")
        else:
            print(f"   ❌ Erro no build: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro ao fazer build: {e}")
        return False
    
    # Voltar ao diretório raiz
    os.chdir('..')
    
    # 2. Criar arquivo de status para verificação
    status_file = {
        'timestamp': timestamp,
        'build_time': datetime.now().isoformat(),
        'version': f"emergency-fix-{timestamp}",
        'status': 'ready'
    }
    
    with open('emergency_status.json', 'w') as f:
        json.dump(status_file, f, indent=2)
    
    print(f"\n✅ CORREÇÃO EMERGENCIAL CONCLUÍDA!")
    print(f"🕐 Timestamp: {timestamp}")
    print(f"📁 Arquivos atualizados com cache bust")
    print(f"🔄 Novo build gerado")
    
    print(f"\n📋 INSTRUÇÕES PARA O USUÁRIO:")
    print(f"1. Pressione Ctrl+Shift+Delete")
    print(f"2. Limpe 'Imagens e arquivos em cache'")
    print(f"3. Pressione Ctrl+F5 para hard refresh")
    print(f"4. Ou acesse: https://1crypten.space?v={timestamp}")
    
    return True

def check_current_version():
    """Verifica versão atual"""
    dist_path = Path("front/dist")
    if dist_path.exists():
        js_files = list(dist_path.glob("assets/index-*.js"))
        if js_files:
            latest_file = max(js_files, key=lambda x: x.stat().st_mtime)
            print(f"📄 Arquivo JS atual: {latest_file.name}")
            return latest_file.name
    return None

def main():
    """Função principal"""
    print("🔍 Verificando versão atual...")
    current_version = check_current_version()
    
    if current_version:
        print(f"   Versão encontrada: {current_version}")
    
    print("\n🚨 Iniciando correção emergencial...")
    success = emergency_fix()
    
    if success:
        print("\n🎉 CORREÇÃO CONCLUÍDA COM SUCESSO!")
        print("\n⚡ AÇÃO IMEDIATA NECESSÁRIA:")
        print("   1. Limpe o cache do browser (Ctrl+Shift+Delete)")
        print("   2. Faça hard refresh (Ctrl+F5)")
        print("   3. Os erros 503 devem ser resolvidos")
        
        new_version = check_current_version()
        if new_version and new_version != current_version:
            print(f"\n✅ Nova versão gerada: {new_version}")
        
        return 0
    else:
        print("\n❌ FALHA NA CORREÇÃO")
        return 1

if __name__ == '__main__':
    exit(main())