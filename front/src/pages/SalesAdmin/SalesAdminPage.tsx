import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Save, Eye, BarChart3, Settings, Clock, Palette, Type, Target } from 'lucide-react';
import StandardFooter from '../../components/StandardFooter/StandardFooter';
import logo3 from '/logo3.png';
import '../Dashboard/DashboardMobile.css';

/**
 * Página de Administração da Página de Vendas
 * Permite configurar headlines, botões CTA, delay de aparição e métricas de retenção
 */

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

interface RetentionMetrics {
  totalViews: number;
  averageWatchTime: number;
  conversionRate: number;
  buttonClicks: number;
}

interface ABTestConfig {
  enabled: boolean;
  rotationIntervalHours: number;
  minViewsPerTest: number;
  currentTestStartTime: string;
  bestPerformingColor: 'red' | 'blue' | 'orange' | null;
  currentCombinationIndex: number;
  testAllCombinations: boolean;
  bestCombination: {
    headlineId: number;
    buttonId: number;
    conversionRate: number;
    totalViews: number;
    totalClicks: number;
  } | null;
}

interface CombinationResult {
  headlineId: number;
  buttonId: number;
  views: number;
  clicks: number;
  conversionRate: number;
  lastTested: string;
  headlineTitle: string;
  buttonText: string;
}

