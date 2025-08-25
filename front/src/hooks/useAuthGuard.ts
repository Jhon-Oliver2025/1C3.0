
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
      return false;
    }
    
    if (!isAuthenticated) {
      return false;
    }
    
    const token = localStorage.getItem('token');
    if (!token) {
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
