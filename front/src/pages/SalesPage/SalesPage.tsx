import React, { useState, useEffect, lazy, Suspense } from 'react';
import styled from 'styled-components';

// Lazy loading para componentes não críticos
const LazyFooter = lazy(() => Promise.resolve({ default: () => (
  <FooterSection>
    <FooterContent>
      <FooterLinks>
        <FooterLink href="/privacy-policy">Política de Privacidade</FooterLink>
        <FooterLink href="/terms-of-service">Termos de Serviço</FooterLink>
      </FooterLinks>
      
      <FooterText>
        © 1Crypten. Todos os direitos reservados.
      </FooterText>
      
      {/* Disclaimer do Facebook (escondido) */}
      <FacebookDisclaimer>
        Este site não é afiliado ao Facebook ou a qualquer entidade do Facebook. 
        Uma vez que você sair do Facebook, a responsabilidade não é deles e sim do nosso site. 
        Fazemos todos os esforços para indicar claramente e mostrar todas as provas do produto 
        e usamos resultados reais. Nós não vendemos o seu e-mail ou qualquer informação para 
        terceiros. Jamais fazemos nenhum tipo de spam. Se você tiver alguma dúvida, sinta-se 
        à vontade para usar o link de contato e falar conosco em horário comercial de 
        Segunda a Sextas das 09h00 às 18h00. Lemos e respondemos todas as mensagens por ordem de chegada.
      </FacebookDisclaimer>
    </FooterContent>
  </FooterSection>
) }));

// Loading skeleton para o rodapé
const FooterSkeleton = () => (
  <FooterSection>
    <FooterContent>
      <div style={{ height: '120px', background: 'rgba(255,255,255,0.1)', borderRadius: '8px', animation: 'pulse 1.5s ease-in-out infinite' }} />
    </FooterContent>
  </FooterSection>
);

// Loading skeleton para vídeo
const VideoSkeleton = () => (
  <VideoContainer isFullscreen={false} isMobile={false}>
    <div style={{ 
      width: '100%', 
      height: '100%', 
      background: 'linear-gradient(90deg, rgba(255,255,255,0.1) 25%, rgba(255,255,255,0.2) 50%, rgba(255,255,255,0.1) 75%)',
      backgroundSize: '200% 100%',
      animation: 'shimmer 2s infinite',
      borderRadius: '8px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      color: 'rgba(255,255,255,0.6)',
      fontSize: '1.2rem'
    }}>
      Carregando vídeo...
    </div>
  </VideoContainer>
);

// Loading skeleton para botão
const ButtonSkeleton = () => (
  <div style={{
    width: '100%',
    maxWidth: '400px',
    height: '80px',
    background: 'rgba(255,255,255,0.1)',
    borderRadius: '12px',
    animation: 'pulse 1.5s ease-in-out infinite'
  }} />
);

// Interfaces para configurações do admin
interface HeadlineConfig {
  id: number;
  title: string;
  subtitle: string;
  active: boolean;
  highlightColor: 'red' | 'blue' | 'orange';
  testResults: {
    views: number;
    clicks: number;
    conversionRate: number;
    lastTested: string;
  };
}

interface ButtonConfig {
  id: number;
  text: string;
  color: string;
  backgroundColor: string;
  link: string;
  active: boolean;
}

interface DelayConfig {
  enabled: boolean;
  delaySeconds: number;
}

interface VideoOverlayConfig {
  id: number;
  style: 'classic' | 'modern' | 'minimal';
  message: string;
  active: boolean;
}

interface VideoConfig {
  videoUrl: string;
  autoplay: boolean;
  muted: boolean;
  showOverlay: boolean;
}

interface ProgressBarConfig {
  primaryColor: string;
  secondaryColor: string;
  backgroundColor: string;
}

interface VideoMetrics {
  totalWatchTime: number;
  pauseCount: number;
  resumeCount: number;
  completionRate: number;
}

/**
 * Componente da página de venda com estrutura baseada no desenho técnico
 * Inclui: headline, vídeo, botão com delay e rodapé
 */
