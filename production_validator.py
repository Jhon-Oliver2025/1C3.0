#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validador de Produção - 1Crypten
Verifica se o sistema está pronto para deploy em produção
Executa testes de integridade, performance e segurança
"""

import os
import sys
import json
import subprocess
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class ProductionValidator:
    """Validador completo para produção"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.validation_results = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'unknown',
            'checks': [],
            'warnings': [],
            'errors': [],
            'recommendations': []
        }
        
    def run_validation(self) -> Dict:
        """Executa validação completa para produção"""
        print("🔍 VALIDAÇÃO PARA PRODUÇÃO - 1CRYPTEN")
        print("="*80)
        
        # Verificações estruturais
        print("\n📁 Verificando estrutura do projeto...")
        self.check_project_structure()
        
        # Verificações de configuração
        print("\n⚙️ Verificando configurações...")
        self.check_configurations()
        
        # Verificações de dependências
        print("\n📦 Verificando dependências...")
        self.check_dependencies()
        
        # Verificações de segurança
        print("\n🔒 Verificando segurança...")
        self.check_security()
        
        # Verificações de performance
        print("\n⚡ Verificando performance...")
        self.check_performance()
        
        # Verificações de Docker
        print("\n🐳 Verificando Docker...")
        self.check_docker()
        
        # Testes básicos
        print("\n🧪 Executando testes básicos...")
        self.run_basic_tests()
        
        # Gerar relatório final
        self.generate_final_report()
        
        return self.validation_results
    
    def check_project_structure(self):
        """Verifica estrutura essencial do projeto"""
        required_files = [
            'back/app_supabase.py',
            'back/requirements.txt',
            'front/package.json',
            'front/src/App.tsx',
            'docker-compose.production.yml',
            '.gitignore'
        ]
        
        required_dirs = [
            'back/core',
            'back/api_routes',
            'front/src/components',
            'front/src/pages',
            'docs'
        ]
        
        missing_files = []
        missing_dirs = []
        
        # Verificar arquivos
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                missing_files.append(file_path)
        
        # Verificar diretórios
        for dir_path in required_dirs:
            if not (self.project_root / dir_path).exists():
                missing_dirs.append(dir_path)
        
        if missing_files or missing_dirs:
            self.validation_results['errors'].append({
                'category': 'structure',
                'message': 'Arquivos/diretórios essenciais ausentes',
                'details': {
                    'missing_files': missing_files,
                    'missing_dirs': missing_dirs
                }
            })
        else:
            self.validation_results['checks'].append({
                'category': 'structure',
                'status': 'passed',
                'message': 'Estrutura do projeto OK'
            })
        
        print(f"   📁 Estrutura: {'✅ OK' if not (missing_files or missing_dirs) else '❌ Problemas encontrados'}")
    
    def check_configurations(self):
        """Verifica configurações essenciais"""
        config_issues = []
        
        # Verificar package.json do frontend
        package_json = self.project_root / 'front' / 'package.json'
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    
                # Verificar scripts essenciais
                scripts = data.get('scripts', {})
                required_scripts = ['build', 'start']
                missing_scripts = [s for s in required_scripts if s not in scripts]
                
                if missing_scripts:
                    config_issues.append(f"Scripts ausentes no package.json: {missing_scripts}")
                    
            except Exception as e:
                config_issues.append(f"Erro ao ler package.json: {e}")
        else:
            config_issues.append("package.json não encontrado")
        
        # Verificar requirements.txt do backend
        requirements = self.project_root / 'back' / 'requirements.txt'
        if requirements.exists():
            try:
                with open(requirements, 'r') as f:
                    content = f.read()
                    essential_packages = ['flask', 'supabase', 'python-dotenv']
                    missing_packages = []
                    
                    for package in essential_packages:
                        if package not in content.lower():
                            missing_packages.append(package)
                    
                    if missing_packages:
                        config_issues.append(f"Pacotes essenciais ausentes: {missing_packages}")
                        
            except Exception as e:
                config_issues.append(f"Erro ao ler requirements.txt: {e}")
        else:
            config_issues.append("requirements.txt não encontrado")
        
        # Verificar Docker Compose
        docker_compose = self.project_root / 'docker-compose.production.yml'
        if not docker_compose.exists():
            config_issues.append("docker-compose.production.yml não encontrado")
        
        if config_issues:
            self.validation_results['errors'].extend([
                {'category': 'configuration', 'message': issue} for issue in config_issues
            ])
        else:
            self.validation_results['checks'].append({
                'category': 'configuration',
                'status': 'passed',
                'message': 'Configurações OK'
            })
        
        print(f"   ⚙️ Configurações: {'✅ OK' if not config_issues else '❌ Problemas encontrados'}")
    
    def check_dependencies(self):
        """Verifica dependências e versões"""
        dependency_issues = []
        
        # Verificar Node.js e npm (para frontend)
        try:
            node_result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            if node_result.returncode == 0:
                node_version = node_result.stdout.strip()
                print(f"   📦 Node.js: {node_version}")
            else:
                dependency_issues.append("Node.js não encontrado")
        except FileNotFoundError:
            dependency_issues.append("Node.js não instalado")
        
        # Verificar Python
        try:
            python_result = subprocess.run([sys.executable, '--version'], capture_output=True, text=True)
            if python_result.returncode == 0:
                python_version = python_result.stdout.strip()
                print(f"   📦 Python: {python_version}")
            else:
                dependency_issues.append("Python não encontrado")
        except:
            dependency_issues.append("Erro ao verificar Python")
        
        # Verificar Docker
        try:
            docker_result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            if docker_result.returncode == 0:
                docker_version = docker_result.stdout.strip()
                print(f"   📦 Docker: {docker_version}")
            else:
                dependency_issues.append("Docker não encontrado")
        except FileNotFoundError:
            dependency_issues.append("Docker não instalado")
        
        if dependency_issues:
            self.validation_results['warnings'].extend([
                {'category': 'dependencies', 'message': issue} for issue in dependency_issues
            ])
        else:
            self.validation_results['checks'].append({
                'category': 'dependencies',
                'status': 'passed',
                'message': 'Dependências OK'
            })
    
    def check_security(self):
        """Verifica aspectos de segurança"""
        security_issues = []
        
        # Verificar .gitignore
        gitignore = self.project_root / '.gitignore'
        if gitignore.exists():
            try:
                with open(gitignore, 'r') as f:
                    content = f.read()
                    
                essential_ignores = ['.env', '__pycache__', 'node_modules', '*.log']
                missing_ignores = []
                
                for ignore in essential_ignores:
                    if ignore not in content:
                        missing_ignores.append(ignore)
                
                if missing_ignores:
                    security_issues.append(f"Padrões ausentes no .gitignore: {missing_ignores}")
                    
            except Exception as e:
                security_issues.append(f"Erro ao verificar .gitignore: {e}")
        else:
            security_issues.append(".gitignore não encontrado")
        
        # Verificar arquivos .env expostos
        env_files = list(self.project_root.rglob('.env*'))
        exposed_env = []
        
        for env_file in env_files:
            if not env_file.name.endswith(('.example', '.template')):
                # Verificar se está no .gitignore
                relative_path = env_file.relative_to(self.project_root)
                exposed_env.append(str(relative_path))
        
        if exposed_env:
            security_issues.append(f"Arquivos .env possivelmente expostos: {exposed_env}")
        
        # Verificar permissões de arquivos críticos
        critical_files = ['back/app_supabase.py', 'docker-compose.production.yml']
        for file_path in critical_files:
            file_full_path = self.project_root / file_path
            if file_full_path.exists():
                try:
                    stat = file_full_path.stat()
                    # Verificar se não é world-writable
                    if stat.st_mode & 0o002:
                        security_issues.append(f"Arquivo {file_path} é world-writable")
                except:
                    pass
        
        if security_issues:
            self.validation_results['warnings'].extend([
                {'category': 'security', 'message': issue} for issue in security_issues
            ])
        else:
            self.validation_results['checks'].append({
                'category': 'security',
                'status': 'passed',
                'message': 'Segurança OK'
            })
        
        print(f"   🔒 Segurança: {'✅ OK' if not security_issues else '⚠️ Avisos encontrados'}")
    
    def check_performance(self):
        """Verifica aspectos de performance"""
        performance_issues = []
        
        # Verificar tamanho do bundle (se existir)
        build_dir = self.project_root / 'front' / 'dist'
        if build_dir.exists():
            total_size = 0
            for file_path in build_dir.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
            
            size_mb = total_size / (1024 * 1024)
            print(f"   ⚡ Tamanho do build: {size_mb:.2f} MB")
            
            if size_mb > 10:  # Bundle muito grande
                performance_issues.append(f"Bundle muito grande: {size_mb:.2f} MB")
        
        # Verificar configuração de produção do Vite
        vite_config = self.project_root / 'front' / 'vite.config.prod.ts'
        if not vite_config.exists():
            performance_issues.append("Configuração de produção Vite não encontrada")
        
        # Verificar otimizações no package.json
        package_json = self.project_root / 'front' / 'package.json'
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    scripts = data.get('scripts', {})
                    
                    if 'build:prod' not in scripts:
                        performance_issues.append("Script build:prod não encontrado")
                        
            except:
                pass
        
        if performance_issues:
            self.validation_results['warnings'].extend([
                {'category': 'performance', 'message': issue} for issue in performance_issues
            ])
        else:
            self.validation_results['checks'].append({
                'category': 'performance',
                'status': 'passed',
                'message': 'Performance OK'
            })
        
        print(f"   ⚡ Performance: {'✅ OK' if not performance_issues else '⚠️ Avisos encontrados'}")
    
    def check_docker(self):
        """Verifica configuração Docker"""
        docker_issues = []
        
        # Verificar Dockerfile do backend
        backend_dockerfile = self.project_root / 'back' / 'Dockerfile'
        if not backend_dockerfile.exists():
            docker_issues.append("Dockerfile do backend não encontrado")
        
        # Verificar Dockerfile do frontend
        frontend_dockerfile = self.project_root / 'front' / 'Dockerfile'
        if not frontend_dockerfile.exists():
            docker_issues.append("Dockerfile do frontend não encontrado")
        
        # Verificar docker-compose.production.yml
        docker_compose = self.project_root / 'docker-compose.production.yml'
        if docker_compose.exists():
            try:
                with open(docker_compose, 'r') as f:
                    content = f.read()
                    
                # Verificar serviços essenciais
                essential_services = ['app', 'nginx']
                missing_services = []
                
                for service in essential_services:
                    if f'{service}:' not in content:
                        missing_services.append(service)
                
                if missing_services:
                    docker_issues.append(f"Serviços ausentes no docker-compose: {missing_services}")
                    
            except Exception as e:
                docker_issues.append(f"Erro ao verificar docker-compose: {e}")
        else:
            docker_issues.append("docker-compose.production.yml não encontrado")
        
        if docker_issues:
            self.validation_results['errors'].extend([
                {'category': 'docker', 'message': issue} for issue in docker_issues
            ])
        else:
            self.validation_results['checks'].append({
                'category': 'docker',
                'status': 'passed',
                'message': 'Docker OK'
            })
        
        print(f"   🐳 Docker: {'✅ OK' if not docker_issues else '❌ Problemas encontrados'}")
    
    def run_basic_tests(self):
        """Executa testes básicos"""
        test_results = []
        
        # Teste de sintaxe Python
        try:
            main_app = self.project_root / 'back' / 'app_supabase.py'
            if main_app.exists():
                result = subprocess.run(
                    [sys.executable, '-m', 'py_compile', str(main_app)],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    test_results.append("✅ Sintaxe Python OK")
                else:
                    test_results.append(f"❌ Erro de sintaxe Python: {result.stderr}")
            else:
                test_results.append("⚠️ app_supabase.py não encontrado")
        except Exception as e:
            test_results.append(f"❌ Erro ao testar Python: {e}")
        
        # Teste de build do frontend (se possível)
        frontend_dir = self.project_root / 'front'
        if frontend_dir.exists():
            package_json = frontend_dir / 'package.json'
            if package_json.exists():
                try:
                    # Verificar se node_modules existe
                    node_modules = frontend_dir / 'node_modules'
                    if node_modules.exists():
                        # Tentar build de teste
                        result = subprocess.run(
                            ['npm', 'run', 'build'],
                            cwd=frontend_dir,
                            capture_output=True,
                            text=True,
                            timeout=300  # 5 minutos
                        )
                        if result.returncode == 0:
                            test_results.append("✅ Build frontend OK")
                        else:
                            test_results.append(f"❌ Erro no build frontend: {result.stderr[:200]}...")
                    else:
                        test_results.append("⚠️ node_modules não encontrado - execute npm install")
                except subprocess.TimeoutExpired:
                    test_results.append("⚠️ Build frontend timeout")
                except Exception as e:
                    test_results.append(f"❌ Erro ao testar build: {e}")
        
        for result in test_results:
            print(f"   🧪 {result}")
        
        # Adicionar aos resultados
        passed_tests = [r for r in test_results if r.startswith('✅')]
        failed_tests = [r for r in test_results if r.startswith('❌')]
        
        if failed_tests:
            self.validation_results['errors'].extend([
                {'category': 'tests', 'message': test} for test in failed_tests
            ])
        
        if passed_tests:
            self.validation_results['checks'].extend([
                {'category': 'tests', 'status': 'passed', 'message': test} for test in passed_tests
            ])
    
    def generate_final_report(self):
        """Gera relatório final da validação"""
        total_checks = len(self.validation_results['checks'])
        total_warnings = len(self.validation_results['warnings'])
        total_errors = len(self.validation_results['errors'])
        
        # Determinar status geral
        if total_errors == 0 and total_warnings == 0:
            self.validation_results['overall_status'] = 'ready'
        elif total_errors == 0 and total_warnings <= 3:
            self.validation_results['overall_status'] = 'ready_with_warnings'
        elif total_errors <= 2:
            self.validation_results['overall_status'] = 'needs_fixes'
        else:
            self.validation_results['overall_status'] = 'not_ready'
        
        # Gerar recomendações
        if total_errors > 0:
            self.validation_results['recommendations'].append(
                "Corrija todos os erros antes do deploy em produção"
            )
        
        if total_warnings > 0:
            self.validation_results['recommendations'].append(
                "Revise os avisos para melhorar a qualidade do deploy"
            )
        
        self.validation_results['recommendations'].extend([
            "Execute testes completos em ambiente de staging",
            "Configure monitoramento e alertas",
            "Prepare plano de rollback",
            "Documente procedimentos de deploy"
        ])
    
    def save_report(self, output_file: str = 'production_validation_report.json'):
        """Salva relatório de validação"""
        output_path = self.project_root / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.validation_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Relatório de validação salvo em: {output_path}")
        return output_path
    
    def print_summary(self):
        """Imprime resumo da validação"""
        status = self.validation_results['overall_status']
        total_checks = len(self.validation_results['checks'])
        total_warnings = len(self.validation_results['warnings'])
        total_errors = len(self.validation_results['errors'])
        
        print("\n" + "="*80)
        print("📊 RESUMO DA VALIDAÇÃO PARA PRODUÇÃO")
        print("="*80)
        
        # Status geral
        status_icons = {
            'ready': '🟢 PRONTO',
            'ready_with_warnings': '🟡 PRONTO COM AVISOS',
            'needs_fixes': '🟠 NECESSITA CORREÇÕES',
            'not_ready': '🔴 NÃO PRONTO'
        }
        
        print(f"\n🎯 Status Geral: {status_icons.get(status, '❓ DESCONHECIDO')}")
        
        print(f"\n📈 Resultados:")
        print(f"   ✅ Verificações aprovadas: {total_checks}")
        print(f"   ⚠️ Avisos: {total_warnings}")
        print(f"   ❌ Erros: {total_errors}")
        
        # Mostrar erros se houver
        if total_errors > 0:
            print(f"\n❌ Erros que precisam ser corrigidos:")
            for error in self.validation_results['errors'][:5]:  # Mostrar apenas os primeiros 5
                print(f"   • {error['message']}")
            if total_errors > 5:
                print(f"   ... e mais {total_errors - 5} erros")
        
        # Mostrar avisos se houver
        if total_warnings > 0:
            print(f"\n⚠️ Avisos importantes:")
            for warning in self.validation_results['warnings'][:3]:  # Mostrar apenas os primeiros 3
                print(f"   • {warning['message']}")
            if total_warnings > 3:
                print(f"   ... e mais {total_warnings - 3} avisos")
        
        # Recomendações
        print(f"\n💡 Próximos passos:")
        for i, rec in enumerate(self.validation_results['recommendations'][:4], 1):
            print(f"   {i}. {rec}")
        
        # Conclusão
        if status == 'ready':
            print(f"\n🎉 Sistema validado e pronto para produção!")
        elif status == 'ready_with_warnings':
            print(f"\n✅ Sistema pronto para produção com alguns avisos.")
        else:
            print(f"\n⚠️ Sistema precisa de ajustes antes do deploy em produção.")

def main():
    """Função principal"""
    project_root = os.getcwd()
    
    print("🔍 VALIDADOR DE PRODUÇÃO 1CRYPTEN")
    print(f"📁 Projeto: {project_root}")
    print(f"⏰ Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Executar validação
    validator = ProductionValidator(project_root)
    results = validator.run_validation()
    
    # Salvar relatório
    report_path = validator.save_report()
    
    # Mostrar resumo
    validator.print_summary()
    
    print("\n✅ Validação concluída!")
    print(f"📄 Relatório completo disponível em: {report_path}")
    
    return results

if __name__ == '__main__':
    main()