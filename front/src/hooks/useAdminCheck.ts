import { useState, useEffect } from 'react';

/**
 * Hook para verificar se o usuário atual é administrador
 * Retorna o status de admin e uma função para recarregar a verificação
 */
export const useAdminCheck = () => {
  const [isAdmin, setIsAdmin] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  /**
   * Verifica se o usuário é admin
   */
  const checkAdminStatus = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const token = localStorage.getItem('token');
      if (!token) {
        setIsAdmin(false);
        setIsLoading(false);
        return;
      }

      const response = await fetch('/api/auth/check-admin', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setIsAdmin(data.is_admin || false);
      } else {
        setIsAdmin(false);
        if (response.status === 401) {
          // Token inválido, remover
          localStorage.removeItem('token');
        }
      }
    } catch (err) {
      console.error('Erro ao verificar status de admin:', err);
      setError('Erro ao verificar permissões');
      setIsAdmin(false);
    } finally {
      setIsLoading(false);
    }
  };

  // Verificar status ao montar o componente
  useEffect(() => {
    checkAdminStatus();
  }, []);

  // Escutar mudanças no token
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'token') {
        checkAdminStatus();
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  return {
    isAdmin,
    isLoading,
    error,
    recheckAdmin: checkAdminStatus
  };
};

export default useAdminCheck;