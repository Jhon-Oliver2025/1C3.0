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
  onToggleFavorite?: () => void;
  isFavorite?: boolean;
}

const SignalCard: React.FC<SignalCardProps> = ({
  symbol,
  type,
  entryPrice,
  targetPrice,
  projectionPercentage,
  date,
  signalClass,
  onToggleFavorite,
  isFavorite,
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
    <div className={`${styles.signalCard} ${styles[type.toLowerCase()]}`}>
      {/* Header do Card - Símbolo e Tipo */}
      <div className={styles.cardHeader}>
        <div className={styles.symbolContainer}>
          <span className={styles.symbol}>{symbol}</span>
        </div>
        <div className={`${styles.typeButton} ${styles[type.toLowerCase()]}`}>
          {type}
        </div>
      </div>
      
      {/* Conteúdo Principal */}
      <div className={styles.cardContent}>
        {/* Linha de Preços */}
        <div className={styles.priceRow}>
          <div className={styles.priceItem}>
            <span className={styles.label}>Entrada</span>
            <span className={styles.priceValue}>{entryPrice}</span>
          </div>
          <div className={styles.priceItem}>
            <span className={styles.label}>Alvo</span>
            <span className={`${styles.priceValue} ${styles.targetPrice}`}>{formattedTargetPrice}</span>
          </div>
        </div>
        
        {/* Footer do Card */}
        <div className={styles.bottomRow}>
          <div className={styles.dateContainer}>
            <span className={styles.date}>{formattedDate}</span>
          </div>
          <div className={styles.projectionContainer}>
            <span className={styles.projectionLabel}>Projeção </span>
            <span className={`${styles.changePercentage} ${styles.positive}`}>
              ({formattedProjection}%)
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SignalCard;