const SalesPage: React.FC = () => {
  const [showButton, setShowButton] = useState(false);
  const [countdown, setCountdown] = useState(180); // 3 minutos padrão
  const [activeHeadline, setActiveHeadline] = useState<HeadlineConfig | null>(null);
  const [activeButton, setActiveButton] = useState<ButtonConfig | null>({
    id: 1,
    text: '🚀 QUERO ACESSO AGORA',
    color: '#ffffff',
    backgroundColor: '#ff6b35',
    link: '/checkout/despertar-crypto',
    active: true
  });
  const [delayConfig, setDelayConfig] = useState<DelayConfig>({ enabled: true, delaySeconds: 180 });
  const [videoMuted, setVideoMuted] = useState(true);
  const [showVideoOverlay, setShowVideoOverlay] = useState(true);
  const [activeVideoOverlay, setActiveVideoOverlay] = useState<VideoOverlayConfig | null>(null);
  const [videoConfig, setVideoConfig] = useState<VideoConfig>({
    videoUrl: '/vsl01.mp4',
    autoplay: false, // Desabilitar autoplay - vídeo só inicia com clique do usuário
    muted: true,
    showOverlay: true
  });
  
  // Debug: Log da configuração do vídeo
  useEffect(() => {
    console.log('🎬 Configuração atual do vídeo:', videoConfig);
  }, [videoConfig]);
  
  // Novos estados para funcionalidades avançadas
  const [isVideoPlaying, setIsVideoPlaying] = useState(false);
  const [showPauseBanner, setShowPauseBanner] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [videoProgress, setVideoProgress] = useState(0);
  const [videoDuration, setVideoDuration] = useState(0);
  const [videoCurrentTime, setVideoCurrentTime] = useState(0);
  const [progressBarConfig, setProgressBarConfig] = useState<ProgressBarConfig>({
    primaryColor: '#ff6b35',
    secondaryColor: '#ffa726',
    backgroundColor: 'rgba(255, 255, 255, 0.3)'
  });
  const [videoMetrics, setVideoMetrics] = useState<VideoMetrics>({
    totalWatchTime: 0,
    pauseCount: 0,
    resumeCount: 0,
    completionRate: 0
  });

  // Estados para otimização de performance
  const [isSlowConnection, setIsSlowConnection] = useState(false);
  const [isVideoLoaded, setIsVideoLoaded] = useState(true); // Iniciar como true para mostrar o vídeo
  const [connectionType, setConnectionType] = useState<string>('unknown');
  const [videoRef, setVideoRef] = useState<HTMLVideoElement | null>(null);

  /**
   * Lista expandida de palavras-chave para destacar com cores
   * Inclui termos de marketing, finanças, família e urgência
   */
  const highlightKeywords = [
    // Termos de Cripto e Trading
    'Segredos', 'Criptomoedas', 'Bitcoin', 'Trading', 'Crypto', 'BTC', 'ETH',
    'profissionais', 'lucros', 'consistentes', 'estratégias', 'gerar',
    'mercado', 'dinheiro', 'ganhar', 'transforme', 'método', 'comprovado',
    'iniciante', 'sistema', 'passo', 'lucrar', 'investir', 'renda',
    
    // Valores e Quantias
    'milhões', 'milhares', 'R$', 'reais', 'dólares', 'USD', 'BRL',
    '1.000', '10.000', '100.000', '1.000.000',
    
    // Família e Proteção
    'pai', 'família', 'proteger', 'futuro', 'financeiro', 'fé', 'estratégia',
    'segurança', 'proteção', 'filhos', 'esposa', 'casa', 'patrimônio',
    'aposentadoria', 'independência', 'liberdade', 'tranquilidade',
    
    // Urgência e Escassez
    'acesso', 'vaga', 'limitada', 'oferta', 'agora', 'hoje', 'urgente',
    'exclusivo', 'especial', 'único', 'garantido', 'certeza', 'sucesso',
    'últimas', 'vagas', 'apenas', 'somente', 'restam', 'tempo', 'limitado',
    
    // Resultados e Benefícios
    'resultados', 'rápido', 'fácil', 'simples', 'automático', 'passivo',
    'extra', 'adicional', 'multiplicar', 'dobrar', 'triplicar',
    'oportunidade', 'chance', 'momento', 'ideal', 'perfeito',
    
    // Emocionais e Persuasivos
    'descobrir', 'revelar', 'segredo', 'verdade', 'real', 'verdadeiro',
    'poderoso', 'incrível', 'surpreendente', 'impressionante',
    'revolucionário', 'inovador', 'exclusivo', 'premium'
  ];

  /**
   * Função para destacar palavras-chave com cor configurável
   */
  const highlightText = (text: string, color: 'red' | 'blue' | 'orange' = 'red'): string => {
    if (!text) return '';
    
    const colorMap = {
      red: '#ff3333',
      blue: '#2196f3', 
      orange: '#ff9800'
    };
    
    let highlightedText = text;
    highlightKeywords.forEach(keyword => {
      const regex = new RegExp(`\\b(${keyword})\\b`, 'gi');
      highlightedText = highlightedText.replace(
        regex, 
        `<span style="color: ${colorMap[color]}; font-weight: 900;">$1</span>`
      );
    });
    
    return highlightedText;
  };

  /**
   * Registra uma visualização para métricas A/B Test
   */
  const trackView = () => {
    if (activeHeadline && activeButton) {
      const savedConfig = localStorage.getItem('salesPageConfig');
      if (savedConfig) {
        try {
          const config = JSON.parse(savedConfig);
          
          // Atualiza métricas da headline individual
          if (config.headlines) {
            const updatedHeadlines = config.headlines.map((h: HeadlineConfig) => 
              h.id === activeHeadline.id 
                ? { ...h, testResults: { ...h.testResults, views: h.testResults.views + 1 } }
                : h
            );
            config.headlines = updatedHeadlines;
          }
          
          // Registra resultado da combinação se o teste de combinações estiver ativo
          if (config.abTestConfig?.testAllCombinations) {
            const combinationResults = config.combinationResults || [];
            const existingIndex = combinationResults.findIndex(
              (r: any) => r.headlineId === activeHeadline.id && r.buttonId === activeButton.id
            );
            
            if (existingIndex >= 0) {
              combinationResults[existingIndex].views += 1;
              combinationResults[existingIndex].conversionRate = 
                combinationResults[existingIndex].views > 0 
                  ? (combinationResults[existingIndex].clicks / combinationResults[existingIndex].views) * 100 
                  : 0;
              combinationResults[existingIndex].lastTested = new Date().toISOString();
            } else {
              combinationResults.push({
                headlineId: activeHeadline.id,
                buttonId: activeButton.id,
                views: 1,
                clicks: 0,
                conversionRate: 0,
                lastTested: new Date().toISOString(),
                headlineTitle: activeHeadline.title.substring(0, 30) + '...',
                buttonText: activeButton.text.substring(0, 20) + '...'
              });
            }
            
            config.combinationResults = combinationResults;
          }
          
          localStorage.setItem('salesPageConfig', JSON.stringify(config));
        } catch (error) {
          console.error('Erro ao registrar view:', error);
        }
      }
    }
  };

  /**
   * Registra um clique no botão para métricas A/B Test
   */
  const trackClick = () => {
    if (activeHeadline && activeButton) {
      const savedConfig = localStorage.getItem('salesPageConfig');
      if (savedConfig) {
        try {
          const config = JSON.parse(savedConfig);
          
          // Atualiza métricas da headline individual
          if (config.headlines) {
            const updatedHeadlines = config.headlines.map((h: HeadlineConfig) => 
              h.id === activeHeadline.id 
                ? { 
                    ...h, 
                    testResults: { 
                      ...h.testResults, 
                      clicks: h.testResults.clicks + 1,
                      conversionRate: h.testResults.views > 0 
                        ? ((h.testResults.clicks + 1) / h.testResults.views) * 100 
                        : 0
                    } 
                  }
                : h
            );
            config.headlines = updatedHeadlines;
          }
          
          // Registra clique da combinação se o teste de combinações estiver ativo
          if (config.abTestConfig?.testAllCombinations) {
            const combinationResults = config.combinationResults || [];
            const existingIndex = combinationResults.findIndex(
              (r: any) => r.headlineId === activeHeadline.id && r.buttonId === activeButton.id
            );
            
            if (existingIndex >= 0) {
              combinationResults[existingIndex].clicks += 1;
              combinationResults[existingIndex].conversionRate = 
                combinationResults[existingIndex].views > 0 
                  ? (combinationResults[existingIndex].clicks / combinationResults[existingIndex].views) * 100 
                  : 0;
              combinationResults[existingIndex].lastTested = new Date().toISOString();
            } else {
              // Se não existe, cria com 1 click (caso raro)
              combinationResults.push({
                headlineId: activeHeadline.id,
                buttonId: activeButton.id,
                views: 0,
                clicks: 1,
                conversionRate: 0,
                lastTested: new Date().toISOString(),
                headlineTitle: activeHeadline.title.substring(0, 30) + '...',
                buttonText: activeButton.text.substring(0, 20) + '...'
              });
            }
            
            config.combinationResults = combinationResults;
          }
          
          localStorage.setItem('salesPageConfig', JSON.stringify(config));
        } catch (error) {
          console.error('Erro ao registrar click:', error);
        }
      }
    }
  };

  /**
   * Função para detectar se é dispositivo móvel
   */
  const detectMobile = () => {
    const userAgent = navigator.userAgent || navigator.vendor;
    return /android|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(userAgent.toLowerCase()) || window.innerWidth <= 768;
  };

  /**
   * Função para detectar conexão lenta e ajustar qualidade
   */
  const detectConnectionSpeed = () => {
    // @ts-ignore - Navigator connection API
    const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    
    if (connection) {
      const { effectiveType, downlink, rtt } = connection;
      setConnectionType(effectiveType || 'unknown');
      
      // Considera conexão lenta se:
      // - Effective type é 'slow-2g' ou '2g'
      // - Downlink menor que 1.5 Mbps
      // - RTT maior que 300ms
      const isSlow = effectiveType === 'slow-2g' || 
                     effectiveType === '2g' || 
                     downlink < 1.5 || 
                     rtt > 300;
      
      setIsSlowConnection(isSlow);
      
      // Ajustar configurações baseado na conexão
      if (isSlow) {
        // Para conexões lentas, manter o mesmo vídeo mas com configurações otimizadas
        console.log('Conexão lenta detectada - mantendo vídeo original');
        // Removido fallback para versão de baixa qualidade pois não existe vsl01_low.mp4
      }
    } else {
      // Fallback: detectar baseado no tempo de carregamento
      const startTime = performance.now();
      const img = new Image();
      img.onload = () => {
        const loadTime = performance.now() - startTime;
        setIsSlowConnection(loadTime > 1000); // Se demorar mais de 1s para carregar uma imagem pequena
      };
      img.src = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'; // 1x1 pixel
    }
  };

  /**
   * Função para ativar o áudio do vídeo quando o usuário clica no overlay
   */
  const handleVideoUnmute = () => {
    setVideoMuted(false);
    setShowVideoOverlay(false);
    setIsVideoPlaying(true);
    
    // Se for mobile, ativa fullscreen
    if (isMobile && videoRef) {
      enterFullscreen();
    }
    
    // SEMPRE reinicia o vídeo do início quando usuário clica
    if (videoRef) {
      videoRef.currentTime = 0; // Reinicia do início
      videoRef.play();
    }
  };

  /**
   * Função para entrar em fullscreen customizado no mobile
   * Usa fullscreen customizado para manter todos os controles da página de vendas
   */
  const enterFullscreen = () => {
    // Usar fullscreen customizado ao invés do nativo para manter controles
    setIsFullscreen(true);
    
    // Desabilitar scroll do body quando em fullscreen
    document.body.style.overflow = 'hidden';
  };

  /**
   * Função para sair do fullscreen customizado
   */
  const exitFullscreen = () => {
    setIsFullscreen(false);
    
    // Restaurar scroll do body
    document.body.style.overflow = 'auto';
  };

  /**
   * Função para controlar play/pause do vídeo
   */
  const handleVideoPlayPause = () => {
    if (!videoRef) return;
    
    if (isVideoPlaying) {
      videoRef.pause();
      setIsVideoPlaying(false);
      setShowPauseBanner(true);
      setVideoMetrics(prev => ({ ...prev, pauseCount: prev.pauseCount + 1 }));
    } else {
      videoRef.play();
      setIsVideoPlaying(true);
      setShowPauseBanner(false);
      setVideoMetrics(prev => ({ ...prev, resumeCount: prev.resumeCount + 1 }));
    }
  };

  /**
   * Função para calcular progresso inteligente da barra
   */
  const calculateSmartProgress = (currentTime: number, duration: number) => {
    if (duration === 0) return 0;
    
    const normalProgress = currentTime / duration;
    
    // Progresso inteligente: rápido no início (primeiros 20%), lento depois
    if (normalProgress <= 0.2) {
      // Nos primeiros 20% do vídeo, a barra avança mais rápido (2x)
      return (normalProgress / 0.2) * 0.4; // 40% da barra nos primeiros 20% do vídeo
    } else {
      // Nos 80% restantes, a barra avança mais devagar
      const remainingProgress = (normalProgress - 0.2) / 0.8;
      return 0.4 + (remainingProgress * 0.6); // 60% da barra nos 80% restantes
    }
  };

  /**
   * Função para atualizar métricas do vídeo
   */
  const updateVideoMetrics = (currentTime: number, duration: number) => {
    const completionRate = duration > 0 ? (currentTime / duration) * 100 : 0;
    setVideoMetrics(prev => ({
      ...prev,
      totalWatchTime: currentTime,
      completionRate
    }));
  };

  /**
   * Função para carregar configurações padrão de overlay de vídeo
   */
  const loadVideoOverlayConfig = () => {
     // Configurações padrão dos overlays (usado apenas se não houver config salva)
     const defaultOverlays: VideoOverlayConfig[] = [
       {
         id: 1,
         style: 'classic',
         message: 'Seu vídeo já começou\nClique para assistir',
         active: true
       },
       {
         id: 2,
         style: 'modern',
         message: 'Clique para ouvir',
         active: false
       },
       {
         id: 3,
         style: 'minimal',
         message: 'CLIQUE PARA OUVIR',
         active: false
       }
     ];

     const activeOverlay = defaultOverlays.find(overlay => overlay.active);
     if (activeOverlay) {
       setActiveVideoOverlay(activeOverlay);
     }
   };

  /**
   * Carrega as configurações do admin do localStorage
   */
  /**
   * Função para carregar configurações do localStorage
   */
  const loadConfigFromStorage = () => {
    const savedConfig = localStorage.getItem('salesPageConfig');
    if (savedConfig) {
      try {
        const config = JSON.parse(savedConfig);
        
        // Encontra a headline ativa
        if (config.headlines) {
          const activeHeadlineConfig = config.headlines.find((h: HeadlineConfig) => h.active);
          if (activeHeadlineConfig) {
            setActiveHeadline(activeHeadlineConfig);
          }
        }
        
        // Encontra o botão ativo
        if (config.buttons) {
          const activeButtonConfig = config.buttons.find((b: ButtonConfig) => b.active);
          if (activeButtonConfig) {
            setActiveButton(activeButtonConfig);
          }
        }
        
        // Configura o delay
        if (config.delayConfig) {
          setDelayConfig(config.delayConfig);
          setCountdown(config.delayConfig.delaySeconds);
        }
        
        // Carrega configurações de vídeo overlay
        if (config.videoOverlays && Array.isArray(config.videoOverlays)) {
          const activeOverlay = config.videoOverlays.find((o: VideoOverlayConfig) => o.active);
          if (activeOverlay) {
            setActiveVideoOverlay(activeOverlay);
            console.log('Overlay carregado:', activeOverlay); // Debug
          }
        }
        
        // Carrega configurações de vídeo (sempre forçar vsl01.mp4)
        if (config.videoConfig) {
          // Força o vídeo correto independente da configuração salva
          setVideoConfig({
            ...config.videoConfig,
            videoUrl: '/vsl01.mp4'
          });
        }
        
        // Carrega configurações da barra de progresso
        if (config.progressBarConfig) {
          setProgressBarConfig(config.progressBarConfig);
        }
        
        // Carrega métricas do vídeo
        if (config.videoMetrics) {
          setVideoMetrics(config.videoMetrics);
        }
      } catch (error) {
        console.error('Erro ao carregar configurações:', error);
      }
    }
  };

  // Carrega configurações na inicialização
  useEffect(() => {
    loadConfigFromStorage();
  }, []);

  // Listener para detectar mudanças no localStorage (quando admin salva)
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'salesPageConfig') {
        console.log('Configurações atualizadas, recarregando...'); // Debug
        loadConfigFromStorage();
      }
    };

    // Listener para mudanças no localStorage de outras abas
    window.addEventListener('storage', handleStorageChange);

    // Listener customizado para mudanças na mesma aba
    const handleCustomStorageChange = () => {
      console.log('Configurações atualizadas na mesma aba, recarregando...'); // Debug
      loadConfigFromStorage();
    };

    window.addEventListener('salesConfigUpdated', handleCustomStorageChange);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('salesConfigUpdated', handleCustomStorageChange);
    };
  }, []);

  useEffect(() => {
    if (!delayConfig.enabled) {
      setShowButton(true);
      return;
    }

    const timer = setInterval(() => {
      setCountdown(prev => {
        if (prev <= 1) {
          setShowButton(true);
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [delayConfig]);

  // Registra view quando a página carrega
  useEffect(() => {
    const timer = setTimeout(() => {
      trackView();
    }, 2000); // Aguarda 2 segundos para considerar uma view válida
    
    return () => clearTimeout(timer);
  }, [activeHeadline]);

  // Carrega configurações padrão de overlay de vídeo se não houver config salva
    useEffect(() => {
      if (!activeVideoOverlay) {
        loadVideoOverlayConfig();
      }
    }, [activeVideoOverlay]);

  // Detecta se é mobile na inicialização
  useEffect(() => {
    setIsMobile(detectMobile());
    detectConnectionSpeed(); // Detectar velocidade da conexão
    
    const handleResize = () => {
      setIsMobile(detectMobile());
    };
    
    // Monitorar mudanças na conexão
    // @ts-ignore
    const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    if (connection) {
      connection.addEventListener('change', detectConnectionSpeed);
    }
    
    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
      if (connection) {
        connection.removeEventListener('change', detectConnectionSpeed);
      }
    };
  }, []);

  // Gerencia eventos do vídeo
  useEffect(() => {
    if (!videoRef) return;

    const handleTimeUpdate = () => {
      const currentTime = videoRef.currentTime;
      const duration = videoRef.duration;
      
      setVideoCurrentTime(currentTime);
      setVideoDuration(duration);
      
      // Calcula progresso inteligente
      const smartProgress = calculateSmartProgress(currentTime, duration);
      setVideoProgress(smartProgress);
      
      // Atualiza métricas
      updateVideoMetrics(currentTime, duration);
    };

    const handlePlay = () => {
      setIsVideoPlaying(true);
      setShowPauseBanner(false);
    };

    const handlePause = () => {
      setIsVideoPlaying(false);
      setShowPauseBanner(true);
    };

    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    videoRef.addEventListener('timeupdate', handleTimeUpdate);
    videoRef.addEventListener('play', handlePlay);
    videoRef.addEventListener('pause', handlePause);
    document.addEventListener('fullscreenchange', handleFullscreenChange);

    return () => {
      videoRef.removeEventListener('timeupdate', handleTimeUpdate);
      videoRef.removeEventListener('play', handlePlay);
      videoRef.removeEventListener('pause', handlePause);
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
    };
  }, [videoRef]);

  // Detecta se é mobile na inicialização
  useEffect(() => {
    setIsMobile(detectMobile());
    
    const handleResize = () => {
      setIsMobile(detectMobile());
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Controla eventos do vídeo
  useEffect(() => {
    if (!videoRef) return;

    const handleLoadedMetadata = () => {
      setVideoDuration(videoRef.duration);
    };

    const handleTimeUpdate = () => {
      const currentTime = videoRef.currentTime;
      const duration = videoRef.duration;
      
      setVideoCurrentTime(currentTime);
      setVideoProgress(calculateSmartProgress(currentTime, duration));
      updateVideoMetrics(currentTime, duration);
    };

    const handlePlay = () => {
      setIsVideoPlaying(true);
      setShowPauseBanner(false);
    };

    const handlePause = () => {
      setIsVideoPlaying(false);
      setShowPauseBanner(true);
    };

    const handleEnded = () => {
      setIsVideoPlaying(false);
      setVideoProgress(1);
      setVideoMetrics(prev => ({ ...prev, completionRate: 100 }));
    };

    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    videoRef.addEventListener('loadedmetadata', handleLoadedMetadata);
    videoRef.addEventListener('timeupdate', handleTimeUpdate);
    videoRef.addEventListener('play', handlePlay);
    videoRef.addEventListener('pause', handlePause);
    videoRef.addEventListener('ended', handleEnded);
    document.addEventListener('fullscreenchange', handleFullscreenChange);

    return () => {
      videoRef.removeEventListener('loadedmetadata', handleLoadedMetadata);
      videoRef.removeEventListener('timeupdate', handleTimeUpdate);
      videoRef.removeEventListener('play', handlePlay);
      videoRef.removeEventListener('pause', handlePause);
      videoRef.removeEventListener('ended', handleEnded);
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
    };
  }, [videoRef]);

  return (
    <PageContainer>
      {/* Seção de Headline */}
      <HeadlineSection>
        <HeadlineContainer>
          <Headline>
            {activeHeadline ? (
              <span dangerouslySetInnerHTML={{ 
                __html: highlightText(activeHeadline.title, activeHeadline.highlightColor)
              }} />
            ) : (
              <>Descubra os <RedText>Segredos</RedText> do Trading de <RedText>Criptomoedas</RedText></>
            )}
          </Headline>
          <SubHeadline>
            {activeHeadline ? (
              <span dangerouslySetInnerHTML={{ 
                __html: highlightText(activeHeadline.subtitle, activeHeadline.highlightColor)
              }} />
            ) : (
              <>Aprenda as estratégias que os <RedText>profissionais</RedText> usam para gerar <RedText>lucros consistentes</RedText> no mercado cripto</>
            )}
          </SubHeadline>
        </HeadlineContainer>
      </HeadlineSection>

      {/* Seção de Vídeo */}
      <VideoSection>
        {!isVideoLoaded ? (
          <VideoSkeleton />
        ) : (
          <VideoContainer isFullscreen={isFullscreen} isMobile={isMobile}>
            {/* Banner de conexão lenta removido conforme solicitado */}
            <VideoPlayer
              ref={(ref) => setVideoRef(ref)}
              src={videoConfig.videoUrl}
              autoPlay={videoConfig.autoplay}
              muted={videoMuted}
              loop
              playsInline
              controls={false}
              controlsList="nodownload nofullscreen noremoteplayback"
              disablePictureInPicture
              disableRemotePlayback
              onClick={handleVideoPlayPause}
              isFullscreen={isFullscreen}
              isMobile={isMobile}
              onLoadedData={() => {
                console.log('✅ Vídeo carregado com sucesso!');
                setIsVideoLoaded(true);
              }}
              onLoadStart={() => {
                console.log('🎬 Iniciando carregamento do vídeo:', videoConfig.videoUrl);
              }}
              onError={(e) => {
                console.error('❌ Erro ao carregar vídeo:', e.target.error);
                console.log('🔍 URL do vídeo:', videoConfig.videoUrl);
              }}
              onAbort={() => {
                console.warn('⚠️ Carregamento do vídeo foi abortado');
              }}
              onCanPlay={() => {
                console.log('▶️ Vídeo pronto para reproduzir');
              }}
            />
            
            {/* Botão de fechar fullscreen removido conforme solicitado */}
          
          {/* Barra de progresso inteligente */}
          <ProgressBar isFullscreen={isFullscreen} isMobile={isMobile}>
            <ProgressBarBackground backgroundColor={progressBarConfig.backgroundColor}>
              <ProgressBarFill 
                progress={videoProgress}
                primaryColor={progressBarConfig.primaryColor}
                secondaryColor={progressBarConfig.secondaryColor}
              />
            </ProgressBarBackground>
          </ProgressBar>
          
          {showVideoOverlay && activeVideoOverlay && (
            <VideoOverlay 
              overlayStyle={activeVideoOverlay.style}
              onClick={handleVideoUnmute}
            >
              <OverlayContent overlayStyle={activeVideoOverlay.style}>
                {activeVideoOverlay.style === 'classic' && (
                  <>
                    <SpeakerIcon>🔊</SpeakerIcon>
                    <OverlayMessage overlayStyle={activeVideoOverlay.style}>
                      {activeVideoOverlay.message.split('\n').map((line, index) => (
                        <div key={index}>{line}</div>
                      ))}
                    </OverlayMessage>
                  </>
                )}
                
                {activeVideoOverlay.style === 'modern' && (
                  <>
                    <PlayButton>
                      <PlayButtonIcon>▶</PlayButtonIcon>
                    </PlayButton>
                    <OverlayMessage overlayStyle={activeVideoOverlay.style}>
                      {activeVideoOverlay.message}
                    </OverlayMessage>
                  </>
                )}
                
                {activeVideoOverlay.style === 'minimal' && (
                  <OverlayMessage overlayStyle={activeVideoOverlay.style}>
                    {activeVideoOverlay.message}
                  </OverlayMessage>
                )}
              </OverlayContent>
            </VideoOverlay>
          )}
          
          {/* Banner de incentivo quando pausar */}
          {showPauseBanner && !showVideoOverlay && (
            <PauseBanner>
              <PauseBannerContent>
                <PauseBannerIcon>⏸️</PauseBannerIcon>
                <PauseBannerTitle>Vídeo Pausado</PauseBannerTitle>
                <PauseBannerMessage>
                  Continue assistindo para descobrir como <strong>multiplicar seus ganhos</strong> com estratégias exclusivas!
                </PauseBannerMessage>
                <PauseBannerButton onClick={handleVideoPlayPause}>
                  ▶ Continuar Assistindo
                </PauseBannerButton>
              </PauseBannerContent>
            </PauseBanner>
          )}
          
          {/* CTA Overlay - aparece sobreposto na parte inferior do vídeo */}
          {showButton && (
            <CTAOverlay isFullscreen={isFullscreen} isMobile={isMobile}>
              <CTAButton
                as="a"
                href={activeButton?.link || '/checkout/despertar-crypto'}
                buttonColor={activeButton?.backgroundColor || '#ff6b35'}
              >
                <CTAButtonContent>
                  <CTAButtonText>{activeButton?.text || '🚀 QUERO ACESSO AGORA'}</CTAButtonText>
                </CTAButtonContent>
              </CTAButton>
            </CTAOverlay>
          )}
          </VideoContainer>
        )}
        
        {/* Placeholder para manter espaçamento quando botão não aparece */}
        {!showButton && <ButtonPlaceholder />}
      </VideoSection>

      {/* Rodapé com Lazy Loading - Oculto em fullscreen mobile */}
      {!(isFullscreen && isMobile) && (
        <Suspense fallback={<FooterSkeleton />}>
          <LazyFooter />
        </Suspense>
      )}
    </PageContainer>
  );
};

// Styled Components
const PageContainer = styled.div`
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #000000;
`;

const HeadlineSection = styled.section`
  background: #000000;
  padding: 4rem 2rem;
  text-align: center;
  color: white;
  position: relative;
  overflow: hidden;
  
  @media (max-width: 768px) {
    padding: 3rem 1rem;
  }
  
  @media (max-width: 480px) {
    padding: 2rem 0.5rem;
  }
`;

const HeadlineContainer = styled.div`
  position: relative;
  z-index: 2;
  max-width: 800px;
  margin: 0 auto;
`;

const Headline = styled.h1`
  font-size: 3.5rem;
  font-weight: 800;
  color: white;
  margin: 0 0 1.5rem 0;
  line-height: 1.1;
  letter-spacing: -0.02em;
  word-wrap: break-word;
  hyphens: auto;
  
  @media (max-width: 768px) {
    font-size: 2.2rem;
    line-height: 1.2;
    padding: 0 1rem;
  }
  
  @media (max-width: 480px) {
    font-size: 1.8rem;
    line-height: 1.3;
    padding: 0 0.5rem;
  }
  
  @media (max-width: 360px) {
    font-size: 1.6rem;
    line-height: 1.4;
  }
`;

const RedText = styled.span`
  color: #ff3333;
  font-weight: 900;
`;

const SubHeadline = styled.p`
  font-size: 1.4rem;
  color: rgba(255, 255, 255, 0.95);
  margin: 0;
  line-height: 1.4;
  font-weight: 400;
  word-wrap: break-word;
  hyphens: auto;
  
  @media (max-width: 768px) {
    font-size: 1.1rem;
    line-height: 1.5;
    padding: 0 1rem;
  }
  
  @media (max-width: 480px) {
    font-size: 1rem;
    line-height: 1.6;
    padding: 0 0.5rem;
  }
  
  @media (max-width: 360px) {
    font-size: 0.95rem;
    line-height: 1.7;
  }
`;

const VideoSection = styled.section`
  flex: 1;
  background-color: #000;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  gap: 2rem;
`;

const VideoContainer = styled.div.withConfig({
  shouldForwardProp: (prop) => prop !== 'isFullscreen' && prop !== 'isMobile'
})<{ isFullscreen: boolean; isMobile: boolean }>`
  width: 100%;
  max-width: 800px;
  aspect-ratio: 16/9;
  background-color: #1a1a1a;
  border: 2px solid #333;
  border-radius: 8px;
  position: relative;
  overflow: hidden;
  
  ${props => props.isFullscreen && props.isMobile && `
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: calc(100vh - 100px);
    max-width: none;
    aspect-ratio: unset;
    border-radius: 0;
    border: none;
    z-index: 9999;
    display: flex;
    flex-direction: column;
  `}
`;

const VideoPlayer = styled.video.withConfig({
  shouldForwardProp: (prop) => prop !== 'isFullscreen' && prop !== 'isMobile'
})<{ isFullscreen: boolean; isMobile: boolean }>`
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 6px;
  cursor: pointer;
  
  ${props => props.isFullscreen && props.isMobile && `
    object-fit: cover;
    border-radius: 0;
  `}
`;

// Barra de progresso inteligente
const ProgressBar = styled.div.withConfig({
  shouldForwardProp: (prop) => prop !== 'isFullscreen' && prop !== 'isMobile'
})<{ isFullscreen?: boolean; isMobile?: boolean }>`
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 4px;
  z-index: 10010;
  
  ${props => props.isFullscreen && props.isMobile && `
    position: fixed;
    bottom: 80px;
    z-index: 10020;
  `}
`;

const ProgressBarBackground = styled.div.withConfig({
  shouldForwardProp: (prop) => prop !== 'backgroundColor'
})<{ backgroundColor: string }>`
  width: 100%;
  height: 100%;
  background: ${props => props.backgroundColor};
`;

const ProgressBarFill = styled.div.withConfig({
  shouldForwardProp: (prop) => prop !== 'progress' && prop !== 'primaryColor' && prop !== 'secondaryColor'
})<{ progress: number; primaryColor: string; secondaryColor: string }>`
  width: ${props => props.progress * 100}%;
  height: 100%;
  background: linear-gradient(90deg, ${props => props.primaryColor}, ${props => props.secondaryColor});
  transition: width 0.3s ease;
  position: relative;
  
  &::after {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 2px;
    height: 100%;
    background: white;
    box-shadow: 0 0 4px rgba(255, 255, 255, 0.8);
  }
`;

// Banner de incentivo quando pausar
const PauseBanner = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10015; /* Z-index alto para funcionar em fullscreen */
  cursor: pointer;
  backdrop-filter: blur(5px);
`;

const PauseBannerContent = styled.div`
  text-align: center;
  color: white;
  padding: 2rem;
  max-width: 400px;
  animation: fadeInScale 0.5s ease-out;
  
  @keyframes fadeInScale {
    from {
      opacity: 0;
      transform: scale(0.9);
    }
    to {
      opacity: 1;
      transform: scale(1);
    }
  }
`;

const PauseBannerIcon = styled.div`
  font-size: 3rem;
  margin-bottom: 1rem;
  animation: pulse 2s infinite;
  
  @keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.1); }
  }
`;

const PauseBannerTitle = styled.h3`
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0 0 1rem 0;
  color: #ff6b35;
`;

const PauseBannerMessage = styled.p`
  font-size: 1rem;
  line-height: 1.5;
  margin: 0 0 1.5rem 0;
  color: rgba(255, 255, 255, 0.9);
  
  strong {
    color: #ff6b35;
    font-weight: 700;
  }
`;

const PauseBannerButton = styled.button`
  background: linear-gradient(135deg, #ff6b35, #ffa726);
  border: none;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 25px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(255, 107, 53, 0.4);
  }
  
  &:active {
    transform: translateY(0);
  }
`;

const VideoOverlay = styled.div.withConfig({
  shouldForwardProp: (prop) => prop !== 'overlayStyle'
})<{ overlayStyle: string }>`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: ${props => {
    switch (props.overlayStyle) {
      case 'classic':
        return 'rgba(0, 0, 0, 0.7)';
      case 'modern':
        return 'rgba(0, 0, 0, 0.5)';
      case 'minimal':
        return 'rgba(0, 0, 0, 0.3)';
      default:
        return 'rgba(0, 0, 0, 0.6)';
    }
  }};
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: ${props => {
      switch (props.overlayStyle) {
        case 'classic':
          return 'rgba(0, 0, 0, 0.8)';
        case 'modern':
          return 'rgba(0, 0, 0, 0.6)';
        case 'minimal':
          return 'rgba(0, 0, 0, 0.4)';
        default:
          return 'rgba(0, 0, 0, 0.7)';
      }
    }};
  }
`;

const OverlayContent = styled.div.withConfig({
  shouldForwardProp: (prop) => prop !== 'overlayStyle'
})<{ overlayStyle: string }>`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: ${props => props.overlayStyle === 'minimal' ? '0' : '1rem'};
  text-align: center;
  padding: 2rem;
`;

const SpeakerIcon = styled.div`
  font-size: 3rem;
  margin-bottom: 0.5rem;
  animation: pulse 2s infinite;
  
  @keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.1); }
    100% { transform: scale(1); }
  }
