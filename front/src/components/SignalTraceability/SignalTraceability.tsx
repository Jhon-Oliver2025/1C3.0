import React, { useState } from 'react';
import styled from 'styled-components';
import {
  FaChevronDown,
  FaChevronUp,
  FaClock,
  FaCheckCircle,
  FaTimesCircle,
  FaInfoCircle,
  FaChartLine,
  FaVolumeUp,
  FaBitcoin,
  FaArrowUp,
  FaEye,
  FaLightbulb,
  FaTrophy,
  FaExclamationTriangle
} from 'react-icons/fa';

/**
 * Interface para dados de rastreabilidade de sinais
 */
interface GenerationReasons {
  timestamp: string;
  symbol: string;
  signal_type: string;
  technical_scores: {
    trend_score: number;
    entry_score: number;
    rsi_score: number;
    pattern_score: number;
    base_total: number;
  };
  key_indicators: {
    rsi_value: number;
    rsi_zone: string;
    trend_strength: number;
    volume_ratio: number;
    macd_signal: number;
    price_change: number;
  };
  trigger_conditions: string[];
  ranking_info: {
    coin: string;
    position: number | null;
    tier: string;
    description: string;
    bonus_applied: number;
  };
  quality_breakdown: {
    base_score: number;
    ranking_bonus: number;
    final_score: number;
    classification: string;
    threshold_passed: boolean;
  };
  market_context: {
    timeframe_trend: string;
    timeframe_entry: string;
    btc_trend: string;
    market_session: string;
  };
}

interface ConfirmationCheck {
  timestamp: string;
  attempt_number: number;
  time_since_creation: number;
  market_conditions: {
    symbol_price: number;
    symbol_volume_24h: number;
    price_change_24h: number;
    btc_trend: string;
    btc_strength: number;
    btc_volatility: number;
  };
  detailed_checks: {
    price_breakout: {
      confirmed: boolean;
      rejected: boolean;
      percentage: number;
      required: number;
    };
    volume_confirmation: {
      confirmed: boolean;
      rejected: boolean;
      ratio: number;
      required: number;
    };
    btc_alignment: {
      confirmed: boolean;
      rejected: boolean;
      alignment_score: number;
      threshold: number;
    };
    momentum_sustainability: {
      confirmed: boolean;
      rejected: boolean;
      candles_count: number;
      required: number;
    };
  };
  verification_summary: {
    confirmations_found: string[];
    rejections_found: string[];
    confirmations_count: number;
    rejections_count: number;
    status: string;
  };
  next_steps: {
    action_recommended: string;
    time_to_next_check: number;
    attempts_remaining: number;
  };
}

interface FinalDecisionReason {
  decision: string;
  timestamp: string;
  total_processing_time_minutes: number;
  primary_reasons: string[];
  decisive_factors: string[];
  market_snapshot: {
    symbol_price: number;
    price_change_from_entry: number;
    volume_24h: number;
    btc_trend: string;
    btc_strength: number;
    market_session: string;
  };
  confirmation_stats: {
    total_attempts: number;
    verification_history_summary: any;
    average_time_between_checks: number;
    final_quality_assessment: string;
  };
  performance_prediction?: {
    estimated_success_probability: number;
    risk_level: string;
    expected_timeframe: string;
  };
  lessons_learned: string[];
  additional_context: {
    signal_generation_quality: number;
    signal_class: string;
    btc_correlation: number;
    ranking_info: any;
  };
}

interface SignalTraceabilityProps {
  signal: {
    id: string;
    symbol: string;
    type: string;
    status: string;
    generation_reasons?: GenerationReasons;
    confirmation_checks?: ConfirmationCheck[];
    final_decision_reason?: FinalDecisionReason;
  };
}

/**
 * Componente para exibir rastreabilidade completa de sinais
 * Mostra motivos de geração, histórico de verificações e decisão final
 */
