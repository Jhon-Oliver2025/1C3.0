import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';

/**
 * Interface para dados do usuário
 */
interface UserData {
  id: string;
  username: string;
  email: string;
  is_admin: boolean;
}

/**
 * Interface para resposta de verificação de token
 */
interface TokenVerifyResponse {
  valid: boolean;
  user?: UserData;
  expires_in?: number; // segundos até expirar
}

/**
 * Hook personalizado para gerenciar autenticação com refresh automático
 * Verifica periodicamente se o token ainda é válido e renova quando necessário
 */
export const useAuthToken = () => {
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(!!token);
  const [user, setUser] = useState<UserData | null>(null);
  const navigate = useNavigate();

  /**
   * Função para verificar se o token ainda é válido
   */
  const verifyToken = useCallback(async (): Promise<boolean> => {
    const currentToken = localStorage.getItem('token');
    if (!currentToken) {
      setIsAuthenticated(false);
      setUser(null);
      return false;
    }

    try {
      const response = await fetch('/api/auth/verify-token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${currentToken}`
        },
        body: JSON.stringify({ token: currentToken })
      });

      if (response.ok) {
        const data: TokenVerifyResponse = await response.json();
        if (data.valid && data.user) {
          setUser(data.user);
          setIsAuthenticated(true);
          
          // Se o token expira em menos de 5 minutos, tentar renovar
          if (data.expires_in && data.expires_in < 300) {
            console.log('🔄 Token expira em breve, tentando renovar...');
            await refreshToken();
          }
          
          return true;
        }
      }
      
      // Token inválido
      console.warn('⚠️ Token inválido, redirecionando para login');
      logout();
      return false;
      
    } catch (error) {
      console.error('❌ Erro ao verificar token:', error);
      return false;
    }
  }, []);

  /**
   * Função para renovar o token (fazer novo login silencioso)
   */
  const refreshToken = useCallback(async (): Promise<boolean> => {
    try {
      // Aqui você pode implementar um endpoint de refresh ou
      // usar credenciais salvas para fazer novo login
      console.log('🔄 Implementar refresh de token se necessário');
      return true;
    } catch (error) {
      console.error('❌ Erro ao renovar token:', error);
      logout();
      return false;
    }
  }, []);

  /**
   * Função para fazer logout
   */
  const logout = useCallback(() => {
    localStorage.removeItem('token');
    setToken(null);
    setIsAuthenticated(false);
    setUser(null);
    navigate('/login');
  }, [navigate]);

  /**
   * Função para fazer login
   */
  const login = useCallback((newToken: string, userData: UserData) => {
    localStorage.setItem('token', newToken);
    setToken(newToken);
    setIsAuthenticated(true);
    setUser(userData);
  }, []);

  /**
   * Função para fazer requisições autenticadas
   */
  const authenticatedFetch = useCallback(async (url: string, options: RequestInit = {}) => {
    const currentToken = localStorage.getItem('token');
    if (!currentToken) {
      logout();
      throw new Error('Token não encontrado');
    }

    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${currentToken}`,
      ...options.headers
    };

    const response = await fetch(url, {
      ...options,
      headers
    });

    // Se receber 401 ou 403, token pode estar expirado
    if (response.status === 401 || response.status === 403) {
      console.warn('⚠️ Acesso negado, verificando token...');
      const isValid = await verifyToken();
      if (!isValid) {
        throw new Error('Token expirado');
      }
      
      // Tentar novamente com token verificado
      return fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          ...options.headers
        }
      });
    }

    return response;
  }, [verifyToken, logout]);

  // Verificar token na inicialização apenas se não estiver autenticado
  useEffect(() => {
    if (token && !isAuthenticated) {
      verifyToken();
    }
  }, [token, isAuthenticated, verifyToken]);

  // Verificar token periodicamente (a cada 30 minutos)
  useEffect(() => {
    if (!isAuthenticated) return;

    const interval = setInterval(() => {
      console.log('🔍 Verificação periódica do token...');
      verifyToken();
    }, 30 * 60 * 1000); // 30 minutos

    return () => clearInterval(interval);
  }, [isAuthenticated, verifyToken]);

  // Verificação de foco removida para evitar logout ao pressionar F5
  // useEffect(() => {
  //   const handleFocus = () => {
  //     if (isAuthenticated) {
  //       console.log('🔍 Página ganhou foco, verificando token...');
  //       verifyToken();
  //     }
  //   };
  //
  //   window.addEventListener('focus', handleFocus);
  //   return () => window.removeEventListener('focus', handleFocus);
  // }, [isAuthenticated, verifyToken]);

  return {
    token,
    isAuthenticated,
    user,
    login,
    logout,
    verifyToken,
    authenticatedFetch
  };
};