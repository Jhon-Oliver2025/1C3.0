import React, { useState, useEffect } from 'react';
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
  FaSync
} from 'react-icons/fa';
import logo3 from '/logo3.png';
import '../Dashboard/DashboardMobile.css';

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
}

interface ConfirmedSignal {
  id: string;
  symbol: string;
  type: 'COMPRA' | 'VENDA';
  entry_price: number;
  target_price: number;
  projection_percentage: number;
  quality_score: number;
  signal_class: string;
  created_at: string;
  confirmed_at: string;
  confirmation_reasons: string[];
  confirmation_attempts: number;
  btc_correlation: number;
  btc_trend: string;
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

const LogoContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 15px;
`;

const Logo = styled.img`
  height: 40px;
  width: auto;
`;

const Title = styled.h1`
  color: #f59e0b;
  font-size: 2.5em;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 15px;
  
  @media (max-width: 768px) {
    font-size: 1.5em;
    text-align: center;
    gap: 10px;
  }
  
  @media (max-width: 480px) {
    font-size: 1.2em;
    flex-direction: column;
    gap: 5px;
  }
`;

const BTCIcon = styled(FaBitcoin)`
  color: #f59e0b;
  font-size: 1.2em;
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

const StatsContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
  
  @media (max-width: 768px) {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    margin-bottom: 20px;
  }
  
  @media (max-width: 480px) {
    grid-template-columns: 1fr;
    gap: 10px;
  }
`;

const StatCard = styled.div`
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

const StatIcon = styled.div`
  font-size: 2em;
  color: #f59e0b;
  margin-bottom: 10px;
  
  @media (max-width: 768px) {
    font-size: 1.5em;
    margin-bottom: 8px;
  }
  
  @media (max-width: 480px) {
    font-size: 1.3em;
    margin-bottom: 6px;
  }
`;

const StatValue = styled.div`
  font-size: 2em;
  font-weight: bold;
  color: white;
  margin-bottom: 5px;
  
  @media (max-width: 768px) {
    font-size: 1.5em;
  }
  
  @media (max-width: 480px) {
    font-size: 1.3em;
  }
`;

const StatLabel = styled.div`
  color: #94a3b8;
  font-size: 0.9em;
  
  @media (max-width: 768px) {
    font-size: 0.8em;
  }
  
  @media (max-width: 480px) {
    font-size: 0.75em;
  }
`;

const BTCOverviewCard = styled.div`
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  padding: 25px;
  border-radius: 12px;
  border: 1px solid #f59e0b;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  margin-bottom: 30px;
  
  @media (max-width: 768px) {
    padding: 20px;
    margin-bottom: 20px;
  }
  
  @media (max-width: 480px) {
    padding: 15px;
  }
`;

const BTCPrice = styled.div`
  font-size: 3em;
  font-weight: bold;
  color: #f59e0b;
  margin-bottom: 10px;
  
  @media (max-width: 768px) {
    font-size: 2em;
    text-align: center;
  }
  
  @media (max-width: 480px) {
    font-size: 1.5em;
  }
`;

const BTCChange = styled.div<{ $positive: boolean }>`
  font-size: 1.5em;
  font-weight: 600;
  color: ${props => props.$positive ? '#10b981' : '#ef4444'};
  margin-bottom: 15px;
  
  @media (max-width: 768px) {
    font-size: 1.2em;
    text-align: center;
  }
  
  @media (max-width: 480px) {
    font-size: 1em;
  }
`;

const BTCTrend = styled.div<{ $trend: string }>`
  display: inline-block;
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: 600;
  background: ${props => {
    switch (props.$trend) {
      case 'BULLISH': return '#10b981';
      case 'BEARISH': return '#ef4444';
      default: return '#6b7280';
    }
  }};
  color: white;
`;

const TabContainer = styled.div`
  display: flex;
  margin-bottom: 20px;
  border-bottom: 2px solid #1e293b;
  
  @media (max-width: 768px) {
    overflow-x: auto;
    scrollbar-width: none;
    -ms-overflow-style: none;
    
    &::-webkit-scrollbar {
      display: none;
    }
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
  
  @media (max-width: 768px) {
    padding: 12px 20px;
    font-size: 0.9em;
  }
  
  @media (max-width: 480px) {
    padding: 10px 15px;
    font-size: 0.8em;
  }

  &:hover {
    background: ${props => props.$active ? '#f59e0b' : '#1e293b'};
    color: ${props => props.$active ? 'black' : 'white'};
  }
`;

const ContentContainer = styled.div`
  background: #1e293b;
  border-radius: 12px;
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

const SignalActions = styled.div`
  display: flex;
  gap: 10px;
  margin-top: 15px;
`;

const ActionButton = styled.button<{ $variant?: 'success' | 'danger' | 'info' }>`
  background: ${props => {
    switch (props.$variant) {
      case 'success': return '#10b981';
      case 'danger': return '#ef4444';
      case 'info': return '#3b82f6';
      default: return '#6b7280';
    }
  }};
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
  
  @media (max-width: 768px) {
    padding: 6px 12px;
    font-size: 0.9em;
    gap: 5px;
  }
  
  @media (max-width: 480px) {
    padding: 5px 10px;
    font-size: 0.8em;
    gap: 3px;
  }

  &:hover {
    transform: translateY(-1px);
    opacity: 0.9;
  }