const SalesAdminPage: React.FC = () => {
  // Estados para configurações
  const [headlines, setHeadlines] = useState<HeadlineConfig[]>([
    { 
      id: 1, 
      title: 'Descubra os Segredos do Trading de Criptomoedas', 
      subtitle: 'Aprenda as estratégias que os profissionais usam para gerar lucros consistentes', 
      active: true,
      highlightColor: 'red',
      testResults: { views: 0, clicks: 0, conversionRate: 0, lastTested: new Date().toISOString() }
    },
    { 
      id: 2, 
      title: 'Transforme R$ 1.000 em R$ 10.000 com Crypto', 
      subtitle: 'Método comprovado usado por traders profissionais', 
      active: false,
      highlightColor: 'blue',
      testResults: { views: 0, clicks: 0, conversionRate: 0, lastTested: new Date().toISOString() }
    },
    { 
      id: 3, 
      title: 'Ganhe Dinheiro com Bitcoin Mesmo Sendo Iniciante', 
      subtitle: 'Sistema passo a passo para lucrar no mercado cripto', 
      active: false,
      highlightColor: 'orange',
      testResults: { views: 0, clicks: 0, conversionRate: 0, lastTested: new Date().toISOString() }
    }
  ]);

  const [buttons, setButtons] = useState<ButtonConfig[]>([
    { id: 1, text: '🚀 QUERO ACESSO AGORA', color: '#ffffff', backgroundColor: '#ff6b35', link: '/checkout/despertar-crypto', active: true },
    { id: 2, text: '💰 GARANTIR MINHA VAGA', color: '#ffffff', backgroundColor: '#28a745', link: '/checkout/despertar-crypto', active: false },
    { id: 3, text: '⚡ COMEÇAR AGORA', color: '#ffffff', backgroundColor: '#dc3545', link: '/checkout/despertar-crypto', active: false }
  ]);

  const [delayConfig, setDelayConfig] = useState<DelayConfig>({
    enabled: true,
    delaySeconds: 180
  });

  const [retentionMetrics, setRetentionMetrics] = useState<RetentionMetrics>({
    totalViews: 1247,
    averageWatchTime: 156,
    conversionRate: 12.3,
    buttonClicks: 89
  });

  const [abTestConfig, setAbTestConfig] = useState<ABTestConfig>({
    enabled: false,
    rotationIntervalHours: 24,
    minViewsPerTest: 100,
    currentTestStartTime: new Date().toISOString(),
    bestPerformingColor: null,
    currentCombinationIndex: 0,
    testAllCombinations: false,
    bestCombination: null
  });

  const [combinationResults, setCombinationResults] = useState<CombinationResult[]>([]);

  const [activeTab, setActiveTab] = useState<'headlines' | 'buttons' | 'delay' | 'video' | 'metrics' | 'abtest'>('headlines');
  
  // Estados para configuração de vídeo
  const [videoOverlays, setVideoOverlays] = useState<VideoOverlayConfig[]>([
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
  ]);
  
  const [videoConfig, setVideoConfig] = useState<VideoConfig>({
    videoUrl: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
    autoplay: true,
    muted: true,
    showOverlay: true
  });
  
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
  
  // Funções para gerenciar overlays de vídeo
  const activateVideoOverlay = (id: number) => {
    setVideoOverlays(prev => prev.map(overlay => ({
      ...overlay,
      active: overlay.id === id
    })));
  };
  
  const updateVideoOverlay = (id: number, field: keyof VideoOverlayConfig, value: any) => {
    setVideoOverlays(prev => prev.map(overlay => 
      overlay.id === id ? { ...overlay, [field]: value } : overlay
    ));
  };
  
  const updateVideoConfig = (field: keyof VideoConfig, value: any) => {
    setVideoConfig(prev => ({ ...prev, [field]: value }));
  };

  /**
   * Salva as configurações no localStorage
   */
  const saveConfigurations = () => {
    const config = {
      headlines,
      buttons,
      delayConfig,
      videoOverlays,
      videoConfig,
      progressBarConfig,
      videoMetrics,
      abTestConfig,
      combinationResults,
      timestamp: new Date().toISOString()
    };
    localStorage.setItem('salesPageConfig', JSON.stringify(config));
    
    // Dispara evento customizado para notificar outras páginas
    window.dispatchEvent(new CustomEvent('salesConfigUpdated'));
    
    console.log('Configurações salvas:', config); // Debug
    alert('Configurações salvas com sucesso!');
  };

  /**
   * Gera todas as combinações possíveis de headlines e botões
   */
  const generateAllCombinations = () => {
    const combinations: { headlineId: number; buttonId: number }[] = [];
    
    headlines.forEach(headline => {
      buttons.forEach(button => {
        combinations.push({
          headlineId: headline.id,
          buttonId: button.id
        });
      });
    });
    
    return combinations;
  };

  /**
   * Sistema de rotação automática A/B Test
   */
  const rotateABTest = () => {
    if (!abTestConfig.enabled) return;

    const now = new Date();
    const testStart = new Date(abTestConfig.currentTestStartTime);
    const hoursSinceStart = (now.getTime() - testStart.getTime()) / (1000 * 60 * 60);

    if (hoursSinceStart >= abTestConfig.rotationIntervalHours) {
      if (abTestConfig.testAllCombinations) {
        // Testa todas as combinações sequencialmente
        const allCombinations = generateAllCombinations();
        const nextIndex = (abTestConfig.currentCombinationIndex + 1) % allCombinations.length;
        const nextCombination = allCombinations[nextIndex];
        
        // Ativa a headline e botão da próxima combinação
        setHeadlines(prev => prev.map(h => ({
          ...h,
          active: h.id === nextCombination.headlineId
        })));
        
        setButtons(prev => prev.map(b => ({
          ...b,
          active: b.id === nextCombination.buttonId
        })));
        
        setAbTestConfig(prev => ({
          ...prev,
          currentCombinationIndex: nextIndex,
          currentTestStartTime: now.toISOString()
        }));
      } else {
        // Rotação simples apenas de headlines
        const currentIndex = headlines.findIndex(h => h.active);
        const nextIndex = (currentIndex + 1) % headlines.length;
        
        setHeadlines(prev => prev.map((h, index) => ({
          ...h,
          active: index === nextIndex
        })));
        
        setAbTestConfig(prev => ({
          ...prev,
          currentTestStartTime: now.toISOString()
        }));
      }
    }
  };

  /**
   * Calcula a melhor cor baseada nos resultados
   */
  const calculateBestColor = () => {
    const colorResults = headlines.reduce((acc, headline) => {
      const color = headline.highlightColor;
      if (!acc[color]) {
        acc[color] = { totalViews: 0, totalClicks: 0, conversionRate: 0 };
      }
      acc[color].totalViews += headline.testResults.views;
      acc[color].totalClicks += headline.testResults.clicks;
      acc[color].conversionRate = acc[color].totalViews > 0 
        ? (acc[color].totalClicks / acc[color].totalViews) * 100 
        : 0;
      return acc;
    }, {} as Record<string, { totalViews: number; totalClicks: number; conversionRate: number }>);

    const bestColor = Object.entries(colorResults)
      .sort(([,a], [,b]) => b.conversionRate - a.conversionRate)[0]?.[0] as 'red' | 'blue' | 'orange' | null;

    setAbTestConfig(prev => ({ ...prev, bestPerformingColor: bestColor }));
    return colorResults;
  };

  /**
   * Registra resultado de uma combinação específica
   */
  const recordCombinationResult = (headlineId: number, buttonId: number, isClick: boolean = false) => {
    const headline = headlines.find(h => h.id === headlineId);
    const button = buttons.find(b => b.id === buttonId);
    
    if (!headline || !button) return;
    
    setCombinationResults(prev => {
      const existingIndex = prev.findIndex(r => r.headlineId === headlineId && r.buttonId === buttonId);
      
      if (existingIndex >= 0) {
        const updated = [...prev];
        const existing = updated[existingIndex];
        
        if (isClick) {
          existing.clicks += 1;
        } else {
          existing.views += 1;
        }
        
        existing.conversionRate = existing.views > 0 ? (existing.clicks / existing.views) * 100 : 0;
        existing.lastTested = new Date().toISOString();
        
        return updated;
      } else {
        const newResult: CombinationResult = {
          headlineId,
          buttonId,
          views: isClick ? 0 : 1,
          clicks: isClick ? 1 : 0,
          conversionRate: 0,
          lastTested: new Date().toISOString(),
          headlineTitle: headline.title.substring(0, 30) + '...',
          buttonText: button.text.substring(0, 20) + '...'
        };
        
        newResult.conversionRate = newResult.views > 0 ? (newResult.clicks / newResult.views) * 100 : 0;
        
        return [...prev, newResult];
      }
    });
  };

  /**
   * Calcula a melhor combinação baseada nos resultados
   */
  const calculateBestCombination = () => {
    if (combinationResults.length === 0) return null;
    
    const bestResult = combinationResults
      .filter(r => r.views >= abTestConfig.minViewsPerTest)
      .sort((a, b) => b.conversionRate - a.conversionRate)[0];
    
    if (bestResult) {
      setAbTestConfig(prev => ({
        ...prev,
        bestCombination: {
          headlineId: bestResult.headlineId,
          buttonId: bestResult.buttonId,
          conversionRate: bestResult.conversionRate,
          totalViews: bestResult.views,
          totalClicks: bestResult.clicks
        }
      }));
    }
    
    return bestResult;
  };

  /**
   * Carrega as configurações do localStorage
   */
  useEffect(() => {
    const savedConfig = localStorage.getItem('salesPageConfig');
    if (savedConfig) {
      const config = JSON.parse(savedConfig);
      
      // Garante que headlines tenham testResults
      if (config.headlines) {
        const headlinesWithTestResults = config.headlines.map((h: any) => ({
          ...h,
          testResults: h.testResults || {
            views: 0,
            clicks: 0,
            conversionRate: 0,
            lastTested: new Date().toISOString()
          }
        }));
        setHeadlines(headlinesWithTestResults);
      }
      
      if (config.buttons) setButtons(config.buttons);
      if (config.delayConfig) setDelayConfig(config.delayConfig);
      if (config.abTestConfig) setAbTestConfig(config.abTestConfig);
      if (config.combinationResults) setCombinationResults(config.combinationResults);
    }
  }, []);

  // Timer para rotação automática do A/B Test
  useEffect(() => {
    if (abTestConfig.enabled) {
      const interval = setInterval(rotateABTest, 60000); // Verifica a cada minuto
      return () => clearInterval(interval);
    }
  }, [abTestConfig, headlines]);

  // Calcula a melhor combinação quando os resultados mudam
  useEffect(() => {
    if (combinationResults.length > 0) {
      calculateBestCombination();
    }
  }, [combinationResults, abTestConfig.minViewsPerTest]);

  /**
   * Atualiza uma headline específica
   */
  const updateHeadline = (id: number, field: keyof HeadlineConfig, value: any) => {
    setHeadlines(prev => prev.map(h => 
      h.id === id ? { ...h, [field]: value } : h
    ));
  };

  /**
   * Atualiza um botão específico
   */
  const updateButton = (id: number, field: keyof ButtonConfig, value: any) => {
    setButtons(prev => prev.map(b => 
      b.id === id ? { ...b, [field]: value } : b
    ));
  };

  /**
   * Ativa uma headline específica (desativa as outras)
   */
  const activateHeadline = (id: number) => {
    setHeadlines(prev => prev.map(h => ({ ...h, active: h.id === id })));
  };

  /**
   * Ativa um botão específico (desativa os outros)
   */
  const activateButton = (id: number) => {
    setButtons(prev => prev.map(b => ({ ...b, active: b.id === id })));
  };

  return (
    <AdminContainer>
      {/* CONTAINER MOTIVACIONAL NO TOPO DA DIV PRINCIPAL (4px) */}
      <div className="mobile-motivation-header-container">
        {/* Seção Motivacional */}
        <div className="mobile-motivational">
          <p className="mobile-motivational-text">
            Configure sua estratégia de vendas e transforme visitantes em clientes.
          </p>
        </div>

        {/* Espaçamento de Segurança (4px) */}
        <div className="mobile-safety-gap"></div>
      </div>

      {/* CONTEÚDO DA PÁGINA SALES ADMIN */}
      <AdminHeader>
        <HeaderContent>
          <Title>Admin - Página de Vendas</Title>
        </HeaderContent>
        <div>
          <span style={{ color: '#94a3b8', fontSize: '0.9em' }}>
            {new Date().toLocaleDateString('pt-BR')}
          </span>
        </div>
      </AdminHeader>

        {/* Botões de ação abaixo do header */}
        <ActionButtons>
          <PreviewButton href="/sales" target="_blank">
            <Eye size={20} />
            Visualizar Página
          </PreviewButton>
          <SaveButton onClick={saveConfigurations}>
            <Save size={20} />
            Salvar Configurações
          </SaveButton>
        </ActionButtons>

      <TabNavigation>
        <TabButton 
          active={activeTab === 'headlines'} 
          onClick={() => setActiveTab('headlines')}
        >
          <Type size={20} />
          Headlines
        </TabButton>
        <TabButton 
          active={activeTab === 'buttons'} 
          onClick={() => setActiveTab('buttons')}
        >
          <Target size={20} />
          Botões CTA
        </TabButton>
        <TabButton 
            active={activeTab === 'delay'} 
            onClick={() => setActiveTab('delay')}
          >
            <Clock size={18} />
            Delay Timer
          </TabButton>
          
          <TabButton 
            active={activeTab === 'video'} 
            onClick={() => setActiveTab('video')}
          >
            <Target size={18} />
            Overlay Vídeo
          </TabButton>
          
          <TabButton 
            active={activeTab === 'metrics'} 
            onClick={() => setActiveTab('metrics')}
          >
            <BarChart3 size={18} />
            Métricas
          </TabButton>
        <TabButton 
          active={activeTab === 'abtest'} 
          onClick={() => setActiveTab('abtest')}
        >
          <Target size={20} />
          A/B Test
        </TabButton>
      </TabNavigation>

      <AdminContent>
        {activeTab === 'headlines' && (
          <Section>
            <SectionTitle>Configuração de Headlines</SectionTitle>
            <SectionDescription>
              Configure até 3 headlines diferentes para testar qual converte melhor
            </SectionDescription>
            
            <HeadlinesGrid>
              {headlines.map(headline => (
                <HeadlineCard key={headline.id} active={headline.active}>
                  <CardHeader>
                    <CardTitle>Headline {headline.id}</CardTitle>
                    <ActiveToggle 
                      active={headline.active}
                      onClick={() => activateHeadline(headline.id)}
                    >
                      {headline.active ? 'ATIVA' : 'INATIVA'}
                    </ActiveToggle>
                  </CardHeader>
                  
                  <InputGroup>
                    <Label>Título Principal</Label>
                    <TextInput
                      value={headline.title}
                      onChange={(e) => updateHeadline(headline.id, 'title', e.target.value)}
                      placeholder="Digite o título principal..."
                    />
                  </InputGroup>
                  
                  <InputGroup>
                    <Label>Subtítulo</Label>
                    <TextArea
                      value={headline.subtitle}
                      onChange={(e) => updateHeadline(headline.id, 'subtitle', e.target.value)}
                      placeholder="Digite o subtítulo..."
                      rows={3}
                    />
                  </InputGroup>
                  
                  <InputGroup>
                    <Label>Cor de Destaque</Label>
                    <ColorSelector>
                      <ColorOption 
                        color="#ff3333" 
                        selected={headline.highlightColor === 'red'}
                        onClick={() => updateHeadline(headline.id, 'highlightColor', 'red')}
                      >
                        Vermelho
                      </ColorOption>
                      <ColorOption 
                        color="#2196f3" 
                        selected={headline.highlightColor === 'blue'}
                        onClick={() => updateHeadline(headline.id, 'highlightColor', 'blue')}
                      >
                        Azul
                      </ColorOption>
                      <ColorOption 
                        color="#ff9800" 
                        selected={headline.highlightColor === 'orange'}
                        onClick={() => updateHeadline(headline.id, 'highlightColor', 'orange')}
                      >
                        Laranja
                      </ColorOption>
                    </ColorSelector>
                  </InputGroup>
                  
                  <TestResults>
                    <ResultItem>
                      <ResultLabel>Views:</ResultLabel>
                      <ResultValue>{headline.testResults?.views || 0}</ResultValue>
                    </ResultItem>
                    <ResultItem>
                      <ResultLabel>Clicks:</ResultLabel>
                      <ResultValue>{headline.testResults?.clicks || 0}</ResultValue>
                    </ResultItem>
                    <ResultItem>
                      <ResultLabel>Conversão:</ResultLabel>
                      <ResultValue>{(headline.testResults?.conversionRate || 0).toFixed(2)}%</ResultValue>
                    </ResultItem>
                  </TestResults>
                </HeadlineCard>
              ))}
            </HeadlinesGrid>
          </Section>
        )}

        {activeTab === 'buttons' && (
          <Section>
            <SectionTitle>Configuração de Botões CTA</SectionTitle>
            <SectionDescription>
              Configure até 3 botões diferentes com cores e textos personalizados
            </SectionDescription>
            
            <ButtonsGrid>
              {buttons.map(button => (
                <ButtonCard key={button.id} active={button.active}>
                  <CardHeader>
                    <CardTitle>Botão {button.id}</CardTitle>
                    <ActiveToggle 
                      active={button.active}
                      onClick={() => activateButton(button.id)}
                    >
                      {button.active ? 'ATIVO' : 'INATIVO'}
                    </ActiveToggle>
                  </CardHeader>
                  
                  <InputGroup>
                    <Label>Texto do Botão</Label>
                    <TextInput
                      value={button.text}
                      onChange={(e) => updateButton(button.id, 'text', e.target.value)}
                      placeholder="Digite o texto do botão..."
                    />
                  </InputGroup>
                  
                  <InputGroup>
                    <Label>Paleta de Cores Recomendadas - {button.id === 1 ? 'Vermelho' : button.id === 2 ? 'Azul' : 'Laranja'}</Label>
                    <ColorPalette>
                      {button.id === 1 && (
                        <>
                          <ColorPaletteButton 
                            onClick={() => {
                              updateButton(button.id, 'backgroundColor', '#ff3333');
                              updateButton(button.id, 'color', '#ffffff');
                            }}
                            color="#ff3333"
                          >
                            Vermelho Clássico
                          </ColorPaletteButton>
                          <ColorPaletteButton 
                            onClick={() => {
                              updateButton(button.id, 'backgroundColor', '#ff4757');
                              updateButton(button.id, 'color', '#ffffff');
                            }}
                            color="#ff4757"
                          >
                            Vermelho Vibrante
                          </ColorPaletteButton>
                          <ColorPaletteButton 
                            onClick={() => {
                              updateButton(button.id, 'backgroundColor', '#e74c3c');
                              updateButton(button.id, 'color', '#ffffff');
                            }}
                            color="#e74c3c"
                          >
                            Vermelho Intenso
                          </ColorPaletteButton>
                          <ColorPaletteButton 
                            onClick={() => {
                              updateButton(button.id, 'backgroundColor', '#c0392b');
                              updateButton(button.id, 'color', '#ffffff');
                            }}
                            color="#c0392b"
                          >
                            Vermelho Escuro
                          </ColorPaletteButton>
                        </>
                      )}
                      
                      {button.id === 2 && (
                        <>
                          <ColorPaletteButton 
                            onClick={() => {
                              updateButton(button.id, 'backgroundColor', '#2196f3');
                              updateButton(button.id, 'color', '#ffffff');
                            }}
                            color="#2196f3"
                          >
                            Azul Clássico
                          </ColorPaletteButton>
                          <ColorPaletteButton 
                            onClick={() => {
                              updateButton(button.id, 'backgroundColor', '#3742fa');
                              updateButton(button.id, 'color', '#ffffff');
                            }}
                            color="#3742fa"
                          >
                            Azul Vibrante
                          </ColorPaletteButton>
                          <ColorPaletteButton 
                            onClick={() => {
                              updateButton(button.id, 'backgroundColor', '#1e88e5');
                              updateButton(button.id, 'color', '#ffffff');
                            }}
                            color="#1e88e5"
                          >
                            Azul Intenso
                          </ColorPaletteButton>
                          <ColorPaletteButton 
                            onClick={() => {
                              updateButton(button.id, 'backgroundColor', '#1565c0');
                              updateButton(button.id, 'color', '#ffffff');
                            }}
                            color="#1565c0"
                          >
                            Azul Escuro
                          </ColorPaletteButton>
                        </>
                      )}
                      
                      {button.id === 3 && (
                        <>
                          <ColorPaletteButton 
                            onClick={() => {
                              updateButton(button.id, 'backgroundColor', '#ff6b35');
                              updateButton(button.id, 'color', '#ffffff');
                            }}
                            color="#ff6b35"
                          >
                            Laranja Clássico
                          </ColorPaletteButton>
                          <ColorPaletteButton 
                            onClick={() => {
                              updateButton(button.id, 'backgroundColor', '#ff9500');
                              updateButton(button.id, 'color', '#ffffff');
                            }}
                            color="#ff9500"
                          >
                            Laranja Vibrante
                          </ColorPaletteButton>
                          <ColorPaletteButton 
                            onClick={() => {
                              updateButton(button.id, 'backgroundColor', '#ffa726');
                              updateButton(button.id, 'color', '#ffffff');
                            }}
                            color="#ffa726"
                          >
                            Laranja Dourado
                          </ColorPaletteButton>
                          <ColorPaletteButton 
                            onClick={() => {
                              updateButton(button.id, 'backgroundColor', '#f57c00');
                              updateButton(button.id, 'color', '#ffffff');
                            }}
                            color="#f57c00"
                          >
                            Laranja Escuro
                          </ColorPaletteButton>
                        </>
                      )}
                    </ColorPalette>
                  </InputGroup>
                  
                  <ColorRow>
                    <InputGroup>
                      <Label>Cor do Texto</Label>
                      <ColorInput
                        type="color"
                        value={button.color}
                        onChange={(e) => updateButton(button.id, 'color', e.target.value)}
                      />
                    </InputGroup>
                    
                    <InputGroup>
                      <Label>Cor de Fundo</Label>
                      <ColorInput
                        type="color"
                        value={button.backgroundColor}
                        onChange={(e) => updateButton(button.id, 'backgroundColor', e.target.value)}
                      />
                    </InputGroup>
                  </ColorRow>
                  
                  <InputGroup>
                    <Label>Link de Destino</Label>
                    <TextInput
                      value={button.link}
                      onChange={(e) => updateButton(button.id, 'link', e.target.value)}
                      placeholder="/checkout/despertar-crypto"
                    />
                  </InputGroup>
                  
                  <ModernButtonPreview 
                    buttonColor={button.backgroundColor}
                    textColor={button.color}
                  >
                    <ButtonPreviewContent>
                      <ButtonPreviewText>{button.text}</ButtonPreviewText>
                      <ButtonPreviewSubtext>Preview do Botão CTA</ButtonPreviewSubtext>
                    </ButtonPreviewContent>
                  </ModernButtonPreview>
                </ButtonCard>
              ))}
            </ButtonsGrid>
          </Section>
        )}

        {activeTab === 'delay' && (
          <Section>
            <SectionTitle>Configuração de Delay</SectionTitle>
            <SectionDescription>
              Configure quando o botão CTA deve aparecer na página de vendas
            </SectionDescription>
            
            <DelayCard>
              <InputGroup>
                <Label>
                  <input
                    type="checkbox"
                    checked={delayConfig.enabled}
                    onChange={(e) => setDelayConfig(prev => ({ ...prev, enabled: e.target.checked }))}
                  />
                  Ativar delay para aparição do botão
                </Label>
              </InputGroup>
              
              {delayConfig.enabled && (
                <InputGroup>
                  <Label>Tempo de delay (segundos)</Label>
                  <NumberInput
                    type="number"
                    value={delayConfig.delaySeconds}
                    onChange={(e) => setDelayConfig(prev => ({ ...prev, delaySeconds: parseInt(e.target.value) }))}
                    min="0"
                    max="600"
                  />
                  <DelayInfo>
                    O botão aparecerá após {Math.floor(delayConfig.delaySeconds / 60)}m {delayConfig.delaySeconds % 60}s
                  </DelayInfo>
                </InputGroup>
              )}
            </DelayCard>
          </Section>
        )}
        
        {activeTab === 'video' && (
          <Section>
            <SectionTitle>🎥 Configuração de Overlay de Vídeo</SectionTitle>
            <SectionDescription>
              Configure os overlays que aparecem sobre o vídeo para ativar o áudio. Teste os 3 estilos diferentes.
            </SectionDescription>
            
            <VideoOverlayGrid>
              {videoOverlays.map(overlay => (
                <VideoOverlayCard key={overlay.id} active={overlay.active}>
                  <CardHeader>
                    <CardTitle>Overlay {overlay.id} - {overlay.style.charAt(0).toUpperCase() + overlay.style.slice(1)}</CardTitle>
                    <ActiveToggle 
                      active={overlay.active}
                      onClick={() => activateVideoOverlay(overlay.id)}
                    >
                      {overlay.active ? 'ATIVO' : 'INATIVO'}
                    </ActiveToggle>
                  </CardHeader>
                  
                  <InputGroup>
                    <Label>Mensagem do Overlay</Label>
                    <TextArea
                      value={overlay.message}
                      onChange={(e) => updateVideoOverlay(overlay.id, 'message', e.target.value)}
                      placeholder="Digite a mensagem do overlay..."
                      rows={3}
                    />
                  </InputGroup>
                  
                  <VideoOverlayPreview overlayStyle={overlay.style}>
                    <OverlayPreviewContent overlayStyle={overlay.style}>
                      {overlay.style === 'classic' && (
                        <>
                          <SpeakerIconPreview>🔊</SpeakerIconPreview>
                          <OverlayMessagePreview overlayStyle={overlay.style}>
                            {overlay.message.split('\n').map((line, index) => (
                              <div key={index}>{line}</div>
                            ))}
                          </OverlayMessagePreview>
                        </>
                      )}
                      
                      {overlay.style === 'modern' && (
                        <>
                          <PlayButtonPreview>
                            <PlayButtonIconPreview>▶</PlayButtonIconPreview>
                          </PlayButtonPreview>
                          <OverlayMessagePreview overlayStyle={overlay.style}>
                            {overlay.message}
                          </OverlayMessagePreview>
                        </>
                      )}
                      
                      {overlay.style === 'minimal' && (
                        <OverlayMessagePreview overlayStyle={overlay.style}>
                          {overlay.message}
                        </OverlayMessagePreview>
                      )}
                    </OverlayPreviewContent>
                  </VideoOverlayPreview>
                </VideoOverlayCard>
              ))}
            </VideoOverlayGrid>
            
            <DelayCard>
              <CardHeader>
                <CardTitle>Configurações do Vídeo</CardTitle>
              </CardHeader>
              
              <InputGroup>
                <Label>URL do Vídeo</Label>
                <TextInput
                  value={videoConfig.videoUrl}
                  onChange={(e) => updateVideoConfig('videoUrl', e.target.value)}
                  placeholder="https://exemplo.com/video.mp4"
                />
              </InputGroup>
              
              <InputGroup>
                <Label>
                  <input
                    type="checkbox"
                    checked={videoConfig.autoplay}
                    onChange={(e) => updateVideoConfig('autoplay', e.target.checked)}
                    style={{ marginRight: '0.5rem' }}
                  />
                  Reprodução Automática
                </Label>
              </InputGroup>
              
              <InputGroup>
                <Label>
                  <input
                    type="checkbox"
                    checked={videoConfig.muted}
                    onChange={(e) => updateVideoConfig('muted', e.target.checked)}
                    style={{ marginRight: '0.5rem' }}
                  />
                  Iniciar Sem Áudio (Mudo)
                </Label>
              </InputGroup>
              
              <InputGroup>
                <Label>
                  <input
                    type="checkbox"
                    checked={videoConfig.showOverlay}
                    onChange={(e) => updateVideoConfig('showOverlay', e.target.checked)}
                    style={{ marginRight: '0.5rem' }}
                  />
                  Mostrar Overlay
                </Label>
              </InputGroup>
            </DelayCard>
            
            <DelayCard>
              <CardHeader>
                <CardTitle>Configurações da Barra de Progresso</CardTitle>
              </CardHeader>
              
              <InputGroup>
                <Label>Cor Primária (Início da Barra)</Label>
                <ColorInput
                  type="color"
                  value={progressBarConfig.primaryColor}
                  onChange={(e) => setProgressBarConfig(prev => ({ ...prev, primaryColor: e.target.value }))}
                />
              </InputGroup>
              
              <InputGroup>
                <Label>Cor Secundária (Final da Barra)</Label>
                <ColorInput
                  type="color"
                  value={progressBarConfig.secondaryColor}
                  onChange={(e) => setProgressBarConfig(prev => ({ ...prev, secondaryColor: e.target.value }))}
                />
              </InputGroup>
              
              <InputGroup>
                <Label>Cor de Fundo da Barra</Label>
                <ColorInput
                  type="color"
                  value={progressBarConfig.backgroundColor.replace('rgba(255, 255, 255, 0.3)', '#ffffff4d')}
                  onChange={(e) => {
                    const hex = e.target.value;
                    const rgba = `rgba(${parseInt(hex.slice(1, 3), 16)}, ${parseInt(hex.slice(3, 5), 16)}, ${parseInt(hex.slice(5, 7), 16)}, 0.3)`;
                    setProgressBarConfig(prev => ({ ...prev, backgroundColor: rgba }));
                  }}
                />
              </InputGroup>
              
              <ProgressBarPreview>
                <ProgressBarPreviewBackground backgroundColor={progressBarConfig.backgroundColor}>
                  <ProgressBarPreviewFill 
                    primaryColor={progressBarConfig.primaryColor}
                    secondaryColor={progressBarConfig.secondaryColor}
                  />
                </ProgressBarPreviewBackground>
                <ProgressBarPreviewLabel>Preview da Barra de Progresso Inteligente</ProgressBarPreviewLabel>
              </ProgressBarPreview>
            </DelayCard>
            
            <DelayCard>
              <CardHeader>
                <CardTitle>Métricas do Vídeo</CardTitle>
              </CardHeader>
              
              <MetricsGrid>
                <MetricCard>
                  <MetricValue>{Math.floor(videoMetrics.totalWatchTime)}s</MetricValue>
                  <MetricLabel>Tempo Total Assistido</MetricLabel>
                </MetricCard>
                
                <MetricCard>
                  <MetricValue>{videoMetrics.pauseCount}</MetricValue>
                  <MetricLabel>Pausas</MetricLabel>
                </MetricCard>
                
                <MetricCard>
                  <MetricValue>{videoMetrics.resumeCount}</MetricValue>
                  <MetricLabel>Retomadas</MetricLabel>
                </MetricCard>
                
                <MetricCard>
                  <MetricValue>{Math.floor(videoMetrics.completionRate)}%</MetricValue>
                  <MetricLabel>Taxa de Conclusão</MetricLabel>
                </MetricCard>
              </MetricsGrid>
            </DelayCard>
          </Section>
        )}

        {activeTab === 'metrics' && (
          <Section>
            <SectionTitle>Métricas de Retenção</SectionTitle>
            <SectionDescription>
              Acompanhe o desempenho da sua página de vendas
            </SectionDescription>
            
            <MetricsGrid>
              <MetricCard>
                <MetricValue>{retentionMetrics.totalViews.toLocaleString()}</MetricValue>
                <MetricLabel>Total de Visualizações</MetricLabel>
              </MetricCard>
              
              <MetricCard>
                <MetricValue>{Math.floor(retentionMetrics.averageWatchTime / 60)}m {retentionMetrics.averageWatchTime % 60}s</MetricValue>
                <MetricLabel>Tempo Médio de Permanência</MetricLabel>
              </MetricCard>
              
              <MetricCard>
                <MetricValue>{retentionMetrics.conversionRate}%</MetricValue>
                <MetricLabel>Taxa de Conversão</MetricLabel>
              </MetricCard>
              
              <MetricCard>
                <MetricValue>{retentionMetrics.buttonClicks}</MetricValue>
                <MetricLabel>Cliques no Botão CTA</MetricLabel>
              </MetricCard>
            </MetricsGrid>
          </Section>
        )}

        {activeTab === 'abtest' && (
          <Section>
            <SectionTitle>Sistema A/B Test Automático</SectionTitle>
            <SectionDescription>
              Configure testes automáticos para descobrir qual cor de destaque converte melhor
            </SectionDescription>
            
            {/* Debug info */}
            <div style={{ background: 'rgba(255,255,0,0.1)', padding: '1rem', marginBottom: '1rem', borderRadius: '8px' }}>
              <p style={{ color: '#ffd700', margin: 0, fontSize: '0.9rem' }}>
                Debug: Headlines: {headlines?.length || 0}, Buttons: {buttons?.length || 0}, CombinationResults: {combinationResults?.length || 0}
              </p>
              <p style={{ color: '#ffd700', margin: 0, fontSize: '0.9rem' }}>
                ABTestConfig enabled: {abTestConfig?.enabled ? 'true' : 'false'}, testAllCombinations: {abTestConfig?.testAllCombinations ? 'true' : 'false'}
              </p>
            </div>
            
            <ABTestCard>
              <CardHeader>
                <CardTitle>Configuração do A/B Test</CardTitle>
                <ActiveToggle 
                  active={abTestConfig.enabled}
                  onClick={() => setAbTestConfig(prev => ({ ...prev, enabled: !prev.enabled }))}
                >
                  {abTestConfig.enabled ? 'ATIVO' : 'INATIVO'}
                </ActiveToggle>
              </CardHeader>
              
              <InputGroup>
                <Label>Intervalo de Rotação (horas)</Label>
                <NumberInput
                  type="number"
                  value={abTestConfig.rotationIntervalHours}
                  onChange={(e) => setAbTestConfig(prev => ({ ...prev, rotationIntervalHours: parseInt(e.target.value) }))}
                  min="1"
                  max="168"
                />
                <DelayInfo>
                  O sistema alternará entre as headlines a cada {abTestConfig.rotationIntervalHours} horas
                </DelayInfo>
              </InputGroup>
              
              <InputGroup>
                 <Label>Mínimo de Views por Teste</Label>
                 <NumberInput
                   type="number"
                   value={abTestConfig.minViewsPerTest}
                   onChange={(e) => setAbTestConfig(prev => ({ ...prev, minViewsPerTest: parseInt(e.target.value) }))}
                   min="10"
                   max="1000"
                 />
                 <DelayInfo>
                   Cada variação precisa de pelo menos {abTestConfig.minViewsPerTest} visualizações
                 </DelayInfo>
               </InputGroup>
               
               <InputGroup>
                 <Label>
                   <input
                     type="checkbox"
                     checked={abTestConfig.testAllCombinations}
                     onChange={(e) => setAbTestConfig(prev => ({ ...prev, testAllCombinations: e.target.checked }))}
                   />
                   Testar todas as combinações (Headlines × Botões)
                 </Label>
                 <DelayInfo>
                   {abTestConfig.testAllCombinations 
                     ? `Testará ${headlines.length} headlines × ${buttons.length} botões = ${headlines.length * buttons.length} combinações`
                     : 'Testará apenas as 3 headlines com cores diferentes'
                   }
                 </DelayInfo>
               </InputGroup>
              
              {abTestConfig.bestPerformingColor && !abTestConfig.testAllCombinations && (
                 <WinnerCard>
                   <WinnerTitle>🏆 Cor Campeã Atual</WinnerTitle>
                   <WinnerColor color={abTestConfig.bestPerformingColor}>
                     {abTestConfig.bestPerformingColor === 'red' ? 'Vermelho' : 
                      abTestConfig.bestPerformingColor === 'blue' ? 'Azul' : 'Laranja'}
                   </WinnerColor>
                   <WinnerDescription>
                     Esta cor está gerando a melhor taxa de conversão
                   </WinnerDescription>
                 </WinnerCard>
               )}
               
               {abTestConfig.bestCombination && abTestConfig.testAllCombinations && (
                 <WinnerCard>
                   <WinnerTitle>🏆 Combinação Campeã</WinnerTitle>
                   <CombinationWinner>
                     <CombinationDetail>
                       <strong>Headline:</strong> {headlines.find(h => h.id === abTestConfig.bestCombination!.headlineId)?.title.substring(0, 40)}...
                     </CombinationDetail>
                     <CombinationDetail>
                       <strong>Botão:</strong> {buttons.find(b => b.id === abTestConfig.bestCombination!.buttonId)?.text.substring(0, 30)}...
                     </CombinationDetail>
                     <CombinationStats>
                       <StatBadge>
                         {abTestConfig.bestCombination.conversionRate.toFixed(2)}% conversão
                       </StatBadge>
                       <StatBadge>
                         {abTestConfig.bestCombination.totalViews} views
                       </StatBadge>
                       <StatBadge>
                         {abTestConfig.bestCombination.totalClicks} clicks
                       </StatBadge>
                     </CombinationStats>
                   </CombinationWinner>
                   <WinnerDescription>
                     Esta combinação está gerando a melhor taxa de conversão
                   </WinnerDescription>
                 </WinnerCard>
               )}
            </ABTestCard>
            
            {!abTestConfig.testAllCombinations && (
               <>
                 <SectionTitle style={{ marginTop: '3rem' }}>Resultados por Cor</SectionTitle>
                 <div style={{ color: 'white', padding: '2rem', background: 'rgba(255,255,255,0.1)', borderRadius: '8px' }}>
                   <p>Seção de resultados por cor temporariamente simplificada para debug.</p>
                   <p>Headlines: {headlines?.length || 0} | Buttons: {buttons?.length || 0}</p>
                 </div>
               </>
             )}
             
             {abTestConfig.testAllCombinations && (
               <>
                 <SectionTitle style={{ marginTop: '3rem' }}>Resultados por Combinação</SectionTitle>
                 <div style={{ color: 'white', padding: '2rem', background: 'rgba(255,255,255,0.1)', borderRadius: '8px' }}>
                   <p>Seção de combinações temporariamente simplificada para debug.</p>
                   <p>Resultados: {combinationResults?.length || 0}</p>
                   <p>Teste ativo: {abTestConfig?.testAllCombinations ? 'Sim' : 'Não'}</p>
                 </div>
               </>
             )}
          </Section>
        )}
      </AdminContent>
      
      <StandardFooter />
    </AdminContainer>
  );
};

