import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { ChevronLeft, ChevronRight, Play, Pause, RotateCcw, CheckCircle, Maximize, Minimize } from 'lucide-react';
import StandardFooter from '../../components/StandardFooter/StandardFooter';
import ProtectedLesson from '../../components/ProtectedLesson/ProtectedLesson';

// Importa os vídeos das aulas
import v1 from '../../assets/vdc/v1.mp4';
import v2 from '../../assets/vdc/v2.mp4';
import v3 from '../../assets/vdc/v3.mp4';
import v4 from '../../assets/vdc/v4.mp4';
import v5 from '../../assets/vdc/v5.mp4';
import v6 from '../../assets/vdc/v6.mp4';
import v7 from '../../assets/vdc/v7.mp4';
import v8 from '../../assets/vdc/v8.mp4';

// Styled Components para a página de aula
const AulaContainer = styled.div`
  min-height: 100vh;
  background: #000000;
  color: white;
  padding: 0;
  margin: 0;
`;

const Header = styled.header`
  background: rgba(0, 0, 0, 0.8);
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
`;

const BackButton = styled.button`
  background: transparent;
  border: 1px solid #2196f3;
  color: #2196f3;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
  
  &:hover {
    background: linear-gradient(135deg, #2196f3, #00bcd4);
    color: white;
    border-color: #00bcd4;
  }
`;

const ProgressBar = styled.div`
  flex: 1;
  margin: 0 2rem;
  background: rgba(255, 255, 255, 0.1);
  height: 8px;
  border-radius: 4px;
  overflow: hidden;
`;

const ProgressFill = styled.div<{ $progress: number }>`
  height: 100%;
  background: linear-gradient(90deg, #2196f3, #00bcd4);
  width: ${props => props.$progress}%;
  transition: width 0.3s ease;
`;

const CourseTitle = styled.h1`
  font-size: 1.2rem;
  margin: 0;
  background: linear-gradient(135deg, #2196f3, #00bcd4);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const MainContent = styled.div`
  display: grid;
  grid-template-columns: 1fr 350px;
  gap: 2rem;
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  
  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
`;

const VideoSection = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 2rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
`;

const VideoPlayer = styled.div`
  position: relative;
  width: 100%;
  aspect-ratio: 16/9;
  background: #000;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 1.5rem;
  
  /* Estilos para fullscreen */
  &:fullscreen {
    width: 100vw;
    height: 100vh;
    border-radius: 0;
    margin: 0;
    
    video {
      width: 100%;
      height: 100%;
      object-fit: contain;
    }
  }
  
  /* Suporte para webkit fullscreen */
  &:-webkit-full-screen {
    width: 100vw;
    height: 100vh;
    border-radius: 0;
    margin: 0;
    
    video {
      width: 100%;
      height: 100%;
      object-fit: contain;
    }
  }
  
  /* Responsividade para dispositivos móveis */
  @media (max-width: 768px) {
    border-radius: 8px;
    
    &:fullscreen,
    &:-webkit-full-screen {
      border-radius: 0;
    }
  }
`;

const VideoElement = styled.video`
  width: 100%;
  height: 100%;
  object-fit: cover;
  cursor: pointer;
`;

const FullscreenButton = styled.button`
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.5);
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.8);
  }
  
  svg {
    width: 20px;
    height: 20px;
  }
`;

const VideoControls = styled.div<{ $visible: boolean }>`
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  opacity: ${props => props.$visible ? 1 : 0};
  visibility: ${props => props.$visible ? 'visible' : 'hidden'};
  transition: opacity 0.3s ease, visibility 0.3s ease;
  z-index: 10;
`;

const PlayButton = styled.button`
  background: linear-gradient(135deg, #2196f3, #1976d2);
  border: none;
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: linear-gradient(135deg, #1976d2, #00bcd4);
    transform: scale(1.1);
  }
`;

