import React from 'react';
import styles from './SignalCard.module.css';

interface SignalCardProps {
  symbol: string;
  type: 'COMPRA' | 'VENDA';
  entryPrice: string;
  targetPrice: string;
  projectionPercentage: string;
  date: string;
  createdAt?: string;
  confirmedAt?: string;
  signalClass: 'PREMIUM' | 'PREMIUM+' | 'ELITE' | 'ELITE+' | 'PADRÃO';
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
  createdAt,
  confirmedAt,
  signalClass,
  onToggleFavorite,
  isFavorite,
}) => {
  // Função para formatar data com timezone correto do Brasil
  const formatDate = (dateString: string) => {
    if (!dateString) return '';
    
    try {
      // Verificar se já está no formato brasileiro
      const brazilianDateRegex = /^\d{2}\/\d{2}\/\d{4} \d{2}:\d{2}:\d{2}$/;
      if (brazilianDateRegex.test(dateString)) {
        return dateString;
      }
      
      // Tentar converter formato ISO ou outros formatos
      let dateObj: Date;
      
      // Se a string contém 'T' (formato ISO), processar como UTC e converter para horário local do Brasil
      if (dateString.includes('T')) {
        dateObj = new Date(dateString);
        
        if (!isNaN(dateObj.getTime())) {
          // Converter para horário do Brasil usando timezone
          const formattedDate = dateObj.toLocaleDateString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            timeZone: 'America/Sao_Paulo'
          });
          
          const formattedTime = dateObj.toLocaleTimeString('pt-BR', {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false,
            timeZone: 'America/Sao_Paulo'
          });
          
          return `${formattedDate} ${formattedTime}`;
        }
      } else {
        // Para outros formatos, tentar conversão direta
        dateObj = new Date(dateString);
        
        if (!isNaN(dateObj.getTime())) {
          const formattedDate = dateObj.toLocaleDateString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            timeZone: 'America/Sao_Paulo'
          });
          
          const formattedTime = dateObj.toLocaleTimeString('pt-BR', {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false,
            timeZone: 'America/Sao_Paulo'
          });
          
          return `${formattedDate} ${formattedTime}`;
        }
      }
    } catch (error) {
      console.error('Erro ao formatar data:', error);
    }
    
    return '';
  };

  // Determinar qual data exibir
  const getDisplayDate = () => {
    if (confirmedAt) {
      return `Confirmado: ${formatDate(confirmedAt)}`;
    }
    if (createdAt) {
      return `Criado: ${formatDate(createdAt)}`;
    }
    if (date && date.trim() !== '') {
      return formatDate(date);
    }
    // Se chegou até aqui, tentar usar qualquer data disponível
    const availableDate = confirmedAt || createdAt || date;
    if (availableDate && availableDate.trim() !== '') {
      return formatDate(availableDate);
    }
    return 'Data não disponível';
  };

  const formattedDate = getDisplayDate();

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

  // Função para renderizar estrelas baseadas na classificação
  const renderStars = (signalClass: string): string => {
    switch (signalClass) {
      case 'PREMIUM+':
        return '⭐'; // 1 estrela
      case 'ELITE':
        return '⭐⭐'; // 2 estrelas
      case 'ELITE+':
        return '⭐⭐⭐'; // 3 estrelas
      default:
        return ''; // Sem estrelas para PREMIUM
    }
  };

  // Função para obter a cor da classificação
  const getClassColor = (signalClass: string): string => {
    switch (signalClass) {
      case 'PREMIUM+':
        return '#C0C0C0'; // Prata
      case 'ELITE':
        return '#FFD700'; // Dourado
      case 'ELITE+':
        return '#FFD700'; // Dourado
      default:
        return '#9ca3af'; // Cinza padrão
    }
  };

  return (
    <div className={`${styles.signalCard} ${styles[type.toLowerCase()]}`}>
      {/* Header do Card - Símbolo e Tipo */}
      <div className={styles.cardHeader}>
        <div className={styles.symbolContainer}>
          <span className={styles.symbol}>{symbol}</span>
          {renderStars(signalClass) && (
            <span 
              className={styles.signalClassStars}
              style={{ color: getClassColor(signalClass) }}
            >
              {renderStars(signalClass)}
            </span>
          )}
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