// Styled Components
const AdminContainer = styled.div`
  min-height: 100vh;
  background: #000000;
  color: white;
  
  @media (max-width: 768px) {
    padding: 0 10px;
  }
`;

const AdminHeader = styled.header`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 20px;
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  border-radius: 12px;
  border: 1px solid #3b82f6;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  
  @media (max-width: 768px) {
    flex-direction: column;
    gap: 15px;
    padding: 15px;
    margin-bottom: 20px;
  }
`;

const HeaderContent = styled.div`
  flex: 1;
`;

const LogoContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
`;

const Logo = styled.img`
  height: 50px;
  width: auto;
`;

const Title = styled.h1`
  color: #64FFDA;
  font-size: 2.5em;
  margin: 0;
  
  @media (max-width: 768px) {
    font-size: 1.8em;
    text-align: center;
  }
  
  @media (max-width: 480px) {
    font-size: 1.5em;
  }
`;

const Subtitle = styled.p`
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
  
  @media (max-width: 768px) {
    font-size: 1rem;
    text-align: center;
  }
  
  @media (max-width: 480px) {
    font-size: 0.9rem;
  }
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  justify-content: flex-start;
  
  @media (max-width: 768px) {
    flex-direction: column;
    gap: 0.75rem;
    margin-bottom: 1.5rem;
  }
  
  @media (max-width: 480px) {
    gap: 0.5rem;
  }
