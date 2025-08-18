import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';

/**
 * Interface para dados do usuário otimizada
 */
interface UserData {
  id: string;
  username: string;
  email: string;
  is_admin: boolean;
}

/**
 * Interface para resposta de login otimizada
 */
interface LoginResponse {
  success: boolean;
  token: string;
  user: UserData;
  message?: string;
}

/**
 * Hook otimizado para autenticação com performance melhorada
 * Reduz chamadas desnecessárias à API e melhora a experiência do usuário
 */
export const useOptimizedAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(() => {
    // Inicialização otimizada - verificar token apenas uma vez
    return !!localStorage.getItem('token');
  });
  
  const [user, setUser] = useState<UserData | null>(() => {
    // Carregar dados do usuário do localStorage se disponível
    const savedUser = localStorage.getItem('user');
    return savedUser ? JSON.parse(savedUser) : null;
  });
  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  /**
   * Função de login otimizada com timeout e validação
   */
  const login = useCallback(async (username: string, password: string): Promise<boolean> => {
    setIsLoading(true);
    setError(null);

    // Validação no frontend para feedback imediato
    if (!username.trim() || !password.trim()) {
      setError('Email e senha são obrigatórios.');
      setIsLoading(false);
      return false;
    }

    try {
      // Controller para timeout otimizado
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 8000); // 8s timeout

      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          username: username.trim(), 
          password 
        }),
        signal: controller.signal
      });

      clearTimeout(timeoutId);
      const data: LoginResponse = await response.json();

      if (response.ok && data.success) {
        // Salvar dados otimizados
        localStorage.setItem('token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        // Atualizar estado
        setUser(data.user);
        setIsAuthenticated(true);
        setError(null);
        
        return true;
      } else {
        setError(data.message || 'Credenciais inválidas');
        return false;
      }
    } catch (err: any) {
      if (err.name === 'AbortError') {
        setError('Tempo limite excedido. Verifique sua conexão.');
      } else {
        setError('Erro de conexão. Tente novamente.');
      }
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Função de logout otimizada
   */
  const logout = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      if (token) {
        // Tentar fazer logout no servidor (não bloquear se falhar)
        fetch('/api/auth/logout', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }).catch(() => {
          // Ignorar erros de logout no servidor
        });
      }
    } finally {
      // Sempre limpar dados locais
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      setUser(null);
      setIsAuthenticated(false);
      setError(null);
    }
  }, []);

  /**
   * Verificação rápida de token (sem chamada à API)
   */
  const checkAuthStatus = useCallback(() => {
    const token = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');
    
    if (token && savedUser) {
      try {
        const userData = JSON.parse(savedUser);
        setUser(userData);
        setIsAuthenticated(true);
        return true;
      } catch {
        // Dados corrompidos, limpar
        logout();
        return false;
      }
    } else {
      setIsAuthenticated(false);
      setUser(null);
      return false;
    }
  }, [logout]);

  /**
   * Navegação protegida otimizada
   */
  const navigateIfAuthenticated = useCallback((path: string) => {
    if (isAuthenticated) {
      navigate(path, { replace: true });
    } else {
      navigate('/login', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  /**
   * Verificar autenticação na inicialização
   */
  useEffect(() => {
    checkAuthStatus();
  }, [checkAuthStatus]);

  /**
   * Limpar erro após um tempo
   */
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  return {
    isAuthenticated,
    user,
    isLoading,
    error,
    login,
    logout,
    checkAuthStatus,
    navigateIfAuthenticated,
    clearError: () => setError(null)
  };
};

export default useOptimizedAuth;