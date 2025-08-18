/**
 * Página dedicada para o App 1Crypten
 * Apresenta informações sobre o aplicativo e funcionalidade de instalação
 */

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import styles from './App1CryptenPage.module.css';
import logo3 from '/logo3.png';
import '../Dashboard/DashboardMobile.css';

interface AppInstallState {
  isInstallable: boolean;
  isInstalled: boolean;
  isInstalling: boolean;
}

/**
 * Hook personalizado para gerenciar instalação do app
 */
const useAppInstall = () => {
  const [state, setState] = useState<AppInstallState>({
    isInstallable: false,
    isInstalled: false,
    isInstalling: false
  });
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);

  /**
   * Verifica se o app já está instalado
   */
  const checkIfInstalled = () => {
    const isStandalone = window.matchMedia('(display-mode: standalone)').matches;
    const isInWebAppiOS = (window.navigator as any).standalone === true;
    const isInWebAppChrome = window.matchMedia('(display-mode: minimal-ui)').matches;
    
    return isStandalone || isInWebAppiOS || isInWebAppChrome;
  };

  /**
   * Instala o aplicativo
   */
  const installApp = async (): Promise<void> => {
    setState(prev => ({ ...prev, isInstalling: true }));

    try {
      if (deferredPrompt) {
        // Instalação automática via prompt nativo
        deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;
        
        if (outcome === 'accepted') {
          console.log('✅ App instalado com sucesso!');
          setState(prev => ({ ...prev, isInstalled: true, isInstallable: false }));
          setDeferredPrompt(null);
        }
      } else {
        // Mostrar instruções manuais
        showInstallInstructions();
      }
    } catch (error) {
      console.error('❌ Erro ao instalar app:', error);
    } finally {
      setState(prev => ({ ...prev, isInstalling: false }));
    }
  };

  /**
   * Mostra instruções de instalação manual
   */
  const showInstallInstructions = () => {
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
    
    // Criar modal personalizado
    const modal = document.createElement('div');
    modal.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.9);
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
        border-radius: 16px;
        padding: 32px;
        max-width: 450px;
        width: 100%;
        color: #E6F1FF;
        text-align: center;
        box-shadow: 0 12px 40px rgba(100, 255, 218, 0.4);
      ">
        <div style="
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 16px;
          margin-bottom: 24px;
        ">
          <img src="${logo3}" alt="1Crypten" style="width: 48px; height: 48px; border-radius: 8px;" />
          <h2 style="margin: 0; color: #64FFDA; font-size: 24px; font-weight: 700;">Instalar 1Crypten</h2>
        </div>
        <p style="
          margin: 0 0 24px 0;
          line-height: 1.6;
          white-space: pre-line;
          font-size: 16px;
          color: #B8D4E3;
        ">${instructions}</p>
        <button onclick="this.parentElement.parentElement.remove()" style="
          background: linear-gradient(135deg, #64FFDA, #4CAF50);
          color: #0A192F;
          border: none;
          padding: 12px 24px;
          border-radius: 8px;
          font-weight: 700;
          cursor: pointer;
          font-size: 16px;
          transition: all 0.3s ease;
        " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">Entendi</button>
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

  useEffect(() => {
    // Verificar se já está instalado
    setState(prev => ({ ...prev, isInstalled: checkIfInstalled() }));

    // Listener para prompt de instalação
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setState(prev => ({ ...prev, isInstallable: true }));
      console.log('💡 App pode ser instalado');
    };

    // Listener para quando o app é instalado
    const handleAppInstalled = () => {
      console.log('🎉 App foi instalado!');
      setState(prev => ({ ...prev, isInstalled: true, isInstallable: false }));
      setDeferredPrompt(null);
    };

    // Verificar se pode ser instalado (fallback)
    const checkInstallability = () => {
      if (!checkIfInstalled()) {
        const isChrome = /Chrome/.test(navigator.userAgent) && /Google Inc/.test(navigator.vendor);
        const isSafari = /Safari/.test(navigator.userAgent) && /Apple Computer/.test(navigator.vendor);
        const isEdge = /Edg/.test(navigator.userAgent);
        const isFirefox = /Firefox/.test(navigator.userAgent);
        
        if (isChrome || isSafari || isEdge || isFirefox) {
          setTimeout(() => {
            if (!deferredPrompt && !checkIfInstalled()) {
              setState(prev => ({ ...prev, isInstallable: true }));
              console.log('💡 App instalável detectado (fallback)');
            }
          }, 2000);
        }
      }
    };

    // Registrar listeners
    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);
    
    // Executar verificação
    setTimeout(checkInstallability, 1000);

    // Cleanup
    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
    };
  }, [deferredPrompt]);

  return {
    ...state,
    installApp
  };
};

