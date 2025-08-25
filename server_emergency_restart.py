#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de reinicialização emergencial do servidor - 1Crypten
Para resolver Gateway Timeout e problemas de conectividade
"""

import requests
import time
import json
from datetime import datetime
from typing import Dict, List

class ServerEmergencyRestart:
    """Reinicialização emergencial do servidor"""
    
    def __init__(self):
        self.base_url = "https://1crypten.space"
        self.endpoints = {
            'health': '/api/health',
            'status': '/api/status',
            'market_status': '/api/market-status',
            'btc_signals': '/api/btc-signals/confirmed',
            'restart_system': '/api/restart-system'
        }
        self.timeout = 10
        
    def check_endpoint(self, endpoint: str, name: str) -> Dict:
        """Verifica status de um endpoint"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            print(f"🔍 Testando {name}: {url}")
            
            response = requests.get(
                url, 
                timeout=self.timeout,
                headers={'User-Agent': 'Emergency-Restart-Script/1.0'}
            )
            
            status = {
                'name': name,
                'url': url,
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'success': response.status_code == 200,
                'error': None
            }
            
            if response.status_code == 200:
                print(f"   ✅ {name}: OK ({response.status_code}) - {response.elapsed.total_seconds():.2f}s")
            else:
                print(f"   ❌ {name}: ERRO {response.status_code} - {response.elapsed.total_seconds():.2f}s")
                
            return status
            
        except requests.exceptions.Timeout:
            print(f"   ⏰ {name}: TIMEOUT (>{self.timeout}s)")
            return {
                'name': name,
                'url': url,
                'status_code': 408,
                'response_time': self.timeout,
                'success': False,
                'error': 'Timeout'
            }
            
        except requests.exceptions.ConnectionError:
            print(f"   🔌 {name}: CONEXÃO RECUSADA")
            return {
                'name': name,
                'url': url,
                'status_code': 0,
                'response_time': 0,
                'success': False,
                'error': 'Connection Error'
            }
            
        except Exception as e:
            print(f"   ❌ {name}: ERRO - {str(e)}")
            return {
                'name': name,
                'url': url,
                'status_code': 0,
                'response_time': 0,
                'success': False,
                'error': str(e)
            }
    
    def force_restart_system(self) -> bool:
        """Força reinicialização do sistema"""
        print("\n🔄 Tentando forçar reinicialização do sistema...")
        
        restart_url = f"{self.base_url}{self.endpoints['restart_system']}"
        
        try:
            response = requests.post(
                restart_url,
                timeout=30,
                headers={
                    'User-Agent': 'Emergency-Restart-Script/1.0',
                    'Content-Type': 'application/json'
                },
                json={'force': True, 'emergency': True}
            )
            
            if response.status_code == 200:
                print("   ✅ Comando de restart enviado com sucesso")
                return True
            else:
                print(f"   ❌ Falha no restart: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Erro ao enviar comando de restart: {e}")
            return False
    
    def wait_for_recovery(self, max_wait: int = 120) -> bool:
        """Aguarda recuperação do servidor"""
        print(f"\n⏳ Aguardando recuperação do servidor (máximo {max_wait}s)...")
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            elapsed = int(time.time() - start_time)
            print(f"   🕐 {elapsed}s - Testando conectividade...")
            
            # Testar endpoint mais simples primeiro
            health_status = self.check_endpoint(self.endpoints['health'], 'health')
            
            if health_status['success']:
                print(f"   ✅ Servidor respondeu após {elapsed}s!")
                return True
            
            time.sleep(5)
        
        print(f"   ❌ Timeout: Servidor não respondeu em {max_wait}s")
        return False
    
    def comprehensive_check(self) -> Dict:
        """Verificação completa de todos os endpoints"""
        print("\n📊 Verificação completa de endpoints...")
        
        results = []
        
        for endpoint_key, endpoint_path in self.endpoints.items():
            if endpoint_key != 'restart_system':  # Não testar endpoint de restart
                result = self.check_endpoint(endpoint_path, endpoint_key)
                results.append(result)
                time.sleep(1)  # Pequena pausa entre testes
        
        # Calcular estatísticas
        total_endpoints = len(results)
        working_endpoints = sum(1 for r in results if r['success'])
        avg_response_time = sum(r['response_time'] for r in results if r['success']) / max(working_endpoints, 1)
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_endpoints': total_endpoints,
            'working_endpoints': working_endpoints,
            'failed_endpoints': total_endpoints - working_endpoints,
            'success_rate': (working_endpoints / total_endpoints) * 100,
            'avg_response_time': avg_response_time,
            'results': results
        }
        
        print(f"\n📈 Resumo:")
        print(f"   📊 Endpoints funcionando: {working_endpoints}/{total_endpoints} ({summary['success_rate']:.1f}%)")
        print(f"   ⏱️ Tempo médio de resposta: {avg_response_time:.2f}s")
        
        return summary
    
    def run_emergency_restart(self) -> bool:
        """Executa reinicialização emergencial completa"""
        print("🚨 REINICIALIZAÇÃO EMERGENCIAL DO SERVIDOR - 1CRYPTEN")
        print("="*70)
        print(f"⏰ Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print()
        
        # 1. Verificação inicial
        print("🔍 FASE 1: Verificação inicial")
        initial_check = self.comprehensive_check()
        
        if initial_check['success_rate'] >= 80:
            print("\n✅ Servidor está funcionando bem (>80% dos endpoints OK)")
            return True
        
        # 2. Tentar restart
        print("\n🔄 FASE 2: Tentativa de restart")
        restart_success = self.force_restart_system()
        
        if restart_success:
            # 3. Aguardar recuperação
            print("\n⏳ FASE 3: Aguardando recuperação")
            recovery_success = self.wait_for_recovery()
            
            if recovery_success:
                # 4. Verificação final
                print("\n✅ FASE 4: Verificação final")
                final_check = self.comprehensive_check()
                
                if final_check['success_rate'] >= 80:
                    print("\n🎉 REINICIALIZAÇÃO EMERGENCIAL CONCLUÍDA COM SUCESSO!")
                    return True
                else:
                    print("\n⚠️ Servidor respondeu mas alguns endpoints ainda com problema")
                    return False
            else:
                print("\n❌ Servidor não respondeu após restart")
                return False
        else:
            print("\n❌ Falha ao enviar comando de restart")
            return False
    
    def save_report(self, data: Dict, filename: str = "emergency_restart_report.json"):
        """Salva relatório em arquivo"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"\n📄 Relatório salvo em: {filename}")
        except Exception as e:
            print(f"\n❌ Erro ao salvar relatório: {e}")

def main():
    """Função principal"""
    restart_manager = ServerEmergencyRestart()
    
    try:
        success = restart_manager.run_emergency_restart()
        
        # Verificação final e relatório
        final_status = restart_manager.comprehensive_check()
        restart_manager.save_report(final_status)
        
        if success:
            print("\n✅ EMERGÊNCIA RESOLVIDA!")
            print("\n🎯 Próximos passos:")
            print("   1. Testar aplicação no browser")
            print("   2. Limpar cache se necessário (Ctrl+F5)")
            print("   3. Monitorar estabilidade")
            return 0
        else:
            print("\n❌ FALHA NA RESOLUÇÃO DA EMERGÊNCIA")
            print("\n🔧 Ações recomendadas:")
            print("   1. Verificar logs do servidor")
            print("   2. Contatar administrador do sistema")
            print("   3. Verificar status do provedor de hospedagem")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Operação cancelada pelo usuário")
        return 1
    except Exception as e:
        print(f"\n\n❌ Erro inesperado: {e}")
        return 1

if __name__ == '__main__':
    exit(main())