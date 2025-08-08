/**
 * Hook personalizado para funcionalidades PWA
 * Gerencia instalação, atualizações e notificações
 */

import { useState, useEffect } from 'react';

interface PWAState {
  isInstallable: boolean;
  isInstalled: boolean;
  isUpdateAvailable: boolean;
  isOnline: boolean;
}

interface PWAActions {
  installApp: () => Promise<void>;
  updateApp: () => void;
  requestNotificationPermission: () => Promise<NotificationPermission>;
  showNotification: (title: string, options?: NotificationOptions) => void;
}

export const usePWA = (): PWAState & PWAActions => {
  const [isInstallable, setIsInstallable] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);
  const [isUpdateAvailable, setIsUpdateAvailable] = useState(false);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);
  const [registration, setRegistration] = useState<ServiceWorkerRegistration | null>(null);

  /**
   * Detecta se o app está instalado como PWA
   */
  const checkIfInstalled = () => {
    const isStandalone = window.matchMedia('(display-mode: standalone)').matches;
    const isInWebAppiOS = (window.navigator as any).standalone === true;
    const isInWebAppChrome = window.matchMedia('(display-mode: minimal-ui)').matches;
    
    return isStandalone || isInWebAppiOS || isInWebAppChrome;
  };

  /**
   * Instala o aplicativo PWA
   */
  const installApp = async (): Promise<void> => {
    if (!deferredPrompt) {
      throw new Error('App não pode ser instalado no momento');
    }

    try {
      // Mostrar prompt de instalação
      deferredPrompt.prompt();
      
      // Aguardar escolha do usuário
      const { outcome } = await deferredPrompt.userChoice;
      
      console.log('PWA install outcome:', outcome);
      
      if (outcome === 'accepted') {
        console.log('✅ PWA instalado com sucesso!');
        setIsInstalled(true);
        setIsInstallable(false);
      }
      
      // Limpar o prompt
      setDeferredPrompt(null);
    } catch (error) {
      console.error('❌ Erro ao instalar PWA:', error);
      throw error;
    }
  };

  /**
   * Atualiza o aplicativo para nova versão
   */
  const updateApp = (): void => {
    if (registration && registration.waiting) {
      // Enviar mensagem para o service worker ativar a nova versão
      registration.waiting.postMessage({ type: 'SKIP_WAITING' });
      
      // Recarregar a página após ativação
      window.location.reload();
    }
  };

  /**
   * Solicita permissão para notificações
   */
  const requestNotificationPermission = async (): Promise<NotificationPermission> => {
    if (!('Notification' in window)) {
      console.warn('Este navegador não suporta notificações');
      return 'denied';
    }

    if (Notification.permission === 'granted') {
      return 'granted';
    }

    if (Notification.permission === 'denied') {
      return 'denied';
    }

    // Solicitar permissão
    const permission = await Notification.requestPermission();
    console.log('Permissão de notificação:', permission);
    
    return permission;
  };

  /**
   * Mostra uma notificação
   */
  const showNotification = (title: string, options?: NotificationOptions): void => {
    if (Notification.permission !== 'granted') {
      console.warn('Permissão de notificação não concedida');
      return;
    }

    const defaultOptions: NotificationOptions = {
      icon: '/icons/icon-192x192.svg',
      badge: '/icons/icon-72x72.svg',
      data: {
        url: '/dashboard'
      },
      ...options
    };

    // Adicionar vibração se suportado (não está no tipo NotificationOptions)
    const notificationOptions = {
      ...defaultOptions,
      ...(navigator.vibrate && { vibrate: [200, 100, 200] })
    } as NotificationOptions;

    // Usar Service Worker se disponível, senão usar API direta
    if (registration) {
      registration.showNotification(title, notificationOptions);
    } else {
      new Notification(title, notificationOptions);
    }
  };

  /**
   * Configura listeners de eventos PWA
   */
  useEffect(() => {
    // Verificar se já está instalado
    setIsInstalled(checkIfInstalled());

    // Listener para prompt de instalação
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setIsInstallable(true);
      
      console.log('💡 PWA pode ser instalado');
    };

    // Listener para quando o app é instalado
    const handleAppInstalled = () => {
      console.log('🎉 PWA foi instalado!');
      setIsInstalled(true);
      setIsInstallable(false);
      setDeferredPrompt(null);
    };

    // Listener para mudanças de conectividade
    const handleOnline = () => {
      console.log('🌐 Conectado à internet');
      setIsOnline(true);
    };

    const handleOffline = () => {
      console.log('📴 Desconectado da internet');
      setIsOnline(false);
    };

    // Registrar listeners
    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Verificar Service Worker
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.ready.then((reg) => {
        setRegistration(reg);
        
        // Verificar atualizações
        reg.addEventListener('updatefound', () => {
          const newWorker = reg.installing;
          if (newWorker) {
            newWorker.addEventListener('statechange', () => {
              if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                console.log('🔄 Nova versão disponível!');
                setIsUpdateAvailable(true);
              }
            });
          }
        });
      });

      // Listener para mensagens do Service Worker
      navigator.serviceWorker.addEventListener('message', (event) => {
        if (event.data && event.data.type === 'SW_UPDATED') {
          setIsUpdateAvailable(true);
        }
      });
    }

    // Cleanup
    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  /**
   * Monitora mudanças no display mode
   */
  useEffect(() => {
    const mediaQuery = window.matchMedia('(display-mode: standalone)');
    
    const handleDisplayModeChange = (e: MediaQueryListEvent) => {
      setIsInstalled(e.matches);
    };

    mediaQuery.addEventListener('change', handleDisplayModeChange);
    
    return () => {
      mediaQuery.removeEventListener('change', handleDisplayModeChange);
    };
  }, []);

  return {
    // Estado
    isInstallable,
    isInstalled,
    isUpdateAvailable,
    isOnline,
    
    // Ações
    installApp,
    updateApp,
    requestNotificationPermission,
    showNotification
  };
};

export default usePWA;