const VideoProgressBar = styled.input`
  flex: 1;
  height: 4px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px;
  outline: none;
  cursor: pointer;
  
  &::-webkit-slider-thumb {
    appearance: none;
    width: 16px;
    height: 16px;
    background: linear-gradient(135deg, #2196f3, #00bcd4);
    border-radius: 50%;
    cursor: pointer;
  }
`;

const LessonInfo = styled.div`
  h2 {
    background: linear-gradient(135deg, #2196f3, #00bcd4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 1rem;
    font-size: 1.8rem;
  }
  
  p {
    color: rgba(255, 255, 255, 0.8);
    line-height: 1.6;
    margin-bottom: 1.5rem;
  }
`;

const LessonNavigation = styled.div`
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
`;

const NavButton = styled.button<{ disabled?: boolean }>`
  flex: 1;
  padding: 1rem;
  border: 1px solid ${props => props.disabled ? 'rgba(255, 255, 255, 0.2)' : '#2196f3'};
  background: ${props => props.disabled ? 'rgba(255, 255, 255, 0.1)' : 'transparent'};
  color: ${props => props.disabled ? 'rgba(255, 255, 255, 0.4)' : '#2196f3'};
  border-radius: 8px;
  cursor: ${props => props.disabled ? 'not-allowed' : 'pointer'};
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
  
  &:hover:not(:disabled) {
    background: linear-gradient(135deg, #2196f3, #00bcd4);
    color: white;
    border-color: #00bcd4;
  }
`;