const SignalTraceability: React.FC<SignalTraceabilityProps> = ({ signal }) => {
  const [expandedSections, setExpandedSections] = useState<{
    generation: boolean;
    verification: boolean;
    decision: boolean;
  }>({ generation: false, verification: false, decision: false });

  const toggleSection = (section: 'generation' | 'verification' | 'decision') => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('pt-BR');
  };

  const getStatusColor = (status: string) => {
    if (!status) return '#94a3b8';
    switch (status.toLowerCase()) {
      case 'confirmed': return '#10b981';
      case 'rejected': return '#ef4444';
      case 'pending': return '#f59e0b';
      case 'expired': return '#6b7280';
      default: return '#94a3b8';
    }
  };

  const getRiskLevelColor = (level: string) => {
    switch (level?.toLowerCase()) {
      case 'low': return '#10b981';
      case 'medium': return '#f59e0b';
      case 'high': return '#ef4444';
      default: return '#94a3b8';
    }
  };

  return (
    <TraceabilityContainer>
      <TraceabilityHeader>
        <HeaderTitle>
          <FaEye /> Rastreabilidade do Sinal
        </HeaderTitle>
        <StatusBadge $color={getStatusColor(signal.status)}>
          {signal.status?.toUpperCase() || 'UNKNOWN'}
        </StatusBadge>
      </TraceabilityHeader>

      {/* Seção: Por que foi gerado */}
      {signal.generation_reasons && (
        <TraceabilitySection>
          <SectionHeader onClick={() => toggleSection('generation')}>
            <SectionTitle>
              <FaChartLine /> Por que foi gerado?
              <ScoreBadge>
                {signal.generation_reasons.quality_breakdown?.final_score?.toFixed(0) || 'N/A'} pts
              </ScoreBadge>
            </SectionTitle>
            {expandedSections.generation ? <FaChevronUp /> : <FaChevronDown />}
          </SectionHeader>
          
          {expandedSections.generation && (
            <SectionContent>
              {/* Pontuação Técnica */}
              <SubSection>
                <SubSectionTitle>📊 Pontuação Técnica</SubSectionTitle>
                <ScoreGrid>
                  <ScoreItem>
                    <ScoreLabel>Tendência</ScoreLabel>
                    <ScoreValue>{signal.generation_reasons.technical_scores?.trend_score || 0}/35</ScoreValue>
                  </ScoreItem>
                  <ScoreItem>
                    <ScoreLabel>Entrada</ScoreLabel>
                    <ScoreValue>{signal.generation_reasons.technical_scores?.entry_score || 0}/25</ScoreValue>
                  </ScoreItem>
                  <ScoreItem>
                    <ScoreLabel>RSI</ScoreLabel>
                    <ScoreValue>{signal.generation_reasons.technical_scores?.rsi_score || 0}/20</ScoreValue>
                  </ScoreItem>
                  <ScoreItem>
                    <ScoreLabel>Padrões</ScoreLabel>
                    <ScoreValue>{signal.generation_reasons.technical_scores?.pattern_score || 0}/20</ScoreValue>
                  </ScoreItem>
                </ScoreGrid>
              </SubSection>

              {/* Indicadores Chave */}
              <SubSection>
                <SubSectionTitle>🎯 Indicadores Chave</SubSectionTitle>
                <IndicatorGrid>
                  <IndicatorItem>
                    <IndicatorLabel>RSI</IndicatorLabel>
                    <IndicatorValue>
                      {signal.generation_reasons.key_indicators?.rsi_value?.toFixed(0) || 'N/A'} 
                      ({signal.generation_reasons.key_indicators?.rsi_zone || 'N/A'})
                    </IndicatorValue>
                  </IndicatorItem>
                  <IndicatorItem>
                    <IndicatorLabel>Volume</IndicatorLabel>
                    <IndicatorValue>
                      {signal.generation_reasons.key_indicators?.volume_ratio?.toFixed(1) || 'N/A'}x média
                    </IndicatorValue>
                  </IndicatorItem>
                  <IndicatorItem>
                    <IndicatorLabel>Tendência</IndicatorLabel>
                    <IndicatorValue>
                      {signal.generation_reasons.key_indicators?.trend_strength?.toFixed(1) || 'N/A'}
                    </IndicatorValue>
                  </IndicatorItem>
                  <IndicatorItem>
                    <IndicatorLabel>MACD</IndicatorLabel>
                    <IndicatorValue $positive={signal.generation_reasons.key_indicators?.macd_signal ? signal.generation_reasons.key_indicators.macd_signal > 0 : undefined}>
                      {signal.generation_reasons.key_indicators?.macd_signal !== undefined ? 
                        (signal.generation_reasons.key_indicators.macd_signal > 0 ? 'Positivo' : 'Negativo') : 'N/A'}
                    </IndicatorValue>
                  </IndicatorItem>
                </IndicatorGrid>
              </SubSection>

              {/* Condições que Dispararam */}
              <SubSection>
                <SubSectionTitle>⚡ Condições que Dispararam</SubSectionTitle>
                <ConditionsList>
                  {signal.generation_reasons.trigger_conditions?.map((condition, index) => (
                    <ConditionItem key={`condition-${signal.id}-${index}-${condition.slice(0, 10)}`}>
                      <FaCheckCircle /> {condition}
                    </ConditionItem>
                  )) || (
                    <ConditionItem key={`no-conditions-${signal.id}`}>
                      <FaCheckCircle /> Dados não disponíveis
                    </ConditionItem>
                  )}
                </ConditionsList>
              </SubSection>

              {/* Ranking da Moeda */}
              <SubSection>
                <SubSectionTitle>🏆 Ranking da Moeda</SubSectionTitle>
                <RankingInfo>
                  <RankingItem>
                    <RankingLabel>Posição:</RankingLabel>
                    <RankingValue>
                      {signal.generation_reasons.ranking_info?.position 
                        ? `#${signal.generation_reasons.ranking_info.position}` 
                        : 'Fora do Top 40'}
                    </RankingValue>
                  </RankingItem>
                  <RankingItem>
                    <RankingLabel>Tier:</RankingLabel>
                    <RankingValue>{signal.generation_reasons.ranking_info?.tier || 'N/A'}</RankingValue>
                  </RankingItem>
                  <RankingItem>
                    <RankingLabel>Bonus:</RankingLabel>
                    <RankingValue $color={signal.generation_reasons.ranking_info?.bonus_applied !== undefined ? 
                      (signal.generation_reasons.ranking_info.bonus_applied >= 0 ? '#10b981' : '#ef4444') : '#94a3b8'}>
                      {signal.generation_reasons.ranking_info?.bonus_applied !== undefined ? 
                        `${signal.generation_reasons.ranking_info.bonus_applied >= 0 ? '+' : ''}${signal.generation_reasons.ranking_info.bonus_applied} pts` : 'N/A'}
                    </RankingValue>
                  </RankingItem>
                </RankingInfo>
              </SubSection>
            </SectionContent>
          )}
        </TraceabilitySection>
      )}

      {/* Seção: Histórico de Verificações */}
      {signal.confirmation_checks && signal.confirmation_checks.length > 0 && (
        <TraceabilitySection>
          <SectionHeader onClick={() => toggleSection('verification')}>
            <SectionTitle>
              <FaClock /> Histórico de Verificações
              <CountBadge>{signal.confirmation_checks.length} tentativas</CountBadge>
            </SectionTitle>
            {expandedSections.verification ? <FaChevronUp /> : <FaChevronDown />}
          </SectionHeader>
          
          {expandedSections.verification && (
            <SectionContent>
              {signal.confirmation_checks.map((check, index) => (
                <VerificationItem key={`check-${signal.id}-${check.timestamp}-${check.attempt_number}`}>
                  <VerificationHeader>
                    <VerificationTitle>
                      Tentativa #{check.attempt_number}
                      <TimeStamp>{formatTime(check.timestamp)}</TimeStamp>
                    </VerificationTitle>
                    <StatusIndicator $status={check.verification_summary.status}>
                      {check.verification_summary.status}
                    </StatusIndicator>
                  </VerificationHeader>
                  
                  <VerificationDetails>
                    <CheckGrid>
                      <CheckItem>
                        <CheckLabel>🔄 Rompimento</CheckLabel>
                        <CheckStatus $confirmed={check.detailed_checks.price_breakout.confirmed}>
                          {check.detailed_checks.price_breakout.confirmed ? '✅' : 
                           check.detailed_checks.price_breakout.rejected ? '❌' : '⏳'}
                          {check.detailed_checks.price_breakout.percentage.toFixed(2)}%
                        </CheckStatus>
                      </CheckItem>
                      
                      <CheckItem>
                        <CheckLabel>📊 Volume</CheckLabel>
                        <CheckStatus $confirmed={check.detailed_checks.volume_confirmation.confirmed}>
                          {check.detailed_checks.volume_confirmation.confirmed ? '✅' : 
                           check.detailed_checks.volume_confirmation.rejected ? '❌' : '⏳'}
                          {check.detailed_checks.volume_confirmation.ratio.toFixed(1)}x
                        </CheckStatus>
                      </CheckItem>
                      
                      <CheckItem>
                        <CheckLabel>₿ BTC</CheckLabel>
                        <CheckStatus $confirmed={check.detailed_checks.btc_alignment.confirmed}>
                          {check.detailed_checks.btc_alignment.confirmed ? '✅' : 
                           check.detailed_checks.btc_alignment.rejected ? '❌' : '⏳'}
                          {(check.detailed_checks.btc_alignment.alignment_score * 100).toFixed(0)}%
                        </CheckStatus>
                      </CheckItem>
                      
                      <CheckItem>
                        <CheckLabel>📈 Momentum</CheckLabel>
                        <CheckStatus $confirmed={check.detailed_checks.momentum_sustainability.confirmed}>
                          {check.detailed_checks.momentum_sustainability.confirmed ? '✅' : '⏳'}
                          {check.detailed_checks.momentum_sustainability.candles_count} velas
                        </CheckStatus>
                      </CheckItem>
                    </CheckGrid>
                    
                    <VerificationSummary>
                      <SummaryItem>
                        <SummaryLabel>Confirmações:</SummaryLabel>
                        <SummaryValue $color="#10b981">
                          {check.verification_summary.confirmations_count}
                        </SummaryValue>
                      </SummaryItem>
                      <SummaryItem>
                        <SummaryLabel>Rejeições:</SummaryLabel>
                        <SummaryValue $color="#ef4444">
                          {check.verification_summary.rejections_count}
                        </SummaryValue>
                      </SummaryItem>
                      <SummaryItem>
                        <SummaryLabel>Próxima ação:</SummaryLabel>
                        <SummaryValue>
                          {check.next_steps.action_recommended}
                        </SummaryValue>
                      </SummaryItem>
                    </VerificationSummary>
                  </VerificationDetails>
                </VerificationItem>
              ))}
            </SectionContent>
          )}
        </TraceabilitySection>
      )}

      {/* Seção: Decisão Final */}
      {signal.final_decision_reason && (
        <TraceabilitySection>
          <SectionHeader onClick={() => toggleSection('decision')}>
            <SectionTitle>
              {signal.final_decision_reason.decision === 'CONFIRMED' ? 
                <><FaCheckCircle /> Por que foi confirmado?</> : 
                <><FaTimesCircle /> Por que foi rejeitado?</>
              }
              <TimeBadge>
                {signal.final_decision_reason.total_processing_time_minutes.toFixed(1)}min
              </TimeBadge>
            </SectionTitle>
            {expandedSections.decision ? <FaChevronUp /> : <FaChevronDown />}
          </SectionHeader>
          
          {expandedSections.decision && (
            <SectionContent>
              {/* Fatores Decisivos */}
              <SubSection>
                <SubSectionTitle>🎯 Fatores Decisivos</SubSectionTitle>
                <FactorsList>
                  {signal.final_decision_reason.decisive_factors.map((factor, index) => (
                    <FactorItem key={`factor-${signal.id}-${index}-${factor.slice(0, 10)}`}>
                      <FaCheckCircle /> {factor}
                    </FactorItem>
                  ))}
                </FactorsList>
              </SubSection>

              {/* Snapshot do Mercado */}
              <SubSection>
                <SubSectionTitle>📸 Snapshot do Mercado</SubSectionTitle>
                <SnapshotGrid>
                  <SnapshotItem>
                    <SnapshotLabel>Preço:</SnapshotLabel>
                    <SnapshotValue>
                      ${signal.final_decision_reason.market_snapshot.symbol_price.toFixed(6)}
                    </SnapshotValue>
                  </SnapshotItem>
                  <SnapshotItem>
                    <SnapshotLabel>Mudança:</SnapshotLabel>
                    <SnapshotValue $color={signal.final_decision_reason.market_snapshot.price_change_from_entry >= 0 ? '#10b981' : '#ef4444'}>
                      {signal.final_decision_reason.market_snapshot.price_change_from_entry >= 0 ? '+' : ''}
                      {signal.final_decision_reason.market_snapshot.price_change_from_entry.toFixed(2)}%
                    </SnapshotValue>
                  </SnapshotItem>
                  <SnapshotItem>
                    <SnapshotLabel>BTC:</SnapshotLabel>
                    <SnapshotValue>
                      {signal.final_decision_reason.market_snapshot.btc_trend}
                    </SnapshotValue>
                  </SnapshotItem>
                  <SnapshotItem>
                    <SnapshotLabel>Sessão:</SnapshotLabel>
                    <SnapshotValue>
                      {signal.final_decision_reason.market_snapshot.market_session}
                    </SnapshotValue>
                  </SnapshotItem>
                </SnapshotGrid>
              </SubSection>

              {/* Predição de Performance (apenas para confirmados) */}
              {signal.final_decision_reason.performance_prediction && (
                <SubSection>
                  <SubSectionTitle>🔮 Predição de Performance</SubSectionTitle>
                  <PredictionGrid>
                    <PredictionItem>
                      <PredictionLabel>Probabilidade de Sucesso:</PredictionLabel>
                      <PredictionValue>
                        {(signal.final_decision_reason.performance_prediction.estimated_success_probability * 100).toFixed(0)}%
                      </PredictionValue>
                    </PredictionItem>
                    <PredictionItem>
                      <PredictionLabel>Nível de Risco:</PredictionLabel>
                      <PredictionValue $color={getRiskLevelColor(signal.final_decision_reason.performance_prediction.risk_level)}>
                        {signal.final_decision_reason.performance_prediction.risk_level}
                      </PredictionValue>
                    </PredictionItem>
                    <PredictionItem>
                      <PredictionLabel>Tempo Esperado:</PredictionLabel>
                      <PredictionValue>
                        {signal.final_decision_reason.performance_prediction.expected_timeframe}
                      </PredictionValue>
                    </PredictionItem>
                  </PredictionGrid>
                </SubSection>
              )}

              {/* Lições Aprendidas */}
              {signal.final_decision_reason.lessons_learned.length > 0 && (
                <SubSection>
                  <SubSectionTitle>💡 Lições Aprendidas</SubSectionTitle>
                  <LessonsList>
                    {signal.final_decision_reason.lessons_learned.map((lesson, index) => (
                      <LessonItem key={`lesson-${signal.id}-${index}-${lesson.slice(0, 10)}`}>
                        <FaLightbulb /> {lesson}
                      </LessonItem>
                    ))}
                  </LessonsList>
                </SubSection>
              )}
            </SectionContent>
          )}
        </TraceabilitySection>
      )}
    </TraceabilityContainer>
  );
};

