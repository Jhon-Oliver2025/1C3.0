import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './DashboardPage.module.css';
import SignalCard from '../components/SignalCard/SignalCard';
// Removed unused imports:
// import logo2 from '../assets/logo2.png';
import terra from '../assets/terra.png';
// import layoutStyles from '../components/Layout/Layout.module.css';


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

// Definir a interface para o tipo de sinal
// Corrigir a interface Signal para usar os tipos corretos do backend
interface Signal {
  symbol: string;
  type: 'LONG' | 'SHORT'; // Alterado de 'COMPRA' | 'VENDA' para 'LONG' | 'SHORT'
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

// REMOVIDAS AS INTERFACES DE SENTIMENTO DO BTC DAQUI

function DashboardPage() {
  const navigate = useNavigate();
  const [currentPhraseIndex, setCurrentPhraseIndex] = useState(0);
  const [signals, setSignals] = useState<Signal[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [buySignalsCount, setBuySignalsCount] = useState<number>(0);
  const [sellSignalsCount, setSellSignalsCount] = useState<number>(0);
  // Since isBackendOnline is used for status checking but not in the UI anymore:
  // REMOVIDO: const [, setIsBackendOnline] = useState<boolean>(false);

  // Função para verificar o status do backend
  // REMOVIDO:
  // const checkBackendStatus = useCallback(async () => {
  //   try {
  //     const response = await fetch('http://localhost:5000/status'); // Endpoint de status do seu backend
  //     setIsBackendOnline(response.ok); // Se a resposta for 200-299, está online
  //   } catch (error) {
  //     console.error('Erro ao verificar status do backend:', error);
  //     setIsBackendOnline(false);
  //   }
  // }, []);

  useEffect(() => {
    // REMOVIDO:
    // // Verifica o status do backend imediatamente ao montar
    // checkBackendStatus();

    // // Configura um intervalo para verificar o status a cada 5 segundos
    // const intervalId = setInterval(checkBackendStatus, 5000);

    // // Limpa o intervalo quando o componente é desmontado
    // return () => clearInterval(intervalId);
  }, [
    // REMOVIDO: checkBackendStatus
  ]);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentPhraseIndex((prevIndex) =>
        (prevIndex + 1) % motivationalPhrases.length
      );
    }, 8000);

