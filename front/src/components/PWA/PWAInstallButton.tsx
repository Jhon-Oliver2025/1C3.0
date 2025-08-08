/**
 * Componente de botão para instalação do PWA
 */

import React, { useState } from 'react';
import { usePWAContext } from './PWAProvider';
import styles from './PWAInstallButton.module.css';
import logo2 from '../../assets/logo2.png';

interface PWAInstallButtonProps {
  variant?: 'primary' | 'secondary' | 'minimal';
  size?: 'small' | 'medium' | 'large';
  showIcon?: boolean;
  className?: string;
}

/**
 * Botão para instalação do PWA com diferentes variantes visuais
 */
const PWAInstallButton: React.FC<PWAInstallButtonProps> = ({
  variant = 'primary',
  size = 'medium',
  showIcon = true,
  className = ''
}) => {
  const { isInstallable, isInstalled, installApp } = usePWAContext();
  const [isInstalling, setIsInstalling] = useState(false);

  /**
   * Manipula o clique no botão de instalação
   */
  const handleInstall = async () => {
    if (!isInstallable || isInstalling) return;

    try {
      setIsInstalling(true);
      await installApp();
      console.log('✅ App instalado com sucesso!');
    } catch (error) {
      console.error('❌ Erro ao instalar app:', error);
      alert('Erro ao instalar o aplicativo. Tente novamente.');
    } finally {
      setIsInstalling(false);
    }
  };

  // Não mostrar se já está instalado ou não é instalável
  if (isInstalled || !isInstallable) {
    return null;
  }

  const buttonClasses = [
    styles.installButton,
    styles[variant],
    styles[size],
    className,
    isInstalling ? styles.installing : ''
  ].filter(Boolean).join(' ');

  return (
    <button
      className={buttonClasses}
      onClick={handleInstall}
      disabled={isInstalling}
      aria-label="Instalar aplicativo"
    >
      {showIcon && (
        <span className={styles.icon}>
          {isInstalling ? (
            <span className={styles.loadingIcon}>⏳</span>
          ) : (
            <img 
              src={logo2} 
              alt="1Crypten Logo" 
              className={styles.logoIcon}
            />
          )}
        </span>
      )}
      <span className={styles.text}>
        {isInstalling ? 'Instalando...' : 'Instalar App'}
      </span>
    </button>
  );
};

export default PWAInstallButton;