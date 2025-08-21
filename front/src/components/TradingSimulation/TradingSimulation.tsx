/**
 * Componente de Simulação de Trading
 * Exibe dados de simulação financeira com investimento de $1.000 USD
 */

import React, { useState, useEffect } from 'react';
import styles from './TradingSimulation.module.css';

interface SimulationData {
  id: string;
  symbol: string;
  signal_type: string;
  status: string;
  entry_price: number;
  current_price: number;
  days_monitored: number;
  simulation: {
    investment: number;
    current_value: number;
    pnl_usd: number;
    pnl_percentage: number;
    max_value_reached: number;
    target_value: number;
    position_size: number;
  };
  leverage: {
    max_leverage: number;
    current_profit: number;
    max_profit_reached: number;
  };
}

interface SimulationStats {
  total_signals: number;
  active_signals: number;
  completed_signals: number;
  success_rate: number;
  total_investment: number;
  total_current_value: number;
  total_pnl_usd: number;
  total_pnl_percentage: number;
}

interface ApiResponse {
  success: boolean;
  data: {
    signals: SimulationData[];
    statistics: SimulationStats;
    last_updated: string;
  };
}

const TradingSimulation: React.FC = () => {
  const [simulationData, setSimulationData] = useState<SimulationData[]>([]);
  const [statistics, setStatistics] = useState<SimulationStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string>('');

  /**
   * Busca dados de simulação da API
   */
  const fetchSimulationData = async () => {
    try {
      setLoading(true);
      const apiUrl = import.meta.env.VITE_API_URL || '';
      const response = await fetch(`${apiUrl}/api/signal-monitoring/signals/simulation`);
      
      if (!response.ok) {
        throw new Error(`Erro na API: ${response.status}`);
      }
      
      const data: ApiResponse = await response.json();
      
      if (data.success) {
        setSimulationData(data.data.signals);
        setStatistics(data.data.statistics);
        setLastUpdated(data.data.last_updated);
        setError(null);
      } else {
        throw new Error('Erro ao carregar dados de simulação');
      }
    } catch (err) {
      console.error('Erro ao buscar dados de simulação:', err);
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Formata valores em dólar
   */
  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };

  /**
   * Formata percentual
   */
  const formatPercentage = (value: number): string => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  /**
   * Retorna cor baseada no P&L
   */
  const getPnlColor = (pnl: number): string => {
    if (pnl > 0) return '#10b981'; // Verde
    if (pnl < 0) return '#ef4444'; // Vermelho
    return '#6b7280'; // Cinza
  };

  /**
   * Retorna ícone baseado no status
   */
  const getStatusIcon = (status: string): string => {
    switch (status) {
      case 'MONITORING': return '🔄';
      case 'COMPLETED': return '🎯';
      case 'EXPIRED': return '⏰';
      default: return '📊';
    }
  };

  /**
   * Retorna texto do status
   */
  const getStatusText = (status: string): string => {
    switch (status) {
      case 'MONITORING': return 'Monitorando';
      case 'COMPLETED': return 'Concluído';
      case 'EXPIRED': return 'Expirado';
      default: return 'Desconhecido';
    }
  };

  // Carregar dados na inicialização
  useEffect(() => {
    fetchSimulationData();
    
    // Atualizar a cada 30 segundos
    const interval = setInterval(fetchSimulationData, 30000);
    
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>
          <div className={styles.spinner}></div>
          <p>Carregando simulação de trading...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>
          <h3>❌ Erro ao carregar dados</h3>
          <p>{error}</p>
          <button onClick={fetchSimulationData} className={styles.retryButton}>
            Tentar novamente
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2 className={styles.title}>💰 Investimentos Simulados</h2>
        <p className={styles.subtitle}>
          Simulação com investimento de $1.000 USD por sinal
        </p>
        <p className={styles.lastUpdated}>
          Última atualização: {lastUpdated}
        </p>
      </div>

      {/* Estatísticas Gerais */}
      {statistics && (
        <div className={styles.statsGrid}>
          <div className={styles.statCard}>
            <div className={styles.statIcon}>📊</div>
            <div className={styles.statContent}>
              <h3>Total de Sinais</h3>
              <p className={styles.statValue}>{statistics.total_signals}</p>
            </div>
          </div>
          
          <div className={styles.statCard}>
            <div className={styles.statIcon}>🔄</div>
            <div className={styles.statContent}>
              <h3>Sinais Ativos</h3>
              <p className={styles.statValue}>{statistics.active_signals}</p>
            </div>
          </div>
          
          <div className={styles.statCard}>
            <div className={styles.statIcon}>🎯</div>
            <div className={styles.statContent}>
              <h3>Taxa de Sucesso</h3>
              <p className={styles.statValue}>{statistics.success_rate}%</p>
            </div>
          </div>
          
          <div className={styles.statCard}>
            <div className={styles.statIcon}>💰</div>
            <div className={styles.statContent}>
              <h3>Investimento Total</h3>
              <p className={styles.statValue}>{formatCurrency(statistics.total_investment)}</p>
            </div>
          </div>
          
          <div className={styles.statCard}>
            <div className={styles.statIcon}>📈</div>
            <div className={styles.statContent}>
              <h3>Valor Atual</h3>
              <p className={styles.statValue}>{formatCurrency(statistics.total_current_value)}</p>
            </div>
          </div>
          
          <div className={styles.statCard}>
            <div className={styles.statIcon}>💵</div>
            <div className={styles.statContent}>
              <h3>P&L Total</h3>
              <p 
                className={styles.statValue}
                style={{ color: getPnlColor(statistics.total_pnl_usd) }}
              >
                {formatCurrency(statistics.total_pnl_usd)}
              </p>
              <p 
                className={styles.statSubvalue}
                style={{ color: getPnlColor(statistics.total_pnl_usd) }}
              >
                {formatPercentage(statistics.total_pnl_percentage)}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Lista de Sinais */}
      <div className={styles.signalsSection}>
        <h3 className={styles.sectionTitle}>📋 Sinais de Trading</h3>
        
        {simulationData.length === 0 ? (
          <div className={styles.emptyState}>
            <p>🔍 Nenhum sinal sendo monitorado no momento</p>
            <p>Os sinais aparecerão aqui quando forem confirmados pelo sistema</p>
          </div>
        ) : (
          <div className={styles.signalsList}>
            {simulationData.map((signal) => (
              <div key={signal.id} className={styles.signalCard}>
                <div className={styles.signalHeader}>
                  <div className={styles.signalSymbol}>
                    <span className={styles.symbolText}>{signal.symbol}</span>
                    <span className={`${styles.signalType} ${styles[signal.signal_type.toLowerCase()]}`}>
                      {signal.signal_type}
                    </span>
                  </div>
                  <div className={styles.signalStatus}>
                    <span className={styles.statusIcon}>{getStatusIcon(signal.status)}</span>
                    <span className={styles.statusText}>{getStatusText(signal.status)}</span>
                  </div>
                </div>
                
                <div className={styles.signalMetrics}>
                  <div className={styles.metric}>
                    <span className={styles.metricLabel}>Preço Entrada:</span>
                    <span className={styles.metricValue}>${signal.entry_price.toFixed(4)}</span>
                  </div>
                  <div className={styles.metric}>
                    <span className={styles.metricLabel}>Preço Atual:</span>
                    <span className={styles.metricValue}>${signal.current_price.toFixed(4)}</span>
                  </div>
                  <div className={styles.metric}>
                    <span className={styles.metricLabel}>Dias:</span>
                    <span className={styles.metricValue}>{signal.days_monitored}</span>
                  </div>
                </div>
                
                <div className={styles.simulationData}>
                  <h4 className={styles.simulationTitle}>💰 Simulação ($1.000)</h4>
                  <div className={styles.simulationMetrics}>
                    <div className={styles.metric}>
                      <span className={styles.metricLabel}>Valor Atual:</span>
                      <span className={styles.metricValue}>
                        {formatCurrency(signal.simulation.current_value)}
                      </span>
                    </div>
                    <div className={styles.metric}>
                      <span className={styles.metricLabel}>P&L:</span>
                      <span 
                        className={styles.metricValue}
                        style={{ color: getPnlColor(signal.simulation.pnl_usd) }}
                      >
                        {formatCurrency(signal.simulation.pnl_usd)}
                      </span>
                    </div>
                    <div className={styles.metric}>
                      <span className={styles.metricLabel}>P&L %:</span>
                      <span 
                        className={styles.metricValue}
                        style={{ color: getPnlColor(signal.simulation.pnl_usd) }}
                      >
                        {formatPercentage(signal.simulation.pnl_percentage)}
                      </span>
                    </div>
                    <div className={styles.metric}>
                      <span className={styles.metricLabel}>Meta:</span>
                      <span className={styles.metricValue}>
                        {formatCurrency(signal.simulation.target_value)}
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className={styles.leverageData}>
                  <h4 className={styles.leverageTitle}>⚡ Alavancagem ({signal.leverage.max_leverage}x)</h4>
                  <div className={styles.leverageMetrics}>
                    <div className={styles.metric}>
                      <span className={styles.metricLabel}>Lucro Atual:</span>
                      <span 
                        className={styles.metricValue}
                        style={{ color: getPnlColor(signal.leverage.current_profit) }}
                      >
                        {formatPercentage(signal.leverage.current_profit)}
                      </span>
                    </div>
                    <div className={styles.metric}>
                      <span className={styles.metricLabel}>Máximo:</span>
                      <span 
                        className={styles.metricValue}
                        style={{ color: getPnlColor(signal.leverage.max_profit_reached) }}
                      >
                        {formatPercentage(signal.leverage.max_profit_reached)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      
      <div className={styles.footer}>
        <button onClick={fetchSimulationData} className={styles.refreshButton}>
          🔄 Atualizar Dados
        </button>
      </div>
    </div>
  );
};

export default TradingSimulation;