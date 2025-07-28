import React from 'react';
import styles from './SignalCard.module.css';

interface SignalCardProps {
  symbol: string;
  type: 'COMPRA' | 'VENDA';
  entryPrice: string;
  targetPrice: string;
  projectionPercentage: string;
  date: string;
  signalClass: 'PREMIUM' | 'ELITE'; // Removido 'PADRÃO'
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

  return (
    <div className={styles.signalCard}>
      <div className={styles.cardHeader}>
        <span className={styles.symbol}>{symbol}</span>
        <button className={`${styles.typeButton} ${type === 'COMPRA' ? styles.buy : styles.sell}`}>
          {type}
        </button>
      </div>
      
      <span className={
        signalClass === 'ELITE' ? styles.eliteText :
        styles.premiumText
      }>
        SINAIS {signalClass}
      </span>
      
      <div className={styles.priceDetail}>
        <span className={styles.label}>Entrada</span>
        <span className={styles.entryPriceValue}>{entryPrice}</span>
      </div>
      
      <div className={styles.priceDetail}>
        <span className={styles.label}>Alvo</span>
        <span className={styles.value}>{targetPrice}</span>
      </div>
      
      <div className={styles.projectionDetail}>
        <span className={styles.label}>Projeção</span>
        <span className={styles.changePercentage}>
          ({projectionPercentage}%)
        </span>
      </div>
      
      <span className={styles.date}>{formattedDate}</span>
    </div>
  );
};

export default SignalCard;