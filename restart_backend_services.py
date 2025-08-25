#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Reinicialização de Serviços Backend - 1Crypten
Tenta reiniciar serviços com problemas identificados no diagnóstico
"""

import requests
import time
import json
from datetime import datetime
from typing import Dict, List

class BackendRestarter:
    """Reinicializador de serviços backend"""
    
    def __init__(self, base_url: str = "https://1crypten.space"):
        self.base_url = base_url
        self.restart_endpoints = {
            'restart_system': '/api/scheduler/restart-system',
            'restart_signals': '/api/signals/restart',
            'restart_market': '/api/market/restart',
            'force_restart': '/api/admin/force-restart'
        }
        self.test_endpoints = {
            'status': '/api/status',
            'market_status': '/api/market-status',
            'btc_signals': '/api/btc-signals/confirmed'
        }
        
    def test_endpoint(self, name: str, path: str, timeout: int = 5) -> bool:
        """Testa se um endpoint está funcionando"""
        url = f"{self.base_url}{path}"
        try:
            response = requests.get(url, timeout=timeout)
            return response.status_code == 200
        except:
            return False
    
    def trigger_restart(self, name: str, path: str) -> bool:
        """Tenta acionar um endpoint de restart"""
        url = f"{self.base_url}{path}"
        try:
            print(f"🔄 Tentando restart via {name}: {url}")
            response = requests.post(url, timeout=10)
            if response.status_code in [200, 202]:
                print(f"   ✅ Restart {name} acionado com sucesso")
                return True
            else:
                print(f"   ⚠️ Restart {name} retornou status {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Erro no restart {name}: {str(e)}")
            return False
    
    def wait_for_services(self, max_wait: int = 60) -> Dict[str, bool]:
        """Aguarda os serviços ficarem disponíveis"""
        print(f"\n⏳ Aguardando serviços ficarem disponíveis (máximo {max_wait}s)...")
        
        start_time = time.time()
        results = {}
        
        while time.time() - start_time < max_wait:
            all_working = True
            
            for name, path in self.test_endpoints.items():
                if name not in results:
                    if self.test_endpoint(name, path):
                        results[name] = True
                        print(f"   ✅ {name} está funcionando")
                    else:
                        all_working = False
            
            if all_working:
                print(f"\n🎉 Todos os serviços estão funcionando!")
                break
            
            time.sleep(5)
            elapsed = int(time.time() - start_time)
            print(f"   ⏳ Aguardando... ({elapsed}s/{max_wait}s)")
        
        # Verificar quais ainda não estão funcionando
        for name, path in self.test_endpoints.items():
            if name not in results:
                results[name] = False
        
        return results
    
    def run_restart_sequence(self) -> Dict:
        """Executa sequência completa de restart"""
        print("🔄 REINICIALIZAÇÃO DE SERVIÇOS BACKEND - 1CRYPTEN")
        print("="*70)
        print(f"⏰ Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print()
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'restart_attempts': [],
            'final_status': {},
            'success': False
        }
        
        # Verificar status inicial
        print("📊 Verificando status inicial...")
        initial_status = {}
        for name, path in self.test_endpoints.items():
            status = self.test_endpoint(name, path)
            initial_status[name] = status
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {name}: {'OK' if status else 'Falha'}")
        
        # Se todos estão funcionando, não precisa restart
        if all(initial_status.values()):
            print("\n✅ Todos os serviços já estão funcionando!")
            results['success'] = True
            results['final_status'] = initial_status
            return results
        
        # Tentar restarts em ordem de prioridade
        print("\n🔄 Iniciando sequência de restart...")
        
        restart_success = False
        
        # 1. Tentar restart do sistema geral
        if self.trigger_restart('sistema', '/api/scheduler/restart-system'):
            restart_success = True
            results['restart_attempts'].append({
                'method': 'system_restart',
                'success': True,
                'timestamp': datetime.now().isoformat()
            })
            
            # Aguardar um pouco após restart do sistema
            print("   ⏳ Aguardando 15 segundos após restart do sistema...")
            time.sleep(15)
        
        # 2. Se não funcionou, tentar restart específico de sinais
        if not restart_success:
            if self.trigger_restart('sinais', '/api/signals/restart'):
                restart_success = True
                results['restart_attempts'].append({
                    'method': 'signals_restart',
                    'success': True,
                    'timestamp': datetime.now().isoformat()
                })
                time.sleep(10)
        
        # 3. Tentar restart do mercado
        if self.trigger_restart('mercado', '/api/market/restart'):
            results['restart_attempts'].append({
                'method': 'market_restart',
                'success': True,
                'timestamp': datetime.now().isoformat()
            })
            time.sleep(5)
        
        # Aguardar serviços ficarem disponíveis
        final_status = self.wait_for_services()
        results['final_status'] = final_status
        results['success'] = all(final_status.values())
        
        return results
    
    def print_summary(self, results: Dict):
        """Imprime resumo dos resultados"""
        print("\n" + "="*70)
        print("📋 RESUMO DA REINICIALIZAÇÃO")
        print("="*70)
        
        success_icon = "✅" if results['success'] else "❌"
        print(f"\n{success_icon} Status Final: {'SUCESSO' if results['success'] else 'FALHA'}")
        
        print(f"\n🔄 Tentativas de Restart ({len(results['restart_attempts'])}):")
        for i, attempt in enumerate(results['restart_attempts'], 1):
            status_icon = "✅" if attempt['success'] else "❌"
            print(f"   {i}. {status_icon} {attempt['method']} - {attempt['timestamp'][:19]}")
        
        print(f"\n📊 Status Final dos Serviços:")
        for name, status in results['final_status'].items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {name}: {'Funcionando' if status else 'Com problemas'}")
        
        if results['success']:
            print("\n🎉 Todos os serviços foram reinicializados com sucesso!")
            print("💡 Recomendações:")
            print("   1. Monitorar estabilidade por alguns minutos")
            print("   2. Verificar logs para garantir funcionamento normal")
            print("   3. Testar funcionalidades críticas")
        else:
            print("\n⚠️ Alguns serviços ainda apresentam problemas")
            print("💡 Próximos passos:")
            print("   1. Verificar logs detalhados do backend")
            print("   2. Considerar restart manual do servidor")
            print("   3. Verificar configuração de rede/proxy")
            print("   4. Contatar suporte técnico se necessário")
    
    def save_report(self, results: Dict, filename: str = "restart_report.json"):
        """Salva relatório de restart"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Relatório salvo em: {filename}")
        return filename

def main():
    """Função principal"""
    restarter = BackendRestarter()
    
    # Executar sequência de restart
    results = restarter.run_restart_sequence()
    
    # Salvar relatório
    restarter.save_report(results)
    
    # Mostrar resumo
    restarter.print_summary(results)
    
    return results

if __name__ == '__main__':
    main()