import React from 'react';
import styles from './SignalCard.module.css';

interface SignalCardProps {
  symbol: string;
  type: 'COMPRA' | 'VENDA';
  entryPrice: string;
  targetPrice: string;
  changePercentage: string;
  date: string;
  isPremium: boolean;
}

const SignalCard: React.FC<SignalCardProps> = ({
  symbol,
  type,
  entryPrice,
  targetPrice,
  changePercentage,
  date,
  isPremium,
}) => {
  // Formata a string da data para um formato mais legível
  const dateObj = new Date(date);
  const formattedDate = date && !isNaN(dateObj.getTime()) ? dateObj.toLocaleString('pt-BR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false, // Usa formato de 24 horas
  }) : '';

  return (
    <div className={styles.signalCard}>
      <div className={styles.cardHeader}>
        <span className={styles.symbol}>{symbol}</span>
        <button className={`${styles.typeButton} ${type === 'COMPRA' ? styles.buy : styles.sell}`}>
          {type}
        </button>
      </div>
      {isPremium && <span className={styles.premiumText}>SINAIS PREMIUM</span>}
      <div className={styles.priceDetail}>
        <span className={styles.label}>Entrada</span>
        <span className={styles.entryPriceValue}>{entryPrice}</span> {/* Removido styles.value, adicionado styles.entryPriceValue */}
      </div>
      <div className={styles.priceDetail}>
        <span className={styles.label}>Alvo</span>
        <span className={styles.value}>{targetPrice}</span>
        <span className={styles.changePercentage}>
          ({changePercentage}) {/* Agora changePercentage já virá com '%' do DashboardPage */}
        </span>
      </div>
      <span className={styles.date}>{formattedDate}</span> {/* Usando a data formatada */}
    </div>
  );
};

export default SignalCard;