import React from 'react';
import styles from './SignalCard.module.css';

interface SignalCardProps {
  symbol: string;
  type: 'COMPRA' | 'VENDA';
  entryPrice: string;
  targetPrice: string;
  projectionPercentage: string;
  date: string;
  signalClass: 'PREMIUM' | 'ELITE' | 'PADRÃO';
}

const SignalCard: React.FC<SignalCardProps> = ({
  symbol,
  type,
  entryPrice,
  targetPrice,
  projectionPercentage,
  date,
  signalClass,
}) => {
  const dateObj = new Date(date);
  const formattedDate = date && !isNaN(dateObj.getTime()) ? dateObj.toLocaleString('pt-BR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  }) : '';

  // Função para formatar preços com as mesmas casas decimais
  const formatPrice = (price: string, referencePrice: string): string => {
    const refDecimalPlaces = (referencePrice.split('.')[1] || '').length;
    const numPrice = parseFloat(price);
    return numPrice.toFixed(refDecimalPlaces);
  };

  // Função para formatar projeção (sempre positiva)
  const formatProjection = (projection: string): string => {
    const numProjection = parseFloat(projection);
    return Math.abs(numProjection).toFixed(2);
  };

  // Formatar preços
  const formattedTargetPrice = formatPrice(targetPrice, entryPrice);
  const formattedProjection = formatProjection(projectionPercentage);

  const isPositiveProjection = parseFloat(projectionPercentage) > 0;

  return (
    <div className="mobile-signal-card">
      {/* Header do Card */}
      <div className="mobile-card-header">
        <div className="mobile-card-symbol">
          <span className="mobile-symbol-text">{symbol}</span>
          <span className="mobile-symbol-class">{signalClass || 'CRYPTO'}</span>
        </div>
        <div className={`mobile-card-type ${type.toLowerCase()}`}>
          {type}
        </div>
      </div>
      
      {/* Conteúdo Principal */}
      <div className="mobile-card-body">
        {/* Linha de Preços */}
        <div className="mobile-prices-row">
          <div className="mobile-price-item">
            <span className="mobile-price-label">Entrada</span>
            <span className="mobile-price-value">{entryPrice}</span>
          </div>
          <div className="mobile-price-divider">→</div>
          <div className="mobile-price-item">
            <span className="mobile-price-label">Alvo</span>
            <span className="mobile-price-value">{formattedTargetPrice}</span>
          </div>
        </div>
        
        {/* Footer do Card */}
        <div className="mobile-card-footer">
          <div className="mobile-card-date">
            <span className="mobile-date-icon">📅</span>
            <span className="mobile-date-text">{formattedDate}</span>
          </div>
          <div className="mobile-card-projection">
            <span className="mobile-projection-text">Projeção</span>
            <span className="mobile-projection-value">({formattedProjection}%)</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SignalCard;