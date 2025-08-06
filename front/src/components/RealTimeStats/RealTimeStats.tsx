import React, { useState, useEffect } from 'react';
import styles from './RealTimeStats.module.css';

/**
 * Interface para dados de estatísticas em tempo real
 */
interface StatsData {
  totalSignals: number;
  buySignals: number;
  sellSignals: number;
  successRate: number;
  activeUsers: number;
  marketStatus: 'BULL' | 'BEAR' | 'NEUTRAL';
  lastUpdate: string;
}

/**
 * Componente de estatísticas em tempo real
 * Exibe métricas importantes do sistema de forma visual e animada
 */
const RealTimeStats: React.FC = () => {
  const [stats, setStats] = useState<StatsData>({
    totalSignals: 0,
    buySignals: 0,
    sellSignals: 0,
    successRate: 0,
    activeUsers: 0,
    marketStatus: 'NEUTRAL',
    lastUpdate: new Date().toISOString()
  });
  const [isLoading, setIsLoading] = useState(true);
  const [animationKey, setAnimationKey] = useState(0);

  /**
   * Simula dados de estatísticas (em produção, viria da API)
   */
  const generateMockStats = (): StatsData => {
    const baseStats = {
      totalSignals: Math.floor(Math.random() * 50) + 150,
      buySignals: Math.floor(Math.random() * 30) + 80,
      sellSignals: Math.floor(Math.random() * 20) + 70,
      successRate: Math.floor(Math.random() * 20) + 75,
      activeUsers: Math.floor(Math.random() * 100) + 500,
      marketStatus: ['BULL', 'BEAR', 'NEUTRAL'][Math.floor(Math.random() * 3)] as 'BULL' | 'BEAR' | 'NEUTRAL',
      lastUpdate: new Date().toISOString()
    };
    return baseStats;
  };

  /**
   * Carrega as estatísticas
   */
  useEffect(() => {
    const loadStats = () => {
      setIsLoading(true);
      // Simula delay de carregamento
      setTimeout(() => {
        setStats(generateMockStats());
        setIsLoading(false);
        setAnimationKey(prev => prev + 1);
      }, 500);
    };

    loadStats();
    
    // Atualiza a cada 30 segundos
    const interval = setInterval(loadStats, 30000);
    
    return () => clearInterval(interval);
  }, []);

  /**
   * Formata números grandes
   */
  const formatNumber = (num: number): string => {
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  /**
   * Retorna a cor baseada no status do mercado
   */
  const getMarketStatusColor = (status: string): string => {
    switch (status) {
      case 'BULL': return '#4CAF50';
      case 'BEAR': return '#E53E3E';
      default: return '#FFD700';
    }
  };

  if (isLoading) {
    return (
      <div className={styles.statsContainer}>
        <div className={styles.loadingSpinner}>
          <div className={styles.spinner}></div>
          <span>Carregando estatísticas...</span>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.statsContainer} key={animationKey}>
      <div className={styles.statsHeader}>
        <h3 className={styles.title}>📊 Estatísticas em Tempo Real</h3>
        <div className={styles.lastUpdate}>
          Atualizado: {new Date(stats.lastUpdate).toLocaleTimeString('pt-BR')}
        </div>
      </div>

      <div className={styles.statsGrid}>
        {/* Total de Sinais */}
        <div className={`${styles.statCard} ${styles.totalSignals}`}>
          <div className={styles.statIcon}>🎯</div>
          <div className={styles.statContent}>
            <div className={styles.statValue}>{stats.totalSignals}</div>
            <div className={styles.statLabel}>Total de Sinais</div>
          </div>
          <div className={styles.statTrend}>+12%</div>
        </div>

        {/* Sinais de Compra */}
        <div className={`${styles.statCard} ${styles.buySignals}`}>
          <div className={styles.statIcon}>📈</div>
          <div className={styles.statContent}>
            <div className={styles.statValue}>{stats.buySignals}</div>
            <div className={styles.statLabel}>Sinais de Compra</div>
          </div>
          <div className={styles.statTrend}>+8%</div>
        </div>

        {/* Sinais de Venda */}
        <div className={`${styles.statCard} ${styles.sellSignals}`}>
          <div className={styles.statIcon}>📉</div>
          <div className={styles.statContent}>
            <div className={styles.statValue}>{stats.sellSignals}</div>
            <div className={styles.statLabel}>Sinais de Venda</div>
          </div>
          <div className={styles.statTrend}>+5%</div>
        </div>

        {/* Taxa de Sucesso */}
        <div className={`${styles.statCard} ${styles.successRate}`}>
          <div className={styles.statIcon}>🏆</div>
          <div className={styles.statContent}>
            <div className={styles.statValue}>{stats.successRate}%</div>
            <div className={styles.statLabel}>Taxa de Sucesso</div>
          </div>
          <div className={styles.progressBar}>
            <div 
              className={styles.progressFill} 
              style={{ width: `${stats.successRate}%` }}
            ></div>
          </div>
        </div>

        {/* Usuários Ativos */}
        <div className={`${styles.statCard} ${styles.activeUsers}`}>
          <div className={styles.statIcon}>👥</div>
          <div className={styles.statContent}>
            <div className={styles.statValue}>{formatNumber(stats.activeUsers)}</div>
            <div className={styles.statLabel}>Usuários Ativos</div>
          </div>
          <div className={styles.statTrend}>+15%</div>
        </div>

        {/* Status do Mercado */}
        <div className={`${styles.statCard} ${styles.marketStatus}`}>
          <div className={styles.statIcon}>🌊</div>
          <div className={styles.statContent}>
            <div 
              className={styles.statValue} 
              style={{ color: getMarketStatusColor(stats.marketStatus) }}
            >
              {stats.marketStatus}
            </div>
            <div className={styles.statLabel}>Sentimento do Mercado</div>
          </div>
          <div 
            className={styles.marketIndicator}
            style={{ backgroundColor: getMarketStatusColor(stats.marketStatus) }}
          ></div>
        </div>
      </div>
    </div>
  );
};

export default RealTimeStats;