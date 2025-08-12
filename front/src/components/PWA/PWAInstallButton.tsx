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

  // Não mostrar se já está instalado
  if (isInstalled) {
    return null;
  }

  // Se não é instalável, tentar instalação manual ou mostrar instruções
  if (!isInstallable) {
    const handleManualInstall = () => {
      // Detectar navegador e mostrar instruções específicas
      const isChrome = /Chrome/.test(navigator.userAgent) && /Google Inc/.test(navigator.vendor);
      const isSafari = /Safari/.test(navigator.userAgent) && /Apple Computer/.test(navigator.vendor);
      const isEdge = /Edg/.test(navigator.userAgent);
      const isFirefox = /Firefox/.test(navigator.userAgent);
      
      let instructions = '';
      
      if (isChrome) {
        instructions = 'Para instalar o 1Crypten:\n\n1. Toque nos 3 pontos (⋮) no canto superior direito\n2. Selecione "Instalar app" ou "Adicionar à tela inicial"\n3. Confirme a instalação';
      } else if (isSafari) {
        instructions = 'Para instalar o 1Crypten:\n\n1. Toque no ícone de compartilhar (□↗)\n2. Role para baixo e toque em "Adicionar à Tela Inicial"\n3. Toque em "Adicionar"';
      } else if (isEdge) {
        instructions = 'Para instalar o 1Crypten:\n\n1. Toque nos 3 pontos (...) no menu\n2. Selecione "Apps"\n3. Toque em "Instalar este site como app"';
      } else if (isFirefox) {
        instructions = 'Para instalar o 1Crypten:\n\n1. Toque nos 3 pontos no menu\n2. Selecione "Instalar"\n3. Confirme a instalação';
      } else {
        instructions = 'Para instalar o 1Crypten como app:\n\n1. Procure a opção "Instalar app" no menu do navegador\n2. Ou "Adicionar à tela inicial"\n3. Confirme a instalação';
      }
      
      // Mostrar modal personalizado em vez de alert
      const modal = document.createElement('div');
      modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        padding: 20px;
      `;
      
      modal.innerHTML = `
        <div style="
          background: #0A192F;
          border: 2px solid #64FFDA;
          border-radius: 12px;
          padding: 24px;
          max-width: 400px;
          width: 100%;
          color: #E6F1FF;
          text-align: center;
          box-shadow: 0 8px 32px rgba(100, 255, 218, 0.3);
        ">
          <div style="
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            margin-bottom: 16px;
          ">
            <img src="${logo2}" alt="1Crypten" style="width: 32px; height: 32px; border-radius: 6px;" />
            <h3 style="margin: 0; color: #64FFDA; font-size: 18px;">Instalar 1Crypten</h3>
          </div>
          <p style="
            margin: 0 0 20px 0;
            line-height: 1.5;
            white-space: pre-line;
            font-size: 14px;
          ">${instructions}</p>
          <button onclick="this.parentElement.parentElement.remove()" style="
            background: linear-gradient(135deg, #64FFDA, #4CAF50);
            color: #0A192F;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            font-size: 14px;
          ">Entendi</button>
        </div>
      `;
      
      document.body.appendChild(modal);
      
      // Remover modal ao clicar fora
      modal.addEventListener('click', (e) => {
        if (e.target === modal) {
          modal.remove();
        }
      });
    };
    
    return (
      <button
        className={`${styles.installButton} ${styles[variant]} ${styles[size]} ${className}`}
        onClick={handleManualInstall}
        disabled={false}
      >
        {showIcon && (
          <img 
            src={logo2} 
            alt="1Crypten" 
            className={`${styles.logoIcon} ${styles[size]}`}
          />
        )}
        <span>Instalar App</span>
      </button>
    );
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