`;

const PreviewButton = styled.a`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: rgba(33, 150, 243, 0.2);
  border: 1px solid #2196f3;
  color: #2196f3;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.3s ease;
  
  @media (max-width: 768px) {
    padding: 0.6rem 1.2rem;
    font-size: 0.9rem;
    justify-content: center;
  }
  
  @media (max-width: 480px) {
    padding: 0.5rem 1rem;
    font-size: 0.8rem;
  }
  
  &:hover {
    background: #2196f3;
    color: white;
  }
`;

const SaveButton = styled.button`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #4caf50, #45a049);
  border: none;
  color: white;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  
  @media (max-width: 768px) {
    padding: 0.6rem 1.2rem;
    font-size: 0.9rem;
    justify-content: center;
  }
  
  @media (max-width: 480px) {
    padding: 0.5rem 1rem;
    font-size: 0.8rem;
  }
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(76, 175, 80, 0.4);
  }
`;

const TabNavigation = styled.nav`
  display: flex;
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid #333;
  overflow-x: auto;
  
  @media (max-width: 768px) {
    scrollbar-width: none;
    -ms-overflow-style: none;
    
    &::-webkit-scrollbar {
      display: none;
    }
  }
`;

const TabButton = styled.button.withConfig({
  shouldForwardProp: (prop) => prop !== 'active'
})<{ active: boolean }>`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  background: ${props => props.active ? 'rgba(33, 150, 243, 0.2)' : 'transparent'};
  border: none;
  color: ${props => props.active ? '#2196f3' : 'rgba(255, 255, 255, 0.7)'};
  border-bottom: 2px solid ${props => props.active ? '#2196f3' : 'transparent'};
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
  
  @media (max-width: 768px) {
    padding: 0.8rem 1.2rem;
    font-size: 0.9rem;
    gap: 0.3rem;
  }
  
  @media (max-width: 480px) {
    padding: 0.6rem 1rem;
    font-size: 0.8rem;
  }
  
  &:hover {
    background: rgba(33, 150, 243, 0.1);
    color: #2196f3;
  }
