#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Diagnóstico Completo - 1Crypten
Analisa todo o sistema para otimização de produção
Identifica código não utilizado, problemas de performance e melhorias
"""

import os
import sys
import json
import re
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple
import ast
import importlib.util

class SystemDiagnostic:
    """Sistema completo de diagnóstico e otimização"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.report = {
            'timestamp': datetime.now().isoformat(),
            'project_root': str(self.project_root),
            'summary': {},
            'backend_analysis': {},
            'frontend_analysis': {},
            'unused_files': [],
            'performance_issues': [],
            'security_issues': [],
            'optimization_suggestions': [],
            'cleanup_actions': []
        }
        
    def run_full_diagnostic(self) -> Dict:
        """Executa diagnóstico completo do sistema"""
        print("🔍 INICIANDO DIAGNÓSTICO COMPLETO DO SISTEMA 1CRYPTEN")
        print("="*80)
        
        # Análise do Backend
        print("\n📊 Analisando Backend Python...")
        self.analyze_backend()
        
        # Análise do Frontend
        print("\n🎨 Analisando Frontend React/TypeScript...")
        self.analyze_frontend()
        
        # Análise de arquivos não utilizados
        print("\n🗑️ Identificando arquivos não utilizados...")
        self.find_unused_files()
        
        # Análise de performance
        print("\n⚡ Analisando performance...")
        self.analyze_performance()
        
        # Análise de segurança
        print("\n🔒 Verificando segurança...")
        self.analyze_security()
        
        # Gerar sugestões de otimização
        print("\n💡 Gerando sugestões de otimização...")
        self.generate_optimization_suggestions()
        
        # Gerar relatório final
        print("\n📋 Gerando relatório final...")
        self.generate_summary()
        
        return self.report
    
    def analyze_backend(self):
        """Analisa o código Python do backend"""
        backend_path = self.project_root / 'back'
        if not backend_path.exists():
            return
        
        analysis = {
            'total_files': 0,
            'total_lines': 0,
            'imports': set(),
            'unused_imports': [],
            'duplicate_code': [],
            'complex_functions': [],
            'missing_docstrings': [],
            'security_issues': [],
            'performance_issues': []
        }
        
        # Analisar todos os arquivos Python
        for py_file in backend_path.rglob('*.py'):
            if '__pycache__' in str(py_file):
                continue
                
            analysis['total_files'] += 1
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    analysis['total_lines'] += len(lines)
                    
                    # Analisar AST
                    try:
                        tree = ast.parse(content)
                        self._analyze_python_ast(tree, py_file, analysis)
                    except SyntaxError:
                        analysis['security_issues'].append({
                            'file': str(py_file),
                            'issue': 'Syntax Error',
                            'severity': 'high'
                        })
                        
            except Exception as e:
                print(f"⚠️ Erro ao analisar {py_file}: {e}")
        
        # Converter sets para listas para JSON
        analysis['imports'] = list(analysis['imports'])
        self.report['backend_analysis'] = analysis
    
    def _analyze_python_ast(self, tree: ast.AST, file_path: Path, analysis: Dict):
        """Analisa AST de arquivo Python"""
        for node in ast.walk(tree):
            # Imports
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis['imports'].add(alias.name)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    analysis['imports'].add(node.module)
            
            # Funções complexas (muitas linhas)
            elif isinstance(node, ast.FunctionDef):
                if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                    lines = node.end_lineno - node.lineno
                    if lines > 50:  # Função muito longa
                        analysis['complex_functions'].append({
                            'file': str(file_path),
                            'function': node.name,
                            'lines': lines,
                            'line_start': node.lineno
                        })
                
                # Verificar docstring
                if not ast.get_docstring(node):
                    analysis['missing_docstrings'].append({
                        'file': str(file_path),
                        'function': node.name,
                        'line': node.lineno
                    })
            
            # Possíveis problemas de segurança
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['eval', 'exec', 'compile']:
                        analysis['security_issues'].append({
                            'file': str(file_path),
                            'issue': f'Uso de {node.func.id}()',
                            'line': node.lineno,
                            'severity': 'high'
                        })
    
    def analyze_frontend(self):
        """Analisa o código React/TypeScript do frontend"""
        frontend_path = self.project_root / 'front' / 'src'
        if not frontend_path.exists():
            return
        
        analysis = {
            'total_files': 0,
            'total_lines': 0,
            'components': [],
            'unused_imports': [],
            'large_components': [],
            'missing_types': [],
            'performance_issues': [],
            'bundle_analysis': {}
        }
        
        # Analisar arquivos TypeScript/JavaScript
        for file_ext in ['*.tsx', '*.ts', '*.jsx', '*.js']:
            for file_path in frontend_path.rglob(file_ext):
                if 'node_modules' in str(file_path):
                    continue
                    
                analysis['total_files'] += 1
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                        analysis['total_lines'] += len(lines)
                        
                        # Analisar componente
                        if file_path.suffix in ['.tsx', '.jsx']:
                            self._analyze_react_component(content, file_path, analysis)
                            
                except Exception as e:
                    print(f"⚠️ Erro ao analisar {file_path}: {e}")
        
        self.report['frontend_analysis'] = analysis
    
    def _analyze_react_component(self, content: str, file_path: Path, analysis: Dict):
        """Analisa componente React"""
        lines = content.split('\n')
        
        # Componente muito grande
        if len(lines) > 500:
            analysis['large_components'].append({
                'file': str(file_path),
                'lines': len(lines),
                'suggestion': 'Considere dividir em componentes menores'
            })
        
        # Verificar imports não utilizados (básico)
        imports = re.findall(r'import\s+.*?from\s+[\'"]([^\'"]*)[\'"]', content)
        for imp in imports:
            if imp not in content.replace(f'from \'{imp}\'', '').replace(f'from "{imp}"', ''):
                analysis['unused_imports'].append({
                    'file': str(file_path),
                    'import': imp
                })
        
        # Verificar possíveis problemas de performance
        if 'useEffect(() => {' in content and 'setInterval' in content:
            analysis['performance_issues'].append({
                'file': str(file_path),
                'issue': 'Possível memory leak com setInterval em useEffect',
                'suggestion': 'Verificar se clearInterval está sendo chamado'
            })
    
    def find_unused_files(self):
        """Identifica arquivos potencialmente não utilizados"""
        unused_files = []
        
        # Arquivos de teste antigos
        test_patterns = ['test_*.py', '*_test.py', '*.test.js', '*.test.ts']
        for pattern in test_patterns:
            for file_path in self.project_root.rglob(pattern):
                # Verificar se é realmente um teste não utilizado
                if self._is_file_unused(file_path):
                    unused_files.append({
                        'file': str(file_path),
                        'type': 'test_file',
                        'reason': 'Arquivo de teste possivelmente não utilizado'
                    })
        
        # Arquivos HTML de debug
        for html_file in self.project_root.rglob('*.html'):
            if any(keyword in html_file.name.lower() for keyword in ['debug', 'test', 'temp', 'fix']):
                unused_files.append({
                    'file': str(html_file),
                    'type': 'debug_file',
                    'reason': 'Arquivo de debug/teste temporário'
                })
        
        # Arquivos de configuração duplicados
        config_files = list(self.project_root.rglob('*.example')) + list(self.project_root.rglob('*.old'))
        for config_file in config_files:
            unused_files.append({
                'file': str(config_file),
                'type': 'config_backup',
                'reason': 'Arquivo de backup/exemplo'
            })
        
        self.report['unused_files'] = unused_files
    
    def _is_file_unused(self, file_path: Path) -> bool:
        """Verifica se um arquivo está sendo utilizado"""
        # Lógica simples - pode ser expandida
        try:
            stat = file_path.stat()
            # Se não foi modificado há mais de 30 dias, pode estar não utilizado
            days_since_modified = (datetime.now().timestamp() - stat.st_mtime) / (24 * 3600)
            return days_since_modified > 30
        except:
            return False
    
    def analyze_performance(self):
        """Analisa problemas de performance"""
        issues = []
        
        # Verificar tamanho de arquivos
        large_files = []
        for file_path in self.project_root.rglob('*'):
            if file_path.is_file():
                try:
                    size_mb = file_path.stat().st_size / (1024 * 1024)
                    if size_mb > 10:  # Arquivos maiores que 10MB
                        large_files.append({
                            'file': str(file_path),
                            'size_mb': round(size_mb, 2)
                        })
                except:
                    pass
        
        if large_files:
            issues.append({
                'category': 'large_files',
                'description': 'Arquivos grandes que podem impactar performance',
                'files': large_files,
                'suggestion': 'Considere otimizar ou mover para CDN'
            })
        
        # Verificar dependências do frontend
        package_json = self.project_root / 'front' / 'package.json'
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    deps = data.get('dependencies', {})
                    dev_deps = data.get('devDependencies', {})
                    
                    total_deps = len(deps) + len(dev_deps)
                    if total_deps > 50:
                        issues.append({
                            'category': 'dependencies',
                            'description': f'Muitas dependências ({total_deps})',
                            'suggestion': 'Revisar e remover dependências não utilizadas'
                        })
            except:
                pass
        
        self.report['performance_issues'] = issues
    
    def analyze_security(self):
        """Analisa problemas de segurança"""
        issues = []
        
        # Verificar arquivos .env expostos
        env_files = list(self.project_root.rglob('.env*'))
        for env_file in env_files:
            if not env_file.name.endswith('.example'):
                issues.append({
                    'category': 'exposed_secrets',
                    'file': str(env_file),
                    'severity': 'high',
                    'description': 'Arquivo .env pode conter credenciais'
                })
        
        # Verificar hardcoded secrets (básico)
        secret_patterns = [r'password\s*=\s*[\'"][^\'"]+[\'"]', 
                          r'api_key\s*=\s*[\'"][^\'"]+[\'"]',
                          r'secret\s*=\s*[\'"][^\'"]+[\'"]']
        
        for py_file in self.project_root.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for pattern in secret_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            issues.append({
                                'category': 'hardcoded_secrets',
                                'file': str(py_file),
                                'severity': 'medium',
                                'description': 'Possível credencial hardcoded'
                            })
            except:
                pass
        
        self.report['security_issues'] = issues
    
    def generate_optimization_suggestions(self):
        """Gera sugestões de otimização"""
        suggestions = []
        
        # Baseado na análise do backend
        backend = self.report['backend_analysis']
        if backend.get('total_files', 0) > 0:
            if len(backend.get('complex_functions', [])) > 0:
                suggestions.append({
                    'category': 'code_quality',
                    'priority': 'medium',
                    'description': 'Refatorar funções complexas',
                    'details': f"{len(backend['complex_functions'])} funções com mais de 50 linhas"
                })
            
            if len(backend.get('missing_docstrings', [])) > 5:
                suggestions.append({
                    'category': 'documentation',
                    'priority': 'low',
                    'description': 'Adicionar docstrings às funções',
                    'details': f"{len(backend['missing_docstrings'])} funções sem documentação"
                })
        
        # Baseado na análise do frontend
        frontend = self.report['frontend_analysis']
        if frontend.get('total_files', 0) > 0:
            if len(frontend.get('large_components', [])) > 0:
                suggestions.append({
                    'category': 'component_optimization',
                    'priority': 'medium',
                    'description': 'Dividir componentes grandes',
                    'details': f"{len(frontend['large_components'])} componentes com mais de 500 linhas"
                })
        
        # Sugestões gerais
        if len(self.report['unused_files']) > 0:
            suggestions.append({
                'category': 'cleanup',
                'priority': 'high',
                'description': 'Remover arquivos não utilizados',
                'details': f"{len(self.report['unused_files'])} arquivos identificados para remoção"
            })
        
        self.report['optimization_suggestions'] = suggestions
    
    def generate_summary(self):
        """Gera resumo do diagnóstico"""
        backend = self.report['backend_analysis']
        frontend = self.report['frontend_analysis']
        
        summary = {
            'total_backend_files': backend.get('total_files', 0),
            'total_backend_lines': backend.get('total_lines', 0),
            'total_frontend_files': frontend.get('total_files', 0),
            'total_frontend_lines': frontend.get('total_lines', 0),
            'unused_files_count': len(self.report['unused_files']),
            'performance_issues_count': len(self.report['performance_issues']),
            'security_issues_count': len(self.report['security_issues']),
            'optimization_suggestions_count': len(self.report['optimization_suggestions']),
            'overall_health': 'good'  # Será calculado
        }
        
        # Calcular saúde geral
        issues_count = (summary['unused_files_count'] + 
                       summary['performance_issues_count'] + 
                       summary['security_issues_count'])
        
        if issues_count == 0:
            summary['overall_health'] = 'excellent'
        elif issues_count <= 5:
            summary['overall_health'] = 'good'
        elif issues_count <= 15:
            summary['overall_health'] = 'fair'
        else:
            summary['overall_health'] = 'needs_attention'
        
        self.report['summary'] = summary
    
    def save_report(self, output_file: str = 'system_diagnostic_report.json'):
        """Salva relatório em arquivo JSON"""
        output_path = self.project_root / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Relatório salvo em: {output_path}")
        return output_path
    
    def print_summary(self):
        """Imprime resumo do diagnóstico"""
        summary = self.report['summary']
        
        print("\n" + "="*80)
        print("📊 RESUMO DO DIAGNÓSTICO DO SISTEMA")
        print("="*80)
        
        print(f"\n🏥 Saúde Geral: {summary['overall_health'].upper()}")
        print(f"\n📈 Estatísticas:")
        print(f"   Backend: {summary['total_backend_files']} arquivos, {summary['total_backend_lines']} linhas")
        print(f"   Frontend: {summary['total_frontend_files']} arquivos, {summary['total_frontend_lines']} linhas")
        
        print(f"\n⚠️ Problemas Identificados:")
        print(f"   🗑️ Arquivos não utilizados: {summary['unused_files_count']}")
        print(f"   ⚡ Problemas de performance: {summary['performance_issues_count']}")
        print(f"   🔒 Problemas de segurança: {summary['security_issues_count']}")
        
        print(f"\n💡 Sugestões de otimização: {summary['optimization_suggestions_count']}")
        
        if self.report['optimization_suggestions']:
            print("\n🎯 Principais Sugestões:")
            for suggestion in self.report['optimization_suggestions'][:3]:
                priority_icon = "🔴" if suggestion['priority'] == 'high' else "🟡" if suggestion['priority'] == 'medium' else "🟢"
                print(f"   {priority_icon} {suggestion['description']} ({suggestion['details']})")

def main():
    """Função principal"""
    project_root = os.getcwd()
    
    print("🚀 SISTEMA DE DIAGNÓSTICO 1CRYPTEN")
    print(f"📁 Projeto: {project_root}")
    print(f"⏰ Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Executar diagnóstico
    diagnostic = SystemDiagnostic(project_root)
    report = diagnostic.run_full_diagnostic()
    
    # Salvar relatório
    report_path = diagnostic.save_report()
    
    # Mostrar resumo
    diagnostic.print_summary()
    
    print("\n✅ Diagnóstico concluído!")
    print(f"📄 Relatório completo disponível em: {report_path}")
    
    return report

if __name__ == '__main__':
    main()