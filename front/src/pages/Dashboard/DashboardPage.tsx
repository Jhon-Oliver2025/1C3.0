import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import SignalCard from '../../components/SignalCard/SignalCard';
import PWAInstallButton from '../../components/PWA/PWAInstallButton';
import styles from './DashboardPage.module.css';
import logo2 from '../../assets/logo2.png';

/**
 * Interface para definir a estrutura de um sinal
 */
interface Signal {
  symbol: string;
  type: 'COMPRA' | 'VENDA';
  entry_price: number;
  entry_time: string;
  target_price: number;
  projection_percentage: number;
  signal_class: 'PREMIUM' | 'ELITE' | 'PADRÃO';
  status: string;
  is_favorite?: boolean;
}

/**
 * Componente principal da página Dashboard
 * Exibe seção motivacional, cabeçalho com horários e lista de sinais
 */
const DashboardPage: React.FC = () => {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [currentPhraseIndex, setCurrentPhraseIndex] = useState(0);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const navigate = useNavigate();

  // Array de frases motivacionais
  const motivationalPhrases = [
    "A nova fronteira do investimento está ao seu alcance.",
    "Desbrave o universo cripto com clareza e precisão, do seu jeito.",
    "Veja os sinais em meio ao caos e transforme sua jornada.",
    "O futuro dos seus investimentos não é no espaço, mas em suas mãos.",
    "Sua nova jornada de riqueza começa com um único passo certo.",
    "Deixe para trás as promessas vazias. Olhe para a nova oportunidade.",
    "A melhor forma de prever o futuro é construí-lo agora.",
    "O mundo dos investimentos mudou. A nova oportunidade está aqui.",
    "Não se perca no espaço. Siga o caminho que te guia à liberdade.",
    "O mundo das criptomoedas é a nova corrida espacial. Você está pronto?"
  ];

  /**
   * Atualiza o horário atual a cada segundo
   */
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  /**
   * Alterna as frases motivacionais a cada 8 segundos
   */
  useEffect(() => {
    const phraseTimer = setInterval(() => {
      setCurrentPhraseIndex((prevIndex) => 
        (prevIndex + 1) % motivationalPhrases.length
      );
    }, 8000);

    return () => clearInterval(phraseTimer);
  }, [motivationalPhrases.length]);

  /**
   * Carrega os sinais da API na inicialização
   */
  useEffect(() => {
    fetchSignals();
  }, []);

  /**
   * Formata a data para exibição
   */
  const formatDate = (date: Date) => {
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  /**
   * Formata o horário para exibição
   */
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  /**
   * Calcula horários dos mercados internacionais
   */
  const getMarketTimes = () => {
    const now = new Date();
    
    // Mercado EUA (NYSE: 9:30-16:00 EST, Segunda a Sexta)
    const usaTime = new Date(now.toLocaleString("en-US", {timeZone: "America/New_York"}));
    const usaHour = usaTime.getHours();
    const usaMinutes = usaTime.getMinutes();
    const usaDay = usaTime.getDay(); // 0 = Domingo, 6 = Sábado
    const usaIsWeekday = usaDay >= 1 && usaDay <= 5;
    const usaIsOpen = usaIsWeekday && 
      ((usaHour > 9) || (usaHour === 9 && usaMinutes >= 30)) && 
      (usaHour < 16);
    const usaStatus = usaIsOpen ? 'ABERTO' : 'FECHADO';
    
    // Mercado Ásia (Tokyo: 9:00-15:00 JST, Segunda a Sexta)
    const asiaTime = new Date(now.toLocaleString("en-US", {timeZone: "Asia/Tokyo"}));
    const asiaHour = asiaTime.getHours();
    const asiaDay = asiaTime.getDay(); // 0 = Domingo, 6 = Sábado
    const asiaIsWeekday = asiaDay >= 1 && asiaDay <= 5;
    const asiaIsOpen = asiaIsWeekday && (asiaHour >= 9 && asiaHour < 15);
    const asiaStatus = asiaIsOpen ? 'ABERTO' : 'FECHADO';
    
    return {
      usa: {
        time: usaTime.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        status: usaStatus
      },
      asia: {
        time: asiaTime.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        status: asiaStatus
      }
    };
  };

  const marketTimes = getMarketTimes();

  // Estado para verificar se o backend está online
  const [isBackendOnline, setIsBackendOnline] = useState(true);

  /**
   * Busca os sinais da API
   */
  const fetchSignals = async () => {
    try {
      setLoading(true);
      setError(null);
      setIsBackendOnline(true);
      
      console.log('🔄 Carregando sinais da API...');
      
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('Token de autenticação não encontrado');
      }
      
      const response = await fetch('/api/signals/public', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        if (response.status === 401) {
          localStorage.removeItem('token');
          navigate('/login');
          return;
        }
        throw new Error(`Erro na API: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('✅ Sinais carregados da API:', data);
      
      // Verificar se a resposta tem a estrutura esperada
      const signalsArray = data.signals || data;
      if (!Array.isArray(signalsArray)) {
        throw new Error('Formato de dados inválido da API');
      }
      
      // Mapear os dados da API para o formato esperado
      const mappedSignals: Signal[] = signalsArray.map((signal: any) => ({
        symbol: signal.symbol,
        type: signal.type === 'LONG' || signal.type === 'COMPRA' ? 'COMPRA' : 'VENDA',
        entry_price: parseFloat(signal.entry_price) || 0,
        entry_time: signal.entry_time,
        target_price: parseFloat(signal.target_price) || 0,
        projection_percentage: parseFloat(signal.projection_percentage) || 0,
        signal_class: signal.signal_class,
        status: signal.status,
        is_favorite: false
      }));
      
      // Ordenar sinais por data/hora mais recente primeiro
      const sortedSignals = mappedSignals.sort((a, b) => {
        const dateA = new Date(a.entry_time).getTime();
        const dateB = new Date(b.entry_time).getTime();
        return dateB - dateA; // Mais recente primeiro
      });
      
      setSignals(sortedSignals);
    } catch (err) {
      console.error('❌ Erro ao carregar sinais:', err);
      setError(err instanceof Error ? err.message : 'Erro ao carregar sinais');
      setIsBackendOnline(false);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Alterna o estado do menu mobile
   */
  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  /**
   * Função para realizar logout
   */
  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  /**
   * Função para alternar favorito de um sinal
   */
  const toggleFavorite = (index: number) => {
    setSignals(prevSignals => 
      prevSignals.map((signal, i) => 
        i === index ? { ...signal, is_favorite: !signal.is_favorite } : signal
      )
    );
  };

  const totalSignals = signals.length;
  const buySignals = signals.filter(s => s.type === 'COMPRA').length;
  const sellSignals = signals.filter(s => s.type === 'VENDA').length;

  return (
    <div className={styles.dashboardContainer}>
      {/* HEADER FIXO (Container 0) */}
      <header className="mobile-top-header">
        <button className="mobile-menu-button" onClick={toggleMobileMenu} aria-label="Menu">
          ☰
        </button>
        <div className="mobile-logo-container">
           <img 
             src={logo2} 
             alt="Logo do Sistema" 
             className={`mobile-system-logo ${isBackendOnline ? 'online' : 'offline'}`}
             title={isBackendOnline ? 'Backend Online' : 'Backend Offline'}
           />
         </div>
      </header>

      {/* MENU MOBILE OVERLAY */}
      {isMobileMenuOpen && (
        <div className="mobile-menu-overlay" onClick={toggleMobileMenu}>
          <div className="mobile-menu-content" onClick={(e) => e.stopPropagation()}>
            <div className="mobile-menu-header">
              <h3>Menu</h3>
              <button className="mobile-menu-close" onClick={toggleMobileMenu}>
                ×
              </button>
            </div>
            <div className="mobile-menu-items">
               <Link to="/suporte" className="mobile-menu-item" onClick={toggleMobileMenu}>
                 Suporte
               </Link>
               
               {/* Botão de instalação PWA */}
               <div style={{ padding: '8px 0' }}>
                 <PWAInstallButton variant="secondary" size="medium" />
               </div>
               
               <button className="mobile-menu-item logout" onClick={handleLogout}>
                 Sair
               </button>
             </div>
          </div>
        </div>
      )}

      {/* CONTAINER 1 - MOTIVAÇÃO + CABEÇALHO (Fixo) */}
      <div className="mobile-motivation-header-container">
        {/* Seção Motivacional */}
        <div className="mobile-motivational">
          <p className="mobile-motivational-text">
            {motivationalPhrases[currentPhraseIndex]}
          </p>
        </div>

        {/* Espaçamento de Segurança (4px) */}
        <div className="mobile-safety-gap"></div>

        {/* Container Principal para Cabeçalho e Cards */}
        <div className="mobile-signals-container">
          {/* Cabeçalho dos Sinais (150px) */}
          <div className="mobile-signals-header">
            {/* Linha 1: Horários dos Mercados */}
            <div className="mobile-market-times">
              <div className="mobile-market-item">
                <span className="mobile-market-label">EUA</span>
                <span className="mobile-market-time">{marketTimes.usa.time}</span>
                <span className={`mobile-market-status ${marketTimes.usa.status === 'ABERTO' ? 'open' : 'closed'}`}>
                  {marketTimes.usa.status}
                </span>
              </div>
              <div className="mobile-market-item">
                <span className="mobile-market-label">ÁSIA</span>
                <span className="mobile-market-time">{marketTimes.asia.time}</span>
                <span className={`mobile-market-status ${marketTimes.asia.status === 'ABERTO' ? 'open' : 'closed'}`}>
                  {marketTimes.asia.status}
                </span>
              </div>
              <div className="mobile-market-item">
                <span className="mobile-market-label">RELÓGIO</span>
                <span className="mobile-market-time">{formatTime(currentTime)}</span>
                <span className="mobile-market-status crypto">24/7</span>
              </div>
            </div>
            
            {/* Linha 2: Estatísticas */}
            <div className="mobile-stats-row">
              <div className="mobile-stat-item">
                <span className="mobile-stat-label">Total</span>
                <span className="mobile-stat-value">{String(totalSignals).padStart(2, '0')}</span>
              </div>
              <div className="mobile-stat-item">
                <span className="mobile-stat-label">Compra</span>
                <span className="mobile-stat-value buy">{String(buySignals).padStart(2, '0')}</span>
              </div>
              <div className="mobile-stat-item">
                <span className="mobile-stat-label">Venda</span>
                <span className="mobile-stat-value sell">{String(sellSignals).padStart(2, '0')}</span>
              </div>
            </div>
          </div>

          {/* Seção de Cards dos Sinais (Scrollável) */}
          <div className={styles.cardsContainer}>
            {/* Lista de Sinais */}
            {loading && <div className={styles.loadingMessage}>Carregando sinais...</div>}
            {error && <div className={styles.errorMessage}>Erro ao carregar sinais: {error}</div>}
            {!loading && !error && signals.length === 0 && (
              <div className={styles.noSignalsMessage}>Nenhum sinal encontrado.</div>
            )}
            {!loading && !error && signals.length > 0 && (
              <div className={styles.signalsList}>
                {signals.map((signal, index) => (
                  <SignalCard
                    key={index}
                    symbol={signal.symbol}
                    type={signal.type}
                    entryPrice={String(signal.entry_price)}
                    targetPrice={String(signal.target_price)}
                    projectionPercentage={String(signal.projection_percentage)}
                    date={signal.entry_time}
                    signalClass={signal.signal_class}
                    onToggleFavorite={() => toggleFavorite(index)}
                    isFavorite={signal.is_favorite || false}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}


export default DashboardPage;