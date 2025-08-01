import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './DashboardPage.module.css';
import SignalCard from '../components/SignalCard/SignalCard';
// Adicionar as importações das imagens
import usaFlag from '../assets/usa.png';
import asiaFlag from '../assets/asia.png';
// Remover import não utilizado
// import terra from '../assets/terra.png';

const motivationalPhrases: string[] = [
  "Invista em conhecimento, ele paga os melhores juros.",
  "O futuro financeiro é descentralizado. Construa o seu agora.",
  "Em cripto, a paciência é a maior virtude e o maior lucro.",
  "Não invista mais do que você pode perder. Invista para aprender.",
  "A blockchain é a confiança. Cripto é a liberdade.",
  "Cada halving é um lembrete: a escassez digital é real.",
  "DeFi: o banco do futuro, sem bancos.",
  "NFTs: a arte digital encontra a propriedade real.",
  "A volatilidade é o preço da inovação. Mantenha a visão de longo prazo.",
  "Seja seu próprio banco. Seja sua própria soberania."
];

// Interface para o tipo de sinal
interface Signal {
  symbol: string;
  type: 'LONG' | 'SHORT';
  entry_price: number;
  entry_time: string;
  target_price: number;
  status: string;
  quality_score: number;
  signal_class: string;
  projection_percentage?: number;
  trend_timeframe?: string;
  entry_timeframe?: string;
  leverage?: number;
  expected_duration?: string;
}

