#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Monitoramento de Timeout
Detecta e resolve problemas de Gateway Timeout automaticamente
"""

import requests
import time
import subprocess
import logging
from datetime import datetime
import os
import sys

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('timeout_monitor.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class TimeoutMonitor:
    """Monitor de timeout para detectar e resolver problemas"""
    
    def __init__(self):
        self.api_url = "https://1crypten.space/api/status"
        self.max_timeout_count = 3
        self.timeout_count = 0
        self.check_interval = 30  # segundos
        self.request_timeout = 10  # segundos
        
    def check_api_health(self) -> bool:
        """Verifica se a API está respondendo corretamente"""
        try:
            response = requests.get(
                self.api_url, 
                timeout=self.request_timeout,
                headers={'User-Agent': 'TimeoutMonitor/1.0'}
            )
            
            if response.status_code == 200:
                logger.info(f"✅ API respondendo normalmente - Status: {response.status_code}")
                self.timeout_count = 0
                return True
            else:
                logger.warning(f"⚠️ API retornou status não esperado: {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            logger.error("❌ Timeout detectado na API")
            self.timeout_count += 1
            return False
            
        except requests.exceptions.ConnectionError:
            logger.error("❌ Erro de conexão com a API")
            self.timeout_count += 1
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro inesperado: {e}")
            self.timeout_count += 1
            return False
    
    def restart_services(self):
        """Reinicia os serviços quando detecta muitos timeouts"""
        logger.warning(f"🔄 Reiniciando serviços após {self.timeout_count} timeouts consecutivos")
        
        try:
            # Reiniciar containers Docker
            subprocess.run([
                'docker-compose', '-f', 'docker-compose.prod.yml', 
                'restart', 'backend', 'nginx'
            ], check=True, cwd='/app')
            
            logger.info("✅ Serviços reiniciados com sucesso")
            self.timeout_count = 0
            
            # Aguardar serviços subirem
            time.sleep(60)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Erro ao reiniciar serviços: {e}")
        except Exception as e:
            logger.error(f"❌ Erro inesperado ao reiniciar: {e}")
    
    def send_alert(self, message: str):
        """Envia alerta sobre problemas detectados"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        alert_message = f"[{timestamp}] ALERTA TIMEOUT: {message}"
        
        # Log do alerta
        logger.critical(alert_message)
        
        # Aqui você pode adicionar integração com Telegram, email, etc.
        # Por exemplo:
        # self.send_telegram_alert(alert_message)
        # self.send_email_alert(alert_message)
    
    def run_monitoring(self):
        """Executa o monitoramento contínuo"""
        logger.info("🚀 Iniciando monitoramento de timeout...")
        logger.info(f"📊 URL monitorada: {self.api_url}")
        logger.info(f"⏱️ Intervalo de verificação: {self.check_interval}s")
        logger.info(f"🔄 Limite de timeouts: {self.max_timeout_count}")
        
        while True:
            try:
                is_healthy = self.check_api_health()
                
                if not is_healthy:
                    if self.timeout_count >= self.max_timeout_count:
                        self.send_alert(f"Detectados {self.timeout_count} timeouts consecutivos")
                        self.restart_services()
                    else:
                        logger.warning(f"⚠️ Timeout {self.timeout_count}/{self.max_timeout_count}")
                
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                logger.info("👋 Monitoramento interrompido pelo usuário")
                break
            except Exception as e:
                logger.error(f"❌ Erro no loop de monitoramento: {e}")
                time.sleep(self.check_interval)

def main():
    """Função principal"""
    monitor = TimeoutMonitor()
    monitor.run_monitoring()

if __name__ == "__main__":
    main()