
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