function DashboardPage() {
  const navigate = useNavigate();
  const [currentPhraseIndex, setCurrentPhraseIndex] = useState(0);
  const [signals, setSignals] = useState<Signal[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false); // NOVO: indicador de refresh sutil
  const [error, setError] = useState<string | null>(null);
  const [buySignalsCount, setBuySignalsCount] = useState<number>(0);
  const [sellSignalsCount, setSellSignalsCount] = useState<number>(0);
  
  // Estados para os relógios regressivos
  const [usaCountdown, setUsaCountdown] = useState<number>(0);
  const [asiaCountdown, setAsiaCountdown] = useState<number>(0);
  const [currentTime, setCurrentTime] = useState<string>(''); // ADICIONAR esta linha

  // Função para formatar countdown em HH:MM:SS
  const formatCountdown = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Função para buscar sinais - MODIFICADA para refresh sutil
  const fetchSignals = useCallback(async (isRefresh = false) => {
    if (isRefresh && signals.length > 0) {
      setRefreshing(true); // Mostrar indicador sutil apenas
    } else {
      setLoading(true); // Loading completo apenas na primeira vez
    }
    setError(null);
    console.log('fetchSignals: Iniciando busca de sinais.');

    try {
      const authToken = localStorage.getItem('authToken');
      if (!authToken) {
        console.warn('fetchSignals: Token de autenticação não encontrado. Redirecionando para login.');
        navigate('/login');
        return;
      }

      // Substituir as linhas 79-83 por:
      console.log('fetchSignals: Token encontrado, fazendo requisição.');
      const response = await fetch('/api/signals', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
          console.error('fetchSignals: Erro de autenticação. Token inválido ou expirado.');
          localStorage.removeItem('authToken');
          navigate('/login');
          throw new Error("Sessão expirada ou não autorizada. Por favor, faça login novamente.");
        }
        throw new Error(`Erro HTTP: ${response.status}`);
      }

      const responseText = await response.text();
      console.log('fetchSignals: Texto bruto recebido do backend:', responseText);

      let rawSignals;
      try {
        rawSignals = JSON.parse(responseText);
      } catch (parseError) {
        console.error('fetchSignals: Erro ao fazer parse do JSON:', parseError);
        throw new Error('Resposta inválida do servidor.');
      }

      console.log('fetchSignals: Dados parseados do backend:', rawSignals);

      if (!Array.isArray(rawSignals)) {
        console.error('fetchSignals: Dados recebidos não são um array:', rawSignals);
        throw new Error('Formato de dados inválido recebido do servidor.');
      }

      const filteredSignals = rawSignals.filter((signal: any) => 
        signal.signal_class === 'ELITE' || signal.signal_class === 'PREMIUM'
      );

      console.log('fetchSignals: Sinais filtrados (ELITE/PREMIUM):', filteredSignals);

      const processedSignals: Signal[] = filteredSignals.map((signal: any) => ({
        ...signal,
        projection_percentage: signal.projection_percentage || 
          ((signal.target_price - signal.entry_price) / signal.entry_price * 100),
      }));

      // Transição suave para novos sinais
      setTimeout(() => {
        setSignals(processedSignals);

        // Calcular contadores
        const buyCount = processedSignals.filter(signal => signal.type === 'LONG').length;
        const sellCount = processedSignals.filter(signal => signal.type === 'SHORT').length;
        
        setBuySignalsCount(buyCount);
        setSellSignalsCount(sellCount);
      }, isRefresh ? 100 : 0); // Pequeno delay apenas no refresh

      console.log('fetchSignals: Sinais processados e estados atualizados.');
      console.log('fetchSignals: Total de sinais:', processedSignals.length);

    } catch (error: any) {
      console.error('fetchSignals: Erro capturado:', error);
      setError(error.message || 'Erro desconhecido ao buscar sinais.');
    } finally {
      setLoading(false);
      setRefreshing(false);
      console.log('fetchSignals: Processo finalizado.');
    }
  }, [navigate, signals.length]);

  // Função para buscar dados dos relógios
  const fetchMarketCountdown = useCallback(async () => {
    try {
      const authToken = localStorage.getItem('authToken');
      if (!authToken) return; // Sai silenciosamente se não há token
      
      const response = await fetch('/api/market-countdown', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setUsaCountdown(data.usa_countdown);
        setAsiaCountdown(data.asia_countdown);
        setCurrentTime(data.current_time);
      }
    } catch (error) {
      console.error('Erro ao buscar countdown dos mercados:', error);
    }
  }, []);

  // Effect para carregar dados iniciais
  useEffect(() => {
    fetchSignals();
    fetchMarketCountdown();
  }, [fetchSignals, fetchMarketCountdown]);

  // Effect para atualizar relógios a cada segundo
  useEffect(() => {
    const interval = setInterval(() => {
      setUsaCountdown(prev => Math.max(0, prev - 1));
      setAsiaCountdown(prev => Math.max(0, prev - 1));
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  // Effect separado para atualizar dados do servidor (menos frequente) - MODIFICADO
  useEffect(() => {
    const serverInterval = setInterval(() => {
      fetchSignals(true); // Indicar que é um refresh
      fetchMarketCountdown();
    }, 60000); // Atualizar a cada 1 minuto

    return () => clearInterval(serverInterval);
  }, [fetchSignals, fetchMarketCountdown]);

  // Effect para rotacionar frases motivacionais
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentPhraseIndex((prevIndex) => (prevIndex + 1) % motivationalPhrases.length);
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className={styles.dashboardContainer}>
      {/* Contêiner principal com toda a estrutura */}
      <div className={styles.mainContentContainer}>
        {/* 1. Seção motivacional no topo */}
        <div className={styles.motivationalSection}>
          <p className={styles.motivationalPhrase}>
            {motivationalPhrases[currentPhraseIndex]}
          </p>
        </div>

        {/* 2. Cabeçalho reorganizado */}
        <div className={styles.signalsHeader}>
          {/* PRIMEIRA LINHA: Data e Horário com indicador de refresh */}
          <div className={styles.timeAndMarkets}>
            {/* Horário simplificado - APENAS UMA DATA */}
            <div className={styles.currentTimeItem}>
              <span className={styles.timeLabel}>AGORA</span>
              <span className={styles.currentTimeValue}>
                {currentTime}
                {refreshing && <span className={styles.refreshIndicator}>●</span>}
              </span>
            </div>
          </div>
          
          {/* SEGUNDA LINHA: Cronômetros dos Mercados */}
          <div className={styles.marketCountdowns}>
            <div className={styles.countdownItem}>
              <div className={styles.marketBanner}>
                <img src={usaFlag} alt="Mercado EUA" className={styles.marketBannerImg} />
                <span className={styles.marketBannerText}>MERCADO EUA</span>
              </div>
              <span className={styles.countdownValue}>{formatCountdown(usaCountdown)}</span>
            </div>
            <div className={styles.countdownItem}>
              <div className={styles.marketBanner}>
                <img src={asiaFlag} alt="Mercado ÁSIA" className={styles.marketBannerImg} />
                <span className={styles.marketBannerText}>MERCADO ÁSIA</span>
              </div>
              <span className={styles.countdownValue}>{formatCountdown(asiaCountdown)}</span>
            </div>
          </div>
          
          {/* TERCEIRA LINHA: Estatísticas dos Sinais */}
          <div className={styles.signalsStats}>
            {/* Total em destaque */}
            <div className={styles.totalSignalsItem}>
              <span className={styles.totalLabel}>Total:</span>
              <span className={styles.totalValue}>{buySignalsCount + sellSignalsCount}</span>
            </div>
            
            {/* Compra e Venda juntos */}
            <div className={styles.buySellContainer}>
              <div className={styles.buySellItem}>
                <span className={styles.buySellLabel}>Compra:</span>
                <span className={`${styles.buySellValue} ${styles.buyText}`}>{buySignalsCount}</span>
              </div>
              <div className={styles.buySellItem}>
                <span className={styles.buySellLabel}>Venda:</span>
                <span className={`${styles.buySellValue} ${styles.sellText}`}>{sellSignalsCount}</span>
              </div>
            </div>
          </div>
        </div>

        {/* 3. Conteúdo dos sinais - MODIFICADO para não sumir durante refresh */}
        {loading && signals.length === 0 && <p className={styles.loadingMessage}>Carregando sinais...</p>}
        {error && <p className={styles.errorMessage}>Erro: {error}</p>}
        {!loading && !error && signals.length === 0 && <p className={styles.noSignalsMessage}>Nenhum sinal disponível no momento.</p>}
        
        {/* Sempre mostrar sinais se existirem, mesmo durante refresh */}
        {signals.length > 0 && (
          <div className={`${styles.signalCardsContainer} ${refreshing ? styles.refreshing : ''}`}>
            {signals.map((signal, index) => (
              <SignalCard
                key={`${signal.symbol}-${signal.entry_time}-${index}`} // Key mais específica
                symbol={signal.symbol}
                type={signal.type === 'LONG' ? 'COMPRA' : 'VENDA'}
                entryPrice={String(signal.entry_price)}
                targetPrice={String(signal.target_price)}
                projectionPercentage={String(signal.projection_percentage || 0)}
                date={signal.entry_time}
                signalClass={signal.signal_class as 'PREMIUM' | 'ELITE'}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default DashboardPage;