// Styled Components
const TraceabilityContainer = styled.div`
  background: #1e293b;
  border-radius: 12px;
  border: 1px solid #374151;
  overflow: hidden;
  margin: 20px 0;
`;

const TraceabilityHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
  border-bottom: 1px solid #374151;
`;

const HeaderTitle = styled.h3`
  color: #f59e0b;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.2em;
`;

const StatusBadge = styled.span<{ $color: string }>`
  background: ${props => props.$color};
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.8em;
  font-weight: 600;
`;

const TraceabilitySection = styled.div`
  border-bottom: 1px solid #374151;
  
  &:last-child {
    border-bottom: none;
  }
`;

const SectionHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  
  &:hover {
    background: rgba(245, 158, 11, 0.05);
  }
`;

const SectionTitle = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  color: #f59e0b;
  font-weight: 600;
  font-size: 1.1em;
`;

const ScoreBadge = styled.span`
  background: #f59e0b;
  color: black;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8em;
  font-weight: 600;
`;

const CountBadge = styled.span`
  background: #374151;
  color: #94a3b8;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8em;
`;

const TimeBadge = styled.span`
  background: #10b981;
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8em;
  font-weight: 600;
`;

const SectionContent = styled.div`
  padding: 20px;
  background: #2d3748;
`;

const SubSection = styled.div`
  margin-bottom: 25px;
  
  &:last-child {
    margin-bottom: 0;
  }
