/**
 * Provider de contexto PWA para gerenciar funcionalidades em toda a aplicação
 */

import React, { createContext, useContext, ReactNode } from 'react';
import { usePWA } from '../../hooks/usePWA';

interface PWAContextType {
  isInstallable: boolean;
  isInstalled: boolean;
  isUpdateAvailable: boolean;
  isOnline: boolean;
  installApp: () => Promise<void>;
  updateApp: () => void;
  requestNotificationPermission: () => Promise<NotificationPermission>;
  showNotification: (title: string, options?: NotificationOptions) => void;
}

const PWAContext = createContext<PWAContextType | undefined>(undefined);

interface PWAProviderProps {
  children: ReactNode;
}

/**
 * Provider que disponibiliza funcionalidades PWA para toda a aplicação
 */
export const PWAProvider: React.FC<PWAProviderProps> = ({ children }) => {
  const pwaState = usePWA();

  return (
    <PWAContext.Provider value={pwaState}>
      {children}
    </PWAContext.Provider>
  );
};

/**
 * Hook para usar o contexto PWA
 */
export const usePWAContext = (): PWAContextType => {
  const context = useContext(PWAContext);
  
  if (context === undefined) {
    throw new Error('usePWAContext deve ser usado dentro de um PWAProvider');
  }
  
  return context;
};

export default PWAProvider;