  &:disabled {
    background: #6b7280;
    cursor: not-allowed;
    transform: none;
  }
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

const StrategyExplanation = styled.div`
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  padding: 25px;
  border-radius: 12px;
  border: 1px solid #f59e0b;
  margin-bottom: 30px;
`;

const StrategyTitle = styled.h2`
  color: #f59e0b;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
`;

const StrategyText = styled.p`
  color: #94a3b8;
  line-height: 1.6;
  margin-bottom: 15px;
`;

const StrategyHighlight = styled.span`
  color: #f59e0b;
  font-weight: 600;
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

const RSIBar = styled.div<{ $rsi: number }>`
  width: 100%;
  height: 8px;
  background: #374151;
  border-radius: 4px;
  position: relative;
  margin: 10px 0;
  
  &::after {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    height: 100%;
    width: ${props => props.$rsi}%;
    background: ${props => {
      if (props.$rsi >= 70) return '#ef4444';
      if (props.$rsi <= 30) return '#10b981';
      return '#f59e0b';
    }};
    border-radius: 4px;
    transition: all 0.3s ease;
  }
`;

const TimeframeRow = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #374151;
  
  &:last-child {
    border-bottom: none;
  }
`;

const TimeframeLabel = styled.span`
  color: #94a3b8;
  font-weight: 600;
`;

const TimeframeValue = styled.span<{ $color?: string }>`
  color: ${props => props.$color || 'white'};
  font-weight: 600;
`;

const RangeBar = styled.div<{ $percentage: number }>`
  width: 100%;
  height: 12px;
  background: linear-gradient(90deg, #10b981 0%, #f59e0b 50%, #ef4444 100%);
  border-radius: 6px;
  position: relative;
  margin: 10px 0;
  
  &::after {
    content: '';
    position: absolute;
    left: ${props => props.$percentage}%;
    top: -2px;
    width: 4px;
    height: 16px;
    background: white;
    border-radius: 2px;
    transform: translateX(-50%);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  }
`;

const RefreshControls = styled.div`
  display: flex;
  align-items: center;
  gap: 15px;
  margin-left: auto;
  
  @media (max-width: 768px) {
    gap: 10px;
    margin-left: 0;
    flex-wrap: wrap;
    justify-content: center;
  }
  
  @media (max-width: 480px) {
    gap: 8px;
    flex-direction: column;
    width: 100%;
  }
`;

const AutoRefreshToggle = styled.button<{ $active: boolean }>`
  background: ${props => props.$active 
    ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)' 
    : 'linear-gradient(135deg, #374151 0%, #4b5563 100%)'};
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9em;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  border: 1px solid ${props => props.$active ? '#10b981' : '#6b7280'};
  position: relative;
  overflow: hidden;
  
  @media (max-width: 768px) {
    padding: 8px 12px;
    font-size: 0.8em;
    gap: 5px;
  }
  
  @media (max-width: 480px) {
    padding: 6px 10px;
    font-size: 0.75em;
    width: 100%;
    justify-content: center;
  }

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    transition: left 0.5s;
  }

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    
    &::before {
      left: 100%;
    }
  }

  &:active {
    transform: translateY(0);
  }
`;

const DataFreshnessIndicator = styled.div<{ $freshness: string }>`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 8px;
  background: ${props => {
    switch (props.$freshness) {
      case 'fresh': return 'linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(5, 150, 105, 0.2) 100%)';
      case 'recent': return 'linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(217, 119, 6, 0.2) 100%)';
      case 'aging': return 'linear-gradient(135deg, rgba(249, 115, 22, 0.2) 0%, rgba(234, 88, 12, 0.2) 100%)';
      case 'stale': return 'linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(220, 38, 38, 0.2) 100%)';
      default: return 'linear-gradient(135deg, rgba(107, 114, 128, 0.2) 0%, rgba(75, 85, 99, 0.2) 100%)';
    }
  }};
  border: 1px solid ${props => {
    switch (props.$freshness) {
      case 'fresh': return '#10b981';
      case 'recent': return '#f59e0b';
      case 'aging': return '#f97316';
      case 'stale': return '#ef4444';
      default: return '#6b7280';
    }
  }};
  font-size: 0.85em;
  font-weight: 600;
  color: ${props => {
    switch (props.$freshness) {
      case 'fresh': return '#10b981';
      case 'recent': return '#f59e0b';
      case 'aging': return '#f97316';
      case 'stale': return '#ef4444';
      default: return '#6b7280';
    }
  }};
  transition: all 0.3s ease;
  
  &::before {
    content: '●';
    font-size: 1.2em;
    animation: ${props => props.$freshness === 'fresh' ? 'pulse 2s infinite' : 'none'};
  }
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 8px ${props => {
      switch (props.$freshness) {
        case 'fresh': return 'rgba(16, 185, 129, 0.3)';
        case 'recent': return 'rgba(245, 158, 11, 0.3)';
        case 'aging': return 'rgba(249, 115, 22, 0.3)';
        case 'stale': return 'rgba(239, 68, 68, 0.3)';
        default: return 'rgba(107, 114, 128, 0.3)';
      }
    }};
  }
  
  @keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.7; transform: scale(1.1); }
  }
`;

const NextUpdateTimer = styled.div`
  font-size: 0.8em;
  color: #94a3b8;
  display: flex;
  align-items: center;
  gap: 4px;
`;

// Componente Principal
const BTCAnalysisPage: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'pending' | 'confirmed' | 'rejected' | 'metrics'>('pending');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  
  // Estados dos dados
  const [pendingSignals, setPendingSignals] = useState<PendingSignal[]>([]);
  const [confirmedSignals, setConfirmedSignals] = useState<ConfirmedSignal[]>([]);
  const [rejectedSignals, setRejectedSignals] = useState<RejectedSignal[]>([]);
  const [btcMetrics, setBtcMetrics] = useState<BTCMetrics | null>(null);
  const [btcAnalysis, setBtcAnalysis] = useState<BTCAnalysis | null>(null);
  const [restartSystemInfo, setRestartSystemInfo] = useState<RestartSystemInfo | null>(null);
  
