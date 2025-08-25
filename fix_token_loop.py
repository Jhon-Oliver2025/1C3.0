#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir problema de loop infinito de token - 1Crypten
Identifica e corrige problemas de gerenciamento de estado de autenticação
"""

import os
import re
import json
from datetime import datetime
from typing import List, Dict

class TokenLoopFixer:
    """Corretor de problemas de loop de token"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = project_root
        self.frontend_path = os.path.join(project_root, "front", "src")
        self.issues_found = []
        self.fixes_applied = []
        
    def analyze_token_usage(self) -> Dict:
        """Analisa uso de tokens no frontend"""
        print("🔍 Analisando uso de tokens no frontend...")
        
        token_patterns = {
            'localStorage_get': r"localStorage\.getItem\(['\"]token['\"]\)",
            'token_not_found': r"Token não encontrado",
            'fetch_with_token': r"fetch\([^)]+headers[^}]+Authorization[^}]+Bearer",
            'token_validation': r"validateToken|verifyToken|checkToken"
        }
        
        results = {
            'files_analyzed': 0,
            'token_usages': {},
            'potential_issues': []
        }
        
        # Analisar arquivos TypeScript/JavaScript
        for root, dirs, files in os.walk(self.frontend_path):
            for file in files:
                if file.endswith(('.ts', '.tsx', '.js', '.jsx')):
                    file_path = os.path.join(root, file)
                    results['files_analyzed'] += 1
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Verificar padrões
                        for pattern_name, pattern in token_patterns.items():
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            if matches:
                                if pattern_name not in results['token_usages']:
                                    results['token_usages'][pattern_name] = []
                                
                                results['token_usages'][pattern_name].append({
                                    'file': file_path,
                                    'matches': len(matches)
                                })
                        
                        # Verificar problemas específicos
                        self._check_file_issues(file_path, content, results)
                        
                    except Exception as e:
                        print(f"   ⚠️ Erro ao analisar {file_path}: {e}")
        
        return results
    
    def _check_file_issues(self, file_path: str, content: str, results: Dict):
        """Verifica problemas específicos em um arquivo"""
        issues = []
        
        # 1. Verificar se há fetch sem verificação de token
        fetch_pattern = r"fetch\([^)]+\)"
        token_check_pattern = r"localStorage\.getItem\(['\"]token['\"]\)"
        
        fetch_matches = re.findall(fetch_pattern, content)
        token_checks = re.findall(token_check_pattern, content)
        
        if len(fetch_matches) > len(token_checks) * 2:  # Heurística
            issues.append({
                'type': 'missing_token_check',
                'description': 'Muitas requisições fetch sem verificação adequada de token',
                'file': file_path
            })
        
        # 2. Verificar loops infinitos potenciais
        if 'Token não encontrado' in content and 'useEffect' in content:
            # Verificar se há useEffect sem dependências adequadas
            useeffect_pattern = r"useEffect\([^}]+\}\s*,\s*\[([^\]]*)\]"
            useeffect_matches = re.findall(useeffect_pattern, content)
            
            for match in useeffect_matches:
                if not match.strip():  # Array de dependências vazio
                    issues.append({
                        'type': 'infinite_loop_risk',
                        'description': 'useEffect com array de dependências vazio pode causar loop infinito',
                        'file': file_path
                    })
        
        # 3. Verificar se há verificação de autenticação antes de fetch
        if 'fetch(' in content and 'Token não encontrado' in content:
            # Verificar se há verificação adequada
            auth_check_patterns = [
                r"isAuthenticated\(\)",
                r"if\s*\(\s*token\s*\)",
                r"if\s*\(!\s*token\s*\)"
            ]
            
            has_auth_check = any(re.search(pattern, content) for pattern in auth_check_patterns)
            
            if not has_auth_check:
                issues.append({
                    'type': 'missing_auth_check',
                    'description': 'Requisições sem verificação adequada de autenticação',
                    'file': file_path
                })
        
        results['potential_issues'].extend(issues)
    
    def create_auth_guard_hook(self) -> str:
        """Cria um hook de proteção de autenticação"""
        hook_content = '''
import { useEffect, useCallback } from 'react';
import { usePWA } from '../components/PWA/PWAProvider';

/**
 * Hook para proteger componentes que precisam de autenticação
 * Evita loops infinitos e gerencia estado de token adequadamente
 */
export const useAuthGuard = () => {
  const { isAuthenticated, user, authLoading } = usePWA();

  /**
   * Verifica se pode fazer requisições autenticadas
   */
  const canMakeAuthenticatedRequest = useCallback((): boolean => {
    if (authLoading) {
      console.log('🔄 Auth: Aguardando verificação de autenticação...');
      return false;
    }
    
    if (!isAuthenticated) {
      console.warn('🔐 Auth: Usuário não autenticado');
      return false;
    }
    
    const token = localStorage.getItem('token');
    if (!token) {
      console.warn('🔐 Auth: Token não encontrado no localStorage');
      return false;
    }
    
    return true;
  }, [isAuthenticated, authLoading]);

  /**
   * Faz requisição autenticada com verificações adequadas
   */
  const authenticatedFetch = useCallback(async (
    url: string, 
    options: RequestInit = {}
  ): Promise<Response | null> => {
    if (!canMakeAuthenticatedRequest()) {
      return null;
    }
    
    const token = localStorage.getItem('token');
    
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          ...options.headers
        }
      });
      
      // Se receber 401 ou 403, não tentar novamente para evitar loop
      if (response.status === 401 || response.status === 403) {
        console.warn('🔐 Auth: Token inválido, redirecionamento será feito pelo PWA');
        return null;
      }
      
      return response;
    } catch (error) {
      console.error('❌ Auth: Erro na requisição autenticada:', error);
      return null;
    }
  }, [canMakeAuthenticatedRequest]);

  /**
   * Executa função apenas se autenticado
   */
  const executeIfAuthenticated = useCallback((
    callback: () => void | Promise<void>
  ) => {
    if (canMakeAuthenticatedRequest()) {
      callback();
    } else {
      console.log('🔐 Auth: Operação cancelada - usuário não autenticado');
    }
  }, [canMakeAuthenticatedRequest]);

  return {
    isAuthenticated,
    user,
    authLoading,
    canMakeAuthenticatedRequest,
    authenticatedFetch,
    executeIfAuthenticated
  };
};

export default useAuthGuard;
'''
        return hook_content
    
    def create_safe_data_loader_hook(self) -> str:
        """Cria um hook para carregamento seguro de dados"""
        hook_content = '''
import { useState, useEffect, useCallback, useRef } from 'react';
import { useAuthGuard } from './useAuthGuard';

interface SafeDataLoaderOptions {
  url: string;
  interval?: number; // Intervalo de atualização em ms
  dependencies?: any[]; // Dependências para recarregar
  requireAuth?: boolean; // Se requer autenticação
}

/**
 * Hook para carregamento seguro de dados com proteção contra loops
 */
export const useSafeDataLoader = <T>(
  options: SafeDataLoaderOptions
) => {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { canMakeAuthenticatedRequest, authenticatedFetch } = useAuthGuard();
  const lastFetchTime = useRef<number>(0);
  const minInterval = 1000; // Mínimo 1 segundo entre requisições
  
  const fetchData = useCallback(async () => {
    // Evitar requisições muito frequentes
    const now = Date.now();
    if (now - lastFetchTime.current < minInterval) {
      console.log('🔄 Data: Requisição muito frequente, aguardando...');
      return;
    }
    
    // Verificar se precisa de autenticação
    if (options.requireAuth && !canMakeAuthenticatedRequest()) {
      console.log('🔐 Data: Aguardando autenticação para carregar dados');
      return;
    }
    
    setLoading(true);
    setError(null);
    lastFetchTime.current = now;
    
    try {
      let response: Response | null;
      
      if (options.requireAuth) {
        response = await authenticatedFetch(options.url);
      } else {
        response = await fetch(options.url);
      }
      
      if (!response) {
        throw new Error('Falha na requisição');
      }
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const result = await response.json();
      setData(result);
      console.log(`✅ Data: Dados carregados de ${options.url}`);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido';
      setError(errorMessage);
      console.error(`❌ Data: Erro ao carregar ${options.url}:`, errorMessage);
    } finally {
      setLoading(false);
    }
  }, [options.url, options.requireAuth, canMakeAuthenticatedRequest, authenticatedFetch]);
  
  // Carregar dados iniciais
  useEffect(() => {
    fetchData();
  }, [fetchData, ...(options.dependencies || [])]);
  
  // Configurar intervalo se especificado
  useEffect(() => {
    if (options.interval && options.interval > 0) {
      const intervalId = setInterval(fetchData, options.interval);
      return () => clearInterval(intervalId);
    }
  }, [fetchData, options.interval]);
  
  return {
    data,
    loading,
    error,
    refetch: fetchData
  };
};

export default useSafeDataLoader;
'''
        return hook_content
    
    def apply_fixes(self, analysis_results: Dict) -> List[str]:
        """Aplica correções baseadas na análise"""
        fixes = []
        
        # 1. Criar hooks de proteção
        auth_guard_path = os.path.join(self.frontend_path, "hooks", "useAuthGuard.ts")
        data_loader_path = os.path.join(self.frontend_path, "hooks", "useSafeDataLoader.ts")
        
        try:
            # Criar diretório hooks se não existir
            hooks_dir = os.path.dirname(auth_guard_path)
            os.makedirs(hooks_dir, exist_ok=True)
            
            # Criar useAuthGuard
            with open(auth_guard_path, 'w', encoding='utf-8') as f:
                f.write(self.create_auth_guard_hook())
            fixes.append(f"✅ Criado: {auth_guard_path}")
            
            # Criar useSafeDataLoader
            with open(data_loader_path, 'w', encoding='utf-8') as f:
                f.write(self.create_safe_data_loader_hook())
            fixes.append(f"✅ Criado: {data_loader_path}")
            
        except Exception as e:
            fixes.append(f"❌ Erro ao criar hooks: {e}")
        
        # 2. Criar exemplo de uso corrigido para DashboardPage
        self._create_dashboard_fix_example(fixes)
        
        return fixes
    
    def _create_dashboard_fix_example(self, fixes: List[str]):
        """Cria exemplo de correção para DashboardPage"""
        example_content = '''
// Exemplo de como corrigir o DashboardPage para evitar loops infinitos

import { useAuthGuard } from '../hooks/useAuthGuard';
import { useSafeDataLoader } from '../hooks/useSafeDataLoader';

// No componente DashboardPage:
export const DashboardPage = () => {
  const { isAuthenticated, executeIfAuthenticated } = useAuthGuard();
  
  // Carregar sinais de forma segura
  const { 
    data: signals, 
    loading: signalsLoading, 
    error: signalsError 
  } = useSafeDataLoader({
    url: '/api/btc-signals/confirmed',
    requireAuth: false, // Este endpoint não requer auth
    interval: 30000 // Atualizar a cada 30 segundos
  });
  
  // Carregar dados que requerem autenticação
  const { 
    data: cleanupStatus, 
    loading: cleanupLoading 
  } = useSafeDataLoader({
    url: '/api/cleanup-status',
    requireAuth: true, // Este endpoint requer auth
    dependencies: [isAuthenticated] // Recarregar quando auth mudar
  });
  
  // Função para ações que requerem autenticação
  const handleAuthenticatedAction = () => {
    executeIfAuthenticated(async () => {
      // Sua lógica aqui
      console.log('Executando ação autenticada');
    });
  };
  
  return (
    <div>
      {/* Seu JSX aqui */}
    </div>
  );
};
'''
        
        example_path = os.path.join(self.frontend_path, "examples", "DashboardPageFixed.example.tsx")
        
        try:
            os.makedirs(os.path.dirname(example_path), exist_ok=True)
            with open(example_path, 'w', encoding='utf-8') as f:
                f.write(example_content)
            fixes.append(f"✅ Criado exemplo: {example_path}")
        except Exception as e:
            fixes.append(f"❌ Erro ao criar exemplo: {e}")
    
    def generate_report(self, analysis: Dict, fixes: List[str]) -> str:
        """Gera relatório das correções"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'analysis': analysis,
            'fixes_applied': fixes,
            'recommendations': [
                '🔄 Substituir fetch direto por useSafeDataLoader nos componentes',
                '🔐 Usar useAuthGuard para verificações de autenticação',
                '⚡ Adicionar debounce em requisições frequentes',
                '🎯 Verificar dependências de useEffect para evitar loops',
                '📊 Monitorar console para mensagens "Token não encontrado"',
                '🔍 Implementar logs estruturados para debug'
            ]
        }
        
        report_path = "token_loop_fix_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report_path
    
    def run_fix(self) -> Dict:
        """Executa correção completa"""
        print("🔧 CORRETOR DE LOOP DE TOKEN - 1CRYPTEN")
        print("="*60)
        print(f"⏰ Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print()
        
        # Analisar problemas
        analysis = self.analyze_token_usage()
        
        print(f"\n📊 Análise concluída:")
        print(f"   📁 Arquivos analisados: {analysis['files_analyzed']}")
        print(f"   🔍 Padrões encontrados: {len(analysis['token_usages'])}")
        print(f"   ⚠️ Problemas potenciais: {len(analysis['potential_issues'])}")
        
        # Aplicar correções
        print(f"\n🔧 Aplicando correções...")
        fixes = self.apply_fixes(analysis)
        
        for fix in fixes:
            print(f"   {fix}")
        
        # Gerar relatório
        report_path = self.generate_report(analysis, fixes)
        print(f"\n📄 Relatório salvo em: {report_path}")
        
        # Resumo
        print(f"\n" + "="*60)
        print(f"📋 RESUMO DAS CORREÇÕES")
        print(f"="*60)
        print(f"✅ Hooks de proteção criados: useAuthGuard, useSafeDataLoader")
        print(f"📝 Exemplo de uso criado para DashboardPage")
        print(f"🎯 Próximos passos:")
        print(f"   1. Implementar os hooks nos componentes problemáticos")
        print(f"   2. Substituir fetch direto por useSafeDataLoader")
        print(f"   3. Testar para verificar se loops foram eliminados")
        print(f"   4. Monitorar console para confirmar correção")
        
        return {
            'analysis': analysis,
            'fixes': fixes,
            'report_path': report_path
        }

def main():
    """Função principal"""
    fixer = TokenLoopFixer()
    results = fixer.run_fix()
    return results

if __name__ == '__main__':
    main()