`;

const PlayButton = styled.div`
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  
  &:hover {
    background: white;
    transform: scale(1.1);
  }
`;

const PlayButtonIcon = styled.div`
  font-size: 2rem;
  color: #333;
  margin-left: 4px;
`;

const OverlayMessage = styled.div.withConfig({
  shouldForwardProp: (prop) => prop !== 'overlayStyle'
})<{ overlayStyle: string }>`
  color: white;
  font-weight: ${props => props.overlayStyle === 'minimal' ? '700' : '600'};
  font-size: ${props => {
    switch (props.overlayStyle) {
      case 'classic':
        return '1.2rem';
      case 'modern':
        return '1.1rem';
      case 'minimal':
        return '1.5rem';
      default:
        return '1.1rem';
    }
  }};
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);
  line-height: 1.4;
  
  ${props => props.overlayStyle === 'classic' && `
    background: rgba(0, 0, 0, 0.8);
    padding: 1rem 1.5rem;
    border-radius: 8px;
    border: 2px solid rgba(255, 255, 255, 0.3);
  `}
  
  ${props => props.overlayStyle === 'modern' && `
    background: linear-gradient(135deg, rgba(33, 150, 243, 0.9), rgba(33, 150, 243, 0.7));
    padding: 0.75rem 1.5rem;
    border-radius: 25px;
    border: 1px solid rgba(255, 255, 255, 0.2);
  `}
  
  ${props => props.overlayStyle === 'minimal' && `
    text-transform: uppercase;
    letter-spacing: 2px;
    font-family: 'Arial', sans-serif;
  `}
  
  @media (max-width: 768px) {
    font-size: ${props => {
      switch (props.overlayStyle) {
        case 'classic':
          return '1rem';
        case 'modern':
          return '0.9rem';
        case 'minimal':
          return '1.2rem';
        default:
          return '0.9rem';
      }
    }};
    padding: ${props => props.overlayStyle === 'classic' ? '0.75rem 1rem' : props.overlayStyle === 'modern' ? '0.5rem 1rem' : '0'};
  }
