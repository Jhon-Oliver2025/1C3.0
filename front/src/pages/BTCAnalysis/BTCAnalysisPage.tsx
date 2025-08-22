import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { 
  FaBitcoin, 
  FaChartLine, 
  FaClock, 
  FaCheckCircle, 
  FaTimesCircle, 
  FaHourglassHalf,
  FaEye,
  FaThumbsUp,
  FaThumbsDown,
  FaCog,
  FaSync,
  FaDesktop,
  FaPlay,
  FaPause,
  FaRedo,
  FaCircle
} from 'react-icons/fa';
import '../Dashboard/DashboardMobile.css';
import SignalTraceability from '../../components/SignalTraceability/SignalTraceability';

// Interfaces
interface PendingSignal {
  id: string;
  symbol: string;
  type: 'COMPRA' | 'VENDA';
  entry_price: number;
  target_price: number;
  projection_percentage: number;
  quality_score: number;
  signal_class: string;
  created_at: string;
  expires_at: string;
  confirmation_attempts: number;
  btc_correlation: number;
  btc_trend: string;
  status: string;
}

interface RejectedSignal {
  id: string;
  symbol: string;
  type: 'COMPRA' | 'VENDA';
  entry_price: number;
  quality_score: number;
  signal_class: string;
  created_at: string;
  rejected_at: string;
  rejection_reasons: string[];
  confirmation_attempts: number;
  status: string;
}

interface ConfirmedSignal {
  id: string;
  symbol: string;
  type: 'COMPRA' | 'VENDA';
  entry_price: number;
  target_price?: number;
  projection_percentage?: number;
  quality_score?: number;
  signal_class?: string;
  created_at: string;
  confirmed_at?: string;
  confirmation_reasons?: string[] | string;
  confirmation_attempts?: number;
  btc_correlation?: number;
  btc_trend?: string;
  status: string;
  entry_time?: string;
}

interface MonitoredSignal {
  id: string;
  symbol: string;
  signal_type: 'COMPRA' | 'VENDA';
  entry_price: number;
  target_price: number;
  created_at: string;
  confirmed_at: string;
  max_leverage: number;
  required_percentage: number;
  current_price: number;
  current_percentage: number;
  current_profit: number;
  max_profit_reached: number;
  status: string;
  last_updated: string;
  days_monitored: number;
  // Informações de confirmação
  confirmation_reasons?: string[] | string;
  quality_score?: number;
  signal_class?: string;
  btc_correlation?: number;
  btc_trend?: string;
  confirmation_attempts?: number;
  technical_indicators?: {
    rsi?: number;
    macd_bullish?: boolean;
    ema_alignment?: boolean;
    volume_increase?: number;
    breakout_percentage?: number;
  };
}

interface ExpiredSignal {
  id: string;
  symbol: string;
  signal_type: 'COMPRA' | 'VENDA';
  entry_price: number;
  target_price: number;
  created_at: string;
  confirmed_at: string;
  max_leverage: number;
  required_percentage: number;
  max_profit_reached: number;
  status: 'COMPLETED' | 'EXPIRED';
  days_monitored: number;
}

interface MonitoringStats {
  total_monitored: number;
  total_expired: number;
  total_completed: number;
  successful_signals: number;
  failed_signals: number;
  total_evaluated_signals: number;
  success_rate: number;
  average_successful_profit: number;
  max_profit: number;
  is_monitoring: boolean;
  last_update: string;
}

interface BTCMetrics {
  total_signals_processed: number;
  confirmed_signals: number;
  rejected_signals: number;
  pending_signals: number;
  confirmation_rate: number;
  average_confirmation_time_minutes: number;
  system_status: string;
}

interface BTCAnalysis {
  trend: string;
  strength: number;
  price: number;
  change_24h: number;
  volume_24h: number;
  high_24h: number;
  low_24h: number;
  last_updated: string;
  volatility: number;
  timeframes: {
    '1h': BTCTimeframe;
    '4h': BTCTimeframe;
  };
}

interface RestartSystemInfo {
  restart_info: {
    next_restart: string;
    countdown: {
      hours: number;
      minutes: number;
      seconds: number;
      total_seconds: number;
    };
    schedule: string;
    timezone: string;
  };
  system_uptime: {
    hours: number;
    minutes: number;
    last_restart: string;
    current_time: string;
  };
  btc_system: {
    status: string;
    confirmed_signals: number;
    pending_signals: number;
    rejected_signals: number;
  };
  restart_features: string[];
  system_status: {
    cleanup_system: string;
    scheduler: string;
    btc_confirmation: string;
  };
}

interface BTCTimeframe {
  rsi: number;
  rsi_condition: string;
  macd_bullish: boolean;
  macd_bearish: boolean;
  ema20: number;
  ema50: number;
  ema_alignment: boolean;
  atr: number;
  atr_percentage: number;
  volatility_level: string;
  trend: string;
  strength: number;
  momentum_aligned: boolean;
  pivot_broken: boolean;
  timestamp: string;
}

// Styled Components
const BTCContainer = styled.div`
  background-color: #000000;
  min-height: 100vh;
  color: white;
  padding: 20px;
  
  @media (max-width: 768px) {
    padding: 10px;
  }
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 20px;
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  border-radius: 12px;
  border: 1px solid #f59e0b;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  
  @media (max-width: 768px) {
    flex-direction: column;
    gap: 15px;
    padding: 15px;
    margin-bottom: 20px;
  }
`;



const Title = styled.h1`
  color: #f59e0b;
  font-size: 2em;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 15px;
  
  @media (max-width: 768px) {
    font-size: 1.3em;
    text-align: center;
    gap: 8px;
  }
  
  @media (max-width: 480px) {
    font-size: 1.1em;
    gap: 5px;
  }
`;

const BTCIcon = styled(FaBitcoin)`
  color: #f59e0b;
  font-size: 1.2em;
`;

const RefreshControls = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  
  @media (max-width: 768px) {
    gap: 8px;
  }
`;

const RefreshButton = styled.button`
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
  border: 1px solid #f59e0b;
  position: relative;
  overflow: hidden;
  
  @media (max-width: 768px) {
    padding: 8px 12px;
    font-size: 0.9em;
    gap: 5px;
  }
  
  @media (max-width: 480px) {
    padding: 6px 10px;
    font-size: 0.8em;
  }

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
    transition: left 0.5s;
  }

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4);
    
    &::before {
      left: 100%;
    }
  }

  &:active {
    transform: translateY(0);
  }

  &:disabled {
    background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
    cursor: not-allowed;
    transform: none;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    border-color: #6b7280;
    
    &::before {
      display: none;
    }
  }
`;

const AutoRefreshContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 8px;
  transition: all 0.3s ease;
  
  @media (max-width: 768px) {
    padding: 6px 8px;
    gap: 6px;
  }
  
  &:hover {
    background: rgba(245, 158, 11, 0.15);
    border-color: rgba(245, 158, 11, 0.5);
  }
`;

const AutoRefreshButton = styled.button<{ $isActive: boolean }>`
  background: ${props => props.$isActive ? '#10b981' : '#6b7280'};
  color: white;
  border: none;
  padding: 6px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  width: 28px;
  height: 28px;
  
  &:hover {
    background: ${props => props.$isActive ? '#059669' : '#4b5563'};
    transform: scale(1.05);
  }
  
  &:active {
    transform: scale(0.95);
  }
`;

const RefreshIndicator = styled.div<{ $isRefreshing: boolean }>`
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85em;
  color: #94a3b8;
  
  .refresh-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: ${props => props.$isRefreshing ? '#10b981' : '#6b7280'};
    animation: ${props => props.$isRefreshing ? 'pulse 1.5s infinite' : 'none'};
  }
  
  @keyframes pulse {
    0%, 100% {
      opacity: 1;
      transform: scale(1);
    }
    50% {
      opacity: 0.5;
      transform: scale(1.2);
    }
  }
`;

const CountdownText = styled.span<{ $timeLeft: number }>`
  font-size: 0.8em;
  color: ${props => props.$timeLeft <= 10 ? '#f59e0b' : '#94a3b8'};
  font-weight: 500;
  min-width: 25px;
  text-align: center;
  transition: color 0.3s ease;
`;

const TabContainer = styled.div`
  display: flex;
  margin-bottom: 20px;
  border-bottom: 2px solid #1e293b;
  
  @media (max-width: 768px) {
    overflow-x: auto;
    scrollbar-width: none;
    -ms-overflow-style: none;
    padding: 0 10px;
    margin: 0 -10px 20px -10px;
    
    &::-webkit-scrollbar {
      display: none;
    }
  }
  
  @media (max-width: 480px) {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    overflow-x: visible;
    padding: 0;
    margin: 0 0 15px 0;
    border-bottom: none;
  }
`;