  // Estados para auto-refresh
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [nextUpdate, setNextUpdate] = useState<Date>(new Date());
  const [refreshInterval, setRefreshInterval] = useState<NodeJS.Timeout | null>(null);

  // Verificar autenticação e permissão admin
  useEffect(() => {
    const checkAdminAccess = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login', {
          state: {
            returnUrl: '/btc-analysis',
            message: 'Faça login para acessar a Análise BTC'
          }
        });
        return;
      }

      try {
        // Verificar se o usuário é admin
        const response = await fetch('/api/auth/check-admin', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (response.ok) {
          const data = await response.json();
          if (data.is_admin) {
            // Usuário é admin, carregar dados
            loadData();
          } else {
            // Usuário não é admin, redirecionar para dashboard
            navigate('/dashboard', {
              state: {
                message: 'Acesso negado: Apenas administradores podem acessar a Análise BTC'
              }
            });
          }
        } else {
          // Token inválido ou erro, redirecionar para login
          localStorage.removeItem('token');
          navigate('/login', {
            state: {
              returnUrl: '/btc-analysis',
              message: 'Sessão expirada. Faça login novamente'
            }
          });
        }
      } catch (error) {
        console.error('Erro ao verificar permissão de admin:', error);
        navigate('/dashboard', {
          state: {
            message: 'Erro ao verificar permissões. Tente novamente'
          }
        });
      }
    };

    checkAdminAccess();
  }, [navigate]);

  // Sistema de Auto-Refresh Inteligente
  useEffect(() => {
    if (!autoRefresh) return;

    const setupAutoRefresh = () => {
      // Limpar interval anterior se existir
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }

      // Calcular intervalo baseado na idade dos dados
      const calculateRefreshInterval = () => {
        if (!btcAnalysis) return 30000; // 30s se não há dados
        
        const now = new Date();
        const lastBtcUpdate = new Date(btcAnalysis.last_updated);
        const dataAge = now.getTime() - lastBtcUpdate.getTime();
        
        // Refresh mais frequente para dados mais antigos
        if (dataAge > 300000) return 15000; // 15s se dados > 5min
        if (dataAge > 120000) return 30000; // 30s se dados > 2min
        if (dataAge > 60000) return 45000;  // 45s se dados > 1min
        return 60000; // 1min para dados recentes
      };

      const interval = calculateRefreshInterval();
      setNextUpdate(new Date(Date.now() + interval));

      const newInterval = setInterval(async () => {
        try {
          await loadData();
          setLastUpdate(new Date());
        } catch (error) {
          console.error('Erro no auto-refresh:', error);
        }
      }, interval);

      setRefreshInterval(newInterval);
    };

    setupAutoRefresh();

    // Cleanup
    return () => {
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }
    };
  }, [autoRefresh, btcAnalysis?.last_updated]);

  const loadData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        loadPendingSignals(),
        loadConfirmedSignals(),
        loadRejectedSignals(),
        loadBTCMetrics(),
        loadRestartSystemInfo()
      ]);
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadRestartSystemInfo = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/restart-system/status', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setRestartSystemInfo(data.data);
      }
    } catch (error) {
      console.error('Erro ao carregar informações do sistema de restart:', error);
    }
  };

  const loadPendingSignals = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/btc-signals/pending', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setPendingSignals(data.data.pending_signals || []);
      }
    } catch (error) {
      console.error('Erro ao carregar sinais pendentes:', error);
    }
  };

  const loadRejectedSignals = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/btc-signals/rejected?limit=20', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setRejectedSignals(data.data.rejected_signals || []);
      }
    } catch (error) {
      console.error('Erro ao carregar sinais rejeitados:', error);
    }
  };

  const loadConfirmedSignals = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/btc-signals/confirmed?limit=20', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setConfirmedSignals(data.data.confirmed_signals || []);
      }
    } catch (error) {
      console.error('Erro ao carregar sinais confirmados:', error);
    }
  };

  const loadBTCMetrics = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/btc-signals/metrics', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setBtcMetrics(data.data.confirmation_metrics);
        
        // Combinar dados de btc_analysis e btc_price_data
        const btcAnalysisData = data.data.btc_analysis;
        const btcPriceData = data.data.btc_price_data;
        
        const combinedBtcData = {
          trend: btcAnalysisData?.trend || 'NEUTRAL',
          strength: btcAnalysisData?.strength || 50,
          price: btcPriceData?.price || 0,
          change_24h: btcPriceData?.change_24h || 0,
          volume_24h: btcPriceData?.volume_24h || 0,
          high_24h: btcPriceData?.high_24h || 0,
          low_24h: btcPriceData?.low_24h || 0,
          last_updated: btcPriceData?.last_updated || '',
          volatility: btcAnalysisData?.volatility || 0,
          timeframes: btcAnalysisData?.timeframes || {
            '1h': {
              rsi: 50,
              rsi_condition: 'NEUTRAL',
              macd_bullish: false,
              macd_bearish: false,
              ema20: 0,
              ema50: 0,
              ema_alignment: false,
              atr: 0,
              atr_percentage: 0,
              volatility_level: 'LOW',
              trend: 'NEUTRAL',
              strength: 50,
              momentum_aligned: false,
              pivot_broken: false,
              timestamp: ''
            },
            '4h': {
              rsi: 50,
              rsi_condition: 'NEUTRAL',
              macd_bullish: false,
              macd_bearish: false,
              ema20: 0,
              ema50: 0,
              ema_alignment: false,
              atr: 0,
              atr_percentage: 0,
              volatility_level: 'LOW',
              trend: 'NEUTRAL',
              strength: 50,
              momentum_aligned: false,
              pivot_broken: false,
              timestamp: ''
            }
          }
        };
        
        setBtcAnalysis(combinedBtcData);
      }
    } catch (error) {
      console.error('Erro ao carregar métricas BTC:', error);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  };

  const handleConfirmSignal = async (signalId: string) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/btc-signals/confirm/${signalId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        await loadData(); // Recarregar dados
        alert('Sinal confirmado com sucesso!');
      } else {
        const error = await response.json();
        alert(`Erro ao confirmar sinal: ${error.message}`);
      }
    } catch (error) {
      console.error('Erro ao confirmar sinal:', error);
      alert('Erro ao confirmar sinal');
    }
  };

  const handleRejectSignal = async (signalId: string) => {
    const reason = prompt('Motivo da rejeição (opcional):');
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/btc-signals/reject/${signalId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ reason: reason || 'MANUAL_REJECTION_BY_ADMIN' })
      });
      
      if (response.ok) {
        await loadData(); // Recarregar dados
        alert('Sinal rejeitado com sucesso!');
      } else {
        const error = await response.json();
        alert(`Erro ao rejeitar sinal: ${error.message}`);
      }
    } catch (error) {
      console.error('Erro ao rejeitar sinal:', error);
      alert('Erro ao rejeitar sinal');
    }
  };

  const formatPrice = (price: number | null | undefined) => {
    if (price === null || price === undefined || isNaN(price)) {
      return '$0.00';
    }
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 8
    }).format(price);
  };

  const formatPercentage = (value: number | null | undefined) => {
    if (value === null || value === undefined || isNaN(value)) {
      return '+0.00%';
    }
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  const formatVolume = (volume: number | null | undefined) => {
    if (volume === null || volume === undefined || isNaN(volume)) {
      return '$0.00B';
    }
    // Volume vem em BTC, converter para bilhões de dólares
    // Assumindo preço médio do BTC ~$117,000
    const volumeInDollars = volume * 117000; // volume em BTC * preço BTC
    const volumeInBillions = volumeInDollars / 1000000000;
    return `$${volumeInBillions.toFixed(2)}B`;
  };

  const formatStrength = (strength: number | null | undefined) => {
    if (strength === null || strength === undefined || isNaN(strength)) {
      return '50';
    }
    // Strength já vem como porcentagem (50.0), não multiplicar por 100
    return strength.toFixed(0);
  };

  const formatRSI = (rsi: number | null | undefined) => {
    if (rsi === null || rsi === undefined || isNaN(rsi)) {
      return '50.0';
    }
    return rsi.toFixed(1);
  };

  const getRSIColor = (rsi: number) => {
    if (rsi >= 70) return '#ef4444'; // Overbought - Red
    if (rsi <= 30) return '#10b981'; // Oversold - Green
    return '#f59e0b'; // Neutral - Orange
  };

  const getRSIBars = (rsi: number) => {
    const bars = Math.round(rsi / 20); // 0-100 -> 0-5 bars
    return '●'.repeat(Math.max(1, bars)) + '○'.repeat(Math.max(0, 5 - bars));
  };

  const formatMACD = (bullish: boolean, bearish: boolean) => {
    if (bullish) return '↑ Bullish';
    if (bearish) return '↓ Bearish';
    return '⚖️ Neutral';
  };

  const getVolatilityColor = (level: string) => {
    switch (level) {
      case 'HIGH': return '#ef4444';
      case 'MEDIUM': return '#f59e0b';
      case 'LOW': return '#10b981';
      default: return '#6b7280';
    }
  };

  const formatRange24h = (high: number, low: number, current: number) => {
    if (!high || !low || !current) return '0.00%';
    const range = high - low;
    const position = current - low;
    const percentage = (position / range) * 100;
    return percentage.toFixed(1) + '%';
  };

  const formatTimeAgo = (dateString: string) => {
    if (!dateString || dateString === '' || dateString === 'null' || dateString === 'undefined') {
      return 'Nunca atualizado';
    }
    
    try {
      // Verificar se já está no formato brasileiro
      const brazilianDateRegex = /^\d{2}\/\d{2}\/\d{4} \d{2}:\d{2}:\d{2}$/;
      if (brazilianDateRegex.test(dateString)) {
        const [datePart, timePart] = dateString.split(' ');
        const [day, month, year] = datePart.split('/');
        const date = new Date(`${year}-${month}-${day}T${timePart}`);
        
        if (isNaN(date.getTime())) {
          return 'Formato inválido';
        }
        
        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
        const diffSec = Math.floor(diffMs / 1000);
        const diffMin = Math.floor(diffSec / 60);
        const diffHour = Math.floor(diffMin / 60);
        
        if (diffSec < 60) return `${diffSec}s atrás`;
        if (diffMin < 60) return `${diffMin}m atrás`;
        if (diffHour < 24) return `${diffHour}h atrás`;
        return date.toLocaleDateString('pt-BR');
      }
      
      // Tentar formato ISO
      const date = new Date(dateString);
      if (isNaN(date.getTime())) {
        return 'Data inválida';
      }
      
      const now = new Date();
      const diffMs = now.getTime() - date.getTime();
      const diffSec = Math.floor(diffMs / 1000);
      const diffMin = Math.floor(diffSec / 60);
      const diffHour = Math.floor(diffMin / 60);
      
      if (diffSec < 60) return `${diffSec}s atrás`;
      if (diffMin < 60) return `${diffMin}m atrás`;
      if (diffHour < 24) return `${diffHour}h atrás`;
      return date.toLocaleDateString('pt-BR');
    } catch (error) {
      console.error('Erro ao formatar data:', error, 'String:', dateString);
      return 'Erro na data';
    }
  };

  const getDataFreshness = (dateString: string) => {
    if (!dateString || dateString === '' || dateString === 'null' || dateString === 'undefined') {
      return 'stale';
    }
    
    try {
      let date: Date;
      
      // Verificar se já está no formato brasileiro
      const brazilianDateRegex = /^\d{2}\/\d{2}\/\d{4} \d{2}:\d{2}:\d{2}$/;
      if (brazilianDateRegex.test(dateString)) {
        const [datePart, timePart] = dateString.split(' ');
        const [day, month, year] = datePart.split('/');
        date = new Date(`${year}-${month}-${day}T${timePart}`);
      } else {
        // Tentar formato ISO
        date = new Date(dateString);
      }
      
      if (isNaN(date.getTime())) {
        console.warn('Data inválida para getDataFreshness:', dateString);
        return 'stale';
      }
      
      const now = new Date();
      const diffMs = now.getTime() - date.getTime();
      
      // Debug para entender o problema
      console.log('getDataFreshness debug:', {
        dateString,
        parsedDate: date.toISOString(),
        now: now.toISOString(),
        diffMs,
        diffSeconds: Math.floor(diffMs / 1000)
      });
      
      if (diffMs < 60000) return 'fresh';     // < 1min
      if (diffMs < 300000) return 'recent';   // < 5min
      if (diffMs < 900000) return 'aging';    // < 15min
      return 'stale';                         // > 15min
    } catch (error) {
      console.error('Erro em getDataFreshness:', error, 'String:', dateString);
      return 'stale';
    }
  };

  const getFreshnessColor = (freshness: string) => {
    switch (freshness) {
      case 'fresh': return '#10b981';   // Verde
      case 'recent': return '#f59e0b';  // Laranja
      case 'aging': return '#f97316';   // Laranja escuro
      case 'stale': return '#ef4444';   // Vermelho
      default: return '#6b7280';        // Cinza
    }
  };

  const toggleAutoRefresh = () => {
    setAutoRefresh(!autoRefresh);
  };

  const formatDateTime = (dateString: string | null | undefined) => {
    // Verificar se a string de data é válida
    if (!dateString || dateString === '' || dateString === 'null' || dateString === 'undefined') {
      return 'Data não disponível';
    }
    
    try {
      // Se a data já está no formato brasileiro (dd/mm/aaaa hh:mm:ss), retornar diretamente
      const brazilianDateRegex = /^\d{2}\/\d{2}\/\d{4} \d{2}:\d{2}:\d{2}$/;
      if (brazilianDateRegex.test(dateString)) {
        return dateString;
      }
      
      // Tentar converter outros formatos
      const date = new Date(dateString);
      
      // Verificar se a data é válida
      if (isNaN(date.getTime())) {
        console.warn('Data inválida recebida:', dateString);
        return 'Data inválida';
      }
      
      return date.toLocaleString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
    } catch (error) {
      console.error('Erro ao formatar data:', error, 'String recebida:', dateString);
      return 'Erro na data';
    }
  };

  if (loading) {
    return (
      <BTCContainer>
        <LoadingSpinner>
          <FaHourglassHalf /> Carregando dados BTC...
        </LoadingSpinner>
      </BTCContainer>
    );
  }

  return (
    <BTCContainer>
      {/* CONTAINER MOTIVACIONAL NO TOPO DA DIV PRINCIPAL (4px) */}
      <div className="mobile-motivation-header-container">
        {/* Seção Motivacional */}
        <div className="mobile-motivational">
          <p className="mobile-motivational-text">
            Analise o Bitcoin com precisão e confirme sinais que geram resultados.
          </p>
        </div>

        {/* Espaçamento de Segurança (4px) */}
        <div className="mobile-safety-gap"></div>
      </div>

      {/* CONTEÚDO DA PÁGINA BTC ANALYSIS */}
      <Header>
        <Title>
          <BTCIcon />
          Análise BTC & Confirmação de Sinais
        </Title>
        <RefreshControls>
          {btcAnalysis && (
            <DataFreshnessIndicator $freshness={getDataFreshness(btcAnalysis.last_updated)}>
              {formatTimeAgo(btcAnalysis.last_updated)}
            </DataFreshnessIndicator>
          )}
          
          <AutoRefreshToggle $active={autoRefresh} onClick={toggleAutoRefresh}>
            {autoRefresh ? '🔄' : '⏸️'} Auto
          </AutoRefreshToggle>
          
          <RefreshButton onClick={handleRefresh} disabled={refreshing}>
            <FaSync /> {refreshing ? 'Atualizando...' : 'Atualizar'}
          </RefreshButton>
        </RefreshControls>
      </Header>

      {/* BTC Overview */}
      {btcAnalysis && (
        <BTCOverviewCard>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <BTCPrice>{formatPrice(btcAnalysis.price)}</BTCPrice>
              <BTCChange $positive={(btcAnalysis.change_24h || 0) >= 0}>
                {formatPercentage(btcAnalysis.change_24h)} (24h)
              </BTCChange>
              <BTCTrend $trend={btcAnalysis.trend || 'NEUTRAL'}>
                {btcAnalysis.trend || 'NEUTRAL'} - Força: {formatStrength(btcAnalysis.strength)}%
              </BTCTrend>
            </div>
            <div style={{ textAlign: 'right' }}>
              <StatLabel>Volume 24h</StatLabel>
              <StatValue style={{ fontSize: '1.5em' }}>
                {formatVolume(btcAnalysis.volume_24h)}
              </StatValue>
            </div>
          </div>
        </BTCOverviewCard>
      )}

      {/* Cards Técnicos Avançados */}
      {btcAnalysis && btcAnalysis.timeframes && (
        <TechnicalGrid>
          {/* Card RSI */}
          <TechnicalCard>
            <TechnicalTitle>
              📊 RSI (Força Relativa)
            </TechnicalTitle>
            <TechnicalValue $color={getRSIColor(btcAnalysis.timeframes['1h'].rsi)}>
              {formatRSI(btcAnalysis.timeframes['1h'].rsi)}
            </TechnicalValue>
            <TechnicalSubtext>1h: {btcAnalysis.timeframes['1h'].rsi_condition}</TechnicalSubtext>
            <RSIBar $rsi={btcAnalysis.timeframes['1h'].rsi} />
            <TimeframeRow>
              <TimeframeLabel>4h:</TimeframeLabel>
              <TimeframeValue $color={getRSIColor(btcAnalysis.timeframes['4h'].rsi)}>
                {formatRSI(btcAnalysis.timeframes['4h'].rsi)} ({btcAnalysis.timeframes['4h'].rsi_condition})
              </TimeframeValue>
            </TimeframeRow>
          </TechnicalCard>

          {/* Card MACD */}
          <TechnicalCard>
            <TechnicalTitle>
              📈 MACD (Convergência)
            </TechnicalTitle>
            <TechnicalValue>
              Multi-Timeframe
            </TechnicalValue>
            <TimeframeRow>
              <TimeframeLabel>1h:</TimeframeLabel>
              <TimeframeValue $color={btcAnalysis.timeframes['1h'].macd_bullish ? '#10b981' : '#ef4444'}>
                {formatMACD(btcAnalysis.timeframes['1h'].macd_bullish, btcAnalysis.timeframes['1h'].macd_bearish)}
              </TimeframeValue>
            </TimeframeRow>
            <TimeframeRow>
              <TimeframeLabel>4h:</TimeframeLabel>
              <TimeframeValue $color={btcAnalysis.timeframes['4h'].macd_bullish ? '#10b981' : '#ef4444'}>
                {formatMACD(btcAnalysis.timeframes['4h'].macd_bullish, btcAnalysis.timeframes['4h'].macd_bearish)}
              </TimeframeValue>
            </TimeframeRow>
            {btcAnalysis.timeframes['1h'].macd_bullish !== btcAnalysis.timeframes['4h'].macd_bullish && (
              <TechnicalSubtext style={{color: '#f59e0b', fontWeight: 'bold'}}>⚠️ Divergência detectada</TechnicalSubtext>
            )}
          </TechnicalCard>

          {/* Card Volatilidade */}
          <TechnicalCard>
            <TechnicalTitle>
              💥 Volatilidade (ATR)
            </TechnicalTitle>
            <TechnicalValue $color={getVolatilityColor(btcAnalysis.timeframes['1h'].volatility_level)}>
              {btcAnalysis.timeframes['1h'].volatility_level}
            </TechnicalValue>
            <TechnicalSubtext>ATR 1h: {btcAnalysis.timeframes['1h'].atr_percentage.toFixed(2)}%</TechnicalSubtext>
            <TimeframeRow>
              <TimeframeLabel>4h:</TimeframeLabel>
              <TimeframeValue $color={getVolatilityColor(btcAnalysis.timeframes['4h'].volatility_level)}>
                {btcAnalysis.timeframes['4h'].volatility_level} ({btcAnalysis.timeframes['4h'].atr_percentage.toFixed(2)}%)
              </TimeframeValue>
            </TimeframeRow>
          </TechnicalCard>

          {/* Card Range 24h */}
          <TechnicalCard>
            <TechnicalTitle>
              📊 Range 24h
            </TechnicalTitle>
            <TechnicalValue>
              {formatPrice(btcAnalysis.high_24h)} - {formatPrice(btcAnalysis.low_24h)}
            </TechnicalValue>
            <TechnicalSubtext>
              Posição atual: {formatRange24h(btcAnalysis.high_24h, btcAnalysis.low_24h, btcAnalysis.price)}
            </TechnicalSubtext>
            <RangeBar $percentage={parseFloat(formatRange24h(btcAnalysis.high_24h, btcAnalysis.low_24h, btcAnalysis.price))} />
            <TechnicalSubtext>
              Amplitude: {formatPrice(btcAnalysis.high_24h - btcAnalysis.low_24h)} ({formatPercentage((btcAnalysis.high_24h - btcAnalysis.low_24h) / btcAnalysis.low_24h * 100)})
            </TechnicalSubtext>
          </TechnicalCard>

          {/* Card EMAs */}
          <TechnicalCard>
            <TechnicalTitle>
              📈 Médias Móveis (EMA)
            </TechnicalTitle>
            <TechnicalValue>
              {btcAnalysis.timeframes['1h'].ema_alignment ? '✅ Alinhadas' : '❌ Não Alinhadas'}
            </TechnicalValue>
            <TimeframeRow>
              <TimeframeLabel>EMA 20 (1h):</TimeframeLabel>
              <TimeframeValue>
                {formatPrice(btcAnalysis.timeframes['1h'].ema20)}
              </TimeframeValue>
            </TimeframeRow>
            <TimeframeRow>
              <TimeframeLabel>EMA 50 (1h):</TimeframeLabel>
              <TimeframeValue>
                {formatPrice(btcAnalysis.timeframes['1h'].ema50)}
              </TimeframeValue>
            </TimeframeRow>
            <TechnicalSubtext>
              4h: {btcAnalysis.timeframes['4h'].ema_alignment ? 'Alinhadas' : 'Não Alinhadas'}
            </TechnicalSubtext>
          </TechnicalCard>

          {/* Card Status de Atualização */}
          <TechnicalCard>
            <TechnicalTitle>
              ⏰ Status de Atualização
            </TechnicalTitle>
            <TechnicalValue $color={getFreshnessColor(getDataFreshness(btcAnalysis.last_updated))} style={{fontSize: '1.2em'}}>
              {formatTimeAgo(btcAnalysis.last_updated)}
            </TechnicalValue>
            <TechnicalSubtext>
              {autoRefresh ? '🔄 Auto-refresh ativo' : '⏸️ Auto-refresh pausado'}
            </TechnicalSubtext>
            
            <TimeframeRow>
              <TimeframeLabel>Dados Gerais:</TimeframeLabel>
              <TimeframeValue $color={getFreshnessColor(getDataFreshness(btcAnalysis.last_updated))}>
                {getDataFreshness(btcAnalysis.last_updated) === 'fresh' ? '🟢 Atuais' : 
                 getDataFreshness(btcAnalysis.last_updated) === 'recent' ? '🟡 Recentes' :
                 getDataFreshness(btcAnalysis.last_updated) === 'aging' ? '🟠 Envelhecendo' : '🔴 Desatualizados'}
              </TimeframeValue>
            </TimeframeRow>
            
            <TimeframeRow>
              <TimeframeLabel>Timeframe 1h:</TimeframeLabel>
              <TimeframeValue $color={getFreshnessColor(getDataFreshness(btcAnalysis.timeframes['1h'].timestamp))}>
                {formatTimeAgo(btcAnalysis.timeframes['1h'].timestamp)}
              </TimeframeValue>
            </TimeframeRow>
            
            <TimeframeRow>
              <TimeframeLabel>Timeframe 4h:</TimeframeLabel>
              <TimeframeValue $color={getFreshnessColor(getDataFreshness(btcAnalysis.timeframes['4h'].timestamp))}>
                {formatTimeAgo(btcAnalysis.timeframes['4h'].timestamp)}
              </TimeframeValue>
            </TimeframeRow>
            
            {autoRefresh && (
              <TechnicalSubtext style={{marginTop: '10px', color: '#10b981'}}>
                📡 Próxima atualização automática em breve
              </TechnicalSubtext>
            )}
          </TechnicalCard>

          {/* Card de Restart System */}
          {restartSystemInfo && (
            <TechnicalCard>
              <TechnicalTitle>
                <FaCog /> 🔄 Sistema de Restart
              </TechnicalTitle>
              
              <TechnicalValue $color="#f59e0b">
                {String(restartSystemInfo.restart_info.countdown.hours).padStart(2, '0')}:
                {String(restartSystemInfo.restart_info.countdown.minutes).padStart(2, '0')}:
                {String(restartSystemInfo.restart_info.countdown.seconds).padStart(2, '0')}
              </TechnicalValue>
              
              <TechnicalSubtext>
                Próximo restart às 21:00 (SP)
              </TechnicalSubtext>
              
              <TimeframeRow>
                <TimeframeLabel>Uptime Sistema:</TimeframeLabel>
                <TimeframeValue $color="#10b981">
                  {restartSystemInfo.system_uptime.hours}h {restartSystemInfo.system_uptime.minutes}m
                </TimeframeValue>
              </TimeframeRow>
              
              <TimeframeRow>
                <TimeframeLabel>Sistema BTC:</TimeframeLabel>
                <TimeframeValue $color={restartSystemInfo.btc_system.status === 'active' ? '#10b981' : '#ef4444'}>
                  {restartSystemInfo.btc_system.status === 'active' ? '🟢 Ativo' : '🔴 Inativo'}
                </TimeframeValue>
              </TimeframeRow>
              
              <TimeframeRow>
                <TimeframeLabel>Último Restart:</TimeframeLabel>
                <TimeframeValue>
                  {restartSystemInfo.system_uptime.last_restart}
                </TimeframeValue>
              </TimeframeRow>
              
              <TechnicalSubtext style={{marginTop: '10px', fontSize: '0.8em'}}>
                🧹 Limpeza automática de sinais<br/>
                ₿ Reset do sistema BTC<br/>
                📊 Atualização de estatísticas
              </TechnicalSubtext>
            </TechnicalCard>
          )}
        </TechnicalGrid>
      )}

      {/* Estratégia Explicativa */}
      <StrategyExplanation>
        <StrategyTitle>
          <FaChartLine /> Nossa Estratégia de Confirmação BTC
        </StrategyTitle>
        <StrategyText>
          O sistema de <StrategyHighlight>confirmação inteligente</StrategyHighlight> analisa cada sinal técnico 
          detectado e aguarda confirmação de movimento antes de enviá-lo para o dashboard principal.
        </StrategyText>
        <StrategyText>
          <StrategyHighlight>Critérios de Confirmação:</StrategyHighlight> Rompimento efetivo (0.5%+), 
          aumento de volume (20%+), alinhamento com BTC, e sustentação do momentum por 2+ candles.
        </StrategyText>
        <StrategyText>
          <StrategyHighlight>Vantagem:</StrategyHighlight> Reduz sinais falsos em 40-50% e melhora 
          a precisão geral do sistema, especialmente em operações com alta alavancagem.
        </StrategyText>
      </StrategyExplanation>

      {/* Métricas */}
      {btcMetrics && (
        <StatsContainer>
          <StatCard>
            <StatIcon><FaHourglassHalf /></StatIcon>
            <StatValue>{btcMetrics.pending_signals}</StatValue>
            <StatLabel>Sinais Pendentes</StatLabel>
          </StatCard>
          <StatCard>
            <StatIcon><FaCheckCircle /></StatIcon>
            <StatValue>{btcMetrics.confirmed_signals}</StatValue>
            <StatLabel>Sinais Confirmados</StatLabel>
          </StatCard>
          <StatCard>
            <StatIcon><FaTimesCircle /></StatIcon>
            <StatValue>{btcMetrics.rejected_signals}</StatValue>
            <StatLabel>Sinais Rejeitados</StatLabel>
          </StatCard>
          <StatCard>
            <StatIcon><FaChartLine /></StatIcon>
            <StatValue>{btcMetrics.confirmation_rate.toFixed(1)}%</StatValue>
            <StatLabel>Taxa de Confirmação</StatLabel>
          </StatCard>
          <StatCard>
            <StatIcon><FaClock /></StatIcon>
            <StatValue>{btcMetrics.average_confirmation_time_minutes.toFixed(1)}min</StatValue>
            <StatLabel>Tempo Médio</StatLabel>
          </StatCard>
        </StatsContainer>
      )}

      {/* Tabs */}
      <TabContainer>
        <Tab 
          $active={activeTab === 'pending'} 
          onClick={() => setActiveTab('pending')}
        >
          Sinais Pendentes ({pendingSignals.length})
        </Tab>
        <Tab 
          $active={activeTab === 'confirmed'} 
          onClick={() => setActiveTab('confirmed')}
        >
          Sinais Confirmados ({confirmedSignals.length})
        </Tab>
        <Tab 
          $active={activeTab === 'rejected'} 
          onClick={() => setActiveTab('rejected')}
        >
          Sinais Rejeitados ({rejectedSignals.length})
        </Tab>
      </TabContainer>

      {/* Conteúdo das Tabs */}
      <ContentContainer>
        {activeTab === 'pending' && (
          <div>
            {pendingSignals.length === 0 ? (
              <EmptyState>
                <EmptyIcon><FaHourglassHalf /></EmptyIcon>
                <div>Nenhum sinal aguardando confirmação</div>
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
                      <DetailLabel>Projeção</DetailLabel>
                      <DetailValue>{formatPercentage(signal.projection_percentage)}</DetailValue>
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
                      <DetailValue>{signal.confirmation_attempts}/12</DetailValue>
                    </SignalDetail>
                    <SignalDetail>
                      <DetailLabel>BTC Correlação</DetailLabel>
                      <DetailValue>{signal.btc_correlation.toFixed(2)} ({signal.btc_trend})</DetailValue>
                    </SignalDetail>
                  </SignalDetails>
                  
                  <SignalActions>
                    <ActionButton 
                      $variant="success" 
                      onClick={() => handleConfirmSignal(signal.id)}
                    >
                      <FaThumbsUp /> Confirmar
                    </ActionButton>
                    <ActionButton 
                      $variant="danger" 
                      onClick={() => handleRejectSignal(signal.id)}
                    >
                      <FaThumbsDown /> Rejeitar
                    </ActionButton>
                  </SignalActions>
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
                      <DetailValue>{formatPrice(signal.target_price)}</DetailValue>
                    </SignalDetail>
                    <SignalDetail>
                      <DetailLabel>Projeção</DetailLabel>
                      <DetailValue>{formatPercentage(signal.projection_percentage)}</DetailValue>
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
                      <DetailLabel>Confirmado em</DetailLabel>
                      <DetailValue>{formatDateTime(signal.confirmed_at)}</DetailValue>
                    </SignalDetail>
                    <SignalDetail>
                      <DetailLabel>Tentativas</DetailLabel>
                      <DetailValue>{signal.confirmation_attempts}</DetailValue>
                    </SignalDetail>
                    <SignalDetail>
                      <DetailLabel>BTC Correlação</DetailLabel>
                      <DetailValue>{signal.btc_correlation.toFixed(2)} ({signal.btc_trend})</DetailValue>
                    </SignalDetail>
                    <SignalDetail>
                      <DetailLabel>Motivos</DetailLabel>
                      <DetailValue>{signal.confirmation_reasons.join(', ')}</DetailValue>
                    </SignalDetail>
                  </SignalDetails>
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
                      <DetailLabel>Motivos</DetailLabel>
                      <DetailValue>{signal.rejection_reasons.join(', ')}</DetailValue>
                    </SignalDetail>
                  </SignalDetails>
                </SignalCard>
              ))
            )}
          </div>
        )}
      </ContentContainer>
    </BTCContainer>
  );
};

export default BTCAnalysisPage;