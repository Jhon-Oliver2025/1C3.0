import { useState, useCallback, useRef } from 'react';

/**
 * Hook para gerenciar autenticação com retry automático
 * Resolve problemas de login intermitente e melhora a experiência do usuário
 */
export const useAuthManager = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const retryAttempts = useRef<number>(0);
  const maxRetries = 3;
  const retryDelay = 1000; // 1 segundo

  /**
   * Limpa o estado de erro
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  /**
   * Valida se o email tem formato correto
   */
  const validateEmail = useCallback((email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }, []);

  /**
   * Valida se a senha atende aos critérios mínimos
   */
  const validatePassword = useCallback((password: string): boolean => {
    return password.length >= 6;
  }, []);

  /**
   * Aguarda um tempo antes de tentar novamente
   */
  const delay = useCallback((ms: number): Promise<void> => {
    return new Promise(resolve => setTimeout(resolve, ms));
  }, []);

  /**
   * Faz login com retry automático
   */
  const login = useCallback(async (email: string, password: string): Promise<boolean> => {
    // Validações básicas
    if (!validateEmail(email)) {
      setError('Email inválido');
      return false;
    }

    if (!validatePassword(password)) {
      setError('Senha deve ter pelo menos 6 caracteres');
      return false;
    }

    setIsLoading(true);
    setError(null);
    retryAttempts.current = 0;

    while (retryAttempts.current < maxRetries) {
      try {
        console.log(`🔐 Auth: Tentativa de login ${retryAttempts.current + 1}/${maxRetries}`);
        
        const response = await fetch('/api/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ email, password }),
        });

        if (response.ok) {
          const data = await response.json();
          
          if (data.token) {
            // Salvar token
            localStorage.setItem('token', data.token);
            
            // Salvar dados do usuário se disponível
            if (data.user) {
              localStorage.setItem('user', JSON.stringify(data.user));
            }

            console.log('✅ Auth: Login realizado com sucesso');
            setIsLoading(false);
            retryAttempts.current = 0;
            return true;
          } else {
            throw new Error('Token não recebido');
          }
        } else {
          const errorData = await response.json().catch(() => ({ message: 'Erro desconhecido' }));
          
          // Se for erro de credenciais, não tentar novamente
          if (response.status === 401 || response.status === 403) {
            setError('Email ou senha incorretos');
            setIsLoading(false);
            return false;
          }
          
          throw new Error(errorData.message || `Erro ${response.status}`);
        }
      } catch (error) {
        retryAttempts.current++;
        console.warn(`🔐 Auth: Erro na tentativa ${retryAttempts.current}:`, error);
        
        if (retryAttempts.current >= maxRetries) {
          setError(`Falha no login após ${maxRetries} tentativas. Verifique sua conexão.`);
          setIsLoading(false);
          return false;
        }
        
        // Aguardar antes da próxima tentativa
        await delay(retryDelay * retryAttempts.current);
      }
    }

    setIsLoading(false);
    return false;
  }, [validateEmail, validatePassword, delay]);

  /**
   * Faz logout e limpa dados
   */
  const logout = useCallback(async (): Promise<void> => {
    try {
      const token = localStorage.getItem('token');
      
      if (token) {
        // Tentar fazer logout no servidor
        await fetch('/api/auth/logout', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }).catch(() => {
          // Ignorar erros de logout no servidor
          console.warn('🔐 Auth: Erro ao fazer logout no servidor (ignorado)');
        });
      }
    } finally {
      // Sempre limpar dados locais
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      console.log('🔐 Auth: Logout realizado');
    }
  }, []);

  /**
   * Verifica se o usuário está autenticado
   */
  const isAuthenticated = useCallback((): boolean => {
    const token = localStorage.getItem('token');
    return !!token;
  }, []);

  /**
   * Obtém dados do usuário do localStorage
   */
  const getUser = useCallback(() => {
    try {
      const userStr = localStorage.getItem('user');
      return userStr ? JSON.parse(userStr) : null;
    } catch (error) {
      console.warn('🔐 Auth: Erro ao obter dados do usuário:', error);
      return null;
    }
  }, []);

  /**
   * Obtém o token atual
   */
  const getToken = useCallback((): string | null => {
    return localStorage.getItem('token');
  }, []);

  /**
   * Valida token no servidor
   */
  const validateToken = useCallback(async (): Promise<boolean> => {
    const token = getToken();
    if (!token) return false;

    try {
      const response = await fetch('/api/auth/validate', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        await logout();
        return false;
      }

      return true;
    } catch (error) {
      console.warn('🔐 Auth: Erro ao validar token:', error);
      await logout();
      return false;
    }
  }, [getToken, logout]);

  /**
   * Renova o token se necessário
   */
  const refreshToken = useCallback(async (): Promise<boolean> => {
    const token = getToken();
    if (!token) return false;

    try {
      const response = await fetch('/api/auth/refresh', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        if (data.token) {
          localStorage.setItem('token', data.token);
          console.log('🔐 Auth: Token renovado com sucesso');
          return true;
        }
      }

      return false;
    } catch (error) {
      console.warn('🔐 Auth: Erro ao renovar token:', error);
      return false;
    }
  }, [getToken]);

  return {
    login,
    logout,
    isAuthenticated,
    getUser,
    getToken,
    validateToken,
    refreshToken,
    isLoading,
    error,
    clearError,
    retryAttempts: retryAttempts.current
  };
};

export default useAuthManager;