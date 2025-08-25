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
interface Signal {
  symbol: string;
  type: 'LONG' | 'SHORT';
  entry_price: number;
  entry_time: string;
  target_price: number;
  status: string;
  quality_score: number;
  signal_class: string;
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
    console.log('fetchSignals: Iniciando busca de sinais.'); // Log 1

    try {
      const authToken = localStorage.getItem('authToken'); // Recupera o token do localStorage
      if (!authToken) {
        console.warn('fetchSignals: Token de autenticação não encontrado. Redirecionando para login.');
        navigate('/login'); // Redireciona para login se não houver token
        return;
      }

      console.log('fetchSignals: Token encontrado, fazendo requisição.'); // Log 2
      const response = await fetch('http://localhost:5000/signals', { // ALTERADO: Porta para 5000 e IP para localhost
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`, // Adiciona o token ao cabeçalho Authorization
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
        // Tenta analisar o texto como JSON. Isso pode resolver problemas de "JSON dentro de uma string".
        rawSignals = JSON.parse(responseText);
      } catch (parseError) {
        console.error('Erro ao analisar a resposta como JSON:', parseError);
        throw new Error('A resposta do servidor não é um JSON válido.');
      }
      
      console.log('fetchSignals: Dados analisados a partir do texto:', rawSignals);

      const transformedSignals: Signal[] = (rawSignals as any[]).map(item => {
        // Adicionar logs para depuração dos valores de preço
        console.log(`DEBUG: Sinal ${item.symbol}`);
        console.log(`DEBUG: item.entry_price (raw): '${item.entry_price}', type: ${typeof item.entry_price}`);
        console.log(`DEBUG: item.target_price (raw): '${item.target_price}', type: ${typeof item.target_price}`);

        // Garante que entry_price e target_price são números válidos
        const entryPrice = parseFloat(item.entry_price);
        const targetPrice = parseFloat(item.target_price);

        console.log(`DEBUG: entryPrice (parsed): ${entryPrice}, isNaN: ${isNaN(entryPrice)}`);
        console.log(`DEBUG: targetPrice (parsed): ${targetPrice}, isNaN: ${isNaN(targetPrice)}`);

        return {
          symbol: item.symbol || '',
          type: (item.type === 'LONG' || item.type === 'SHORT') ? item.type : 'LONG', // Garante que o tipo é válido
          entry_price: isNaN(entryPrice) ? 0 : entryPrice, // Fallback para 0 se NaN
          entry_time: item.entry_time || '',
          target_price: isNaN(targetPrice) ? 0 : targetPrice, // Fallback para 0 se NaN
          status: item.status || '',
          quality_score: parseFloat(item.quality_score) || 0, // Garante que é número
          signal_class: item.signal_class || '',
        };
      });

      // Ordenar os sinais por data (do mais recente para o mais antigo)
      const sortedSignals = transformedSignals.sort((a, b) => {
        const dateA = new Date(a.entry_time);
        const dateB = new Date(b.entry_time);
        return dateB.getTime() - dateA.getTime();
      });

      console.log('Dados transformados para validação:', sortedSignals);
  
      // Validação simplificada para garantir que é um array
      if (!Array.isArray(sortedSignals)) {
        console.error('fetchSignals: Dados transformados não são um array:', sortedSignals);
        throw new Error('Formato de dados de sinais inválido recebido do servidor.');
      }

      setSignals(sortedSignals);
      console.log('fetchSignals: Sinais atualizados no estado:', transformedSignals); // Log 7

      // NOVO: Calcular contagem de sinais de compra e venda
      const buyCount = sortedSignals.filter(signal => signal.type === 'LONG').length;
      const sellCount = sortedSignals.filter(signal => signal.type === 'SHORT').length;
      setBuySignalsCount(buyCount);
      setSellSignalsCount(sellCount);

    } catch (err) {
      console.error('fetchSignals: Erro ao buscar sinais:', err);
      setError(err instanceof Error ? err.message : 'Erro desconhecido ao buscar sinais.');
    } finally {
      setLoading(false);
      console.log('fetchSignals: Busca de sinais finalizada.'); // Log 8
    }
  }, [navigate]); // Dependency array for useCallback

  // Novo useEffect para chamar fetchSignals quando o componente for montado
  useEffect(() => {
    fetchSignals();
  }, [fetchSignals]);

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
              <div className={styles.signalStat}>
                <p>Sinais Ativos</p>
              </div>
              <div className={styles.signalStat}>
                <p>Compra: <span className={styles.buyText}>{buySignalsCount.toString().padStart(2, '0')}</span></p>
              </div>
              <div className={styles.signalStat}>
                <p>Venda: <span className={styles.sellText}>{sellSignalsCount.toString().padStart(2, '0')}</span></p>
              </div>
            </div>
            {loading && <p>Carregando sinais...</p>}
            {error && <p className={styles.errorMessage}>Erro: {error}</p>}
            {!loading && !error && signals.length === 0 && (
              <p>Nenhum sinal disponível no momento.</p>
            )}
            <div className={styles.signalCardsContainer}>
              {!loading && !error && signals.length > 0 && signals.map((signal, index) => (
                <SignalCard
                  key={index} // Usar um ID único do sinal seria melhor se disponível
                  symbol={signal.symbol}
                  type={signal.type === 'LONG' ? 'COMPRA' : 'VENDA'}
                  entryPrice={String(signal.entry_price)}
                  targetPrice={String(signal.target_price)}
                  changePercentage={`${(((signal.target_price / signal.entry_price) - 1) * 100).toFixed(2)}%`}
                  date={signal.entry_time}
                  isPremium={signal.signal_class === 'Sinais Premium'}
                />
              ))}
            </div>
          </div>
          {/* REMOVIDO: BtcSentimentCard */}
        </div>
      </div>
    
  );
}

export default DashboardPage;
