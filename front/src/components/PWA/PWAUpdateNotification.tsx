/**
 * Componente de notificação para atualizações do PWA
 */

import React, { useState, useEffect } from 'react';
import { usePWAContext } from './PWAProvider';
import styles from './PWAUpdateNotification.module.css';

interface PWAUpdateNotificationProps {
  autoShow?: boolean;
  position?: 'top' | 'bottom';
  className?: string;
}

/**
 * Notificação que aparece quando há uma atualização disponível
 */
const PWAUpdateNotification: React.FC<PWAUpdateNotificationProps> = ({
  autoShow = true,
  position = 'top',
  className = ''
}) => {
  const { isUpdateAvailable, updateApp } = usePWAContext();
  const [isVisible, setIsVisible] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);

  /**
   * Mostra a notificação quando há atualização disponível
   */
  useEffect(() => {
    if (isUpdateAvailable && autoShow) {
      setIsVisible(true);
    }
  }, [isUpdateAvailable, autoShow]);

  /**
   * Manipula o clique no botão de atualização
   */
  const handleUpdate = async () => {
    try {
      setIsUpdating(true);
      updateApp();
      // A página será recarregada automaticamente
    } catch (error) {
      console.error('❌ Erro ao atualizar app:', error);
      setIsUpdating(false);
    }
  };

  /**
   * Fecha a notificação
   */
  const handleDismiss = () => {
    setIsVisible(false);
  };

  // Não mostrar se não há atualização ou não está visível
  if (!isUpdateAvailable || !isVisible) {
    return null;
  }

  const notificationClasses = [
    styles.updateNotification,
    styles[position],
    className,
    isUpdating ? styles.updating : ''
  ].filter(Boolean).join(' ');

  return (
    <div className={notificationClasses} role="alert" aria-live="polite">
      <div className={styles.content}>
        <div className={styles.icon}>
          {isUpdating ? '⏳' : '🔄'}
        </div>
        
        <div className={styles.message}>
          <div className={styles.title}>
            {isUpdating ? 'Atualizando...' : 'Nova versão disponível!'}
          </div>
          <div className={styles.description}>
            {isUpdating 
              ? 'Aplicando atualização, aguarde...' 
              : 'Clique em "Atualizar" para obter a versão mais recente.'
            }
          </div>
        </div>
        
        <div className={styles.actions}>
          {!isUpdating && (
            <>
              <button
                className={styles.updateButton}
                onClick={handleUpdate}
                disabled={isUpdating}
                aria-label="Atualizar aplicativo"
              >
                Atualizar
              </button>
              
              <button
                className={styles.dismissButton}
                onClick={handleDismiss}
                disabled={isUpdating}
                aria-label="Dispensar notificação"
              >
                ✕
              </button>
            </>
          )}
        </div>
      </div>
      
      {/* Barra de progresso durante atualização */}
      {isUpdating && (
        <div className={styles.progressBar}>
          <div className={styles.progressFill}></div>
        </div>
      )}
    </div>
  );
};

export default PWAUpdateNotification;