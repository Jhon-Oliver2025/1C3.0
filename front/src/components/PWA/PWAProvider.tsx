import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import usePWAManager from '../../hooks/usePWAManager';
import useAuthManager from '../../hooks/useAuthManager';

/**
 * Interface para o contexto PWA
 */
interface PWAContextType {
  // Estado da aplicação
  isOnline: boolean;
  isAppReady: boolean;
  needsUpdate: boolean;
  
  // Autenticação
  isAuthenticated: boolean;
  user: any;
  authLoading: boolean;
  authError: string | null;
  
  // Funções
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => Promise<void>;
  forceRefresh: () => void;
  clearAuthError: () => void;
  
  // Estatísticas
  reconnectAttempts: number;
  authRetryAttempts: number;
}

/**
 * Contexto PWA
 */
const PWAContext = createContext<PWAContextType | undefined>(undefined);

/**
 * Hook para usar o contexto PWA
 */
export const usePWA = (): PWAContextType => {
  const context = useContext(PWAContext);
  if (!context) {
    throw new Error('usePWA deve ser usado dentro de um PWAProvider');
  }
  return context;
};

/**
 * Props do PWAProvider
 */
interface PWAProviderProps {
  children: ReactNode;
}

/**
 * Provider PWA que gerencia todo o estado da aplicação
 * Integra gerenciamento de conectividade, autenticação e atualizações
 */
export const PWAProvider: React.FC<PWAProviderProps> = ({ children }) => {
  const [isAppReady, setIsAppReady] = useState(false);
  const [needsUpdate, setNeedsUpdate] = useState(false);
  const [user, setUser] = useState<any>(null);

  // Hooks personalizados
  const pwaManager = usePWAManager();
  const authManager = useAuthManager();

  /**
   * Inicializa a aplicação
   */
  useEffect(() => {
    const initializeApp = async () => {
      console.log('🚀 PWA: Inicializando aplicação...');
      
      try {
        // Verificar se está autenticado
        if (authManager.isAuthenticated()) {
          // Validar token
          const tokenValid = await authManager.validateToken();
          
          if (tokenValid) {
            // Carregar dados do usuário
            const userData = authManager.getUser();
            setUser(userData);
            console.log('✅ PWA: Usuário autenticado carregado');
          } else {
            console.log('🔐 PWA: Token inválido, usuário deslogado');
          }
        }
        
        setIsAppReady(true);
        console.log('✅ PWA: Aplicação inicializada');
      } catch (error) {
        console.error('❌ PWA: Erro ao inicializar aplicação:', error);
        setIsAppReady(true); // Continuar mesmo com erro
      }
    };

    initializeApp();
  }, [authManager]);

  /**
   * Gerencia eventos personalizados PWA
   */
  useEffect(() => {
    const handleRefreshData = () => {
      console.log('🔄 PWA: Evento de atualização de dados recebido');
      // Disparar atualização de dados nas páginas
      window.location.reload();
    };

    const handleConnectivityRestored = async () => {
      console.log('🌐 PWA: Conectividade restaurada');
      
      // Se estiver autenticado, validar token
      if (authManager.isAuthenticated()) {
        const tokenValid = await authManager.validateToken();
        if (!tokenValid) {
          console.log('🔐 PWA: Token expirado após reconexão');
          setUser(null);
        }
      }
    };

    // Adicionar listeners
    window.addEventListener('pwa-refresh-data', handleRefreshData);
    window.addEventListener('pwa-connectivity-restored', handleConnectivityRestored);

    // Cleanup
    return () => {
      window.removeEventListener('pwa-refresh-data', handleRefreshData);
      window.removeEventListener('pwa-connectivity-restored', handleConnectivityRestored);
    };
  }, [authManager]);

  /**
   * Gerencia atualizações do Service Worker
   */
  useEffect(() => {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.addEventListener('message', (event) => {
        if (event.data && event.data.type === 'UPDATE_AVAILABLE') {
          console.log('🔄 PWA: Atualização disponível');
          setNeedsUpdate(true);
        }
      });
    }
  }, []);

  /**
   * Função de login personalizada
   */
  const handleLogin = async (email: string, password: string): Promise<boolean> => {
    const success = await authManager.login(email, password);
    
    if (success) {
      // Carregar dados do usuário
      const userData = authManager.getUser();
      setUser(userData);
      console.log('✅ PWA: Login realizado e usuário carregado');
    }
    
    return success;
  };

  /**
   * Função de logout personalizada
   */
  const handleLogout = async (): Promise<void> => {
    await authManager.logout();
    setUser(null);
    console.log('🔐 PWA: Logout realizado e usuário removido');
  };

  /**
   * Força atualização da aplicação
   */
  const handleForceRefresh = () => {
    setNeedsUpdate(false);
    pwaManager.forceRefresh();
  };

  /**
   * Valor do contexto
   */
  const contextValue: PWAContextType = {
    // Estado da aplicação
    isOnline: pwaManager.isOnline,
    isAppReady,
    needsUpdate,
    
    // Autenticação
    isAuthenticated: authManager.isAuthenticated(),
    user,
    authLoading: authManager.isLoading,
    authError: authManager.error,
    
    // Funções
    login: handleLogin,
    logout: handleLogout,
    forceRefresh: handleForceRefresh,
    clearAuthError: authManager.clearError,
    
    // Estatísticas
    reconnectAttempts: pwaManager.reconnectAttempts,
    authRetryAttempts: authManager.retryAttempts
  };

  return (
    <PWAContext.Provider value={contextValue}>
      {children}
      
      {/* Notificação de atualização */}
      {needsUpdate && (
        <div 
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            backgroundColor: '#2196f3',
            color: 'white',
            padding: '12px',
            textAlign: 'center',
            zIndex: 9999,
            cursor: 'pointer'
          }}
          onClick={handleForceRefresh}
        >
          🔄 Nova versão disponível! Toque para atualizar.
        </div>
      )}
      
      {/* Indicador de status offline */}
      {!pwaManager.isOnline && (
        <div 
          style={{
            position: 'fixed',
            bottom: 0,
            left: 0,
            right: 0,
            backgroundColor: '#f44336',
            color: 'white',
            padding: '8px',
            textAlign: 'center',
            zIndex: 9999,
            fontSize: '14px'
          }}
        >
          📱 Modo offline - Algumas funcionalidades podem estar limitadas
        </div>
      )}
      
      {/* Loading inicial */}
      {!isAppReady && (
        <div 
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 10000,
            color: 'white',
            fontSize: '18px'
          }}
        >
          <div style={{ textAlign: 'center' }}>
            <div style={{ marginBottom: '16px' }}>🚀</div>
            <div>Carregando 1Crypten...</div>
          </div>
        </div>
      )}
    </PWAContext.Provider>
  );
};

export default PWAProvider;