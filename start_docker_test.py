#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para Iniciar e Testar Sistema Docker Desktop
Automatiza o processo de subir os containers e executar testes
"""

import subprocess
import time
import sys
import os
from typing import List, Dict

class DockerManager:
    """Gerenciador do ambiente Docker"""
    
    def __init__(self):
        """Inicializa o gerenciador"""
        self.compose_file = "docker-compose.dev.yml"
        self.project_name = "crypten-dev"
        
        print("🐳 === GERENCIADOR DOCKER DESKTOP ===")
        print(f"📁 Compose file: {self.compose_file}")
        print(f"🏷️ Project name: {self.project_name}")
        print()
    
    def check_docker(self) -> bool:
        """Verifica se Docker está disponível"""
        print("🔍 Verificando Docker...")
        
        try:
            # Verificar se Docker está instalado
            result = subprocess.run(
                ["docker", "--version"], 
                capture_output=True, text=True, check=True
            )
            print(f"✅ Docker: {result.stdout.strip()}")
            
            # Verificar se Docker está rodando
            result = subprocess.run(
                ["docker", "info"], 
                capture_output=True, text=True, check=True
            )
            print("✅ Docker daemon: rodando")
            
            # Verificar Docker Compose
            result = subprocess.run(
                ["docker", "compose", "version"], 
                capture_output=True, text=True, check=True
            )
            print(f"✅ Docker Compose: {result.stdout.strip()}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro no Docker: {e}")
            return False
        except FileNotFoundError:
            print("❌ Docker não encontrado. Instale o Docker Desktop.")
            return False
    
    def cleanup_existing(self) -> bool:
        """Limpa containers existentes"""
        print("\n🧹 Limpando ambiente existente...")
        
        try:
            # Parar e remover containers
            subprocess.run([
                "docker", "compose", 
                "-f", self.compose_file,
                "-p", self.project_name,
                "down", "-v", "--remove-orphans"
            ], check=False)  # Não falhar se não existir
            
            print("✅ Ambiente limpo")
            return True
            
        except Exception as e:
            print(f"⚠️ Erro na limpeza: {e}")
            return False
    
    def build_images(self) -> bool:
        """Constrói as imagens Docker"""
        print("\n🔨 Construindo imagens...")
        
        try:
            # Build das imagens
            result = subprocess.run([
                "docker", "compose", 
                "-f", self.compose_file,
                "-p", self.project_name,
                "build", "--no-cache"
            ], check=True)
            
            print("✅ Imagens construídas com sucesso")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro na construção: {e}")
            return False
    
    def start_services(self) -> bool:
        """Inicia os serviços"""
        print("\n🚀 Iniciando serviços...")
        
        try:
            # Iniciar serviços
            result = subprocess.run([
                "docker", "compose", 
                "-f", self.compose_file,
                "-p", self.project_name,
                "up", "-d"
            ], check=True)
            
            print("✅ Serviços iniciados")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao iniciar serviços: {e}")
            return False
    
    def wait_for_services(self, timeout: int = 120) -> bool:
        """Aguarda serviços ficarem prontos"""
        print(f"\n⏳ Aguardando serviços ficarem prontos (timeout: {timeout}s)...")
        
        services = [
            ("redis", "crypto-redis-dev"),
            ("backend", "crypto-backend-dev"),
            ("frontend", "crypto-frontend-dev"),
            ("nginx", "crypto-nginx-dev")
        ]
        
        start_time = time.time()
        
        for service_name, container_name in services:
            print(f"🔍 Verificando {service_name}...")
            
            service_ready = False
            service_start = time.time()
            
            while time.time() - start_time < timeout:
                try:
                    # Verificar se container está rodando
                    result = subprocess.run([
                        "docker", "ps", "--filter", f"name={container_name}", 
                        "--format", "{{.Status}}"
                    ], capture_output=True, text=True, check=True)
                    
                    if "Up" in result.stdout:
                        # Verificar health check se disponível
                        health_result = subprocess.run([
                            "docker", "inspect", container_name,
                            "--format", "{{.State.Health.Status}}"
                        ], capture_output=True, text=True, check=False)
                        
                        health_status = health_result.stdout.strip()
                        
                        if health_status in ["", "healthy"]:
                            elapsed = time.time() - service_start
                            print(f"✅ {service_name}: pronto ({elapsed:.1f}s)")
                            service_ready = True
                            break
                        elif health_status == "unhealthy":
                            print(f"❌ {service_name}: unhealthy")
                            return False
                        else:
                            print(f"⏳ {service_name}: {health_status}...")
                    
                    time.sleep(2)
                    
                except subprocess.CalledProcessError:
                    time.sleep(2)
                    continue
            
            if not service_ready:
                print(f"❌ {service_name}: timeout")
                return False
        
        total_time = time.time() - start_time
        print(f"\n✅ Todos os serviços prontos em {total_time:.1f}s")
        return True
    
    def show_status(self) -> None:
        """Mostra status dos serviços"""
        print("\n📊 Status dos Serviços:")
        print("-" * 50)
        
        try:
            result = subprocess.run([
                "docker", "compose", 
                "-f", self.compose_file,
                "-p", self.project_name,
                "ps"
            ], check=True)
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao verificar status: {e}")
    
    def show_logs(self, service: str = None, lines: int = 20) -> None:
        """Mostra logs dos serviços"""
        print(f"\n📋 Logs ({lines} linhas):")
        print("-" * 50)
        
        try:
            cmd = [
                "docker", "compose", 
                "-f", self.compose_file,
                "-p", self.project_name,
                "logs", "--tail", str(lines)
            ]
            
            if service:
                cmd.append(service)
            
            subprocess.run(cmd, check=True)
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao verificar logs: {e}")
    
    def run_tests(self) -> bool:
        """Executa os testes do sistema"""
        print("\n🧪 Executando testes do sistema...")
        
        try:
            # Instalar dependências se necessário
            subprocess.run([
                sys.executable, "-m", "pip", "install", 
                "requests", "psycopg2-binary", "redis"
            ], check=False, capture_output=True)
            
            # Executar testes
            result = subprocess.run([
                sys.executable, "test_docker_system.py"
            ], check=True)
            
            print("✅ Testes executados com sucesso")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Testes falharam: {e}")
            return False
    
    def stop_services(self) -> None:
        """Para os serviços"""
        print("\n🛑 Parando serviços...")
        
        try:
            subprocess.run([
                "docker", "compose", 
                "-f", self.compose_file,
                "-p", self.project_name,
                "down"
            ], check=True)
            
            print("✅ Serviços parados")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao parar serviços: {e}")

def main():
    """Função principal"""
    print("🐳 === INICIALIZADOR DO SISTEMA DOCKER DESKTOP ===")
    print("Este script vai subir todo o ambiente e executar testes")
    print()
    
    manager = DockerManager()
    
    try:
        # Verificar Docker
        if not manager.check_docker():
            print("\n❌ Docker não está disponível. Instale o Docker Desktop.")
            return False
        
        # Limpar ambiente existente
        manager.cleanup_existing()
        
        # Construir imagens
        if not manager.build_images():
            print("\n❌ Falha na construção das imagens")
            return False
        
        # Iniciar serviços
        if not manager.start_services():
            print("\n❌ Falha ao iniciar serviços")
            return False
        
        # Aguardar serviços ficarem prontos
        if not manager.wait_for_services():
            print("\n❌ Serviços não ficaram prontos")
            manager.show_logs()
            return False
        
        # Mostrar status
        manager.show_status()
        
        # Executar testes
        print("\n" + "="*60)
        print("🧪 EXECUTANDO TESTES ABRANGENTES")
        print("="*60)
        
        if manager.run_tests():
            print("\n🎉 === SISTEMA APROVADO PARA PRODUÇÃO! ===")
            print("\n📊 URLs de Acesso:")
            print("   🖥️ Frontend: http://localhost:3000")
            print("   🔧 API: http://localhost:5000")
            print("   🌐 Nginx: http://localhost:8080")
            print("\n📱 Para testar PWA:")
            print("   1. Acesse http://localhost:8080")
            print("   2. Faça login")
            print("   3. Procure o botão de instalação no menu")
            print("\n📖 Tutorial PWA: TUTORIAL_PWA_INSTALACAO.md")
            
            return True
        else:
            print("\n⚠️ === SISTEMA PRECISA DE CORREÇÕES ===")
            manager.show_logs()
            return False
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrompido pelo usuário")
        manager.stop_services()
        return False
    
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        manager.show_logs()
        return False

if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\n🔧 Para debug, execute:")
        print("   docker compose -f docker-compose.dev.yml -p crypten-dev logs")
        print("\n🛑 Para parar tudo:")
        print("   docker compose -f docker-compose.dev.yml -p crypten-dev down -v")
    
    sys.exit(0 if success else 1)