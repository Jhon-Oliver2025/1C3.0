
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
  
  // Carregar dados iniciais apenas se não requer auth ou se está autenticado
  useEffect(() => {
    if (!options.requireAuth || canMakeAuthenticatedRequest()) {
      fetchData();
    }
  }, [fetchData, canMakeAuthenticatedRequest, ...(options.dependencies || [])]);
  
  // Configurar intervalo se especificado e se pode fazer requisições
  useEffect(() => {
    if (options.interval && options.interval > 0) {
      if (!options.requireAuth || canMakeAuthenticatedRequest()) {
        const intervalId = setInterval(fetchData, options.interval);
        return () => clearInterval(intervalId);
      }
    }
  }, [fetchData, options.interval, canMakeAuthenticatedRequest, options.requireAuth]);
  
  return {
    data,
    loading,
    error,
    refetch: fetchData
  };
};

export default useSafeDataLoader;