`;

const SubSectionTitle = styled.h4`
  color: #f59e0b;
  margin: 0 0 15px 0;
  font-size: 1em;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const ScoreGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 15px;
`;

const ScoreItem = styled.div`
  background: #374151;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
`;

const ScoreLabel = styled.div`
  color: #94a3b8;
  font-size: 0.9em;
  margin-bottom: 8px;
`;

const ScoreValue = styled.div`
  color: #f59e0b;
  font-weight: 600;
  font-size: 1.1em;
`;

const IndicatorGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
`;

const IndicatorItem = styled.div`
  background: #374151;
  padding: 12px;
  border-radius: 8px;
`;

const IndicatorLabel = styled.div`
  color: #94a3b8;
  font-size: 0.8em;
  margin-bottom: 5px;
`;

const IndicatorValue = styled.div<{ $positive?: boolean }>`
  color: ${props => props.$positive !== undefined ? 
    (props.$positive ? '#10b981' : '#ef4444') : 'white'};
  font-weight: 600;
`;

const ConditionsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const ConditionItem = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  color: #10b981;
  font-size: 0.9em;
`;

const RankingInfo = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
`;

const RankingItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #374151;
  padding: 12px;
  border-radius: 8px;
`;

const RankingLabel = styled.span`
  color: #94a3b8;
  font-size: 0.9em;
