#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Diagnóstico para Gateway Timeout 504 em Produção
Este script identifica e resolve problemas de timeout no ambiente de produção.
"""

import requests
import time
import json
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Any

class TimeoutDiagnostic:
    """
    Classe para diagnosticar problemas de Gateway Timeout 504
    """
    
    def __init__(self, domain: str = "1crypten.space"):
        self.domain = domain
        self.base_url = f"https://{domain}"
        self.results = []
        
    def log_result(self, test_name: str, status: str, details: str, response_time: float = 0):
        """
        Registra resultado de um teste
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "test": test_name,
            "status": status,
            "details": details,
            "response_time": response_time
        }
        self.results.append(result)
        
        # Log colorido no console
        color = "\033[92m" if status == "PASS" else "\033[91m" if status == "FAIL" else "\033[93m"
        reset = "\033[0m"
        print(f"{color}[{status}]{reset} {test_name}: {details} ({response_time:.2f}s)")
    
    def test_basic_connectivity(self):
        """
        Testa conectividade básica com o domínio
        """
        print("\n🔍 Testando conectividade básica...")
        
        try:
            start_time = time.time()
            response = requests.get(self.base_url, timeout=30)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                self.log_result("Conectividade Básica", "PASS", 
                              f"Status {response.status_code}", response_time)
            else:
                self.log_result("Conectividade Básica", "WARN", 
                              f"Status {response.status_code}", response_time)
                
        except requests.exceptions.Timeout:
            self.log_result("Conectividade Básica", "FAIL", 
                          "Timeout após 30s", 30.0)
        except Exception as e:
            self.log_result("Conectividade Básica", "FAIL", 
                          f"Erro: {str(e)}", 0)
    
    def test_api_endpoints(self):
        """
        Testa endpoints específicos da API
        """
        print("\n🔍 Testando endpoints da API...")
        
        endpoints = [
            "/api/status",
            "/api/btc-signals/confirmed",
            "/manifest.json",
            "/logo3.png"
        ]
        
        for endpoint in endpoints:
            try:
                start_time = time.time()
                url = f"{self.base_url}{endpoint}"
                response = requests.get(url, timeout=60)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    self.log_result(f"Endpoint {endpoint}", "PASS", 
                                  f"Status {response.status_code}", response_time)
                elif response.status_code == 504:
                    self.log_result(f"Endpoint {endpoint}", "FAIL", 
                                  "Gateway Timeout 504", response_time)
                else:
                    self.log_result(f"Endpoint {endpoint}", "WARN", 
                                  f"Status {response.status_code}", response_time)
                    
            except requests.exceptions.Timeout:
                self.log_result(f"Endpoint {endpoint}", "FAIL", 
                              "Timeout após 60s", 60.0)
            except Exception as e:
                self.log_result(f"Endpoint {endpoint}", "FAIL", 
                              f"Erro: {str(e)}", 0)
    
    def test_server_response_times(self):
        """
        Testa tempos de resposta em múltiplas tentativas
        """
        print("\n🔍 Testando tempos de resposta...")
        
        response_times = []
        failures = 0
        
        for i in range(5):
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}/api/status", timeout=30)
                response_time = time.time() - start_time
                response_times.append(response_time)
                
                if response.status_code != 200:
                    failures += 1
                    
            except Exception:
                failures += 1
                response_times.append(30.0)  # Timeout
            
            time.sleep(2)  # Aguardar entre tentativas
        
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            min_time = min(response_times)
            
            status = "PASS" if avg_time < 10 and failures == 0 else "WARN" if failures < 3 else "FAIL"
            details = f"Avg: {avg_time:.2f}s, Min: {min_time:.2f}s, Max: {max_time:.2f}s, Failures: {failures}/5"
            
            self.log_result("Tempos de Resposta", status, details, avg_time)
    
    def check_dns_resolution(self):
        """
        Verifica resolução DNS
        """
        print("\n🔍 Verificando resolução DNS...")
        
        try:
            import socket
            start_time = time.time()
            ip = socket.gethostbyname(self.domain)
            response_time = time.time() - start_time
            
            self.log_result("Resolução DNS", "PASS", 
                          f"IP: {ip}", response_time)
            
        except Exception as e:
            self.log_result("Resolução DNS", "FAIL", 
                          f"Erro: {str(e)}", 0)
    
    def check_ssl_certificate(self):
        """
        Verifica certificado SSL
        """
        print("\n🔍 Verificando certificado SSL...")
        
        try:
            import ssl
            import socket
            from datetime import datetime
            
            context = ssl.create_default_context()
            
            with socket.create_connection((self.domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=self.domain) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Verificar expiração
                    not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_until_expiry = (not_after - datetime.now()).days
                    
                    if days_until_expiry > 30:
                        status = "PASS"
                    elif days_until_expiry > 7:
                        status = "WARN"
                    else:
                        status = "FAIL"
                    
                    details = f"Expira em {days_until_expiry} dias ({not_after.strftime('%Y-%m-%d')})"
                    self.log_result("Certificado SSL", status, details, 0)
                    
        except Exception as e:
            self.log_result("Certificado SSL", "FAIL", 
                          f"Erro: {str(e)}", 0)
    
    def analyze_headers(self):
        """
        Analisa headers de resposta para identificar problemas
        """
        print("\n🔍 Analisando headers de resposta...")
        
        try:
            response = requests.get(self.base_url, timeout=30)
            headers = response.headers
            
            # Verificar servidor
            server = headers.get('Server', 'Unknown')
            
            # Verificar cache
            cache_control = headers.get('Cache-Control', 'None')
            
            # Verificar compressão
            content_encoding = headers.get('Content-Encoding', 'None')
            
            details = f"Server: {server}, Cache: {cache_control}, Encoding: {content_encoding}"
            self.log_result("Headers de Resposta", "INFO", details, 0)
            
            # Verificar se há indicações de proxy/load balancer
            if 'nginx' in server.lower():
                self.log_result("Servidor Web", "INFO", "Nginx detectado", 0)
            
        except Exception as e:
            self.log_result("Headers de Resposta", "FAIL", 
                          f"Erro: {str(e)}", 0)
    
    def generate_recommendations(self):
        """
        Gera recomendações baseadas nos resultados dos testes
        """
        print("\n📋 Gerando recomendações...")
        
        failed_tests = [r for r in self.results if r['status'] == 'FAIL']
        slow_tests = [r for r in self.results if r['response_time'] > 10]
        
        recommendations = []
        
        if failed_tests:
            recommendations.append("🚨 CRÍTICO: Há falhas nos testes básicos")
            
            # Verificar se há timeouts
            timeout_tests = [r for r in failed_tests if 'timeout' in r['details'].lower()]
            if timeout_tests:
                recommendations.extend([
                    "• Verificar se o backend está rodando",
                    "• Verificar configurações de timeout no Nginx",
                    "• Verificar recursos do servidor (CPU, RAM, Disk)",
                    "• Aplicar configurações do GATEWAY_TIMEOUT_FIX.md"
                ])
        
        if slow_tests:
            recommendations.append("⚠️ PERFORMANCE: Respostas lentas detectadas")
            recommendations.extend([
                "• Otimizar queries do banco de dados",
                "• Implementar cache Redis",
                "• Verificar logs do backend para gargalos",
                "• Considerar scaling horizontal"
            ])
        
        # Verificar padrões específicos
        api_failures = [r for r in failed_tests if '/api/' in r['test']]
        if api_failures:
            recommendations.extend([
                "• Verificar se o backend Python está rodando",
                "• Verificar logs do Gunicorn/Flask",
                "• Verificar conectividade com banco de dados"
            ])
        
        static_failures = [r for r in failed_tests if any(ext in r['test'] for ext in ['.png', '.js', '.css', '.json'])]
        if static_failures:
            recommendations.extend([
                "• Verificar se arquivos estáticos estão sendo servidos corretamente",
                "• Verificar configuração do Nginx para arquivos estáticos",
                "• Verificar permissões de arquivos"
            ])
        
        if not recommendations:
            recommendations.append("✅ Todos os testes passaram! Sistema funcionando normalmente.")
        
        return recommendations
    
    def run_full_diagnostic(self):
        """
        Executa diagnóstico completo
        """
        print(f"🔍 Iniciando diagnóstico completo para {self.domain}")
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Executar todos os testes
        self.check_dns_resolution()
        self.test_basic_connectivity()
        self.check_ssl_certificate()
        self.analyze_headers()
        self.test_api_endpoints()
        self.test_server_response_times()
        
        # Gerar relatório
        print("\n" + "=" * 60)
        print("📊 RELATÓRIO DE DIAGNÓSTICO")
        print("=" * 60)
        
        # Estatísticas
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.results if r['status'] == 'FAIL'])
        warned_tests = len([r for r in self.results if r['status'] == 'WARN'])
        
        print(f"Total de testes: {total_tests}")
        print(f"✅ Passou: {passed_tests}")
        print(f"⚠️ Aviso: {warned_tests}")
        print(f"❌ Falhou: {failed_tests}")
        
        # Recomendações
        recommendations = self.generate_recommendations()
        print("\n🎯 RECOMENDAÇÕES:")
        for rec in recommendations:
            print(f"  {rec}")
        
        # Salvar relatório
        self.save_report()
        
        return self.results
    
    def save_report(self):
        """
        Salva relatório em arquivo JSON
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"timeout_diagnostic_{timestamp}.json"
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "domain": self.domain,
            "results": self.results,
            "recommendations": self.generate_recommendations()
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Relatório salvo em: {filename}")
        except Exception as e:
            print(f"\n❌ Erro ao salvar relatório: {e}")

def main():
    """
    Função principal
    """
    print("🚨 Diagnóstico de Gateway Timeout 504")
    print("=====================================\n")
    
    # Permitir domínio customizado
    domain = input("Digite o domínio (ou Enter para 1crypten.space): ").strip()
    if not domain:
        domain = "1crypten.space"
    
    # Executar diagnóstico
    diagnostic = TimeoutDiagnostic(domain)
    results = diagnostic.run_full_diagnostic()
    
    # Verificar se há problemas críticos
    critical_issues = [r for r in results if r['status'] == 'FAIL']
    
    if critical_issues:
        print("\n🚨 AÇÃO NECESSÁRIA: Problemas críticos detectados!")
        print("📖 Consulte o arquivo GATEWAY_TIMEOUT_FIX.md para soluções")
        return 1
    else:
        print("\n✅ Sistema funcionando normalmente")
        return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️ Diagnóstico interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Erro inesperado: {e}")
        sys.exit(1)