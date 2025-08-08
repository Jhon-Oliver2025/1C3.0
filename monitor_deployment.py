#!/usr/bin/env python3
"""
Script para monitorar o deployment da aplicação no Coolify.
Monitora continuamente o endpoint de health e outros indicadores.
"""

import requests
import time
import sys
import os
from datetime import datetime
from urllib.parse import urljoin

class DeploymentMonitor:
    """
    Monitor de deployment para acompanhar o status da aplicação.
    """
    
    def __init__(self, base_url="https://1crypten.space", check_interval=10):
        """
        Inicializa o monitor de deployment.
        
        Args:
            base_url (str): URL base da aplicação
            check_interval (int): Intervalo entre verificações em segundos
        """
        self.base_url = base_url
        self.check_interval = check_interval
        self.health_url = urljoin(base_url, "/api/health")
        self.start_time = datetime.now()
        self.successful_checks = 0
        self.failed_checks = 0
        
    def log_message(self, message, level="INFO"):
        """
        Registra uma mensagem com timestamp.
        
        Args:
            message (str): Mensagem a ser registrada
            level (str): Nível do log (INFO, SUCCESS, WARNING, ERROR)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elapsed = datetime.now() - self.start_time
        elapsed_str = str(elapsed).split('.')[0]  # Remove microsegundos
        
        icons = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "CHECKING": "🔄"
        }
        
        icon = icons.get(level, "📝")
        print(f"[{timestamp}] [{elapsed_str}] {icon} {message}")
        
    def check_health(self):
        """
        Verifica o endpoint de health.
        
        Returns:
            dict: Resultado da verificação com status e detalhes
        """
        try:
            response = requests.get(self.health_url, timeout=15)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, dict) and data.get('status') == 'healthy':
                        return {
                            'success': True,
                            'status_code': response.status_code,
                            'data': data,
                            'response_time': response.elapsed.total_seconds()
                        }
                    else:
                        return {
                            'success': False,
                            'status_code': response.status_code,
                            'error': f"Status inesperado: {data}",
                            'response_time': response.elapsed.total_seconds()
                        }
                except ValueError:
                    return {
                        'success': False,
                        'status_code': response.status_code,
                        'error': f"Resposta não é JSON: {response.text[:100]}",
                        'response_time': response.elapsed.total_seconds()
                    }
            else:
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'error': f"HTTP {response.status_code}: {response.text[:100]}",
                    'response_time': response.elapsed.total_seconds()
                }
                
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': "Erro de conexão - aplicação pode estar iniciando"
            }
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': "Timeout - aplicação não respondeu em 15s"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Erro inesperado: {str(e)}"
            }
    
    def check_frontend(self):
        """
        Verifica se o frontend está respondendo.
        
        Returns:
            bool: True se o frontend estiver acessível
        """
        try:
            response = requests.get(self.base_url, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def print_statistics(self):
        """
        Imprime estatísticas do monitoramento.
        """
        total_checks = self.successful_checks + self.failed_checks
        success_rate = (self.successful_checks / total_checks * 100) if total_checks > 0 else 0
        elapsed = datetime.now() - self.start_time
        
        print("\n" + "=" * 60)
        print("📊 ESTATÍSTICAS DO MONITORAMENTO")
        print("=" * 60)
        print(f"⏱️  Tempo de monitoramento: {str(elapsed).split('.')[0]}")
        print(f"✅ Verificações bem-sucedidas: {self.successful_checks}")
        print(f"❌ Verificações falharam: {self.failed_checks}")
        print(f"📈 Taxa de sucesso: {success_rate:.1f}%")
        print(f"🎯 URL monitorada: {self.health_url}")
        print("=" * 60)
    
    def monitor(self, max_duration_minutes=30):
        """
        Inicia o monitoramento contínuo.
        
        Args:
            max_duration_minutes (int): Duração máxima do monitoramento em minutos
        """
        self.log_message(f"Iniciando monitoramento de deployment", "INFO")
        self.log_message(f"URL alvo: {self.health_url}", "INFO")
        self.log_message(f"Intervalo de verificação: {self.check_interval}s", "INFO")
        self.log_message(f"Duração máxima: {max_duration_minutes} minutos", "INFO")
        print("\n" + "-" * 60)
        
        max_duration_seconds = max_duration_minutes * 60
        consecutive_successes = 0
        
        try:
            while True:
                elapsed = (datetime.now() - self.start_time).total_seconds()
                
                if elapsed > max_duration_seconds:
                    self.log_message(f"Tempo limite de {max_duration_minutes} minutos atingido", "WARNING")
                    break
                
                self.log_message("Verificando health endpoint...", "CHECKING")
                result = self.check_health()
                
                if result['success']:
                    self.successful_checks += 1
                    consecutive_successes += 1
                    response_time = result.get('response_time', 0)
                    self.log_message(
                        f"Aplicação saudável! (tempo: {response_time:.2f}s, consecutivos: {consecutive_successes})", 
                        "SUCCESS"
                    )
                    
                    # Se tiver 3 sucessos consecutivos, considerar deployment bem-sucedido
                    if consecutive_successes >= 3:
                        self.log_message("🎉 DEPLOYMENT BEM-SUCEDIDO! Aplicação está estável.", "SUCCESS")
                        
                        # Verificar frontend também
                        if self.check_frontend():
                            self.log_message("✅ Frontend também está acessível!", "SUCCESS")
                        else:
                            self.log_message("⚠️ Frontend pode não estar acessível ainda", "WARNING")
                        
                        self.print_statistics()
                        return True
                        
                else:
                    self.failed_checks += 1
                    consecutive_successes = 0
                    error = result.get('error', 'Erro desconhecido')
                    status_code = result.get('status_code', 'N/A')
                    self.log_message(f"Falha na verificação (HTTP {status_code}): {error}", "ERROR")
                
                # Aguardar antes da próxima verificação
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.log_message("Monitoramento interrompido pelo usuário", "WARNING")
        
        self.print_statistics()
        return False

def main():
    """
    Função principal do script.
    """
    print("🚀 Monitor de Deployment - 1Crypten")
    print("=" * 60)
    
    # Verificar argumentos da linha de comando
    base_url = sys.argv[1] if len(sys.argv) > 1 else "https://1crypten.space"
    check_interval = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    max_duration = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    
    print(f"🎯 URL: {base_url}")
    print(f"⏱️ Intervalo: {check_interval}s")
    print(f"⏰ Duração máxima: {max_duration} minutos")
    print()
    
    # Criar e iniciar monitor
    monitor = DeploymentMonitor(base_url, check_interval)
    success = monitor.monitor(max_duration)
    
    # Resultado final
    if success:
        print("\n🎉 DEPLOYMENT MONITORADO COM SUCESSO!")
        sys.exit(0)
    else:
        print("\n❌ DEPLOYMENT PODE TER FALHADO OU AINDA ESTÁ EM PROGRESSO")
        sys.exit(1)

if __name__ == "__main__":
    main()