/**
 * Página principal do App 1Crypten
 */
const App1CryptenPage: React.FC = () => {
  const { isInstallable, isInstalled, isInstalling, installApp } = useAppInstall();

  return (
    <div className={styles.container}>
      {/* CONTAINER MOTIVACIONAL NO TOPO DA DIV PRINCIPAL (4px) */}
      <div className="mobile-motivation-header-container">
        {/* Seção Motivacional */}
        <div className="mobile-motivational">
          <p className="mobile-motivational-text">
            Tenha o poder dos sinais na palma da sua mão, onde quer que esteja.
          </p>
        </div>

        {/* Espaçamento de Segurança (4px) */}
        <div className="mobile-safety-gap"></div>
      </div>

      {/* CONTEÚDO DA PÁGINA APP1CRYPTEN */}
      {/* Hero Section */}
      <section className={styles.hero}>
        <div className={styles.heroContent}>
          <img src={logo3} alt="1Crypten" className={styles.appIcon} />
          <h2 className={styles.heroTitle}>1Crypten</h2>
          <p className={styles.heroSubtitle}>Sinais de Trading em Tempo Real</p>
          <div className={styles.versionInfo}>
            <span className={styles.version}>v1.3.0</span>
            <span className={styles.versionLabel}>Versão Atual</span>
          </div>
          
          {/* Status do App */}
          {isInstalled ? (
            <div className={styles.installedBadge}>
              ✅ App Instalado
            </div>
          ) : (
            <button 
              className={styles.installButton}
              onClick={installApp}
              disabled={isInstalling}
            >
              {isInstalling ? (
                <>
                  <span className={styles.loadingIcon}>⏳</span>
                  Instalando...
                </>
              ) : (
                <>
                  <span className={styles.downloadIcon}>📱</span>
                  Baixar App
                </>
              )}
            </button>
          )}
        </div>
      </section>

      {/* Features Section */}
      <section className={styles.features}>
        <h3 className={styles.sectionTitle}>Por que usar o App 1Crypten?</h3>
        
        <div className={styles.featureGrid}>
          <div className={styles.featureCard}>
            <div className={styles.featureIcon}>⚡</div>
            <h4 className={styles.featureTitle}>Ultra Rápido</h4>
            <p className={styles.featureDescription}>
              Acesso instantâneo aos sinais de trading sem demora
            </p>
          </div>

          <div className={styles.featureCard}>
            <div className={styles.featureIcon}>📱</div>
            <h4 className={styles.featureTitle}>Experiência Nativa</h4>
            <p className={styles.featureDescription}>
              Interface otimizada para celular com navegação fluida
            </p>
          </div>

          <div className={styles.featureCard}>
            <div className={styles.featureIcon}>🔄</div>
            <h4 className={styles.featureTitle}>Sempre Atualizado</h4>
            <p className={styles.featureDescription}>
              Atualizações automáticas sem precisar baixar da loja
            </p>
          </div>

          <div className={styles.featureCard}>
            <div className={styles.featureIcon}>💾</div>
            <h4 className={styles.featureTitle}>Super Leve</h4>
            <p className={styles.featureDescription}>
              Ocupa menos de 5MB no seu celular
            </p>
          </div>

          <div className={styles.featureCard}>
            <div className={styles.featureIcon}>🌐</div>
            <h4 className={styles.featureTitle}>Funciona Offline</h4>
            <p className={styles.featureDescription}>
              Acesse dados em cache mesmo sem internet
            </p>
          </div>

          <div className={styles.featureCard}>
            <div className={styles.featureIcon}>🔔</div>
            <h4 className={styles.featureTitle}>Notificações</h4>
            <p className={styles.featureDescription}>
              Receba alertas de novos sinais em tempo real
            </p>
          </div>
        </div>
      </section>

      {/* Installation Guide */}
      <section className={styles.guide}>
        <h3 className={styles.sectionTitle}>Como Instalar</h3>
        
        <div className={styles.guideSteps}>
          <div className={styles.step}>
            <div className={styles.stepNumber}>1</div>
            <div className={styles.stepContent}>
              <h4 className={styles.stepTitle}>Clique em "Baixar App"</h4>
              <p className={styles.stepDescription}>
                Toque no botão azul acima para iniciar a instalação
              </p>
            </div>
          </div>

          <div className={styles.step}>
            <div className={styles.stepNumber}>2</div>
            <div className={styles.stepContent}>
              <h4 className={styles.stepTitle}>Confirme a Instalação</h4>
              <p className={styles.stepDescription}>
                Seu navegador mostrará uma popup para confirmar
              </p>
            </div>
          </div>

          <div className={styles.step}>
            <div className={styles.stepNumber}>3</div>
            <div className={styles.stepContent}>
              <h4 className={styles.stepTitle}>Pronto!</h4>
              <p className={styles.stepDescription}>
                O ícone do 1Crypten aparecerá na sua tela inicial
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className={styles.faq}>
        <h3 className={styles.sectionTitle}>Perguntas Frequentes</h3>
        
        <div className={styles.faqList}>
          <div className={styles.faqItem}>
            <h4 className={styles.faqQuestion}>O app é gratuito?</h4>
            <p className={styles.faqAnswer}>
              Sim! O app 1Crypten é completamente gratuito para instalar e usar.
            </p>
          </div>

          <div className={styles.faqItem}>
            <h4 className={styles.faqQuestion}>Funciona em todos os celulares?</h4>
            <p className={styles.faqAnswer}>
              Sim, funciona em Android e iPhone com qualquer navegador moderno.
            </p>
          </div>

          <div className={styles.faqItem}>
            <h4 className={styles.faqQuestion}>Preciso de internet para usar?</h4>
            <p className={styles.faqAnswer}>
              Para sinais em tempo real sim, mas dados em cache funcionam offline.
            </p>
          </div>

          <div className={styles.faqItem}>
            <h4 className={styles.faqQuestion}>Como desinstalar?</h4>
            <p className={styles.faqAnswer}>
              Mantenha pressionado o ícone na tela inicial e selecione "Remover".
            </p>
          </div>
        </div>
      </section>

      {/* CTA Final */}
      <section className={styles.cta}>
        <div className={styles.ctaContent}>
          <h3 className={styles.ctaTitle}>Pronto para começar?</h3>
          <p className={styles.ctaDescription}>
            Instale o app 1Crypten agora e tenha acesso aos melhores sinais de trading na palma da sua mão!
          </p>
          
          {!isInstalled && (
            <button 
              className={styles.ctaButton}
              onClick={installApp}
              disabled={isInstalling}
            >
              {isInstalling ? (
                <>
                  <span className={styles.loadingIcon}>⏳</span>
                  Instalando...
                </>
              ) : (
                <>
                  <span className={styles.downloadIcon}>📱</span>
                  Baixar App Agora
                </>
              )}
            </button>
          )}
        </div>
      </section>
    </div>
  );
};

export default App1CryptenPage;