`;



const CloseFullscreenButton = styled.button`
  position: absolute;
  top: 20px;
  right: 20px;
  width: 50px;
  height: 50px;
  background: rgba(0, 0, 0, 0.7);
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  color: white;
  font-size: 1.5rem;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10025; /* Acima de todos os outros elementos */
  transition: all 0.3s ease;
  backdrop-filter: blur(5px);
  
  &:hover {
    background: rgba(255, 0, 0, 0.8);
    border-color: rgba(255, 255, 255, 0.6);
    transform: scale(1.1);
  }
  
  &:active {
    transform: scale(0.95);
  }
`;

const CTAOverlay = styled.div.withConfig({
  shouldForwardProp: (prop) => prop !== 'isFullscreen' && prop !== 'isMobile'
})<{ isFullscreen?: boolean; isMobile?: boolean }>`
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10020; /* Z-index alto para funcionar em fullscreen */
  width: 90%;
  max-width: 400px;
  
  ${props => props.isFullscreen && props.isMobile && `
    position: fixed;
    bottom: 10px;
    z-index: 10020;
    width: 90%;
    max-width: 350px;
  `}
  
  @media (max-width: 768px) {
    bottom: 15px;
    width: 85%;
    max-width: 350px;
  }
  
  @media (max-width: 480px) {
    bottom: 10px;
    width: 80%;
    max-width: 300px;
  }