`;

const AdminContent = styled.main`
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  
  @media (max-width: 768px) {
    padding: 1.5rem;
  }
  
  @media (max-width: 480px) {
    padding: 1rem;
  }
`;

const Section = styled.section`
  margin-bottom: 3rem;
  
  @media (max-width: 768px) {
    margin-bottom: 2rem;
  }
  
  @media (max-width: 480px) {
    margin-bottom: 1.5rem;
  }
`;

const SectionTitle = styled.h2`
  font-size: 2rem;
  font-weight: 600;
  margin: 0 0 0.5rem 0;
  color: white;
  
  @media (max-width: 768px) {
    font-size: 1.5rem;
  }
  
  @media (max-width: 480px) {
    font-size: 1.3rem;
  }
`;

const SectionDescription = styled.p`
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.7);
  margin: 0 0 2rem 0;
  
  @media (max-width: 768px) {
    font-size: 1rem;
    margin-bottom: 1.5rem;
  }
  
  @media (max-width: 480px) {
    font-size: 0.9rem;
    margin-bottom: 1rem;
  }
`;

const HeadlinesGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
  
  @media (max-width: 768px) {
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
  }
  
  @media (max-width: 480px) {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
`;

const ButtonsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
  
  @media (max-width: 768px) {
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
  }
  
  @media (max-width: 480px) {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
`;

const HeadlineCard = styled.div.withConfig({
  shouldForwardProp: (prop) => prop !== 'active'
})<{ active: boolean }>`
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid ${props => props.active ? '#4caf50' : 'rgba(255, 255, 255, 0.1)'};
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
  
  @media (max-width: 768px) {
    padding: 1.2rem;
  }
  
  @media (max-width: 480px) {
    padding: 1rem;
  }
`;

const ButtonCard = styled.div.withConfig({
  shouldForwardProp: (prop) => prop !== 'active'
})<{ active: boolean }>`
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid ${props => props.active ? '#4caf50' : 'rgba(255, 255, 255, 0.1)'};
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
  
  @media (max-width: 768px) {
    padding: 1.2rem;
  }
  
  @media (max-width: 480px) {
    padding: 1rem;
  }
`;

const DelayCard = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 2rem;
  max-width: 600px;
  
  @media (max-width: 768px) {
    padding: 1.5rem;
    max-width: 100%;
  }
  
  @media (max-width: 480px) {
    padding: 1.2rem;
  }
`;

const CardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  
  @media (max-width: 480px) {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
`;

const CardTitle = styled.h3`
  font-size: 1.3rem;
  font-weight: 600;
  margin: 0;
  color: white;
  
  @media (max-width: 768px) {
    font-size: 1.2rem;
  }
  
  @media (max-width: 480px) {
    font-size: 1.1rem;
  }
`;

const ActiveToggle = styled.button.withConfig({
  shouldForwardProp: (prop) => prop !== 'active'
})<{ active: boolean }>`
  padding: 0.5rem 1rem;
  background: ${props => props.active ? '#4caf50' : '#666'};
  border: none;
  color: white;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  
  @media (max-width: 768px) {
    padding: 0.4rem 0.8rem;
    font-size: 0.75rem;
  }
  
  @media (max-width: 480px) {
    padding: 0.3rem 0.6rem;
    font-size: 0.7rem;
  }
  
  &:hover {
    transform: scale(1.05);
  }
`;

const InputGroup = styled.div`
  margin-bottom: 1.5rem;
  
  @media (max-width: 768px) {
    margin-bottom: 1.2rem;
  }
  
  @media (max-width: 480px) {
    margin-bottom: 1rem;
  }
`;

const Label = styled.label`
  display: block;
  font-size: 0.9rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 0.5rem;
  
  @media (max-width: 768px) {
    font-size: 0.85rem;
  }
  
  @media (max-width: 480px) {
    font-size: 0.8rem;
  }
`;

const TextInput = styled.input`
  width: 100%;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  color: white;
  font-size: 1rem;
  
  @media (max-width: 768px) {
    padding: 0.6rem;
    font-size: 0.9rem;
  }
  
  @media (max-width: 480px) {
    padding: 0.5rem;
    font-size: 0.85rem;
  }
  
  &:focus {
    outline: none;
    border-color: #2196f3;
    box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2);
  }
  
  &::placeholder {
    color: rgba(255, 255, 255, 0.5);
  }
`;

const TextArea = styled.textarea`
  width: 100%;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  color: white;
  font-size: 1rem;
  resize: vertical;
  
  @media (max-width: 768px) {
    padding: 0.6rem;
    font-size: 0.9rem;
  }
  
  @media (max-width: 480px) {
    padding: 0.5rem;
    font-size: 0.85rem;
  }
  
  &:focus {
    outline: none;
    border-color: #2196f3;
    box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2);
  }
  
  &::placeholder {
    color: rgba(255, 255, 255, 0.5);
  }
