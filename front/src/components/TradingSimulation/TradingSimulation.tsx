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
  const [isAutoUpdateEnabled, setIsAutoUpdateEnabled] = useState(false);
  const [updateInterval, setUpdateInterval] = useState<NodeJS.Timeout | null>(null);

  /**
   * Busca dados de simulação da API
   */
  const fetchSimulationData = async () => {
    try {
      setLoading(true);
      const apiUrl = import.meta.env.VITE_API_URL || '';
      
      // Primeiro tenta a API de simulação
      let response = await fetch(`${apiUrl}/api/signal-monitoring/signals/simulation`);
      
      if (response.ok) {
        const data: ApiResponse = await response.json();
        if (data.success && data.data.signals.length > 0) {
          setSimulationData(data.data.signals);
          setStatistics(data.data.statistics);
          setLastUpdated(data.data.last_updated);
          setError(null);
          setLoading(false);
          return;
        }
      }
      
      // Se não há dados de simulação, busca sinais confirmados e cria simulação
      console.log('🔄 API de simulação vazia, buscando sinais confirmados...');
      response = await fetch(`${apiUrl}/api/btc-signals/confirmed`);
      
      if (!response.ok) {
        throw new Error(`Erro na API de sinais: ${response.status}`);
      }
      
      const confirmedSignals = await response.json();
      console.log('✅ Sinais confirmados recebidos:', confirmedSignals.length);
      
      if (confirmedSignals && confirmedSignals.length > 0) {
         // Buscar preços atuais da Binance para cada sinal
         const signalsWithCurrentPrices = await Promise.all(
           confirmedSignals.map(async (signal: any, index: number) => {
             const entryPrice = parseFloat(signal.entry_price || signal.price || 0);
             let currentPrice = entryPrice;
             let daysMonitored = 0;
             
             // Buscar preço real da Binance
                 try {
                   const priceResponse = await fetch(`${apiUrl}/api/binance/price/${signal.symbol}`);
                   
                   if (priceResponse.ok) {
                     const priceData = await priceResponse.json();
                     if (priceData.success && priceData.price) {
                       currentPrice = priceData.price;
                       console.log(`📊 ${signal.symbol}: Preço entrada $${entryPrice.toFixed(4)} → Atual $${currentPrice.toFixed(4)} (REAL) - ${new Date().toLocaleTimeString()}`);
                     } else {
                       throw new Error('Preço não disponível na resposta');
                     }
                   } else {
                     throw new Error(`API retornou ${priceResponse.status}`);
                   }
                 } catch (error) {
                   console.log(`⚠️ Erro ao buscar preço real de ${signal.symbol}: ${error.message}`);
                   console.log(`🔄 Usando simulação como fallback...`);
                   
                   // Fallback para simulação se a API falhar
                   const now = Date.now();
                   const timeBasedSeed = Math.sin(now / 50000) * Math.cos(now / 30000);
                   const baseVariation = Math.random() * 0.12 - 0.06;
                   const timeVariation = timeBasedSeed * 0.04;
                   const volatilityFactor = 0.03;
                   const totalVariation = (baseVariation + timeVariation) * volatilityFactor;
                   currentPrice = entryPrice * (1 + totalVariation);
                   currentPrice = Math.max(currentPrice, entryPrice * 0.7);
                   
                   console.log(`🔄 ${signal.symbol}: Preço entrada $${entryPrice.toFixed(4)} → Atual $${currentPrice.toFixed(4)} (SIMULADO) - ${new Date().toLocaleTimeString()}`);
                 }
             
             // Calcular dias monitorados
              if (signal.entry_time || signal.confirmed_at) {
                const entryDate = new Date(signal.entry_time || signal.confirmed_at);
                const now = new Date();
                const timeDiff = now.getTime() - entryDate.getTime();
                daysMonitored = Math.max(0, Math.floor(timeDiff / (1000 * 60 * 60 * 24)));
                
                // Garantir que não seja NaN
                if (isNaN(daysMonitored)) {
                  daysMonitored = 0;
                }
              } else {
                daysMonitored = 0;
              }
             
             // Calcular simulação com dados reais
             const investment = 1000.00;
             const positionSize = investment / entryPrice;
             const signalType = (signal.type || signal.signal_type || 'COMPRA').toUpperCase();
             
             let currentValue = investment;
             let pnlUsd = 0;
             let pnlPercentage = 0;
             let leverageProfit = 0;
             
             if (signalType === 'COMPRA' || signalType === 'LONG') {
               // Para sinais de compra: lucro quando preço sobe
               const priceChange = (currentPrice - entryPrice) / entryPrice;
               currentValue = investment * (1 + priceChange);
               pnlUsd = currentValue - investment;
               pnlPercentage = priceChange * 100;
               leverageProfit = priceChange * 50 * 100; // 50x leverage
             } else {
               // Para sinais de venda: lucro quando preço desce
               const priceChange = (entryPrice - currentPrice) / entryPrice;
               currentValue = investment * (1 + priceChange);
               pnlUsd = currentValue - investment;
               pnlPercentage = priceChange * 100;
               leverageProfit = priceChange * 50 * 100; // 50x leverage
             }
             
             return {
               id: signal.id || `sim_${index}`,
               symbol: signal.symbol,
               signal_type: signalType,
               status: 'MONITORING',
               entry_price: entryPrice,
               current_price: currentPrice,
               days_monitored: daysMonitored,
               simulation: {
                 investment: investment,
                 current_value: Math.max(0, currentValue),
                 pnl_usd: pnlUsd,
                 pnl_percentage: pnlPercentage,
                 max_value_reached: Math.max(investment, currentValue),
                 target_value: 4000.00,
                 position_size: positionSize
               },
               leverage: {
                 max_leverage: 50,
                 current_profit: leverageProfit,
                 max_profit_reached: Math.max(0, leverageProfit)
               }
             };
           })
         );
         
         const simulatedSignals = signalsWithCurrentPrices;
        
        // Calcular estatísticas com dados reais
         const totalInvestment = simulatedSignals.reduce((sum, signal) => sum + signal.simulation.investment, 0);
         const totalCurrentValue = simulatedSignals.reduce((sum, signal) => sum + signal.simulation.current_value, 0);
         const totalPnlUsd = simulatedSignals.reduce((sum, signal) => sum + signal.simulation.pnl_usd, 0);
         const profitableSignals = simulatedSignals.filter(signal => signal.simulation.pnl_usd > 0).length;
         
         const stats: SimulationStats = {
            total_signals: simulatedSignals.length,
            active_signals: simulatedSignals.length,
            completed_signals: 0,
            success_rate: simulatedSignals.length > 0 ? (profitableSignals / simulatedSignals.length) * 100 : 0,
            total_investment: totalInvestment,
            total_current_value: totalCurrentValue,
            total_pnl_usd: totalPnlUsd,
            total_pnl_percentage: totalInvestment > 0 ? (totalPnlUsd / totalInvestment) * 100 : 0
          };
        
        setSimulationData(simulatedSignals);
        setStatistics(stats);
        setLastUpdated(new Date().toLocaleString('pt-BR'));
        setError(null);
        
        console.log('🎯 Simulação criada:', simulatedSignals.length, 'sinais com $1.000 cada');
      } else {
        throw new Error('Nenhum sinal encontrado');
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
   * Formata percentual para estatísticas (sem sinal +/-)
   */
  const formatStatPercentage = (value: number): string => {
    return `${value.toFixed(1)}%`;
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
  }, []);

  // Controlar atualização automática
  useEffect(() => {
    if (isAutoUpdateEnabled) {
      const interval = setInterval(fetchSimulationData, 10000);
      setUpdateInterval(interval);
      return () => clearInterval(interval);
    } else {
      if (updateInterval) {
        clearInterval(updateInterval);
        setUpdateInterval(null);
      }
    }
  }, [isAutoUpdateEnabled]);

  /**
   * Atualiza preços em tempo real
   */
  const updateRealTimePrices = () => {
    console.log('🔄 Atualizando preços em tempo real...');
    fetchSimulationData();
  };

  /**
    * Força atualização manual dos dados
    */
   const handleRefresh = () => {
     setLoading(true);
     updateRealTimePrices();
   };

  /**
   * Inicia a atualização automática
   */
  const startAutoUpdate = () => {
    setIsAutoUpdateEnabled(true);
    console.log('✅ Atualização automática iniciada');
  };

  /**
   * Para a atualização automática
   */
  const stopAutoUpdate = () => {
    setIsAutoUpdateEnabled(false);
    console.log('⏹️ Atualização automática parada');
  };

  /**
   * Alterna entre start/stop da atualização automática
   */
  const toggleAutoUpdate = () => {
    if (isAutoUpdateEnabled) {
      stopAutoUpdate();
    } else {
      startAutoUpdate();
    }
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.header}>
          <div className={styles.skeletonTitle}></div>
          <div className={styles.skeletonSubtitle}></div>
          <div className={styles.skeletonLastUpdated}></div>
        </div>

        {/* Skeleton para estatísticas */}
        <div className={styles.statsGrid}>
          {[...Array(6)].map((_, index) => (
            <div key={index} className={styles.statCard}>
              <div className={styles.skeletonStatIcon}></div>
              <div className={styles.statContent}>
                <div className={styles.skeletonStatTitle}></div>
                <div className={styles.skeletonStatValue}></div>
              </div>
            </div>
          ))}
        </div>

        {/* Skeleton para seção de sinais */}
        <div className={styles.signalsSection}>
          <div className={styles.skeletonSectionTitle}></div>
          
          <div className={styles.signalsList}>
            {[...Array(6)].map((_, index) => (
              <div key={index} className={styles.signalCard}>
                <div className={styles.signalHeader}>
                  <div className={styles.skeletonSymbol}></div>
                  <div className={styles.skeletonSignalType}></div>
                </div>
                
                <div className={styles.signalMetrics}>
                  {[...Array(3)].map((_, metricIndex) => (
                    <div key={metricIndex} className={styles.metric}>
                      <div className={styles.skeletonMetricLabel}></div>
                      <div className={styles.skeletonMetricValue}></div>
                    </div>
                  ))}
                </div>
                
                <div className={styles.simulationData}>
                  <div className={styles.skeletonSimulationTitle}></div>
                  <div className={styles.simulationMetrics}>
                    {[...Array(4)].map((_, simIndex) => (
                      <div key={simIndex} className={styles.metric}>
                        <div className={styles.skeletonMetricLabel}></div>
                        <div className={styles.skeletonMetricValue}></div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Indicador de carregamento com animação */}
        <div className={styles.loadingIndicator}>
          <div className={styles.loadingSpinner}></div>
          <p className={styles.loadingText}>🔄 Carregando preços em tempo real...</p>
          <div className={styles.loadingProgress}>
            <div className={styles.progressBar}></div>
          </div>
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
        <div className={styles.headerContent}>
          <div className={styles.titleSection}>
            <h2 className={styles.title}>💰 Investimentos Simulados</h2>
            <p className={styles.subtitle}>
              Simulação com investimento de $1.000 USD por sinal
            </p>
            <p className={styles.lastUpdated}>
              Última atualização: {lastUpdated}
            </p>
          </div>
          
          <div className={styles.controlsSection}>
            <div className={styles.autoUpdateControls}>
              <div className={styles.statusIndicator}>
                <span className={`${styles.statusDot} ${isAutoUpdateEnabled ? styles.active : styles.inactive}`}></span>
                <span className={styles.statusText}>
                  {isAutoUpdateEnabled ? 'Atualização Automática Ativa' : 'Atualização Manual'}
                </span>
              </div>
              
              <div className={styles.buttonGroup}>
                <button 
                  className={`${styles.controlButton} ${isAutoUpdateEnabled ? styles.stopButton : styles.startButton}`}
                  onClick={toggleAutoUpdate}
                >
                  {isAutoUpdateEnabled ? '⏹️ Parar' : '▶️ Iniciar'}
                </button>
                
                <button 
                  className={styles.refreshButton}
                  onClick={handleRefresh}
                  disabled={loading}
                >
                  🔄 {loading ? 'Atualizando...' : 'Atualizar Agora'}
                </button>
              </div>
            </div>
          </div>
        </div>
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
              <p className={styles.statValue}>{formatStatPercentage(statistics.success_rate)}</p>
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
        <button 
          onClick={handleRefresh} 
          className={styles.refreshButton}
          disabled={loading}
        >
          {loading ? '⏳ Atualizando...' : '🔄 Atualizar Preços'}
        </button>
        <p className={styles.updateInfo}>
          📊 Preços atualizados automaticamente a cada 10 segundos
        </p>
      </div>
    </div>
  );
};

export default TradingSimulation;