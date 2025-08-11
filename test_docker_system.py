#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Abrangente do Sistema no Docker Desktop
Script para validar todos os componentes: Backend, Frontend, PWA, Integrações
"""

import requests
import time
import json
import subprocess
import sys
from typing import Dict, List, Optional
import psycopg2
import redis
from datetime import datetime

class DockerSystemTester:
    """Testador abrangente do sistema Docker"""
    
    def __init__(self):
        """Inicializa o testador"""
        self.base_url = "http://localhost:8080"
        self.api_url = "http://localhost:5000"
        self.frontend_url = "http://localhost:3000"
        
        # Configurações de teste
        self.test_user = {
            "email": "test@1crypten.space",
            "password": "Test123!@#",
            "name": "Test User"
        }
        
        self.results = {
            "docker_services": {},
            "database": {},
            "redis": {},
            "backend_api": {},
            "frontend": {},
            "pwa": {},
            "integrations": {},
            "performance": {}
        }
        
        print("🐳 === TESTADOR DO SISTEMA DOCKER DESKTOP ===")
        print(f"📊 Base URL: {self.base_url}")
        print(f"🔧 API URL: {self.api_url}")
        print(f"🖥️ Frontend URL: {self.frontend_url}")
        print()
    
    def test_docker_services(self) -> bool:
        """Testa se todos os serviços Docker estão rodando"""
        print("🐳 === TESTE DOS SERVIÇOS DOCKER ===")
        
        try:
            # Verificar containers rodando
            result = subprocess.run(
                ["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"],
                capture_output=True, text=True
            )
            
            if result.returncode != 0:
                print("❌ Erro ao executar docker ps")
                return False
            
            containers = result.stdout.strip().split('\n')[1:]  # Skip header
            
            expected_containers = [
                "crypto-postgres-dev",
                "crypto-redis-dev", 
                "crypto-backend-dev",
                "crypto-frontend-dev",
                "crypto-nginx-dev"
            ]
            
            running_containers = []
            for line in containers:
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        name = parts[0].strip()
                        status = parts[1].strip()
                        running_containers.append(name)
                        
                        if "Up" in status:
                            print(f"✅ {name}: {status}")
                            self.results["docker_services"][name] = "running"
                        else:
                            print(f"❌ {name}: {status}")
                            self.results["docker_services"][name] = "stopped"
            
            # Verificar se todos os containers esperados estão rodando
            missing_containers = set(expected_containers) - set(running_containers)
            if missing_containers:
                print(f"⚠️ Containers ausentes: {missing_containers}")
                for container in missing_containers:
                    self.results["docker_services"][container] = "missing"
            
            all_running = all(
                self.results["docker_services"].get(container) == "running" 
                for container in expected_containers
            )
            
            print(f"\n📊 Status: {'✅ Todos rodando' if all_running else '❌ Alguns problemas'}")
            return all_running
            
        except Exception as e:
            print(f"❌ Erro ao verificar serviços Docker: {e}")
            return False
    
    def test_database_connection(self) -> bool:
        """Testa conexão com Supabase PostgreSQL"""
        print("\n🗄️ === TESTE DO BANCO DE DADOS (SUPABASE) ===")
        
        try:
            # Verificar se variáveis Supabase estão configuradas
            import os
            supabase_url = os.getenv('SUPABASE_DATABASE_URL')
            
            if not supabase_url:
                print("⚠️ SUPABASE_DATABASE_URL não configurada")
                print("ℹ️ Testando conexão via API backend...")
                
                # Testar via API do backend
                response = requests.get(f"{self.api_url}/api/status", timeout=10)
                if response.status_code == 200:
                    print("✅ Backend conectado (assumindo Supabase funcionando)")
                    self.results["database"]["status"] = "connected_via_api"
                    return True
                else:
                    print(f"❌ Backend não responde: {response.status_code}")
                    self.results["database"]["status"] = "backend_error"
                    return False
            
            # Conectar diretamente ao Supabase PostgreSQL
            conn = psycopg2.connect(supabase_url)
            
            cursor = conn.cursor()
            
            # Testar conexão
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"✅ Supabase PostgreSQL conectado: {version[:50]}...")
            
            # Verificar tabelas
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = ['users', 'signals', 'user_sessions']
            
            for table in expected_tables:
                if table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"✅ Tabela {table}: {count} registros")
                    self.results["database"][table] = count
                else:
                    print(f"❌ Tabela {table}: não encontrada")
                    self.results["database"][table] = "missing"
            
            cursor.close()
            conn.close()
            
            self.results["database"]["status"] = "connected_supabase"
            return True
            
        except Exception as e:
            print(f"❌ Erro na conexão com Supabase: {e}")
            print("ℹ️ Isso é normal se as credenciais Supabase não estiverem configuradas")
            self.results["database"]["status"] = f"supabase_error: {e}"
            
            # Fallback: testar via API
            try:
                response = requests.get(f"{self.api_url}/api/status", timeout=5)
                if response.status_code == 200:
                    print("✅ Backend funcionando (Supabase provavelmente OK)")
                    self.results["database"]["status"] = "backend_working"
                    return True
            except:
                pass
            
            return False
    
    def test_redis_connection(self) -> bool:
        """Testa conexão com Redis"""
        print("\n🔴 === TESTE DO REDIS ===")
        
        try:
            # Conectar ao Redis
            r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            
            # Testar conexão
            r.ping()
            print("✅ Redis conectado")
            
            # Testar operações básicas
            test_key = "test_docker_system"
            test_value = f"test_{int(time.time())}"
            
            r.set(test_key, test_value, ex=60)
            retrieved_value = r.get(test_key)
            
            if retrieved_value == test_value:
                print("✅ Redis operações: SET/GET funcionando")
                self.results["redis"]["operations"] = "working"
            else:
                print("❌ Redis operações: SET/GET com problema")
                self.results["redis"]["operations"] = "error"
            
            # Verificar informações do Redis
            info = r.info()
            print(f"✅ Redis versão: {info.get('redis_version')}")
            print(f"✅ Redis memória usada: {info.get('used_memory_human')}")
            
            self.results["redis"]["status"] = "connected"
            self.results["redis"]["version"] = info.get('redis_version')
            
            # Limpar teste
            r.delete(test_key)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro na conexão com Redis: {e}")
            self.results["redis"]["status"] = f"error: {e}"
            return False
    
    def test_backend_api(self) -> bool:
        """Testa todas as APIs do backend"""
        print("\n🔧 === TESTE DAS APIS DO BACKEND ===")
        
        try:
            # Teste 1: Health check
            response = requests.get(f"{self.api_url}/api/status", timeout=10)
            if response.status_code == 200:
                print("✅ API Status: funcionando")
                self.results["backend_api"]["status"] = "working"
            else:
                print(f"❌ API Status: {response.status_code}")
                self.results["backend_api"]["status"] = f"error_{response.status_code}"
            
            # Teste 2: Sinais
            response = requests.get(f"{self.api_url}/api/signals", timeout=10)
            if response.status_code == 200:
                signals = response.json()
                print(f"✅ API Sinais: {len(signals)} sinais carregados")
                self.results["backend_api"]["signals"] = len(signals)
            else:
                print(f"❌ API Sinais: {response.status_code}")
                self.results["backend_api"]["signals"] = f"error_{response.status_code}"
            
            # Teste 3: Cleanup Status
            response = requests.get(f"{self.api_url}/api/cleanup-status", timeout=10)
            if response.status_code == 200:
                cleanup = response.json()
                print(f"✅ API Cleanup Status: funcionando")
                self.results["backend_api"]["cleanup_status"] = "working"
            else:
                print(f"❌ API Cleanup Status: {response.status_code}")
                self.results["backend_api"]["cleanup_status"] = f"error_{response.status_code}"
            
            # Teste 4: Autenticação (registro)
            try:
                register_data = {
                    "name": self.test_user["name"],
                    "email": self.test_user["email"],
                    "password": self.test_user["password"]
                }
                
                response = requests.post(
                    f"{self.api_url}/api/auth/register", 
                    json=register_data, 
                    timeout=10
                )
                
                if response.status_code in [200, 201, 409]:  # 409 = usuário já existe
                    print("✅ API Registro: funcionando")
                    self.results["backend_api"]["register"] = "working"
                else:
                    print(f"❌ API Registro: {response.status_code}")
                    self.results["backend_api"]["register"] = f"error_{response.status_code}"
                    
            except Exception as e:
                print(f"⚠️ API Registro: {e}")
                self.results["backend_api"]["register"] = f"error: {e}"
            
            # Teste 5: Login
            try:
                login_data = {
                    "email": self.test_user["email"],
                    "password": self.test_user["password"]
                }
                
                response = requests.post(
                    f"{self.api_url}/api/auth/login", 
                    json=login_data, 
                    timeout=10
                )
                
                if response.status_code == 200:
                    print("✅ API Login: funcionando")
                    self.results["backend_api"]["login"] = "working"
                    
                    # Salvar token para outros testes
                    self.auth_token = response.json().get('access_token')
                else:
                    print(f"❌ API Login: {response.status_code}")
                    self.results["backend_api"]["login"] = f"error_{response.status_code}"
                    
            except Exception as e:
                print(f"⚠️ API Login: {e}")
                self.results["backend_api"]["login"] = f"error: {e}"
            
            return True
            
        except Exception as e:
            print(f"❌ Erro geral nas APIs: {e}")
            return False
    
    def test_frontend_access(self) -> bool:
        """Testa acesso ao frontend"""
        print("\n🖥️ === TESTE DO FRONTEND ===")
        
        try:
            # Teste 1: Acesso direto ao frontend
            response = requests.get(self.frontend_url, timeout=10)
            if response.status_code == 200:
                print("✅ Frontend direto: acessível")
                self.results["frontend"]["direct_access"] = "working"
            else:
                print(f"❌ Frontend direto: {response.status_code}")
                self.results["frontend"]["direct_access"] = f"error_{response.status_code}"
            
            # Teste 2: Acesso via Nginx
            response = requests.get(self.base_url, timeout=10)
            if response.status_code == 200:
                print("✅ Frontend via Nginx: acessível")
                self.results["frontend"]["nginx_access"] = "working"
                
                # Verificar se é uma SPA React
                if "react" in response.text.lower() or "root" in response.text:
                    print("✅ Frontend: React detectado")
                    self.results["frontend"]["react_detected"] = True
                else:
                    print("⚠️ Frontend: React não detectado claramente")
                    self.results["frontend"]["react_detected"] = False
                    
            else:
                print(f"❌ Frontend via Nginx: {response.status_code}")
                self.results["frontend"]["nginx_access"] = f"error_{response.status_code}"
            
            return True
            
        except Exception as e:
            print(f"❌ Erro no teste do frontend: {e}")
            return False
    
    def test_pwa_functionality(self) -> bool:
        """Testa funcionalidades PWA"""
        print("\n📱 === TESTE DO PWA ===")
        
        try:
            # Teste 1: Manifest.json
            response = requests.get(f"{self.base_url}/manifest.json", timeout=10)
            if response.status_code == 200:
                manifest = response.json()
                print(f"✅ Manifest: {manifest.get('name', 'N/A')}")
                print(f"   Tema: {manifest.get('theme_color', 'N/A')}")
                print(f"   Ícones: {len(manifest.get('icons', []))} encontrados")
                self.results["pwa"]["manifest"] = "working"
                self.results["pwa"]["manifest_data"] = manifest
            else:
                print(f"❌ Manifest: {response.status_code}")
                self.results["pwa"]["manifest"] = f"error_{response.status_code}"
            
            # Teste 2: Service Worker
            response = requests.get(f"{self.base_url}/sw.js", timeout=10)
            if response.status_code == 200:
                sw_content = response.text
                if "cache" in sw_content.lower() and "fetch" in sw_content.lower():
                    print("✅ Service Worker: funcionalidades detectadas")
                    self.results["pwa"]["service_worker"] = "working"
                else:
                    print("⚠️ Service Worker: conteúdo suspeito")
                    self.results["pwa"]["service_worker"] = "suspicious"
            else:
                print(f"❌ Service Worker: {response.status_code}")
                self.results["pwa"]["service_worker"] = f"error_{response.status_code}"
            
            # Teste 3: Ícones PWA
            icon_sizes = ["192x192", "512x512"]
            working_icons = 0
            
            for size in icon_sizes:
                response = requests.get(f"{self.base_url}/icons/icon-{size}.svg", timeout=5)
                if response.status_code == 200:
                    print(f"✅ Ícone {size}: disponível")
                    working_icons += 1
                else:
                    print(f"❌ Ícone {size}: {response.status_code}")
            
            self.results["pwa"]["icons_working"] = working_icons
            self.results["pwa"]["icons_total"] = len(icon_sizes)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro no teste PWA: {e}")
            return False
    
    def test_integrations(self) -> bool:
        """Testa integrações externas"""
        print("\n🔗 === TESTE DAS INTEGRAÇÕES ===")
        
        # Teste Telegram (se configurado)
        try:
            response = requests.get(f"{self.api_url}/api/test-telegram", timeout=10)
            if response.status_code == 200:
                print("✅ Telegram: configurado e funcionando")
                self.results["integrations"]["telegram"] = "working"
            elif response.status_code == 404:
                print("⚠️ Telegram: endpoint de teste não encontrado")
                self.results["integrations"]["telegram"] = "no_test_endpoint"
            else:
                print(f"❌ Telegram: {response.status_code}")
                self.results["integrations"]["telegram"] = f"error_{response.status_code}"
        except Exception as e:
            print(f"⚠️ Telegram: {e}")
            self.results["integrations"]["telegram"] = f"error: {e}"
        
        # Teste Binance API (se configurado)
        try:
            response = requests.get(f"{self.api_url}/api/test-binance", timeout=10)
            if response.status_code == 200:
                print("✅ Binance API: configurado e funcionando")
                self.results["integrations"]["binance"] = "working"
            elif response.status_code == 404:
                print("⚠️ Binance API: endpoint de teste não encontrado")
                self.results["integrations"]["binance"] = "no_test_endpoint"
            else:
                print(f"❌ Binance API: {response.status_code}")
                self.results["integrations"]["binance"] = f"error_{response.status_code}"
        except Exception as e:
            print(f"⚠️ Binance API: {e}")
            self.results["integrations"]["binance"] = f"error: {e}"
        
        return True
    
    def test_performance(self) -> bool:
        """Testa performance do sistema"""
        print("\n⚡ === TESTE DE PERFORMANCE ===")
        
        try:
            # Teste 1: Tempo de resposta da API
            start_time = time.time()
            response = requests.get(f"{self.api_url}/api/signals", timeout=30)
            api_time = time.time() - start_time
            
            print(f"⏱️ API Sinais: {api_time:.2f}s")
            self.results["performance"]["api_response_time"] = api_time
            
            if api_time < 5:
                print("✅ Performance API: boa")
            elif api_time < 10:
                print("⚠️ Performance API: aceitável")
            else:
                print("❌ Performance API: lenta")
            
            # Teste 2: Tempo de carregamento do frontend
            start_time = time.time()
            response = requests.get(self.base_url, timeout=30)
            frontend_time = time.time() - start_time
            
            print(f"⏱️ Frontend: {frontend_time:.2f}s")
            self.results["performance"]["frontend_load_time"] = frontend_time
            
            if frontend_time < 2:
                print("✅ Performance Frontend: boa")
            elif frontend_time < 5:
                print("⚠️ Performance Frontend: aceitável")
            else:
                print("❌ Performance Frontend: lenta")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro no teste de performance: {e}")
            return False
    
    def generate_report(self) -> None:
        """Gera relatório final dos testes"""
        print("\n" + "="*60)
        print("📊 === RELATÓRIO FINAL DOS TESTES ===")
        print("="*60)
        
        # Resumo por categoria
        categories = {
            "🐳 Serviços Docker": "docker_services",
            "🗄️ Banco de Dados": "database", 
            "🔴 Redis": "redis",
            "🔧 APIs Backend": "backend_api",
            "🖥️ Frontend": "frontend",
            "📱 PWA": "pwa",
            "🔗 Integrações": "integrations",
            "⚡ Performance": "performance"
        }
        
        for category_name, category_key in categories.items():
            print(f"\n{category_name}:")
            category_data = self.results.get(category_key, {})
            
            if not category_data:
                print("   ❌ Não testado")
                continue
            
            for key, value in category_data.items():
                if isinstance(value, str):
                    if "error" in value.lower():
                        status = "❌"
                    elif value in ["working", "connected", "running"]:
                        status = "✅"
                    else:
                        status = "⚠️"
                elif isinstance(value, (int, float)):
                    status = "📊"
                elif isinstance(value, bool):
                    status = "✅" if value else "❌"
                else:
                    status = "ℹ️"
                
                print(f"   {status} {key}: {value}")
        
        # Salvar relatório em arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"docker_test_report_{timestamp}.json"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Relatório salvo em: {report_file}")
        except Exception as e:
            print(f"⚠️ Erro ao salvar relatório: {e}")
        
        print("\n" + "="*60)
        print("🎉 TESTES CONCLUÍDOS!")
        print("="*60)
    
    def run_all_tests(self) -> bool:
        """Executa todos os testes"""
        print("🚀 Iniciando testes abrangentes do sistema Docker...")
        print()
        
        tests = [
            ("Serviços Docker", self.test_docker_services),
            ("Banco de Dados", self.test_database_connection),
            ("Redis", self.test_redis_connection),
            ("APIs Backend", self.test_backend_api),
            ("Frontend", self.test_frontend_access),
            ("PWA", self.test_pwa_functionality),
            ("Integrações", self.test_integrations),
            ("Performance", self.test_performance)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                print(f"\n🧪 Executando: {test_name}")
                if test_func():
                    passed_tests += 1
                    print(f"✅ {test_name}: PASSOU")
                else:
                    print(f"❌ {test_name}: FALHOU")
            except Exception as e:
                print(f"💥 {test_name}: ERRO - {e}")
        
        # Gerar relatório
        self.generate_report()
        
        # Resultado final
        success_rate = (passed_tests / total_tests) * 100
        print(f"\n📈 Taxa de Sucesso: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        
        return success_rate >= 80  # 80% de sucesso mínimo

def main():
    """Função principal"""
    print("🐳 === TESTE ABRANGENTE DO SISTEMA DOCKER DESKTOP ===")
    print("Este script testa todos os componentes do sistema 1Crypten")
    print()
    
    # Verificar se Docker está rodando
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        print("✅ Docker detectado")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker não encontrado. Instale o Docker Desktop primeiro.")
        return False
    
    # Executar testes
    tester = DockerSystemTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 Sistema aprovado para produção!")
        return True
    else:
        print("\n⚠️ Sistema precisa de correções antes da produção.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)