`;

const ColorRow = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  
  @media (max-width: 480px) {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }
`;

const ColorInput = styled.input`
  width: 100%;
  height: 50px;
  padding: 0;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  cursor: pointer;
  
  @media (max-width: 768px) {
    height: 45px;
  }
  
  @media (max-width: 480px) {
    height: 40px;
  }
  
  &:focus {
    outline: none;
    border-color: #2196f3;
  }
`;

const NumberInput = styled.input`
  width: 100%;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  color: white;
  font-size: 1rem;
  
  @media (max-width: 768px) {
    padding: 0.6rem;
    font-size: 0.9rem;
  }
  
  @media (max-width: 480px) {
    padding: 0.5rem;
    font-size: 0.85rem;
  }
  
  &:focus {
    outline: none;
    border-color: #2196f3;
    box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2);
  }
`;

const DelayInfo = styled.div`
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 0.5rem;
  
  @media (max-width: 768px) {
    font-size: 0.85rem;
  }
  
  @media (max-width: 480px) {
    font-size: 0.8rem;
  }
`;

const ModernButtonPreview = styled.div.withConfig({
  shouldForwardProp: (prop) => prop !== 'buttonColor' && prop !== 'textColor'
})<{ buttonColor: string; textColor: string }>`
  background: linear-gradient(135deg, 
    ${props => props.buttonColor}, 
    ${props => {
      // Cria gradientes que combinam com a cor escolhida
      const color = props.buttonColor;
      if (color.includes('#ff') || color.includes('orange')) {
        return '#ff6b35'; // Laranja para vermelho
      } else if (color.includes('#f7') || color.includes('yellow')) {
        return '#ffd700'; // Amarelo dourado
      } else if (color.includes('red')) {
        return '#ff4757'; // Vermelho vibrante
      } else if (color.includes('blue')) {
        return '#3742fa'; // Azul vibrante
      } else {
        return color + 'dd'; // Fallback com transparência
      }
    }}
  );
  border: 3px solid ${props => props.buttonColor};
  border-radius: 12px;
  padding: 0;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  animation: fadeInUp 0.6s ease-out;
  box-shadow: 
    0 8px 25px rgba(0, 0, 0, 0.15),
    0 4px 10px rgba(0, 0, 0, 0.1),
    inset 0 2px 0 rgba(255, 255, 255, 0.15),
    0 0 0 1px rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;
  margin-top: 1rem;
  max-width: 350px;
  width: 100%;
  
  &:before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
    transition: left 0.6s ease;
  }
  
  &:hover {
    transform: translateY(-6px) scale(1.03);
    box-shadow: 
      0 20px 40px rgba(0, 0, 0, 0.25),
      0 10px 20px rgba(0, 0, 0, 0.15),
      inset 0 2px 0 rgba(255, 255, 255, 0.2),
      0 0 0 2px ${props => props.buttonColor};
    border-color: ${props => props.buttonColor};
    
    &:before {
      left: 100%;
    }
  }
  
  &:active {
    transform: translateY(-3px) scale(0.98);
  }
  
  @keyframes fadeInUp {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
`;

