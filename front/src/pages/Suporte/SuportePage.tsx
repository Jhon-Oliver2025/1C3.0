import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import styles from './SuportePage.module.css';
import logo3 from '/logo3.png';
import '../Dashboard/DashboardMobile.css';

/**
 * Componente da página de Suporte
 * Exibe informações de contato e canais de suporte
 */
const SuportePage: React.FC = () => {
  const navigate = useNavigate();
  const [isBackendOnline, setIsBackendOnline] = useState<boolean>(false);

  /**
   * Verifica o status do backend
   */
  useEffect(() => {
    const checkBackendStatus = async () => {
      try {
        const response = await fetch('/api/status');
        setIsBackendOnline(response.ok);
      } catch (error) {
        setIsBackendOnline(false);
      }
    };

    checkBackendStatus();
    const interval = setInterval(checkBackendStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  // Funções de navegação removidas - agora gerenciadas pelo MainLayout

  return (
    <div className={styles.suporteContainer}>
      {/* CONTAINER MOTIVACIONAL NO TOPO DA DIV PRINCIPAL (4px) */}
      <div className="mobile-motivation-header-container">
        {/* Seção Motivacional */}
        <div className="mobile-motivational">
          <p className="mobile-motivational-text">
            Estamos aqui para apoiar sua jornada rumo ao sucesso financeiro.
          </p>
        </div>

        {/* Espaçamento de Segurança (4px) */}
        <div className="mobile-safety-gap"></div>
      </div>

      {/* CONTEÚDO DA PÁGINA SUPORTE */}
      <div className={styles.mainContent}>
        <div className={styles.suporteHeader}>
          <h1 className={styles.title}>Central de Suporte</h1>
          <p className={styles.subtitle}>Estamos aqui para ajudar você</p>
        </div>

        <div className={styles.suporteCards}>
          {/* Card Telegram */}
          <div className={styles.suporteCard}>
            <div className={styles.cardIcon}>💬</div>
            <h3 className={styles.cardTitle}>Telegram</h3>
            <p className={styles.cardDescription}>
              Suporte rápido e direto através do nosso canal oficial
            </p>
            <a 
              href="https://t.me/cryptosignals_suporte" 
              target="_blank" 
              rel="noopener noreferrer"
              className={styles.cardButton}
            >
              Abrir Telegram
            </a>
          </div>

          {/* Card Email */}
          <div className={styles.suporteCard}>
            <div className={styles.cardIcon}>📧</div>
            <h3 className={styles.cardTitle}>Email</h3>
            <p className={styles.cardDescription}>
              Envie suas dúvidas detalhadas para nossa equipe
            </p>
            <a 
              href="mailto:suporte@cryptosignals.com" 
              className={styles.cardButton}
            >
              Enviar Email
            </a>
          </div>

          {/* Card WhatsApp */}
          <div className={styles.suporteCard}>
            <div className={styles.cardIcon}>📱</div>
            <h3 className={styles.cardTitle}>WhatsApp</h3>
            <p className={styles.cardDescription}>
              Atendimento personalizado via WhatsApp
            </p>
            <a 
              href="https://wa.me/5511999999999" 
              target="_blank" 
              rel="noopener noreferrer"
              className={styles.cardButton}
            >
              Abrir WhatsApp
            </a>
          </div>

          {/* Card FAQ */}
          <div className={styles.suporteCard}>
            <div className={styles.cardIcon}>❓</div>
            <h3 className={styles.cardTitle}>FAQ</h3>
            <p className={styles.cardDescription}>
              Perguntas frequentes e respostas rápidas
            </p>
            <button className={styles.cardButton}>
              Ver FAQ
            </button>
          </div>
        </div>

        {/* Informações Adicionais */}
        <div className={styles.infoSection}>
          <h2 className={styles.infoTitle}>Horário de Atendimento</h2>
          <div className={styles.infoGrid}>
            <div className={styles.infoItem}>
              <strong>Segunda a Sexta:</strong> 08:00 - 18:00
            </div>
            <div className={styles.infoItem}>
              <strong>Sábado:</strong> 09:00 - 14:00
            </div>
            <div className={styles.infoItem}>
              <strong>Domingo:</strong> Fechado
            </div>
            <div className={styles.infoItem}>
              <strong>Telegram:</strong> 24/7 (resposta automática)
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SuportePage;