const Sidebar = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 1.5rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  height: fit-content;
`;

const SidebarTitle = styled.h3`
  background: linear-gradient(135deg, #2196f3, #00bcd4);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 1.5rem;
  font-size: 1.3rem;
`;

const LessonList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
`;

const LessonItem = styled.div<{ $active?: boolean; $completed?: boolean }>`
  padding: 1rem;
  border-radius: 8px;
  background: ${props => props.$active ? 'rgba(33, 150, 243, 0.2)' : 'rgba(255, 255, 255, 0.05)'};
  border: 1px solid ${props => props.$active ? '#2196f3' : 'rgba(255, 255, 255, 0.1)'};
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  
  &:hover {
    background: rgba(33, 150, 243, 0.1);
    border-color: #2196f3;
  }
  
  .lesson-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }
  
  .lesson-number {
    background: ${props => props.$completed ? '#4caf50' : props.$active ? 'linear-gradient(135deg, #2196f3, #1976d2)' : 'rgba(255, 255, 255, 0.2)'};
    color: white;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8rem;
    font-weight: bold;
  }
  
  .lesson-title {
    flex: 1;
    font-size: 0.9rem;
    color: ${props => props.$active ? '#00bcd4' : 'rgba(255, 255, 255, 0.9)'};
  }
  
  .lesson-duration {
    font-size: 0.8rem;
    color: rgba(255, 255, 255, 0.6);
  }
  
  .lesson-progress {
    width: 100%;
    height: 3px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 2px;
    overflow: hidden;
    
    .progress-fill {
      height: 100%;
      background: linear-gradient(90deg, #2196f3, #00bcd4);
      transition: width 0.3s ease;
    }
  }
`;

const CompletedIcon = styled(CheckCircle)`
  width: 16px;
  height: 16px;
  color: #4caf50;
`;

// Interface para dados das aulas
interface Lesson {
  id: string;
  title: string;
  description: string;
  videoUrl: string;
  duration: string;
  completed: boolean;
}

// Mapeamento dos vídeos por ID da aula
const videoMap: { [key: string]: string } = {
  '1': v1,
  '2': v2,
  '3': v3,
  '4': v4,
  '5': v5,
  '6': v6,
  '7': v7,
  '8': v8
};

// Dados das aulas do Despertar Crypto
const despertar_crypto_lessons: Lesson[] = [
  {
    id: '1',
    title: 'Aula 1 - O PONTO DE PARTIDA',
    description: '"O Jogo do Dinheiro Mudou para Sempre" - Descubra como o mundo financeiro se transformou e por que você precisa estar preparado para essa nova realidade.',
    videoUrl: 'https://via.placeholder.com/800x450/000000/FFFFFF?text=Video+Aula+1',
    duration: '2:00',
    completed: false
  },
  {
    id: '2',
    title: 'Aula 2 - QUEBRANDO MITOS',
    description: '"Você Precisa ser Rico ou Gênio para Investir?" - Desmistificamos as principais barreiras que impedem pessoas comuns de começar a investir.',
    videoUrl: 'https://via.placeholder.com/800x450/000000/FFFFFF?text=Video+Aula+2',
    duration: '1:45',
    completed: false
  },
  {
    id: '3',
    title: 'Aula 3 - A REVOLUÇÃO DIGITAL',
    description: 'Entenda como as criptomoedas estão revolucionando o sistema financeiro mundial e criando novas oportunidades de investimento.',
    videoUrl: 'https://via.placeholder.com/800x450/000000/FFFFFF?text=Video+Aula+3',
    duration: '2:15',
    completed: false
  },
  {
    id: '4',
    title: 'Aula 4 - PRIMEIROS PASSOS',
    description: 'Aprenda os conceitos fundamentais e dê seus primeiros passos no mundo das criptomoedas com segurança e conhecimento.',
    videoUrl: 'https://via.placeholder.com/800x450/000000/FFFFFF?text=Video+Aula+4',
    duration: '1:50',
    completed: false
  },
  {
    id: '5',
    title: 'Aula 5 - ESTRATÉGIAS BÁSICAS',
    description: 'Conheça as estratégias básicas de investimento em criptomoedas e como aplicá-las de forma inteligente.',
    videoUrl: 'https://via.placeholder.com/800x450/000000/FFFFFF?text=Video+Aula+5',
    duration: '2:05',
    completed: false
  },
  {
    id: '6',
    title: 'Aula 6 - GERENCIAMENTO DE RISCO',
    description: 'Aprenda a proteger seus investimentos e gerenciar riscos de forma eficiente no mercado de criptomoedas.',
    videoUrl: 'https://via.placeholder.com/800x450/000000/FFFFFF?text=Video+Aula+6',
    duration: '1:55',
    completed: false
  },
  {
    id: '7',
    title: 'Aula 7 - FERRAMENTAS ESSENCIAIS',
    description: 'Descubra as ferramentas e plataformas essenciais para acompanhar e gerenciar seus investimentos em crypto.',
    videoUrl: 'https://via.placeholder.com/800x450/000000/FFFFFF?text=Video+Aula+7',
    duration: '2:10',
    completed: false
  },
  {
    id: '8',
    title: 'Aula 8 - PRÓXIMOS PASSOS',
    description: 'Planeje seu futuro no mundo crypto e descubra os próximos passos para continuar sua jornada de aprendizado.',
    videoUrl: 'https://via.placeholder.com/800x450/000000/FFFFFF?text=Video+Aula+8',
    duration: '1:40',
    completed: false
  }
];

/**
 * Componente principal da página de aula
 * Gerencia a reprodução de vídeos, navegação entre aulas e progresso do curso
 */
const AulaPage: React.FC = () => {
  const { aulaId } = useParams<{ aulaId: string }>();
  const navigate = useNavigate();
  
  // Estados do componente
  const [lessons, setLessons] = useState<Lesson[]>(despertar_crypto_lessons);
  const [currentLesson, setCurrentLesson] = useState<Lesson | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [videoProgress, setVideoProgress] = useState(0);
  const [videoDuration, setVideoDuration] = useState(0);
  const [showControls, setShowControls] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [controlsTimeout, setControlsTimeout] = useState<NodeJS.Timeout | null>(null);
  
  // Sistema de progresso por vídeo com persistência no localStorage
  const [videoProgressData, setVideoProgressData] = useState<{[key: string]: {currentTime: number, duration: number}}>(() => {
    const saved = localStorage.getItem('videoProgressData');
    return saved ? JSON.parse(saved) : {};
  });
  
  // Referência para o elemento de vídeo
  const videoRef = useRef<HTMLVideoElement>(null);
  
  // Encontra a aula atual baseada no ID da URL
  useEffect(() => {
    if (!aulaId) return;
    
    // Extrai o número da aula da URL (ex: despertar-crypto-01 -> 1)
    const lessonNumber = aulaId.replace('despertar-crypto-', '').replace(/^0+/, '') || '1';
    const lesson = lessons.find(l => l.id === lessonNumber);
    
    if (lesson) {
      setCurrentLesson(lesson);
    } else {
      // Se não encontrar a aula, redireciona para a primeira
      navigate('/aula/despertar-crypto-01');
    }
  }, [aulaId, lessons, navigate]);

  // Gerencia eventos de fullscreen e orientação
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    const handleOrientationChange = () => {
      // Detecta orientação landscape em dispositivos móveis
      if (window.innerHeight < window.innerWidth && window.innerWidth <= 768) {
        if (!document.fullscreenElement && videoRef.current) {
          toggleFullscreen();
        }
      }
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    window.addEventListener('orientationchange', handleOrientationChange);
    window.addEventListener('resize', handleOrientationChange);

    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
      window.removeEventListener('orientationchange', handleOrientationChange);
      window.removeEventListener('resize', handleOrientationChange);
    };
  }, []);

  // Gerencia auto-hide dos controles quando o vídeo está tocando
  useEffect(() => {
    if (isPlaying) {
      hideControlsAfterDelay();
    } else {
      setShowControls(true);
      if (controlsTimeout) {
        clearTimeout(controlsTimeout);
      }
    }

    return () => {
      if (controlsTimeout) {
        clearTimeout(controlsTimeout);
      }
    };
  }, [isPlaying]);

  // Cleanup do timeout ao desmontar o componente
  useEffect(() => {
    return () => {
      if (controlsTimeout) {
        clearTimeout(controlsTimeout);
      }
    };
  }, []);
  
  // Calcula o progresso real baseado no tempo assistido de cada vídeo
  const calculateCourseProgress = () => {
    let totalWatchedTime = 0;
    let totalDuration = 0;
    
    lessons.forEach(lesson => {
      const progressData = videoProgressData[lesson.id];
      if (progressData) {
        totalWatchedTime += progressData.currentTime;
        totalDuration += progressData.duration;
      }
    });
    
    return totalDuration > 0 ? (totalWatchedTime / totalDuration) * 100 : 0;
  };
  
  const courseProgress = calculateCourseProgress();
  
  /**
   * Navega para a próxima aula
   */
  const goToNextLesson = () => {
    if (!currentLesson) return;
    
    const currentIndex = lessons.findIndex(l => l.id === currentLesson.id);
    if (currentIndex < lessons.length - 1) {
      const nextLesson = lessons[currentIndex + 1];
      navigate(`/aula/despertar-crypto-${nextLesson.id.padStart(2, '0')}`);
    }
  };
  
  /**
   * Navega para a aula anterior
   */
  const goToPreviousLesson = () => {
    if (!currentLesson) return;
    
    const currentIndex = lessons.findIndex(l => l.id === currentLesson.id);
    if (currentIndex > 0) {
      const previousLesson = lessons[currentIndex - 1];
      navigate(`/aula/despertar-crypto-${previousLesson.id.padStart(2, '0')}`);
    }
  };
  
  /**
   * Marca a aula atual como concluída
   */
  const markLessonAsCompleted = () => {
    if (!currentLesson) return;
    
    setLessons(prev => prev.map(lesson => 
      lesson.id === currentLesson.id 
        ? { ...lesson, completed: true }
        : lesson
    ));
  };
  
  /**
   * Navega para uma aula específica
   */
  const goToLesson = (lessonId: string) => {
    navigate(`/aula/despertar-crypto-${lessonId.padStart(2, '0')}`);
  };
  
  /**
   * Controla play/pause do vídeo
   */
  const togglePlayPause = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };
  
  /**
   * Volta para a página principal
   */
  const goBack = () => {
    navigate('/vitrine-alunos');
  };

  /**
   * Controla a visibilidade dos controles do vídeo
   */
  const hideControlsAfterDelay = () => {
    if (controlsTimeout) {
      clearTimeout(controlsTimeout);
    }
    
    const timeout = setTimeout(() => {
      if (isPlaying) {
        setShowControls(false);
      }
    }, 3000); // Esconde após 3 segundos
    
    setControlsTimeout(timeout);
  };

  /**
   * Mostra os controles temporariamente
   */
  const showControlsTemporarily = () => {
    setShowControls(true);
    hideControlsAfterDelay();
  };

  /**
   * Alterna entre fullscreen e modo normal
   */
  const toggleFullscreen = () => {
    const videoElement = videoRef.current;
    if (!videoElement) return;

    if (!document.fullscreenElement) {
      videoElement.requestFullscreen().then(() => {
        setIsFullscreen(true);
      }).catch(err => {
        console.error('Erro ao entrar em fullscreen:', err);
      });
    } else {
      document.exitFullscreen().then(() => {
        setIsFullscreen(false);
      }).catch(err => {
        console.error('Erro ao sair do fullscreen:', err);
      });
    }
  };

  /**
   * Manipula cliques no vídeo
   */
  const handleVideoClick = () => {
    if (isPlaying) {
      showControlsTemporarily();
    } else {
      togglePlayPause();
    }
  };
  
  if (!currentLesson) {
    return (
      <AulaContainer>
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
          <h2>Carregando aula...</h2>
        </div>
      </AulaContainer>
    );
  }
  
  const currentIndex = lessons.findIndex(l => l.id === currentLesson.id);
  const isFirstLesson = currentIndex === 0;
  const isLastLesson = currentIndex === lessons.length - 1;
  
  // Extrair o ID da aula do parâmetro da URL
  const lessonId = aulaId || '1';
  
  return (
    <ProtectedLesson lessonId={`despertar-crypto-${lessonId.padStart(2, '0')}`}>
      <AulaContainer>
        <Header>
          <BackButton onClick={goBack}>
            <ChevronLeft size={20} />
            Voltar ao Curso
          </BackButton>
          
          <ProgressBar>
            <ProgressFill $progress={courseProgress} />
          </ProgressBar>
          
          <CourseTitle>Despertar Crypto</CourseTitle>
        </Header>
        
        <MainContent>
        <VideoSection>
          <VideoPlayer>
            <VideoElement
              ref={videoRef}
              onClick={handleVideoClick}
              onTimeUpdate={(e) => {
                const currentTime = e.currentTarget.currentTime;
                setVideoProgress(currentTime);
                
                // Atualiza o progresso do vídeo atual
                 if (currentLesson) {
                   const newProgressData = {
                     ...videoProgressData,
                     [currentLesson.id]: {
                       currentTime: currentTime,
                       duration: videoDuration
                     }
                   };
                   setVideoProgressData(newProgressData);
                   localStorage.setItem('videoProgressData', JSON.stringify(newProgressData));
                 }
              }}
              onLoadedMetadata={(e) => {
                const duration = e.currentTarget.duration;
                setVideoDuration(duration);
                
                // Restaura o progresso salvo
                if (currentLesson) {
                  const savedProgress = videoProgressData[currentLesson.id];
                  if (savedProgress && videoRef.current) {
                    videoRef.current.currentTime = savedProgress.currentTime;
                    setVideoProgress(savedProgress.currentTime);
                  }
                  
                  // Salva a duração do vídeo
                   const newProgressData = {
                     ...videoProgressData,
                     [currentLesson.id]: {
                       currentTime: savedProgress?.currentTime || 0,
                       duration: duration
                     }
                   };
                   setVideoProgressData(newProgressData);
                   localStorage.setItem('videoProgressData', JSON.stringify(newProgressData));
                }
              }}
              onPlay={() => setIsPlaying(true)}
              onPause={() => setIsPlaying(false)}
              onError={(e) => {
                console.error('Erro ao carregar vídeo:', e.target.error);
                console.log('Tentando carregar:', currentLesson ? videoMap[currentLesson.id] : v1);
              }}
              onLoadStart={() => {
                console.log('Iniciando carregamento do vídeo:', currentLesson ? videoMap[currentLesson.id] : v1);
              }}
              onMouseMove={showControlsTemporarily}
            >
              <source src={currentLesson ? videoMap[currentLesson.id] : v1} type="video/mp4" />
              <p style={{ color: 'white', padding: '20px', textAlign: 'center' }}>
                Seu navegador não suporta o elemento de vídeo ou o arquivo não foi encontrado.
                <br />
                <small>Vídeo: {currentLesson ? `Aula ${currentLesson.id}` : 'Aula 1'}</small>
              </p>
            </VideoElement>
            
            <VideoControls $visible={showControls}>
              <PlayButton onClick={togglePlayPause}>
                {isPlaying ? <Pause size={20} /> : <Play size={20} />}
              </PlayButton>
              
              <VideoProgressBar
                type="range"
                min="0"
                max={videoDuration || 100}
                value={videoProgress}
                onChange={(e) => {
                  const newTime = Number(e.target.value);
                  setVideoProgress(newTime);
                  if (videoRef.current) {
                    videoRef.current.currentTime = newTime;
                  }
                  showControlsTemporarily();
                }}
              />
              
              <FullscreenButton onClick={toggleFullscreen} title="Tela cheia">
                {isFullscreen ? <Minimize size={20} /> : <Maximize size={20} />}
              </FullscreenButton>
              
              <button
                onClick={markLessonAsCompleted}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: currentLesson.completed ? '#4caf50' : 'rgba(255, 255, 255, 0.7)',
                  cursor: 'pointer'
                }}
                title="Marcar como concluída"
              >
                <CheckCircle size={20} />
              </button>
            </VideoControls>
          </VideoPlayer>
          
          <LessonInfo>
            <h2>{currentLesson.title}</h2>
            <p>{currentLesson.description}</p>
          </LessonInfo>
          
          <LessonNavigation>
            <NavButton 
              onClick={goToPreviousLesson} 
              disabled={isFirstLesson}
            >
              <ChevronLeft size={20} />
              Aula Anterior
            </NavButton>
            
            <NavButton 
              onClick={goToNextLesson} 
              disabled={isLastLesson}
            >
              Próxima Aula
              <ChevronRight size={20} />
            </NavButton>
          </LessonNavigation>
        </VideoSection>
        
        <Sidebar>
          <SidebarTitle>Aulas do Curso</SidebarTitle>
          <LessonList>
            {lessons.map((lesson, index) => {
              const progressData = videoProgressData[lesson.id];
              const lessonProgress = progressData && progressData.duration > 0 
                ? (progressData.currentTime / progressData.duration) * 100 
                : 0;
              
              return (
                <LessonItem
                  key={lesson.id}
                  $active={lesson.id === currentLesson.id}
                  $completed={lessonProgress >= 95} // Considera completa se assistiu 95% ou mais
                  onClick={() => goToLesson(lesson.id)}
                >
                  <div className="lesson-header">
                    <div className="lesson-number">
                      {lessonProgress >= 95 ? <CompletedIcon /> : index + 1}
                    </div>
                    <div className="lesson-title">{lesson.title}</div>
                    <div className="lesson-duration">{Math.round(lessonProgress)}%</div>
                  </div>
                  <div className="lesson-progress">
                    <div 
                      className="progress-fill" 
                      style={{ width: `${lessonProgress}%` }}
                    />
                  </div>
                </LessonItem>
              );
            })}
          </LessonList>
        </Sidebar>
        </MainContent>
        <StandardFooter />
      </AulaContainer>
    </ProtectedLesson>
  );
};

export default AulaPage;