`;

const RankingValue = styled.span<{ $color?: string }>`
  color: ${props => props.$color || 'white'};
  font-weight: 600;
`;

const VerificationItem = styled.div`
  background: #374151;
  border-radius: 8px;
  margin-bottom: 15px;
  overflow: hidden;
  
  &:last-child {
    margin-bottom: 0;
  }
`;

const VerificationHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #4a5568;
`;

const VerificationTitle = styled.div`
  color: #f59e0b;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
`;

const TimeStamp = styled.span`
  color: #94a3b8;
  font-size: 0.8em;
  font-weight: normal;
`;

const StatusIndicator = styled.span<{ $status: string }>`
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8em;
  font-weight: 600;
  background: ${props => {
    switch (props.$status) {
      case 'READY_TO_CONFIRM': return '#10b981';
      case 'READY_TO_REJECT': return '#ef4444';
      case 'LEANING_POSITIVE': return '#f59e0b';
      case 'LEANING_NEGATIVE': return '#f97316';
      default: return '#6b7280';
    }
  }};
  color: white;
`;

const VerificationDetails = styled.div`
  padding: 15px;
`;

const CheckGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 10px;
  margin-bottom: 15px;
`;

const CheckItem = styled.div`
  background: #2d3748;
  padding: 10px;
  border-radius: 6px;
  text-align: center;