const Tab = styled.button<{ $active: boolean }>`
  background: ${props => props.$active ? '#f59e0b' : 'transparent'};
  color: ${props => props.$active ? 'black' : '#94a3b8'};
  border: none;
  padding: 15px 25px;
  cursor: pointer;
  font-size: 1em;
  font-weight: 600;
  border-radius: 8px 8px 0 0;
  transition: all 0.2s ease;
  white-space: nowrap;
  min-width: fit-content;
  
  @media (max-width: 768px) {
    padding: 12px 16px;
    font-size: 0.85em;
    min-width: 120px;
  }
  
  @media (max-width: 480px) {
    padding: 10px 8px;
    font-size: 0.7em;
    min-width: unset;
    width: 100%;
    border-radius: 8px;
    text-align: center;
    white-space: normal;
    line-height: 1.2;
    height: auto;
    min-height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: ${props => props.$active ? '#f59e0b' : '#2d3748'};
    border: 1px solid ${props => props.$active ? '#f59e0b' : '#374151'};
    
    &:last-child:nth-child(odd) {
      grid-column: 1 / -1;
    }
  }

  &:hover {
    background: ${props => props.$active ? '#f59e0b' : '#1e293b'};
    color: ${props => props.$active ? 'black' : 'white'};
    
    @media (max-width: 480px) {
      background: ${props => props.$active ? '#f59e0b' : '#374151'};
    }
  }
`;

const ContentContainer = styled.div`
  background: #1e293b;
  border-radius: 12px;
  padding: 25px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  min-height: 400px;
`;

const SignalCard = styled.div`
  background: #2d3748;
  margin: 15px;
  padding: 20px;
  border-radius: 12px;
  border: 1px solid #374151;
  transition: all 0.2s ease;
  
  @media (max-width: 768px) {
    margin: 10px;
    padding: 15px;
  }
  
  @media (max-width: 480px) {
    margin: 8px;
    padding: 12px;
  }

  &:hover {
    border-color: #f59e0b;
    transform: translateY(-2px);
  }
`;

const SignalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  
  @media (max-width: 480px) {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
`;

const SignalSymbol = styled.h3`
  color: #f59e0b;
  margin: 0;
  font-size: 1.5em;
  
  @media (max-width: 768px) {
    font-size: 1.3em;
  }
  
  @media (max-width: 480px) {
    font-size: 1.1em;
  }
`;

const SignalType = styled.span<{ $type: string }>`
  padding: 6px 12px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.9em;
  background: ${props => props.$type === 'COMPRA' ? '#10b981' : '#ef4444'};
  color: white;
`;

const SignalDetails = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 15px;
  
  @media (max-width: 768px) {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 10px;
  }
  
  @media (max-width: 480px) {
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }
`;

const SignalDetail = styled.div`
  display: flex;
  flex-direction: column;
  gap: 5px;
`;

const DetailLabel = styled.span`
  color: #94a3b8;
  font-size: 0.9em;
`;

const DetailValue = styled.span`
  color: white;
  font-weight: 600;
`;

const LoadingSpinner = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  font-size: 1.2em;
  color: #f59e0b;
`;

const EmptyState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: #94a3b8;
  font-size: 1.1em;
`;

const EmptyIcon = styled.div`
  font-size: 4em;
  margin-bottom: 20px;
  opacity: 0.5;
`;

const TechnicalGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
  
  @media (max-width: 768px) {
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 15px;
    margin-bottom: 20px;
  }
  
  @media (max-width: 480px) {
    grid-template-columns: 1fr;
    gap: 10px;
  }
`;

const TechnicalCard = styled.div`
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  padding: 20px;
  border-radius: 12px;
  border: 1px solid #f59e0b;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  transition: transform 0.2s ease;
  
  @media (max-width: 768px) {
    padding: 15px;
  }
  
  @media (max-width: 480px) {
    padding: 12px;
  }

  &:hover {
    transform: translateY(-2px);
  }
`;

const TechnicalTitle = styled.h3`
  color: #f59e0b;
  margin: 0 0 15px 0;
  font-size: 1.1em;
  display: flex;
  align-items: center;
  gap: 8px;
  
  @media (max-width: 768px) {
    font-size: 1em;
    margin-bottom: 10px;
  }
  
  @media (max-width: 480px) {
    font-size: 0.9em;
    gap: 5px;
  }
`;

const TechnicalValue = styled.div<{ $color?: string }>`
  font-size: 1.5em;
  font-weight: bold;
  color: ${props => props.$color || 'white'};
  margin-bottom: 8px;
  
  @media (max-width: 768px) {
    font-size: 1.2em;
  }
  
  @media (max-width: 480px) {
    font-size: 1em;
  }
`;

const TechnicalSubtext = styled.div`
  color: #94a3b8;
  font-size: 0.9em;
  margin-bottom: 10px;
  
  @media (max-width: 768px) {
    font-size: 0.8em;
  }
  
  @media (max-width: 480px) {
    font-size: 0.75em;
  }
`;

const StrategyTitle = styled.h2`
  color: #f59e0b;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
`;

// Componentes para Justificativas de Confirmação
const ConfirmationSection = styled.div`
  margin-top: 20px;
  padding: 15px;
  background: rgba(245, 158, 11, 0.1);
  border-radius: 8px;
  border: 1px solid #f59e0b;
`;

const ConfirmationTitle = styled.h4`
  color: #f59e0b;
  margin: 0 0 15px 0;
  font-size: 1.1em;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const ConfirmationGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 15px;
  
  @media (max-width: 768px) {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 10px;
  }
  
  @media (max-width: 480px) {
    grid-template-columns: 1fr;
    gap: 8px;
  }
`;

const ConfirmationItem = styled.div`
  display: flex;
  flex-direction: column;
  gap: 5px;
`;

const ConfirmationLabel = styled.span`
  color: #f59e0b;
  font-size: 0.9em;
  font-weight: 600;
`;

const ConfirmationValue = styled.span`
  color: white;
  font-weight: 500;
`;

const ReasonsList = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
`;

const ReasonTag = styled.span`
  background: #10b981;
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8em;
  font-weight: 500;
`;

const TechnicalIndicators = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 10px;
  margin-top: 15px;
  padding: 10px;
  background: rgba(16, 185, 129, 0.1);
  border-radius: 6px;
  border: 1px solid #10b981;
`;

const IndicatorItem = styled.div`
  text-align: center;
`;

const IndicatorLabel = styled.div`
  color: #10b981;
  font-size: 0.8em;
  margin-bottom: 4px;
`;

const IndicatorValue = styled.div<{ $positive?: boolean }>`
  color: ${props => props.$positive ? '#10b981' : '#ef4444'};
  font-weight: 600;
  font-size: 0.9em;
`;

// Main Component
const BTCAnalysisPage: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('pending');
  const [loading, setLoading] = useState(true);
  const [pendingSignals, setPendingSignals] = useState<PendingSignal[]>([]);
  const [confirmedSignals, setConfirmedSignals] = useState<ConfirmedSignal[]>([]);
  const [rejectedSignals, setRejectedSignals] = useState<RejectedSignal[]>([]);
  const [monitoredSignals, setMonitoredSignals] = useState<MonitoredSignal[]>([]);
  const [expiredSignals, setExpiredSignals] = useState<ExpiredSignal[]>([]);
  const [monitoringStats, setMonitoringStats] = useState<MonitoringStats | null>(null);
  const [btcMetrics, setBtcMetrics] = useState<BTCMetrics | null>(null);
  const [btcAnalysis, setBtcAnalysis] = useState<BTCAnalysis | null>(null);
  const [restartInfo, setRestartInfo] = useState<RestartSystemInfo | null>(null);
  
  // Estados para auto-refresh elegante
  const [isAutoRefreshEnabled, setIsAutoRefreshEnabled] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [refreshCountdown, setRefreshCountdown] = useState(30);
  const refreshIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const countdownIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Função para formatar preços
  const formatPrice = (price: number): string => {
    if (price >= 1) {
      return `$${price.toFixed(4)}`;
    } else {
      return `$${price.toFixed(8)}`;
    }
  };

  // Função para formatar data/hora
  const formatDateTime = (dateString: string): string => {
    if (!dateString || dateString === 'null' || dateString === 'undefined') {
      return 'N/A';
    }
    
    try {
      // Tentar diferentes formatos de data
      let date: Date;
      
      // Formato brasileiro: DD/MM/YYYY HH:MM:SS
      if (dateString.includes('/')) {
        const [datePart, timePart] = dateString.split(' ');
        const [day, month, year] = datePart.split('/');
        const [hour, minute, second] = (timePart || '00:00:00').split(':');
        date = new Date(parseInt(year), parseInt(month) - 1, parseInt(day), 
                       parseInt(hour), parseInt(minute), parseInt(second));
      } else {
        // Formato ISO ou outros
        date = new Date(dateString);
      }
      
      // Verificar se a data é válida
      if (isNaN(date.getTime())) {
        return dateString; // Retornar string original se não conseguir parsear
      }
      
      return date.toLocaleString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
    } catch {
      return dateString;
    }
  };



  // Função para traduzir motivos de rejeição
  const translateRejectionReasons = (reasons: string[]) => {
    const translations: { [key: string]: string } = {
      'reversal_detected': '🔄 Reversão Detectada',
      'volume_insufficient': '📉 Volume Insuficiente',
      'btc_opposite': '₿ BTC em Direção Oposta',
      'timeout_expired': '⏰ Tempo Esgotado',
      'support_resistance_hold': '📊 Suporte/Resistência Mantido'
    };
    return reasons.map(reason => translations[reason] || reason);
  };

  // Função para executar restart manual do sistema
  const handleManualRestart = async () => {
    if (!window.confirm('⚠️ ATENÇÃO: Isso irá deletar todos os sinais atuais e reiniciar o sistema. Deseja continuar?')) {
      return;
    }

    try {
      setIsRefreshing(true);
      
      const response = await fetch('/api/scheduler/delete-signals', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ type: 'all' })
      });

      const result = await response.json();
      
      if (result.success) {
        alert('✅ Sistema reiniciado com sucesso! Todos os sinais foram limpos e o sistema está pronto para gerar novos sinais.');
        // Recarregar dados após restart
        await loadData();
      } else {
        throw new Error(result.message || 'Erro desconhecido');
      }
    } catch (error) {
      console.error('Erro ao executar restart manual:', error);
      alert('❌ Erro ao executar restart manual. Tente novamente.');
    } finally {
      setIsRefreshing(false);
    }
  };

  // Função para traduzir motivos de confirmação
  const translateConfirmationReasons = (reasons: string[] | string) => {
    const translations: { [key: string]: string } = {
      'breakout_confirmed': '🚀 Rompimento Confirmado',
      'volume_confirmed': '📈 Volume Confirmado',
      'btc_aligned': '₿ BTC Alinhado',
      'momentum_sustained': '⚡ Momentum Sustentado',
      'support_resistance_hold': '📊 Suporte/Resistência Confirmado'
    };
    
    // Se reasons é uma string, converter para array
    let reasonsArray: string[];
    if (typeof reasons === 'string') {
      // Tratar diferentes formatos de string
      if (reasons.includes(',')) {
        // Formato: "breakout_confirmed, volume_confirmed"
        reasonsArray = reasons.split(',').map(r => r.trim());
      } else if (reasons.startsWith('[') && reasons.endsWith(']')) {
        // Formato: "['breakout_confirmed', 'volume_confirmed']"
        try {
          reasonsArray = JSON.parse(reasons.replace(/'/g, '"'));
        } catch {
          reasonsArray = [reasons];
        }
      } else {
        // String simples
        reasonsArray = [reasons];
      }
    } else if (Array.isArray(reasons)) {
      reasonsArray = reasons;
    } else {
      reasonsArray = [];
    }
    
    return reasonsArray.map(reason => translations[reason] || reason);
  };



  // Função auxiliar para verificar autenticação
  const checkAuthAndRedirect = (response: Response) => {
    if (response.status === 401 || response.status === 403) {
      console.warn('Token expirado, redirecionando para login...');
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      navigate('/login', { 
        state: { 
          message: 'Sessão expirada. Faça login novamente.',
          returnUrl: '/btc-analysis'
        }
      });
      return true;
    }
    return false;
  };

  // Funções para carregar dados
  const loadPendingSignals = async () => {
    try {
      console.log('🔄 Carregando sinais pendentes...');
      const response = await fetch('/api/btc-signals/pending');
      console.log('📊 Resposta pending signals:', response.status);
      
      const data = await response.json();
      console.log('✅ Dados pending signals recebidos:', data);
      
      if (data.success && data.data && Array.isArray(data.data.pending_signals)) {
        setPendingSignals(data.data.pending_signals);
        console.log(`✅ ${data.data.pending_signals.length} sinais pendentes carregados`);
      } else if (data.success && Array.isArray(data.data)) {
        // Fallback para estrutura antiga
        setPendingSignals(data.data);
        console.log(`✅ ${data.data.length} sinais pendentes carregados (estrutura antiga)`);
      } else {
        console.warn('⚠️ Resposta pending signals sem dados válidos:', data);
        setPendingSignals([]);
      }
    } catch (error) {
      console.error('❌ Erro ao carregar sinais pendentes:', error);
      setPendingSignals([]);
    }
  };

  const loadConfirmedSignals = async () => {
    try {
      console.log('🔄 Carregando sinais confirmados...');
      const response = await fetch('/api/btc-signals/confirmed');
      console.log('📊 Resposta confirmed signals:', response.status);
      
      const data = await response.json();
      console.log('✅ Dados confirmed signals recebidos:', data);
      
      if (Array.isArray(data)) {
        // API retorna array diretamente
        setConfirmedSignals(data);
        console.log(`✅ ${data.length} sinais confirmados carregados`);
      } else if (data.success && data.data && Array.isArray(data.data.confirmed_signals)) {
        // Estrutura com data.confirmed_signals
        setConfirmedSignals(data.data.confirmed_signals);
        console.log(`✅ ${data.data.confirmed_signals.length} sinais confirmados carregados`);
      } else if (data.success && Array.isArray(data.data)) {
        // Fallback para estrutura antiga
        setConfirmedSignals(data.data);
        console.log(`✅ ${data.data.length} sinais confirmados carregados (estrutura antiga)`);
      } else {
        console.warn('⚠️ Resposta confirmed signals sem dados válidos:', data);
        setConfirmedSignals([]);
      }
    } catch (error) {
      console.error('❌ Erro ao carregar sinais confirmados:', error);
      setConfirmedSignals([]);
    }
  };

  const loadRejectedSignals = async () => {
    try {
      console.log('🔄 Carregando sinais rejeitados...');
      const response = await fetch('/api/btc-signals/rejected');
      console.log('📊 Resposta rejected signals:', response.status);
      
      const data = await response.json();
      console.log('✅ Dados rejected signals recebidos:', data);
      
      if (data.success && data.data && Array.isArray(data.data.rejected_signals)) {
        setRejectedSignals(data.data.rejected_signals);
        console.log(`✅ ${data.data.rejected_signals.length} sinais rejeitados carregados`);
      } else if (data.success && Array.isArray(data.data)) {
        // Fallback para estrutura antiga
        setRejectedSignals(data.data);
        console.log(`✅ ${data.data.length} sinais rejeitados carregados (estrutura antiga)`);
      } else {
        console.warn('⚠️ Resposta rejected signals sem dados válidos:', data);
        setRejectedSignals([]);
      }
    } catch (error) {
      console.error('❌ Erro ao carregar sinais rejeitados:', error);
      setRejectedSignals([]);
    }
  };

  const loadMonitoredSignals = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');
        return;
      }
      
      const response = await fetch('/api/signal-monitoring/signals/active', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (checkAuthAndRedirect(response)) return;
      
      const data = await response.json();
      if (data.success && Array.isArray(data.data)) {
        setMonitoredSignals(data.data);
      } else {
        setMonitoredSignals([]);
      }
    } catch (error) {
      console.error('Erro ao carregar sinais monitorados:', error);
      setMonitoredSignals([]);
    }
  };

  const loadExpiredSignals = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');
        return;
      }
      
      const response = await fetch('/api/signal-monitoring/signals/expired', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (checkAuthAndRedirect(response)) return;
      
      const data = await response.json();
      if (data.success && Array.isArray(data.data)) {
        setExpiredSignals(data.data);
      } else {
        setExpiredSignals([]);
      }
    } catch (error) {
      console.error('Erro ao carregar sinais expirados:', error);
      setExpiredSignals([]);
    }
  };

  const loadMonitoringStats = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');
        return;
      }
      
      const response = await fetch('/api/signal-monitoring/stats', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (checkAuthAndRedirect(response)) return;
      
      const data = await response.json();
      if (data.success) {
        setMonitoringStats(data.data || null);
      }
    } catch (error) {
      console.error('Erro ao carregar estatísticas de monitoramento:', error);
    }
  };

  const loadBtcMetrics = async () => {
    try {
      console.log('🔄 Carregando métricas BTC...');
      const token = localStorage.getItem('token');
      if (!token) {
        console.warn('❌ Token não encontrado, redirecionando para login');
        navigate('/login');
        return;
      }
      
      const response = await fetch('/api/btc-signals/metrics', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      console.log('📊 Resposta métricas BTC:', response.status);
      
      if (checkAuthAndRedirect(response)) return;
      
      const data = await response.json();
      if (data.success) {
        setBtcMetrics(data.data || null);
      }
    } catch (error) {
      console.error('Erro ao carregar métricas BTC:', error);
    }
  };

  const loadBtcAnalysis = async () => {
    try {
      console.log('🔄 Carregando análise BTC...');
      const response = await fetch('/api/market-status');
      console.log('📊 Resposta market-status:', response.status);
      
      const data = await response.json();
      console.log('✅ Dados market-status recebidos:', data);
      
      if (data.success) {
        setBtcAnalysis(data.data || null);
        console.log('✅ Análise BTC atualizada');
      } else {
        console.warn('⚠️ Resposta market-status sem sucesso:', data);
      }
    } catch (error) {
      console.error('❌ Erro ao carregar análise BTC:', error);
    }
  };

  const loadRestartInfo = async () => {
    try {
      console.log('🔄 Carregando informações de restart...');
      const response = await fetch('/api/restart-system/status');
      console.log('📊 Resposta restart-system:', response.status);
      
      const data = await response.json();
      console.log('✅ Dados restart-system recebidos:', data);
      
      if (data.success) {
        setRestartInfo(data.data || null);
        console.log('✅ Informações de restart atualizadas');
      } else {
        console.warn('⚠️ Resposta restart-system sem sucesso:', data);
      }
    } catch (error) {
      console.error('❌ Erro ao carregar informações de restart:', error);
    }
  };

  const loadData = async () => {
    console.log('🚀 Iniciando carregamento de todos os dados...');
    setLoading(true);
    
    try {
      await Promise.all([
        loadPendingSignals(),
        loadConfirmedSignals(),
        loadRejectedSignals(),
        loadMonitoredSignals(),
        loadExpiredSignals(),
        loadMonitoringStats(),
        loadBtcMetrics(),
        loadBtcAnalysis(),
        loadRestartInfo()
      ]);
      console.log('✅ Todos os dados carregados com sucesso!');
    } catch (error) {
      console.error('❌ Erro durante carregamento dos dados:', error);
    } finally {
      setLoading(false);
    }
  };

  // Função para refresh manual
  const handleManualRefresh = async () => {
    if (isRefreshing) return;
    
    setIsRefreshing(true);
    await loadData();
    setIsRefreshing(false);
    
    // Resetar countdown
    setRefreshCountdown(30);
  };
  
  // Função para toggle do auto-refresh
  const toggleAutoRefresh = () => {
    setIsAutoRefreshEnabled(!isAutoRefreshEnabled);
  };
  
  // Configurar auto-refresh
  useEffect(() => {
    if (isAutoRefreshEnabled) {
      // Iniciar countdown
      countdownIntervalRef.current = setInterval(() => {
        setRefreshCountdown(prev => {
          if (prev <= 1) {
            return 30; // Reset countdown
          }
          return prev - 1;
        });
      }, 1000);
      
      // Iniciar auto-refresh
      refreshIntervalRef.current = setInterval(async () => {
        if (!isRefreshing) {
          setIsRefreshing(true);
          await loadData();
          setIsRefreshing(false);
        }
      }, 30000);
    } else {
      // Limpar intervalos
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current);
        refreshIntervalRef.current = null;
      }
      if (countdownIntervalRef.current) {
        clearInterval(countdownIntervalRef.current);
        countdownIntervalRef.current = null;
      }
    }
    
    return () => {
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current);
      }
      if (countdownIntervalRef.current) {
        clearInterval(countdownIntervalRef.current);
      }
    };
  }, [isAutoRefreshEnabled, isRefreshing]);
  
  // Carregar dados iniciais
   useEffect(() => {
     loadData();
   }, []);

  if (loading) {
    return (
      <BTCContainer>
        <LoadingSpinner>
          <FaSync className="fa-spin" /> Carregando dados...
        </LoadingSpinner>
      </BTCContainer>
    );
  }

  return (
    <BTCContainer>
      <Header>
        <div>
          <Title>
            <BTCIcon /> Análise BTC
          </Title>
          <div style={{ 
            display: 'flex', 
            gap: '20px', 
            marginTop: '10px',
            fontSize: '0.9em',
            color: '#94a3b8'
          }}>
            <div>
              <strong style={{ color: '#f59e0b' }}>Preço BTC:</strong> 
              <span style={{ color: btcAnalysis?.change_24h >= 0 ? '#10b981' : '#ef4444', marginLeft: '5px' }}>
                ${btcAnalysis?.price?.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0'}
              </span>
              <span style={{ marginLeft: '5px' }}>
                ({btcAnalysis?.change_24h >= 0 ? '+' : ''}{btcAnalysis?.change_24h?.toFixed(2) || '0'}%)
              </span>
            </div>

          </div>
        </div>
        <RefreshControls>
          <AutoRefreshContainer>
            <AutoRefreshButton 
              $isActive={isAutoRefreshEnabled}
              onClick={toggleAutoRefresh}
              title={isAutoRefreshEnabled ? 'Pausar auto-refresh' : 'Ativar auto-refresh'}
            >
              {isAutoRefreshEnabled ? <FaPause size={12} /> : <FaPlay size={12} />}
            </AutoRefreshButton>
            
            <RefreshIndicator $isRefreshing={isRefreshing}>
              <div className="refresh-dot"></div>
              <CountdownText $timeLeft={refreshCountdown}>
                {isAutoRefreshEnabled ? `${refreshCountdown}s` : 'Off'}
              </CountdownText>
            </RefreshIndicator>
          </AutoRefreshContainer>
          
          <RefreshButton 
            onClick={handleManualRefresh}
            disabled={isRefreshing}
          >
            <FaSync className={isRefreshing ? 'fa-spin' : ''} /> 
            {isRefreshing ? 'Atualizando...' : 'Atualizar'}
          </RefreshButton>
        </RefreshControls>
      </Header>

      <TabContainer>
        <Tab 
          $active={activeTab === 'pending'} 
          onClick={() => setActiveTab('pending')}
        >
          Pendentes ({pendingSignals.length})
        </Tab>
        <Tab 
          $active={activeTab === 'confirmed'} 
          onClick={() => setActiveTab('confirmed')}
        >
          Confirmados ({confirmedSignals.length})
        </Tab>
        <Tab 
          $active={activeTab === 'rejected'} 
          onClick={() => setActiveTab('rejected')}
        >
          Rejeitados ({rejectedSignals.length})
        </Tab>
        <Tab 
          $active={activeTab === 'monitoring'} 
          onClick={() => setActiveTab('monitoring')}
        >
          Monitoramento ({monitoredSignals.length})
        </Tab>
        <Tab 
          $active={activeTab === 'expired'} 
          onClick={() => setActiveTab('expired')}
        >
          Expirados ({expiredSignals.length})
        </Tab>
      </TabContainer>

      <ContentContainer>
        {activeTab === 'pending' && (
          <div>
            {pendingSignals.length === 0 ? (
              <EmptyState>
                <EmptyIcon><FaHourglassHalf /></EmptyIcon>
                <div>Nenhum sinal pendente no momento</div>
              </EmptyState>
            ) : (
              pendingSignals.map(signal => (
                <SignalCard key={signal.id}>
                  <SignalHeader>
                    <SignalSymbol>{signal.symbol}</SignalSymbol>
                    <SignalType $type={signal.type}>{signal.type}</SignalType>
                  </SignalHeader>
                  
                  <SignalDetails>
                    <SignalDetail>
                      <DetailLabel>Entrada</DetailLabel>
                      <DetailValue>{formatPrice(signal.entry_price)}</DetailValue>
                    </SignalDetail>
                    <SignalDetail>
                      <DetailLabel>Alvo</DetailLabel>
                      <DetailValue>{formatPrice(signal.target_price)}</DetailValue>
                    </SignalDetail>
                    <SignalDetail>
                      <DetailLabel>Qualidade</DetailLabel>
                      <DetailValue>{signal.quality_score.toFixed(1)} ({signal.signal_class})</DetailValue>
                    </SignalDetail>
                    <SignalDetail>
                      <DetailLabel>Criado em</DetailLabel>
                      <DetailValue>{formatDateTime(signal.created_at)}</DetailValue>
                    </SignalDetail>
                    <SignalDetail>
                      <DetailLabel>Expira em</DetailLabel>
                      <DetailValue>{formatDateTime(signal.expires_at)}</DetailValue>
                    </SignalDetail>
                    <SignalDetail>
                      <DetailLabel>Tentativas</DetailLabel>
                      <DetailValue>{signal.confirmation_attempts}</DetailValue>
                    </SignalDetail>
                  </SignalDetails>
                  
                  {/* Componente de Rastreabilidade */}
                  <SignalTraceability signal={signal} />
                </SignalCard>
              ))
            )}
          </div>
        )}

        {activeTab === 'confirmed' && (
          <div>
            {confirmedSignals.length === 0 ? (
              <EmptyState>
                <EmptyIcon><FaCheckCircle /></EmptyIcon>
                <div>Nenhum sinal confirmado recentemente</div>
              </EmptyState>
            ) : (
              confirmedSignals.map(signal => (
                <SignalCard key={signal.id}>
                  <SignalHeader>
                    <SignalSymbol>{signal.symbol}</SignalSymbol>
                    <SignalType $type={signal.type}>{signal.type}</SignalType>
                  </SignalHeader>
                  
                  <SignalDetails>
                    <SignalDetail>
                      <DetailLabel>Entrada</DetailLabel>
                      <DetailValue>{formatPrice(signal.entry_price)}</DetailValue>
                    </SignalDetail>
                    <SignalDetail>
                      <DetailLabel>Alvo</DetailLabel>
                      <DetailValue>{signal.target_price ? formatPrice(signal.target_price) : 'N/A'}</DetailValue>
                    </SignalDetail>
                    <SignalDetail>
                      <DetailLabel>Qualidade</DetailLabel>
                      <DetailValue>{signal.quality_score?.toFixed(1) || 'N/A'} ({signal.signal_class || 'N/A'})</DetailValue>
                    </SignalDetail>
                    <SignalDetail>
                      <DetailLabel>Criado em</DetailLabel>
                      <DetailValue>{formatDateTime(signal.created_at)}</DetailValue>
                    </SignalDetail>
                    <SignalDetail>
                      <DetailLabel>Confirmado em</DetailLabel>
                      <DetailValue>{signal.confirmed_at ? formatDateTime(signal.confirmed_at) : 'N/A'}</DetailValue>
                    </SignalDetail>
                    <SignalDetail>
                      <DetailLabel>Tentativas</DetailLabel>
                      <DetailValue>{signal.confirmation_attempts || 0}</DetailValue>
                    </SignalDetail>
                    {signal.confirmation_reasons && signal.confirmation_reasons.length > 0 && (
                      <SignalDetail style={{gridColumn: '1 / -1'}}>
                        <DetailLabel>Motivos da Confirmação</DetailLabel>
                        <ReasonsList>
                          {translateConfirmationReasons(signal.confirmation_reasons).map((reason, index) => (
                            <ReasonTag key={index} style={{background: '#10b981'}}>
                              {reason}
                            </ReasonTag>
                          ))}
                        </ReasonsList>
                      </SignalDetail>
                    )}
                  </SignalDetails>
                  
                  {/* Componente de Rastreabilidade */}
                  <SignalTraceability signal={signal} />
                </SignalCard>
              ))
            )}
          </div>
        )}

        {activeTab === 'rejected' && (
          <div>
            {rejectedSignals.length === 0 ? (
              <EmptyState>
                <EmptyIcon><FaTimesCircle /></EmptyIcon>
                <div>Nenhum sinal rejeitado recentemente</div>
              </EmptyState>
            ) : (
              rejectedSignals.map(signal => (
                <SignalCard key={signal.id}>
                  <SignalHeader>
                    <SignalSymbol>{signal.symbol}</SignalSymbol>
                    <SignalType $type={signal.type}>{signal.type}</SignalType>
                  </SignalHeader>
                  
                  <SignalDetails>
                    <SignalDetail>
                      <DetailLabel>Entrada</DetailLabel>
                      <DetailValue>{formatPrice(signal.entry_price)}</DetailValue>
                    </SignalDetail>
                    <SignalDetail>
                      <DetailLabel>Qualidade</DetailLabel>
                      <DetailValue>{signal.quality_score.toFixed(1)} ({signal.signal_class})</DetailValue>
                    </SignalDetail>
                    <SignalDetail>
                      <DetailLabel>Criado em</DetailLabel>
                      <DetailValue>{formatDateTime(signal.created_at)}</DetailValue>
                    </SignalDetail>
                    <SignalDetail>
                      <DetailLabel>Rejeitado em</DetailLabel>
                      <DetailValue>{formatDateTime(signal.rejected_at)}</DetailValue>
                    </SignalDetail>
                    <SignalDetail>
                      <DetailLabel>Tentativas</DetailLabel>
                      <DetailValue>{signal.confirmation_attempts}</DetailValue>
                    </SignalDetail>
                    <SignalDetail>
                      <DetailLabel>Motivos da Rejeição</DetailLabel>
                      <ReasonsList>
                        {translateRejectionReasons(signal.rejection_reasons).map((reason, index) => (
                          <ReasonTag key={index} style={{background: '#ef4444'}}>
                            {reason}
                          </ReasonTag>
                        ))}
                      </ReasonsList>
                    </SignalDetail>
                  </SignalDetails>
                  
                  {/* Componente de Rastreabilidade */}
                  <SignalTraceability signal={signal} />
                </SignalCard>
              ))
            )}
          </div>
        )}

        {activeTab === 'monitoring' && (
          <div>
            
            {/* Análise BTC */}
            <TechnicalGrid>
                <TechnicalCard>
                  <TechnicalTitle>
                    <FaBitcoin /> Preço BTC
                  </TechnicalTitle>
                  <TechnicalValue $color={btcAnalysis?.change_24h >= 0 ? '#10b981' : '#ef4444'}>
                    ${btcAnalysis?.price?.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0'}
                  </TechnicalValue>
                  <TechnicalSubtext>
                    {btcAnalysis?.change_24h >= 0 ? '+' : ''}{btcAnalysis?.change_24h?.toFixed(2) || '0'}% (24h)
                  </TechnicalSubtext>
                </TechnicalCard>
                
                <TechnicalCard>
                  <TechnicalTitle>
                    <FaChartLine /> Tendência
                  </TechnicalTitle>
                  <TechnicalValue $color={btcAnalysis?.trend === 'BULLISH' ? '#10b981' : btcAnalysis?.trend === 'BEARISH' ? '#ef4444' : '#f59e0b'}>
                    {btcAnalysis?.trend || 'NEUTRO'}
                  </TechnicalValue>
                  <TechnicalSubtext>
                    Força: {btcAnalysis?.strength?.toFixed(1) || '0'}%
                  </TechnicalSubtext>
                </TechnicalCard>
                
                <TechnicalCard>
                  <TechnicalTitle>
                    📊 Volume 24h
                  </TechnicalTitle>
                  <TechnicalValue $color="#f59e0b">
                    ${(btcAnalysis?.volume_24h / 1000000000)?.toFixed(2) || '0'}B
                  </TechnicalValue>
                  <TechnicalSubtext>
                    Volume de negociação
                  </TechnicalSubtext>
                </TechnicalCard>
                
                <TechnicalCard>
                  <TechnicalTitle>
                    📈 Volatilidade
                  </TechnicalTitle>
                  <TechnicalValue $color={btcAnalysis?.volatility > 5 ? '#ef4444' : btcAnalysis?.volatility > 2 ? '#f59e0b' : '#10b981'}>
                    {btcAnalysis?.volatility?.toFixed(2) || '0'}%
                  </TechnicalValue>
                  <TechnicalSubtext>
                    Nível de volatilidade
                  </TechnicalSubtext>
                </TechnicalCard>
              </TechnicalGrid>
            
            {/* Informações do Sistema de Restart */}
            <TechnicalGrid>
                <TechnicalCard>
                  <TechnicalTitle>
                    <FaClock /> Próximo Restart
                  </TechnicalTitle>
                  <TechnicalValue $color="#f59e0b" style={{fontSize: '1em'}}>
                    {restartInfo?.restart_info?.countdown ? 
                      `${restartInfo.restart_info.countdown.hours}h ${restartInfo.restart_info.countdown.minutes}m` : 
                      'N/A'
                    }
                  </TechnicalValue>
                  <TechnicalSubtext>
                    {restartInfo?.restart_info?.schedule || 'Agendamento não definido'}
                  </TechnicalSubtext>
                  <button
                    onClick={handleManualRestart}
                    style={{
                      marginTop: '10px',
                      padding: '8px 16px',
                      backgroundColor: '#ef4444',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      fontSize: '0.85em',
                      fontWeight: '600',
                      transition: 'all 0.3s ease',
                      width: '100%'
                    }}
                    onMouseEnter={(e) => {
                      (e.target as HTMLButtonElement).style.backgroundColor = '#dc2626';
                      (e.target as HTMLButtonElement).style.transform = 'translateY(-1px)';
                    }}
                    onMouseLeave={(e) => {
                      (e.target as HTMLButtonElement).style.backgroundColor = '#ef4444';
                      (e.target as HTMLButtonElement).style.transform = 'translateY(0)';
                    }}
                  >
                    🔄 Reiniciar Agora
                  </button>
                </TechnicalCard>
                
                <TechnicalCard>
                  <TechnicalTitle>
                    ⏱️ Uptime Sistema
                  </TechnicalTitle>
                  <TechnicalValue $color="#10b981">
                    {restartInfo?.system_uptime ? 
                      `${restartInfo.system_uptime.hours}h ${restartInfo.system_uptime.minutes}m` : 
                      'N/A'
                    }
                  </TechnicalValue>
                  <TechnicalSubtext>
                    Tempo ativo desde último restart
                  </TechnicalSubtext>
                </TechnicalCard>
                
                <TechnicalCard>
                  <TechnicalTitle>
                    🔧 Status BTC System
                  </TechnicalTitle>
                  <TechnicalValue $color={restartInfo?.btc_system?.status === 'ACTIVE' ? '#10b981' : '#ef4444'}>
                    {restartInfo?.btc_system?.status || 'UNKNOWN'}
                  </TechnicalValue>
                  <TechnicalSubtext>
                    Sistema de confirmação BTC
                  </TechnicalSubtext>
                </TechnicalCard>
                
                <TechnicalCard>
                  <TechnicalTitle>
                    📋 Recursos Ativos
                  </TechnicalTitle>
                  <TechnicalValue $color="#f59e0b" style={{fontSize: '0.9em'}}>
                    {restartInfo?.restart_features?.length || 0} recursos
                  </TechnicalValue>
                  <TechnicalSubtext>
                    {restartInfo?.restart_features?.slice(0, 2).join(', ') || 'Nenhum recurso'}
                  </TechnicalSubtext>
                </TechnicalCard>
              </TechnicalGrid>
            
            {/* Estatísticas do Monitoramento */}
            <TechnicalGrid>
              <TechnicalCard>
                <TechnicalTitle>
                  📊 Sinais Ativos
                </TechnicalTitle>
                <TechnicalValue $color="#f59e0b">
                  {monitoringStats?.total_monitored || monitoredSignals.length}
                </TechnicalValue>
                <TechnicalSubtext>
                  Sinais sendo monitorados
                </TechnicalSubtext>
              </TechnicalCard>
              
              <TechnicalCard>
                <TechnicalTitle>
                  🎯 Taxa de Sucesso
                </TechnicalTitle>
                <TechnicalValue $color={monitoringStats?.success_rate >= 50 ? '#10b981' : '#ef4444'}>
                  {monitoringStats?.success_rate?.toFixed(1) || '0.0'}%
                </TechnicalValue>
                <TechnicalSubtext>
                  {monitoringStats?.successful_signals || 0} de {monitoringStats?.total_evaluated_signals || 0} sinais
                </TechnicalSubtext>
              </TechnicalCard>
              
              <TechnicalCard>
                <TechnicalTitle>
                  💰 Lucro Médio
                </TechnicalTitle>
                <TechnicalValue $color="#10b981">
                  {monitoringStats?.average_successful_profit?.toFixed(1) || '0.0'}%
                </TechnicalValue>
                <TechnicalSubtext>
                  Média dos sinais bem-sucedidos
                </TechnicalSubtext>
              </TechnicalCard>
              
              <TechnicalCard>
                <TechnicalTitle>
                  🏆 Melhor Performance
                </TechnicalTitle>
                <TechnicalValue $color="#10b981">
                  {monitoringStats?.max_profit?.toFixed(1) || '0.0'}%
                </TechnicalValue>
                <TechnicalSubtext>
                  Maior lucro registrado
                </TechnicalSubtext>
              </TechnicalCard>
              
              <TechnicalCard>
                <TechnicalTitle>
                  ✅ Sinais Completados
                </TechnicalTitle>
                <TechnicalValue $color="#10b981">
                  {monitoringStats?.total_completed || 0}
                </TechnicalValue>
                <TechnicalSubtext>
                  Atingiram 300% de lucro
                </TechnicalSubtext>
              </TechnicalCard>
              
              <TechnicalCard>
                <TechnicalTitle>
                  ⏰ Sinais Expirados
                </TechnicalTitle>
                <TechnicalValue $color="#ef4444">
                  {monitoringStats?.total_expired || 0}
                </TechnicalValue>
                <TechnicalSubtext>
                  Expiraram após 15 dias
                </TechnicalSubtext>
              </TechnicalCard>
              
              <TechnicalCard>
                <TechnicalTitle>
                  🔄 Status do Sistema
                </TechnicalTitle>
                <TechnicalValue $color={
                  (monitoringStats?.is_monitoring || 
                   btcMetrics?.system_status === 'active' || 
                   restartInfo?.btc_system?.status === 'ACTIVE' ||
                   restartInfo?.system_status?.btc_confirmation === 'active') ? '#10b981' : '#ef4444'
                }>
                  {(monitoringStats?.is_monitoring || 
                    btcMetrics?.system_status === 'active' || 
                    restartInfo?.btc_system?.status === 'ACTIVE' ||
                    restartInfo?.system_status?.btc_confirmation === 'active') ? 'ATIVO' : 'INATIVO'}
                </TechnicalValue>
                <TechnicalSubtext>
                  Sistema de monitoramento
                </TechnicalSubtext>
              </TechnicalCard>
              
              <TechnicalCard>
                <TechnicalTitle>
                  📅 Última Atualização
                </TechnicalTitle>
                <TechnicalValue $color="#94a3b8" style={{fontSize: '1em'}}>
                  {monitoringStats?.last_update ? new Date(monitoringStats.last_update).toLocaleString('pt-BR') : 'Nunca'}
                </TechnicalValue>
                <TechnicalSubtext>
                  Dados do sistema
                </TechnicalSubtext>
              </TechnicalCard>
            </TechnicalGrid>
            
            {/* Lista de Sinais Monitorados */}
            {monitoredSignals.length === 0 ? (
              <EmptyState>
                <EmptyIcon><FaDesktop /></EmptyIcon>
                <div>Nenhum sinal sendo monitorado no momento</div>
                <div style={{fontSize: '0.9em', marginTop: '10px', color: '#6b7280'}}>
                  Sinais confirmados serão automaticamente adicionados aqui
                </div>
              </EmptyState>
            ) : (
              monitoredSignals.map(signal => (
                <SignalCard key={signal.id} style={{borderLeft: `4px solid ${signal.current_profit >= 0 ? '#10b981' : '#ef4444'}`}}>
                  <SignalHeader>
                    <SignalSymbol>{signal.symbol}</SignalSymbol>
                    <div style={{display: 'flex', gap: '10px', alignItems: 'center'}}>
                      <SignalType $type={signal.signal_type}>{signal.signal_type}</SignalType>
                      <div style={{
                        padding: '4px 8px',
                        borderRadius: '12px',
                        fontSize: '0.8em',
                        fontWeight: '600',
                        background: signal.current_profit >= signal.required_percentage ? '#10b981' : signal.current_profit >= 0 ? '#f59e0b' : '#ef4444',
                        color: 'white'
                      }}>
                        {signal.current_profit >= signal.required_percentage ? '🎯 META ATINGIDA' : 
                         signal.current_profit >= 0 ? '📈 LUCRO' : '📉 PREJUÍZO'}
                      </div>
                    </div>
                  </SignalHeader>
                  
                  {/* Barra de Progresso do Lucro */}
                  <div style={{marginBottom: '20px'}}>
                    <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '8px'}}>
                      <span style={{color: '#94a3b8', fontSize: '0.9em'}}>Progresso para 300% de Lucro</span>
                      <span style={{color: '#f59e0b', fontWeight: '600'}}>
                        {((signal.current_profit / signal.required_percentage) * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div style={{
                      width: '100%',
                      height: '12px',
                      background: '#374151',
                      borderRadius: '6px',
                      position: 'relative',
                      overflow: 'hidden'
                    }}>
                      <div style={{
                        width: `${Math.min(100, (signal.current_profit / signal.required_percentage) * 100)}%`,
                        height: '100%',
                        background: signal.current_profit >= signal.required_percentage ? 
                          'linear-gradient(90deg, #10b981, #059669)' : 
                          signal.current_profit >= 0 ? 
                          'linear-gradient(90deg, #f59e0b, #d97706)' : 
                          'linear-gradient(90deg, #ef4444, #dc2626)',
                        borderRadius: '6px',
                        transition: 'all 0.3s ease'
                      }} />
                    </div>
                  </div>
                  
                  <SignalDetails>
                    <SignalDetail>
                      <DetailLabel>💰 Lucro Atual</DetailLabel>
                      <DetailValue style={{color: signal.current_profit >= 0 ? '#10b981' : '#ef4444'}}>
                        {signal.current_profit >= 0 ? '+' : ''}{signal.current_profit.toFixed(2)}%
                      </DetailValue>
                    </SignalDetail>
                    <SignalDetail>
                      <DetailLabel>🎯 Meta de Lucro</DetailLabel>
                      <DetailValue style={{color: '#f59e0b'}}>
                        {signal.required_percentage.toFixed(1)}% ({signal.max_leverage}x)
                      </DetailValue>
                    </SignalDetail>
                    <SignalDetail>
                      <DetailLabel>📊 Preço Entrada</DetailLabel>
                      <DetailValue>{formatPrice(signal.entry_price)}</DetailValue>
                    </SignalDetail>
                    <SignalDetail>
                      <DetailLabel>📈 Preço Atual</DetailLabel>
                      <DetailValue style={{color: signal.current_price > signal.entry_price ? '#10b981' : '#ef4444'}}>
                        {formatPrice(signal.current_price)}
                      </DetailValue>
                    </SignalDetail>
                    <SignalDetail>
                      <DetailLabel>⏱️ Dias Monitorados</DetailLabel>
                      <DetailValue>{signal.days_monitored} de 15 dias</DetailValue>
                    </SignalDetail>
                    <SignalDetail>
                      <DetailLabel>⏰ Dias Restantes</DetailLabel>
                      <DetailValue style={{color: (15 - signal.days_monitored) <= 3 ? '#ef4444' : '#94a3b8'}}>
                        {15 - signal.days_monitored} dias
                      </DetailValue>
                    </SignalDetail>
                    <SignalDetail>
                      <DetailLabel>🏆 Lucro Máximo</DetailLabel>
                      <DetailValue style={{color: '#10b981'}}>
                        +{signal.max_profit_reached.toFixed(2)}%
                      </DetailValue>
                    </SignalDetail>
                    <SignalDetail>
                      <DetailLabel>🔄 Última Atualização</DetailLabel>
                      <DetailValue>{signal.last_updated}</DetailValue>
                    </SignalDetail>
                  </SignalDetails>
                  
                  {/* Indicador de Tempo Restante */}
                  <div style={{
                    marginTop: '15px',
                    padding: '10px',
                    background: (15 - signal.days_monitored) <= 3 ? 'rgba(239, 68, 68, 0.1)' : 'rgba(107, 114, 128, 0.1)',
                    borderRadius: '8px',
                    border: `1px solid ${(15 - signal.days_monitored) <= 3 ? '#ef4444' : '#374151'}`
                  }}>
                    <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                      <span style={{fontSize: '0.9em', color: '#94a3b8'}}>
                        {(15 - signal.days_monitored) <= 3 ? '⚠️ Expirando em breve' : '⏳ Tempo de monitoramento'}
                      </span>
                      <span style={{fontWeight: '600', color: (15 - signal.days_monitored) <= 3 ? '#ef4444' : '#f59e0b'}}>
                        {Math.round(((15 - signal.days_monitored) / 15) * 100)}% restante
                      </span>
                    </div>
                  </div>
                  
                  {/* Seção de Justificativas de Confirmação */}
                  <ConfirmationSection>
                    <ConfirmationTitle>
                      <FaCheckCircle /> Por que este sinal foi confirmado?
                    </ConfirmationTitle>
                    
                    <ConfirmationGrid>
                      <ConfirmationItem>
                        <ConfirmationLabel>📊 Qualidade do Sinal</ConfirmationLabel>
                        <ConfirmationValue style={{color: signal.quality_score >= 80 ? '#10b981' : '#f59e0b'}}>
                          {signal.quality_score?.toFixed(1) || 'N/A'} pontos
                        </ConfirmationValue>
                      </ConfirmationItem>
                      
                      <ConfirmationItem>
                        <ConfirmationLabel>🏷️ Classe do Sinal</ConfirmationLabel>
                        <ConfirmationValue>{signal.signal_class || 'N/A'}</ConfirmationValue>
                      </ConfirmationItem>
                      
                      <ConfirmationItem>
                        <ConfirmationLabel>₿ Correlação BTC</ConfirmationLabel>
                        <ConfirmationValue style={{color: signal.btc_correlation >= 0.5 ? '#10b981' : '#ef4444'}}>
                          {signal.btc_correlation ? `${(signal.btc_correlation * 100).toFixed(1)}%` : 'N/A'}
                        </ConfirmationValue>
                      </ConfirmationItem>
                      
                      <ConfirmationItem>
                        <ConfirmationLabel>📈 Tendência BTC</ConfirmationLabel>
                        <ConfirmationValue style={{color: signal.btc_trend === 'BULLISH' ? '#10b981' : signal.btc_trend === 'BEARISH' ? '#ef4444' : '#f59e0b'}}>
                          {signal.btc_trend || 'N/A'}
                        </ConfirmationValue>
                      </ConfirmationItem>
                      
                      <ConfirmationItem>
                        <ConfirmationLabel>🔄 Tentativas</ConfirmationLabel>
                        <ConfirmationValue>{signal.confirmation_attempts || 1} tentativa(s)</ConfirmationValue>
                      </ConfirmationItem>
                      
                      <ConfirmationItem>
                        <ConfirmationLabel>⏰ Confirmado em</ConfirmationLabel>
                        <ConfirmationValue>{signal.confirmed_at}</ConfirmationValue>
                      </ConfirmationItem>
                    </ConfirmationGrid>
                    
                    {/* Motivos de Confirmação */}
                    {signal.confirmation_reasons && (
                      <div>
                        <ConfirmationLabel style={{display: 'block', marginBottom: '8px'}}>✅ Motivos da Confirmação:</ConfirmationLabel>
                        <ReasonsList>
                          {Array.isArray(signal.confirmation_reasons) 
                            ? signal.confirmation_reasons.map((reason, index) => (
                                <ReasonTag key={`reason-${signal.id}-${index}`}>{reason}</ReasonTag>
                              ))
                            : <ReasonTag key={`reason-${signal.id}-single`}>{signal.confirmation_reasons}</ReasonTag>
                          }
                        </ReasonsList>
                      </div>
                    )}
                    
                    {/* Indicadores Técnicos */}
                    {signal.technical_indicators && (
                      <TechnicalIndicators>
                        <IndicatorItem>
                          <IndicatorLabel>RSI</IndicatorLabel>
                          <IndicatorValue $positive={signal.technical_indicators.rsi >= 30 && signal.technical_indicators.rsi <= 70}>
                            {signal.technical_indicators.rsi?.toFixed(1) || 'N/A'}
                          </IndicatorValue>
                        </IndicatorItem>
                        
                        <IndicatorItem>
                          <IndicatorLabel>MACD</IndicatorLabel>
                          <IndicatorValue $positive={signal.technical_indicators.macd_bullish}>
                            {signal.technical_indicators.macd_bullish ? 'BULLISH' : 'BEARISH'}
                          </IndicatorValue>
                        </IndicatorItem>
                        
                        <IndicatorItem>
                          <IndicatorLabel>EMA Align</IndicatorLabel>
                          <IndicatorValue $positive={signal.technical_indicators.ema_alignment}>
                            {signal.technical_indicators.ema_alignment ? 'SIM' : 'NÃO'}
                          </IndicatorValue>
                        </IndicatorItem>
                        
                        <IndicatorItem>
                          <IndicatorLabel>Volume</IndicatorLabel>
                          <IndicatorValue $positive={signal.technical_indicators.volume_increase >= 1.2}>
                            +{signal.technical_indicators.volume_increase ? `${((signal.technical_indicators.volume_increase - 1) * 100).toFixed(1)}%` : '0%'}
                          </IndicatorValue>
                        </IndicatorItem>
                        
                        <IndicatorItem>
                          <IndicatorLabel>Breakout</IndicatorLabel>
                          <IndicatorValue $positive={signal.technical_indicators.breakout_percentage >= 0.5}>
                            {signal.technical_indicators.breakout_percentage ? `${signal.technical_indicators.breakout_percentage.toFixed(2)}%` : 'N/A'}
                          </IndicatorValue>
                        </IndicatorItem>
                      </TechnicalIndicators>
                    )}
                  </ConfirmationSection>
                </SignalCard>
              ))
            )}
          </div>
        )}

        {activeTab === 'expired' && (
          <div>
            {/* Estatísticas dos Sinais Expirados */}
            {monitoringStats && (
              <TechnicalGrid>
                <TechnicalCard>
                  <TechnicalTitle>
                    ✅ Sinais Bem-Sucedidos
                  </TechnicalTitle>
                  <TechnicalValue $color="#10b981">
                    {monitoringStats.successful_signals || 0}
                  </TechnicalValue>
                  <TechnicalSubtext>
                    Atingiram 300% de lucro
                  </TechnicalSubtext>
                </TechnicalCard>
                
                <TechnicalCard>
                  <TechnicalTitle>
                    ❌ Sinais Expirados
                  </TechnicalTitle>
                  <TechnicalValue $color="#ef4444">
                    {monitoringStats.failed_signals || 0}
                  </TechnicalValue>
                  <TechnicalSubtext>
                    Expiraram após 15 dias
                  </TechnicalSubtext>
                </TechnicalCard>
                
                <TechnicalCard>
                  <TechnicalTitle>
                    🏆 Lucro Máximo Atingido
                  </TechnicalTitle>
                  <TechnicalValue $color="#f59e0b">
                    {monitoringStats.max_profit.toFixed(1)}%
                  </TechnicalValue>
                  <TechnicalSubtext>
                    Melhor performance registrada
                  </TechnicalSubtext>
                </TechnicalCard>
              </TechnicalGrid>
            )}
            
            {/* Lista de Sinais Expirados */}
            {expiredSignals.length === 0 ? (
              <EmptyState>
                <EmptyIcon><FaClock /></EmptyIcon>
                <div>Nenhum sinal finalizado ainda</div>
                <div style={{fontSize: '0.9em', marginTop: '10px', color: '#6b7280'}}>
                  Sinais aparecerão aqui após 15 dias de monitoramento ou ao atingir 300% de lucro
                </div>
              </EmptyState>
            ) : (
              <div>
                {/* Separar sinais bem-sucedidos dos expirados */}
                {expiredSignals.filter(signal => signal.status === 'COMPLETED').length > 0 && (
                  <div style={{marginBottom: '30px'}}>
                    <StrategyTitle style={{color: '#10b981'}}>
                      🎯 Sinais Bem-Sucedidos (300% Atingido)
                    </StrategyTitle>
                    {expiredSignals.filter(signal => signal.status === 'COMPLETED').map(signal => (
                      <SignalCard key={signal.id} style={{borderLeft: '4px solid #10b981'}}>
                        <SignalHeader>
                          <SignalSymbol>{signal.symbol}</SignalSymbol>
                          <div style={{display: 'flex', gap: '10px', alignItems: 'center'}}>
                            <SignalType $type={signal.signal_type}>{signal.signal_type}</SignalType>
                            <div style={{
                              padding: '4px 8px',
                              borderRadius: '12px',
                              fontSize: '0.8em',
                              fontWeight: '600',
                              background: '#10b981',
                              color: 'white'
                            }}>
                              🎯 SUCESSO
                            </div>
                          </div>
                        </SignalHeader>
                        
                        {/* Barra de Sucesso */}
                        <div style={{marginBottom: '20px'}}>
                          <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '8px'}}>
                            <span style={{color: '#94a3b8', fontSize: '0.9em'}}>Meta de 300% de Lucro</span>
                            <span style={{color: '#10b981', fontWeight: '600'}}>✅ ATINGIDA</span>
                          </div>
                          <div style={{
                            width: '100%',
                            height: '12px',
                            background: 'linear-gradient(90deg, #10b981, #059669)',
                            borderRadius: '6px'
                          }} />
                        </div>
                        
                        <SignalDetails>
                          <SignalDetail>
                            <DetailLabel>🏆 Lucro Máximo</DetailLabel>
                            <DetailValue style={{color: '#10b981'}}>
                              +{signal.max_profit_reached.toFixed(2)}%
                            </DetailValue>
                          </SignalDetail>
                          <SignalDetail>
                            <DetailLabel>🎯 Meta Necessária</DetailLabel>
                            <DetailValue style={{color: '#f59e0b'}}>
                              {signal.required_percentage.toFixed(1)}% ({signal.max_leverage}x)
                            </DetailValue>
                          </SignalDetail>
                          <SignalDetail>
                            <DetailLabel>📊 Preço Entrada</DetailLabel>
                            <DetailValue>{formatPrice(signal.entry_price)}</DetailValue>
                          </SignalDetail>
                          <SignalDetail>
                            <DetailLabel>🎯 Preço Alvo</DetailLabel>
                            <DetailValue>{formatPrice(signal.target_price)}</DetailValue>
                          </SignalDetail>
                          <SignalDetail>
                            <DetailLabel>⏱️ Tempo para Sucesso</DetailLabel>
                            <DetailValue style={{color: '#10b981'}}>
                              {signal.days_monitored} dias
                            </DetailValue>
                          </SignalDetail>
                          <SignalDetail>
                            <DetailLabel>📅 Confirmado em</DetailLabel>
                            <DetailValue>{signal.confirmed_at}</DetailValue>
                          </SignalDetail>
                        </SignalDetails>
                        
                        {/* Indicador de Sucesso */}
                        <div style={{
                          marginTop: '15px',
                          padding: '10px',
                          background: 'rgba(16, 185, 129, 0.1)',
                          borderRadius: '8px',
                          border: '1px solid #10b981'
                        }}>
                          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                            <span style={{fontSize: '0.9em', color: '#10b981'}}>
                              🎉 Meta de 300% de lucro atingida com sucesso!
                            </span>
                            <span style={{fontWeight: '600', color: '#10b981'}}>
                              {((signal.max_profit_reached / signal.required_percentage) * 100).toFixed(0)}% da meta
                            </span>
                          </div>
                        </div>
                      </SignalCard>
                    ))}
                  </div>
                )}
                
                {/* Sinais que expiraram sem atingir a meta */}
                {expiredSignals.filter(signal => signal.status === 'EXPIRED').length > 0 && (
                  <div>
                    <StrategyTitle style={{color: '#ef4444'}}>
                      ⏰ Sinais Expirados (15 Dias Completos)
                    </StrategyTitle>
                    {expiredSignals.filter(signal => signal.status === 'EXPIRED').map(signal => (
                      <SignalCard key={signal.id} style={{borderLeft: '4px solid #ef4444'}}>
                        <SignalHeader>
                          <SignalSymbol>{signal.symbol}</SignalSymbol>
                          <div style={{display: 'flex', gap: '10px', alignItems: 'center'}}>
                            <SignalType $type={signal.signal_type}>{signal.signal_type}</SignalType>
                            <div style={{
                              padding: '4px 8px',
                              borderRadius: '12px',
                              fontSize: '0.8em',
                              fontWeight: '600',
                              background: '#ef4444',
                              color: 'white'
                            }}>
                              ⏰ EXPIRADO
                            </div>
                          </div>
                        </SignalHeader>
                        
                        {/* Barra de Progresso Final */}
                        <div style={{marginBottom: '20px'}}>
                          <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '8px'}}>
                            <span style={{color: '#94a3b8', fontSize: '0.9em'}}>Progresso Final (Meta: 300%)</span>
                            <span style={{color: '#ef4444', fontWeight: '600'}}>
                              {((signal.max_profit_reached / signal.required_percentage) * 100).toFixed(1)}%
                            </span>
                          </div>
                          <div style={{
                            width: '100%',
                            height: '12px',
                            background: '#374151',
                            borderRadius: '6px',
                            position: 'relative',
                            overflow: 'hidden'
                          }}>
                            <div style={{
                              width: `${Math.min(100, (signal.max_profit_reached / signal.required_percentage) * 100)}%`,
                              height: '100%',
                              background: signal.max_profit_reached >= 0 ? 
                                'linear-gradient(90deg, #f59e0b, #d97706)' : 
                                'linear-gradient(90deg, #ef4444, #dc2626)',
                              borderRadius: '6px'
                            }} />
                          </div>
                        </div>
                        
                        <SignalDetails>
                          <SignalDetail>
                            <DetailLabel>🏆 Lucro Máximo</DetailLabel>
                            <DetailValue style={{color: signal.max_profit_reached >= 0 ? '#f59e0b' : '#ef4444'}}>
                              {signal.max_profit_reached >= 0 ? '+' : ''}{signal.max_profit_reached.toFixed(2)}%
                            </DetailValue>
                          </SignalDetail>
                          <SignalDetail>
                            <DetailLabel>🎯 Meta Necessária</DetailLabel>
                            <DetailValue style={{color: '#f59e0b'}}>
                              {signal.required_percentage.toFixed(1)}% ({signal.max_leverage}x)
                            </DetailValue>
                          </SignalDetail>
                          <SignalDetail>
                            <DetailLabel>📊 Preço Entrada</DetailLabel>
                            <DetailValue>{formatPrice(signal.entry_price)}</DetailValue>
                          </SignalDetail>
                          <SignalDetail>
                            <DetailLabel>🎯 Preço Alvo</DetailLabel>
                            <DetailValue>{formatPrice(signal.target_price)}</DetailValue>
                          </SignalDetail>
                          <SignalDetail>
                            <DetailLabel>⏱️ Tempo Monitorado</DetailLabel>
                            <DetailValue style={{color: '#ef4444'}}>
                              {signal.days_monitored} dias (completo)
                            </DetailValue>
                          </SignalDetail>
                          <SignalDetail>
                            <DetailLabel>📅 Confirmado em</DetailLabel>
                            <DetailValue>{signal.confirmed_at}</DetailValue>
                          </SignalDetail>
                        </SignalDetails>
                        
                        {/* Indicador de Expiração */}
                        <div style={{
                          marginTop: '15px',
                          padding: '10px',
                          background: 'rgba(239, 68, 68, 0.1)',
                          borderRadius: '8px',
                          border: '1px solid #ef4444'
                        }}>
                          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                            <span style={{fontSize: '0.9em', color: '#ef4444'}}>
                              ⏰ Sinal expirou após 15 dias sem atingir a meta
                            </span>
                            <span style={{fontWeight: '600', color: '#ef4444'}}>
                              Faltaram {(signal.required_percentage - signal.max_profit_reached).toFixed(1)}%
                            </span>
                          </div>
                        </div>
                      </SignalCard>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </ContentContainer>
    </BTCContainer>
  );
};

export default BTCAnalysisPage;