const ButtonPreviewContent = styled.div`
  padding: 1rem 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.2rem;
  position: relative;
  z-index: 1;
`;

const ButtonPreviewText = styled.span`
  color: white;
  font-size: 0.9rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  text-align: center;
  line-height: 1.2;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.4);
`;

const ButtonPreviewSubtext = styled.span`
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.7rem;
  font-weight: 500;
  text-align: center;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  font-style: italic;
`;

const ColorPalette = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 0.75rem;
  margin-bottom: 1rem;
  
  @media (max-width: 768px) {
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 0.5rem;
  }
  
  @media (max-width: 480px) {
    grid-template-columns: repeat(2, 1fr);
    gap: 0.4rem;
  }
`;

const ColorPaletteButton = styled.button.withConfig({
  shouldForwardProp: (prop) => prop !== 'color'
})<{ color: string }>`
  background: linear-gradient(135deg, ${props => props.color}, ${props => props.color}dd);
  border: 2px solid ${props => props.color};
  border-radius: 8px;
  padding: 0.75rem 1rem;
  color: white;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  position: relative;
  overflow: hidden;
  
  &:before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transition: left 0.4s;
  }
  
  &:hover {
    transform: translateY(-2px) scale(1.05);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
    border-color: ${props => props.color};
    
    &:before {
      left: 100%;
    }
  }
  
  &:active {
    transform: translateY(0) scale(0.98);
  }
`;

const MetricsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
`;

const MetricCard = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
`;

const MetricValue = styled.div`
  font-size: 2.5rem;
  font-weight: 700;
  color: #2196f3;
  margin-bottom: 0.5rem;
`;

const MetricLabel = styled.div`
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.7);
`;

const ABTestCard = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 2rem;
  max-width: 800px;
`;

const ColorSelector = styled.div`
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
`;

const ColorOption = styled.button<{ color: string; selected: boolean }>`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: ${props => props.selected ? props.color : 'rgba(255, 255, 255, 0.1)'};
  border: 2px solid ${props => props.selected ? props.color : 'rgba(255, 255, 255, 0.2)'};
  color: ${props => props.selected ? 'white' : 'rgba(255, 255, 255, 0.8)'};
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
  
  &:before {
    content: '';
    width: 12px;
    height: 12px;
    background: ${props => props.color};
    border-radius: 50%;
    display: block;
  }
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
  }
`;

const TestResults = styled.div`
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  flex-wrap: wrap;
`;

const ResultItem = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
`;

const ResultLabel = styled.span`
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.6);
`;

const ResultValue = styled.span`
  font-size: 1.1rem;
  font-weight: 600;
  color: #2196f3;
`;

const WinnerCard = styled.div`
  background: linear-gradient(135deg, rgba(76, 175, 80, 0.2), rgba(76, 175, 80, 0.1));
  border: 2px solid #4caf50;
  border-radius: 12px;
  padding: 1.5rem;
  margin-top: 2rem;
  text-align: center;
`;

const WinnerTitle = styled.h3`
  font-size: 1.3rem;
  font-weight: 700;
  color: #4caf50;
  margin: 0 0 1rem 0;
`;

const WinnerColor = styled.div<{ color: string }>`
  display: inline-block;
  padding: 0.5rem 1.5rem;
  background: ${props => 
    props.color === 'red' ? '#ff3333' : 
    props.color === 'blue' ? '#2196f3' : '#ff9800'};
  color: white;
  border-radius: 20px;
  font-weight: 600;
  font-size: 1.1rem;
  margin-bottom: 1rem;
`;

const WinnerDescription = styled.p`
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
  font-size: 0.95rem;
`;

const ColorResultsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin-top: 2rem;
  
  @media (max-width: 768px) {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin-top: 1.5rem;
  }
  
  @media (max-width: 480px) {
    grid-template-columns: 1fr;
    gap: 1rem;
    margin-top: 1rem;
  }
`;

const ColorResultCard = styled.div<{ color: string }>`
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid ${props => 
    props.color === 'red' ? '#ff3333' : 
    props.color === 'blue' ? '#2196f3' : '#ff9800'};
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
  
  @media (max-width: 768px) {
    padding: 1.2rem;
  }
  
  @media (max-width: 480px) {
    padding: 1rem;
  }
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
  }
`;

const ColorResultHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  
  @media (max-width: 480px) {
    gap: 0.75rem;
    margin-bottom: 1rem;
  }
`;

const ColorDot = styled.div<{ color: string }>`
  width: 20px;
  height: 20px;
  background: ${props => props.color};
  border-radius: 50%;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
`;

const ColorResultTitle = styled.h3`
  font-size: 1.2rem;
  font-weight: 600;
  color: white;
  margin: 0;
  
  @media (max-width: 768px) {
    font-size: 1.1rem;
  }
  
  @media (max-width: 480px) {
    font-size: 1rem;
  }
`;

const ColorResultStats = styled.div`
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  
  @media (max-width: 480px) {
    flex-direction: column;
    gap: 0.75rem;
  }
`;

const StatItem = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
`;

const StatValue = styled.div`
  font-size: 1.5rem;
  font-weight: 700;
  color: #2196f3;
  
  @media (max-width: 768px) {
    font-size: 1.3rem;
  }
  
  @media (max-width: 480px) {
    font-size: 1.2rem;
  }
`;

const StatLabel = styled.div`
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.6);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  
  @media (max-width: 768px) {
    font-size: 0.75rem;
  }
  
  @media (max-width: 480px) {
    font-size: 0.7rem;
  }
`;

const CombinationWinner = styled.div`
  margin: 1rem 0;
`;

const CombinationDetail = styled.div`
  margin: 0.5rem 0;
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.9rem;
  line-height: 1.4;
`;