`;

const CTAButton = styled.button.withConfig({
  shouldForwardProp: (prop) => prop !== 'buttonColor'
})<{ buttonColor: string }>`
  background: linear-gradient(135deg, ${props => props.buttonColor}, ${props => props.buttonColor}dd);
  border: 2px solid ${props => props.buttonColor};
  border-radius: 12px;
  padding: 0;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  animation: fadeInUp 0.6s ease-out;
  box-shadow: 
    0 8px 25px rgba(0, 0, 0, 0.15),
    0 4px 10px rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;
  text-decoration: none;
  display: block;
  max-width: 400px;
  width: 100%;
  
  &:before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transition: left 0.5s;
  }
  
  &:hover {
    transform: translateY(-4px) scale(1.02);
    box-shadow: 
      0 15px 35px rgba(0, 0, 0, 0.2),
      0 8px 15px rgba(0, 0, 0, 0.15),
      inset 0 1px 0 rgba(255, 255, 255, 0.2);
    border-color: ${props => props.buttonColor};
    
    &:before {
      left: 100%;
    }
  }
  
  &:active {
    transform: translateY(-2px) scale(0.98);
  }
  
  @keyframes fadeInUp {
    from {
      opacity: 0;
      transform: translateY(30px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  @media (max-width: 768px) {
    max-width: 350px;
  }
  
  @media (max-width: 480px) {
    max-width: 300px;
  }
`;

const CTAButtonContent = styled.div`
  padding: 1.2rem 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.3rem;
  position: relative;
  z-index: 1;
  
  @media (max-width: 768px) {
    padding: 1rem 1.5rem;
  }
  
  @media (max-width: 480px) {
    padding: 0.9rem 1.2rem;
  }
`;

const CTAButtonText = styled.span`
  color: white;
  font-size: 1rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  text-align: center;
  line-height: 1.2;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  
  @media (max-width: 768px) {
    font-size: 0.9rem;
  }
  
  @media (max-width: 480px) {
    font-size: 0.85rem;
    letter-spacing: 0.3px;
  }
`;

const CTAButtonSubtext = styled.span`
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.8rem;
  font-weight: 500;
  text-align: center;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  
  @media (max-width: 768px) {
    font-size: 0.75rem;
  }
  
  @media (max-width: 480px) {
    font-size: 0.7rem;
  }
`;

const ButtonPlaceholder = styled.div`
  height: 80px;
  width: 100%;
  max-width: 400px;
  
  @media (max-width: 768px) {
    height: 70px;
    max-width: 350px;
  }
  
  @media (max-width: 480px) {
    height: 65px;
    max-width: 300px;
  }
`;



const FooterSection = styled.footer`
  background-color: #000000; /* Fundo preto igual aos outros */
  color: #808080; /* Cor igual ao StandardFooter */
  padding: 40px 20px;
  font-size: 0.9em;
  border-top: 1px solid #333;
  margin-top: 40px;
`;

const FooterContent = styled.div`
  max-width: 1000px;
  margin: 0 auto;
  text-align: center;
`;

const FooterLinks = styled.div`
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  
  @media (max-width: 768px) {
    gap: 1rem;
    flex-direction: column;
    align-items: center;
  }
`;

const FooterLink = styled.a`
  color: #808080; /* Cor igual ao StandardFooter */
  text-decoration: none;
  font-size: 0.9em;
  
  &:hover {
    text-decoration: underline;
  }
`;

const FooterText = styled.p`
  color: #555; /* Cor do copyright igual ao StandardFooter */
  font-size: 0.8em;
  margin: 20px 0;
  text-align: center;
`;

const FacebookDisclaimer = styled.div`
  color: #555;
  font-size: 0.75rem;
  line-height: 1.4;
  margin-top: 2rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  text-align: left;
  max-width: 800px;
  margin: 2rem auto 0;
  opacity: 0.7;

  @media (max-width: 768px) {
    font-size: 0.7rem;
    padding: 0.8rem;
  }
`;

// Adicionar animações CSS globais para skeletons
const GlobalSkeletonStyles = `
  @keyframes pulse {
    0%, 100% {
      opacity: 1;
    }
    50% {
      opacity: 0.5;
    }
  }
  
  @keyframes shimmer {
    0% {
      background-position: -200% 0;
    }
    100% {
      background-position: 200% 0;
    }
  }
`;

// Injetar estilos globais
if (typeof document !== 'undefined') {
  const styleSheet = document.createElement('style');
  styleSheet.textContent = GlobalSkeletonStyles;
  document.head.appendChild(styleSheet);
}

export default SalesPage;