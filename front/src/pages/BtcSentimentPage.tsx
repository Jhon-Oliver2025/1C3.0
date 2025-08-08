import { useState, useEffect, useCallback } from 'react';
import styles from '../components/BtcSentimentCard/BtcSentimentCard.module.css'; // Reutiliza o CSS do card

// NOVAS INTERFACES PARA O SENTIMENTO DO BTC
interface OverallSentiment {
  score: number;
  description: string;
  color_code: string;
}

interface PriceData {
  current_price: number;
  price_change_24h_percent: number;
  description: string;
}

interface FundingRateData {
  value: number;
  score_contribution: number;
  description: string;
  next_funding_time: number; // Timestamp em milissegundos
}

interface OpenInterestData {
  value: number;
  change_1h_percent: number;
  score_contribution: number;
  description: string;
}

interface LongShortRatioData {
  value: number;
  score_contribution: number;
  description: string;
}

interface VolumeData {
  value_usdt_24h: number;
  description: string;
}

interface BtcSentimentData {
  symbol: string;
  timestamp: number; // Timestamp em milissegundos
  overall_sentiment: OverallSentiment;
  price_data: PriceData;
  funding_rate_data: FundingRateData;
  open_interest_data: OpenInterestData;
  long_short_ratio_data: LongShortRatioData;
  volume_data: VolumeData;
}

function BtcSentimentPage() {
  const [btcSentiment, setBtcSentiment] = useState<BtcSentimentData | null>(null);
  const [loadingBtcSentiment, setLoadingBtcSentiment] = useState<boolean>(true);
  const [errorBtcSentiment, setErrorBtcSentiment] = useState<string | null>(null);

  // Função para formatar timestamp para data/hora local
  const formatTimestamp = (timestamp: number) => {
    return new Date(timestamp).toLocaleString();
  };

  // Função para buscar o sentimento do BTC
  const fetchBtcSentiment = useCallback(async () => {
    setLoadingBtcSentiment(true);
    setErrorBtcSentiment(null);
    try {
      const response = await fetch('/api/btc_sentiment'); // Usar proxy relativo
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data: BtcSentimentData = await response.json();
      setBtcSentiment(data);
    } catch (err) {
      console.error('Erro ao buscar sentimento do BTC:', err);
      setErrorBtcSentiment('Não foi possível carregar o sentimento do BTC. Tente novamente mais tarde.');
    } finally {
      setLoadingBtcSentiment(false);
    }
  }, []);

  useEffect(() => {
    fetchBtcSentiment(); // Chama a função de busca na montagem do componente

    // Opcional: Configura um intervalo para recarregar o sentimento do BTC
    // const refreshBtcSentimentInterval = setInterval(() => {
    //   fetchBtcSentiment();
    // }, 60000); // Exemplo: recarrega a cada 60 segundos

    // return () => clearInterval(refreshBtcSentimentInterval);
  }, [fetchBtcSentiment]);

  return (
    <div id="btc-sentiment" className={styles.btcSentimentSection}>
      <h2>Sentimento do Bitcoin</h2>
      {loadingBtcSentiment && <p className={styles.loadingMessage}>Carregando sentimento do BTC...</p>}
      {errorBtcSentiment && <p className={styles.errorMessage}>{errorBtcSentiment}</p>}
      {btcSentiment && (
        <div className={styles.sentimentCard}>
          <div className={styles.overallSentiment} style={{ backgroundColor: btcSentiment.overall_sentiment.color_code }}>
            <h3>Sentimento Geral: {btcSentiment.overall_sentiment.description}</h3>
            <p className={styles.sentimentScore}>{btcSentiment.overall_sentiment.score}/100</p>
          </div>
          <p className={styles.lastUpdated}>Última Atualização: {formatTimestamp(btcSentiment.timestamp)}</p>

          <div className={styles.metricGrid}>
            <div className={styles.metricItem}>
              <h4>Preço ({btcSentiment.symbol})</h4>
              <p className={styles.metricValue}>${btcSentiment.price_data.current_price.toFixed(2)}</p>
              <p className={styles.metricDescription}>Variação 24h: {btcSentiment.price_data.price_change_24h_percent.toFixed(2)}%</p>
              <p className={styles.metricDescription}>{btcSentiment.price_data.description}</p>
            </div>

            <div className={styles.metricItem}>
              <h4>Funding Rate</h4>
              <p className={styles.metricValue}>{btcSentiment.funding_rate_data.value.toFixed(5)}</p>
              <p className={styles.metricDescription}>{btcSentiment.funding_rate_data.description}</p>
              <p className={styles.metricDescription}>Próximo Funding: {formatTimestamp(btcSentiment.funding_rate_data.next_funding_time)}</p>
            </div>

            <div className={styles.metricItem}>
              <h4>Open Interest</h4>
              <p className={styles.metricValue}>${(btcSentiment.open_interest_data.value / 1_000_000_000).toFixed(2)} Bilhões</p>
              <p className={styles.metricDescription}>Variação 1h: {btcSentiment.open_interest_data.change_1h_percent.toFixed(2)}%</p>
              <p className={styles.metricDescription}>{btcSentiment.open_interest_data.description}</p>
            </div>

            <div className={styles.metricItem}>
              <h4>Long/Short Ratio</h4>
              <p className={styles.metricValue}>{btcSentiment.long_short_ratio_data.value.toFixed(2)}</p>
              <p className={styles.metricDescription}>{btcSentiment.long_short_ratio_data.description}</p>
            </div>

            <div className={styles.metricItem}>
              <h4>Volume (24h)</h4>
              <p className={styles.metricValue}>${(btcSentiment.volume_data.value_usdt_24h / 1_000_000_000).toFixed(2)} Bilhões</p>
              <p className={styles.metricDescription}>{btcSentiment.volume_data.description}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default BtcSentimentPage;