const CombinationStats = styled.div`
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
  flex-wrap: wrap;
`;

const StatBadge = styled.div`
  background: rgba(33, 150, 243, 0.2);
  color: #2196f3;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  border: 1px solid rgba(33, 150, 243, 0.3);
`;

const CombinationResultsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
  margin-top: 2rem;
  
  @media (max-width: 768px) {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1.2rem;
    margin-top: 1.5rem;
  }
  
  @media (max-width: 480px) {
    grid-template-columns: 1fr;
    gap: 1rem;
    margin-top: 1rem;
  }
`;

const CombinationResultCard = styled.div<{ isWinner: boolean }>`
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid ${props => props.isWinner ? '#4caf50' : 'rgba(255, 255, 255, 0.1)'};
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
  position: relative;
  
  ${props => props.isWinner && `
    background: linear-gradient(135deg, rgba(76, 175, 80, 0.1), rgba(76, 175, 80, 0.05));
    box-shadow: 0 4px 20px rgba(76, 175, 80, 0.2);
  `}
  
  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
  }
`;

const CombinationResultHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
`;

const CombinationRank = styled.div<{ isWinner: boolean }>`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: ${props => props.isWinner ? '1.5rem' : '1rem'};
  background: ${props => props.isWinner ? 'linear-gradient(135deg, #4caf50, #45a049)' : 'rgba(255, 255, 255, 0.1)'};
  color: ${props => props.isWinner ? 'white' : 'rgba(255, 255, 255, 0.7)'};
  border: 2px solid ${props => props.isWinner ? '#4caf50' : 'rgba(255, 255, 255, 0.2)'};
`;

const CombinationResultTitle = styled.h3`
  font-size: 1.1rem;
  font-weight: 600;
  color: white;
  margin: 0;
`;

const CombinationDetails = styled.div`
  margin: 1rem 0;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
`;

const CombinationResultStats = styled.div`
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  margin-top: 1rem;
`;

const TestingBadge = styled.div`
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: rgba(255, 152, 0, 0.2);
  color: #ff9800;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
  border: 1px solid rgba(255, 152, 0, 0.3);
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 3rem 2rem;
  color: rgba(255, 255, 255, 0.6);
`;

const EmptyStateIcon = styled.div`
  font-size: 4rem;
  margin-bottom: 1rem;
`;

const EmptyStateTitle = styled.h3`
  font-size: 1.5rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
  margin: 0 0 0.5rem 0;
`;

const EmptyStateDescription = styled.p`
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
  max-width: 400px;
  margin: 0 auto;
  line-height: 1.5;
`;

// Styled components para overlay de vídeo
const VideoOverlayGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
  
  @media (max-width: 768px) {
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
    margin-bottom: 1.5rem;
  }
  
  @media (max-width: 480px) {
    grid-template-columns: 1fr;
    gap: 1rem;
    margin-bottom: 1rem;
  }
`;

const VideoOverlayCard = styled.div.withConfig({
  shouldForwardProp: (prop) => prop !== 'active'
})<{ active: boolean }>`
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid ${props => props.active ? '#4caf50' : 'rgba(255, 255, 255, 0.1)'};
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
  
  @media (max-width: 768px) {
    padding: 1.2rem;
  }
  
  @media (max-width: 480px) {
    padding: 1rem;
  }
`;

const VideoOverlayPreview = styled.div.withConfig({
  shouldForwardProp: (prop) => prop !== 'overlayStyle'
})<{ overlayStyle: string }>`
  width: 100%;
  height: 200px;
  background: ${props => {
    switch (props.overlayStyle) {
      case 'classic':
        return 'linear-gradient(135deg, rgba(33, 150, 243, 0.8), rgba(33, 150, 243, 0.6))';
      case 'modern':
        return 'linear-gradient(135deg, rgba(76, 175, 80, 0.8), rgba(76, 175, 80, 0.6))';
      case 'minimal':
        return 'linear-gradient(135deg, rgba(255, 152, 0, 0.8), rgba(255, 152, 0, 0.6))';
      default:
        return 'rgba(0, 0, 0, 0.7)';
    }
  }};
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  margin-top: 1rem;
  border: 2px solid ${props => {
    switch (props.overlayStyle) {
      case 'classic':
        return '#2196f3';
      case 'modern':
        return '#4caf50';
      case 'minimal':
        return '#ff9800';
      default:
        return 'rgba(255, 255, 255, 0.2)';
    }
  }};
  
  &:before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: ${props => {
      switch (props.overlayStyle) {
        case 'classic':
          return 'url("data:image/svg+xml,%3Csvg width="20" height="20" xmlns="http://www.w3.org/2000/svg"%3E%3Cdefs%3E%3Cpattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse"%3E%3Cpath d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="1"/%3E%3C/pattern%3E%3C/defs%3E%3Crect width="100%25" height="100%25" fill="url(%23grid)" /%3E%3C/svg%3E")';
        case 'modern':
          return 'radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.1) 0%, transparent 50%)';
        case 'minimal':
          return 'linear-gradient(45deg, rgba(255, 255, 255, 0.05) 25%, transparent 25%, transparent 75%, rgba(255, 255, 255, 0.05) 75%)';
        default:
          return 'none';
      }
    }};
    pointer-events: none;
  }
`;

const OverlayPreviewContent = styled.div.withConfig({
  shouldForwardProp: (prop) => prop !== 'overlayStyle'
})<{ overlayStyle: string }>`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: ${props => props.overlayStyle === 'minimal' ? '0' : '1rem'};
  text-align: center;
  padding: 2rem;
  position: relative;
  z-index: 1;
`;

const SpeakerIconPreview = styled.div`
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
  animation: pulse 2s infinite;
  
  @keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.1); }
    100% { transform: scale(1); }
  }
`;

const PlayButtonPreview = styled.div`
  width: 60px;
  height: 60px;
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

const PlayButtonIconPreview = styled.div`
  font-size: 1.5rem;
  color: #333;
  margin-left: 3px;
`;

const OverlayMessagePreview = styled.div.withConfig({
  shouldForwardProp: (prop) => prop !== 'overlayStyle'
})<{ overlayStyle: string }>`
  color: white;
  font-weight: ${props => props.overlayStyle === 'minimal' ? '700' : '600'};
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
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);
  line-height: 1.4;
  
  ${props => props.overlayStyle === 'classic' && `
    background: rgba(0, 0, 0, 0.8);
    padding: 0.75rem 1rem;
    border-radius: 6px;
    border: 2px solid rgba(255, 255, 255, 0.3);
  `}
  
  ${props => props.overlayStyle === 'modern' && `
    background: linear-gradient(135deg, rgba(33, 150, 243, 0.9), rgba(33, 150, 243, 0.7));
    padding: 0.5rem 1rem;
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.2);
  `}
  
  ${props => props.overlayStyle === 'minimal' && `
    text-transform: uppercase;
    letter-spacing: 2px;
    font-family: 'Arial', sans-serif;
  `}
 `;

// Styled components para preview da barra de progresso
const ProgressBarPreview = styled.div`
  margin-top: 1rem;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
`;

const ProgressBarPreviewBackground = styled.div.withConfig({
  shouldForwardProp: (prop) => prop !== 'backgroundColor'
})<{ backgroundColor: string }>`
  width: 100%;
  height: 6px;
  background: ${props => props.backgroundColor};
  border-radius: 3px;
  position: relative;
  overflow: hidden;
`;

const ProgressBarPreviewFill = styled.div.withConfig({
  shouldForwardProp: (prop) => prop !== 'primaryColor' && prop !== 'secondaryColor'
})<{ primaryColor: string; secondaryColor: string }>`
  width: 60%;
  height: 100%;
  background: linear-gradient(90deg, ${props => props.primaryColor}, ${props => props.secondaryColor});
  border-radius: 3px;
  position: relative;
  animation: progressDemo 3s ease-in-out infinite;
  
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
  
  @keyframes progressDemo {
    0% { width: 10%; }
    50% { width: 60%; }
    100% { width: 90%; }
  }
`;

const ProgressBarPreviewLabel = styled.div`
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.8rem;
  margin-top: 0.5rem;
  text-align: center;
`;

export default SalesAdminPage;