    return () => clearInterval(interval);
  }, []);

  const fetchSignals = useCallback(async () => {
    setLoading(true);
    setError(null);
    console.log('fetchSignals: Iniciando busca de sinais.');

    try {
      const authToken = localStorage.getItem('authToken');
      if (!authToken) {
        console.warn('fetchSignals: Token de autenticação não encontrado. Redirecionando para login.');
        navigate('/login');
        return;
      }

      console.log('fetchSignals: Token encontrado, fazendo requisição.');
      const response = await fetch('http://localhost:5000/signals', {
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
        console.error('Erro ao analisar a resposta como JSON:', parseError);
        throw new Error('A resposta do servidor não é um JSON válido.');
      }
      
      console.log('fetchSignals: Dados analisados a partir do texto:', rawSignals);

      const transformedSignals: Signal[] = (rawSignals as any[]).map(item => {
        const entryPrice = parseFloat(item.entry_price);
        const targetPrice = parseFloat(item.target_price);

        console.log(`DEBUG: entryPrice (parsed): ${entryPrice}, isNaN: ${isNaN(entryPrice)}`);
        console.log(`DEBUG: targetPrice (parsed): ${targetPrice}, isNaN: ${isNaN(targetPrice)}`);

        const projectionPercentage = item.projection_percentage || 
          (targetPrice && entryPrice ? ((targetPrice / entryPrice - 1) * 100) : 0);
      
        return {
          symbol: item.symbol || '',
          type: (item.type === 'LONG' || item.type === 'SHORT') ? item.type : 'LONG', // Manter LONG/SHORT
          entry_price: isNaN(entryPrice) ? 0 : entryPrice,
          entry_time: item.entry_time || '',
          target_price: isNaN(targetPrice) ? 0 : targetPrice,
          status: item.status || '',
          quality_score: parseFloat(item.quality_score) || 0,
          signal_class: item.signal_class || 'PADRÃO',
          projection_percentage: projectionPercentage,
        };
      });

      // Ordenar os sinais por data (do mais recente para o mais antigo)
      const sortedSignals = transformedSignals.sort((a, b) => {
        const dateA = new Date(a.entry_time);
        const dateB = new Date(b.entry_time);
        return dateB.getTime() - dateA.getTime();
      });

      // Filtrar apenas sinais ELITE e PREMIUM
      const filteredSignals = sortedSignals.filter(signal => {
        return signal.signal_class === 'ELITE' || signal.signal_class === 'PREMIUM';
      });
      // REMOVIDO: const filteredSignals = sortedSignals; // Mostrar todos os sinais
      
      console.log('fetchSignals: Sinais filtrados:', filteredSignals);

      // Validação simplificada para garantir que é um array
      if (!Array.isArray(filteredSignals)) {
        console.error('fetchSignals: Dados filtrados não são um array:', filteredSignals);
        throw new Error('Formato de dados de sinais inválido recebido do servidor.');
      }

      setSignals(filteredSignals);
      console.log('fetchSignals: Sinais atualizados no estado:', filteredSignals);

      // Calcular contagem de sinais de compra e venda apenas dos filtrados
      // Calcular contagem de sinais de compra e venda apenas dos filtrados
      const buyCount = filteredSignals.filter(signal => signal.type === 'LONG').length;
      const sellCount = filteredSignals.filter(signal => signal.type === 'SHORT').length;
      setBuySignalsCount(buyCount);
      setSellSignalsCount(sellCount);

    } catch (err) {
      console.error('fetchSignals: Erro ao buscar sinais:', err);
      setError(err instanceof Error ? err.message : 'Erro desconhecido ao buscar sinais.');
    } finally {
      setLoading(false);
      console.log('fetchSignals: Busca de sinais finalizada.');
    }
  }, [navigate]);

  // Novo useEffect para chamar fetchSignals quando o componente for montado
  useEffect(() => {
    fetchSignals();
  }, [fetchSignals]);

  // Calculate total signals count
  const totalSignalsCount = buySignalsCount + sellSignalsCount;

  return (
    
      <div className={styles.dashboardContainer}>
        {/* REMOVIDO: Logo e status do backend que estavam duplicados aqui */}
        {/* <div className={styles.logoAndStatusDashboard}>
          <img src={logo2} alt="Logo" className={styles.dashboardLogo} />
          <div className={`${layoutStyles.statusIndicator} ${isBackendOnline ? layoutStyles.statusOnline : layoutStyles.statusOffline}`}></div>
        </div> */}
        <div className={styles.headerSection} style={{ backgroundImage: `url(${terra})`, backgroundSize: 'cover', backgroundPosition: 'center' }}>
          <div className={styles.headerContent}>
            <p className={styles.motivationalPhrase}>
              {motivationalPhrases[currentPhraseIndex]}
            </p>
          </div>
        </div>

        <div className={styles.contentSection}>
          <div className={styles.signalsSection}>
            {/* REMOVIDO: <h2>Sinais de Trading</h2> */}
            <div className={styles.signalsHeader}> {/* NOVO: Contêiner para o cabeçalho dos cards */}
              {/* Displaying total, buy, and sell signals as requested */}
              <div className={styles.signalStat}>
                <p>
                  Total: <span className={styles.totalText}>{totalSignalsCount.toString().padStart(2, '0')}</span>{' '}
                  Compra: <span className={styles.buyText}>{buySignalsCount.toString().padStart(2, '0')}</span>{' '}
                  e Venda: <span className={styles.sellText}>{sellSignalsCount.toString().padStart(2, '0')}</span>
                </p>
              </div>
            </div>
            {loading && <p>Carregando sinais...</p>}
            {error && <p className={styles.errorMessage}>Erro: {error}</p>}
            {!loading && !error && signals.length === 0 && (
              <p>Nenhum sinal disponível no momento.</p>
            )}
            <div className={styles.signalCardsContainer}>
              {!loading && !error && signals.length > 0 && signals.map((signal, index) => {
                // Calcular a projeção percentual sempre como valor absoluto positivo
                const calculateProjectionPercentage = () => {
                  if (!signal.target_price || !signal.entry_price) return '0.00';
                  
                  // Para sinais de COMPRA (LONG): (target - entry) / entry * 100
                  // Para sinais de VENDA (SHORT): (entry - target) / entry * 100
                  let percentage;
                  if (signal.type === 'LONG') {
                    percentage = ((signal.target_price - signal.entry_price) / signal.entry_price) * 100;
                  } else {
                    percentage = ((signal.entry_price - signal.target_price) / signal.entry_price) * 100;
                  }
                  
                  // Garantir que sempre seja positivo e maior que 6%
                  const absolutePercentage = Math.abs(percentage);
                  return Math.max(absolutePercentage, 6.0).toFixed(2);
                };
                
                // Mapear a classificação corretamente
                const getSignalClass = (signalClass: string): 'PREMIUM' | 'ELITE' => {
                  if (signalClass === 'ELITE') return 'ELITE';
                  return 'PREMIUM'; // Default para PREMIUM
                };
              
                return (
                  <SignalCard
                    key={index}
                    symbol={signal.symbol}
                    type={signal.type === 'LONG' ? 'COMPRA' : 'VENDA'} // Converter para exibição
                    entryPrice={(() => {
                      // Determinar o número de casas decimais do preço de entrada
                      const entryStr = signal.entry_price.toString();
                      const decimalPlaces = entryStr.includes('.') ? entryStr.split('.')[1].length : 0;
                      return signal.entry_price.toFixed(Math.max(decimalPlaces, 3)); // Mínimo 3 casas decimais
                    })()}
                    targetPrice={(() => {
                      // Usar o mesmo número de casas decimais do preço de entrada
                      const entryStr = signal.entry_price.toString();
                      const decimalPlaces = entryStr.includes('.') ? entryStr.split('.')[1].length : 0;
                      return signal.target_price.toFixed(Math.max(decimalPlaces, 3)); // Mínimo 3 casas decimais
                    })()}
                    projectionPercentage={calculateProjectionPercentage()}
                    date={signal.entry_time}
                    signalClass={getSignalClass(signal.signal_class)}
                  />
                );
              })}
            </div>
          </div>
          {/* REMOVIDO: BtcSentimentCard */}
        </div>
      </div>
    
  );
}

export default DashboardPage;