`;

const CheckLabel = styled.div`
  color: #94a3b8;
  font-size: 0.8em;
  margin-bottom: 5px;
`;

const CheckStatus = styled.div<{ $confirmed?: boolean }>`
  color: ${props => props.$confirmed ? '#10b981' : '#94a3b8'};
  font-weight: 600;
  font-size: 0.9em;
`;

const VerificationSummary = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 10px;
  padding: 10px;
  background: #2d3748;
  border-radius: 6px;
`;

const SummaryItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const SummaryLabel = styled.span`
  color: #94a3b8;
  font-size: 0.8em;
`;

const SummaryValue = styled.span<{ $color?: string }>`
  color: ${props => props.$color || 'white'};
  font-weight: 600;
  font-size: 0.9em;
`;

const FactorsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const FactorItem = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  color: #10b981;
  font-size: 0.9em;
`;

const SnapshotGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
`;

const SnapshotItem = styled.div`
  background: #374151;
  padding: 12px;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const SnapshotLabel = styled.span`
  color: #94a3b8;
  font-size: 0.9em;
`;

const SnapshotValue = styled.span<{ $color?: string }>`
  color: ${props => props.$color || 'white'};
  font-weight: 600;
`;

const PredictionGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
`;

const PredictionItem = styled.div`
  background: #374151;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
`;

const PredictionLabel = styled.div`
  color: #94a3b8;
  font-size: 0.9em;
  margin-bottom: 8px;
`;

const PredictionValue = styled.div<{ $color?: string }>`
  color: ${props => props.$color || '#f59e0b'};
  font-weight: 600;
  font-size: 1.1em;
`;

const LessonsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const LessonItem = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  color: #f59e0b;
  font-size: 0.9em;
  padding: 8px;
  background: rgba(245, 158, 11, 0.1);
  border-radius: 6px;
  border: 1px solid rgba(245, 158, 11, 0.3);
`;

export default SignalTraceability;