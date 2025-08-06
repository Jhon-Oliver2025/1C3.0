import React, { useState, useEffect } from 'react';
import styles from './DashboardPage.module.css';
import '../../styles/mobile-essential.css';
import SignalCard from '../../components/SignalCard/SignalCard';
import RealTimeStats from '../../components/RealTimeStats/RealTimeStats';

/**
 * Interface para definir a estrutura de um sinal
 */
interface Signal {
  symbol: string;
  type: 'COMPRA' | 'VENDA';
  entry_price: number;
  entry_time: string;
  target_price: number;
  projection_percentage: number;
  signal_class: 'PREMIUM' | 'ELITE' | 'PADRÃO';
  status: string;
}

/**
 * Componente principal da página Dashboard
 * Exibe seção motivacional, cabeçalho com horários e lista de sinais
 */
const DashboardPage: React.FC = () => {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [currentPhraseIndex, setCurrentPhraseIndex] = useState(0);

  // Array de frases motivacionais
  const motivationalPhrases = [
    "Cada halving é um lembrete: a escassez digital é real.",
    "O futuro pertence àqueles que acreditam na beleza de seus sonhos.",
    "Bitcoin não é apenas uma moeda, é uma revolução financeira.",
    "A paciência é a chave para o sucesso no mundo cripto.",
    "Hodl forte, o tempo está do seu lado.",
    "A volatilidade é o preço da inovação.",
    "Seja ganancioso quando outros têm medo.",
    "O conhecimento é o melhor investimento que você pode fazer."
  ];

  /**
   * Atualiza o horário atual a cada segundo
   */
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  /**
   * Alterna as frases motivacionais a cada 8 segundos
   */
  useEffect(() => {
    const phraseTimer = setInterval(() => {
      setCurrentPhraseIndex((prevIndex) => 
        (prevIndex + 1) % motivationalPhrases.length
      );
    }, 8000);

    return () => clearInterval(phraseTimer);
  }, [motivationalPhrases.length]);

  /**
   * Carrega os sinais da API na inicialização
   */
  useEffect(() => {
    fetchSignals();
  }, []);

  /**
   * Formata a data para exibição
   */
  const formatDate = (date: Date) => {
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  /**
   * Formata o horário para exibição
   */
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  /**
   * Calcula horários dos mercados internacionais
   */
  const getMarketTimes = () => {
    const now = new Date();
    
    // Mercado EUA (NYSE: 9:30-16:00 EST)
    const usaTime = new Date(now.toLocaleString("en-US", {timeZone: "America/New_York"}));
    const usaHour = usaTime.getHours();
    const usaStatus = (usaHour >= 9 && usaHour < 16) ? 'ABERTO' : 'FECHADO';
    
    // Mercado Ásia (Tokyo: 9:00-15:00 JST)
    const asiaTime = new Date(now.toLocaleString("en-US", {timeZone: "Asia/Tokyo"}));
    const asiaHour = asiaTime.getHours();
    const asiaStatus = (asiaHour >= 9 && asiaHour < 15) ? 'ABERTO' : 'FECHADO';
    
    return {
      usa: {
        time: usaTime.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        status: usaStatus
      },
      asia: {
        time: asiaTime.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        status: asiaStatus
      }
    };
  };

  const marketTimes = getMarketTimes();

  // Estado para verificar se o backend está online
  const [isBackendOnline, setIsBackendOnline] = useState(true);

  /**
   * Função para recarregar sinais
   */
  const fetchSignals = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/signals/', {
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Erro ao carregar sinais');
      }

      const data = await response.json();
      setSignals(data.signals || []);
      setIsBackendOnline(true);
    } catch (err) {
      console.error('❌ Erro ao carregar sinais:', err);
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
      setIsBackendOnline(false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mobile-container">
      {/* Header Mobile - 72px */}
      <header className="mobile-top-header">
        <button className="mobile-menu-button" aria-label="Menu">
          ☰
        </button>
        <div className="mobile-logo-status">
          <span>CRYPTO SIGNALS</span>
          <div 
            className={`mobile-status-indicator ${isBackendOnline ? 'online' : 'offline'}`}
            title={isBackendOnline ? 'Backend Online' : 'Backend Offline'}
          ></div>
        </div>
      </header>

      {/* Seção Motivacional - 90px fixo */}
      <section className="mobile-motivational">
        <p className="mobile-motivational-text">
          {motivationalPhrases[currentPhraseIndex]}
        </p>
      </section>

      {/* Container Principal - margin-top: 162px */}
      <main className="mobile-main-container">
        {/* Estatísticas em Tempo Real */}
        <RealTimeStats />

        {/* Cabeçalho dos Sinais - 2 Linhas conforme desenho técnico */}
        <div className="mobile-signals-header">
          {/* Linha 1: Horários dos Mercados */}
          <div className="mobile-market-times">
            <div className="mobile-market-item">
              <div className="mobile-market-flag">🇺🇸</div>
              <div className="mobile-market-name">EUA</div>
              <div className="mobile-market-time">{marketTimes.usa.time.slice(0, 5)}</div>
              <div className={`mobile-market-status ${marketTimes.usa.status === 'ABERTO' ? 'open' : 'closed'}`}>
                {marketTimes.usa.status}
              </div>
            </div>
            <div className="mobile-market-item">
              <div className="mobile-market-flag">🌏</div>
              <div className="mobile-market-name">ÁSIA</div>
              <div className="mobile-market-time">{marketTimes.asia.time.slice(0, 5)}</div>
              <div className={`mobile-market-status ${marketTimes.asia.status === 'ABERTO' ? 'open' : 'closed'}`}>
                {marketTimes.asia.status}
              </div>
            </div>
            <div className="mobile-market-item">
              <div className="mobile-market-flag">⏰</div>
              <div className="mobile-market-name">TIMER</div>
              <div className="mobile-market-time">{formatTime(currentTime)}</div>
              <div className="mobile-market-status timer">24/7</div>
            </div>
          </div>
          
          {/* Linha 2: Estatísticas */}
          <div className="mobile-stats-row">
            <div className="mobile-stat-item">
              <div className="mobile-stat-label">Total:</div>
              <div className="mobile-stat-value">{signals.length.toString().padStart(2, '0')}</div>
            </div>
            <div className="mobile-stat-item">
              <div className="mobile-stat-label">Compra:</div>
              <div className="mobile-stat-value">{signals.filter(s => s.type === 'COMPRA').length.toString().padStart(2, '0')}</div>
            </div>
            <div className="mobile-stat-item">
              <div className="mobile-stat-label">Venda:</div>
              <div className="mobile-stat-value">{signals.filter(s => s.type === 'VENDA').length.toString().padStart(2, '0')}</div>
            </div>
          </div>
        </div>

        {/* Lista de Sinais */}
        <div className="mobile-signals-list">
          {loading && (
            <div className="mobile-loading">
              <div className="mobile-loading-spinner"></div>
              <p className="mobile-loading-text">Carregando sinais...</p>
            </div>
          )}
          
          {error && (
            <div className="mobile-error">
              <div className="mobile-error-icon">⚠️</div>
              <p className="mobile-error-text">Erro ao carregar sinais</p>
              <button className="mobile-retry-button" onClick={fetchSignals}>
                Tentar Novamente
              </button>
            </div>
          )}
          
          {!loading && !error && signals.length === 0 && (
            <div className="mobile-empty">
              <div className="mobile-empty-icon">📊</div>
              <p className="mobile-empty-text">Nenhum sinal disponível no momento</p>
            </div>
          )}
          
          {!loading && !error && signals.length > 0 && (
            signals.map((signal) => (
              <SignalCard
                key={`${signal.symbol}-${signal.entry_time}`}
                symbol={signal.symbol}
                type={signal.type}
                entryPrice={String(signal.entry_price)}
                targetPrice={String(signal.target_price)}
                projectionPercentage={String(signal.projection_percentage)}
                date={signal.entry_time}
                signalClass={signal.signal_class}
              />
            ))
          )}
        </div>
      </main>
    </div>
  );
};

export default DashboardPage;