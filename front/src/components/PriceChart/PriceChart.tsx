import React, { useState, useEffect, useRef } from 'react';
import styles from './PriceChart.module.css';

/**
 * Interface para dados de preço
 */
interface PricePoint {
  timestamp: number;
  price: number;
  volume: number;
}

/**
 * Interface para propriedades do componente
 */
interface PriceChartProps {
  symbol?: string;
  timeframe?: '1m' | '5m' | '15m' | '1h' | '4h' | '1d';
  height?: number;
}

/**
 * Componente de gráfico de preços em tempo real
 * Exibe um gráfico de linha simples com dados de preço
 */
const PriceChart: React.FC<PriceChartProps> = ({ 
  symbol = 'BTC/USDT', 
  timeframe = '5m',
  height = 300 
}) => {
  const [priceData, setPriceData] = useState<PricePoint[]>([]);
  const [currentPrice, setCurrentPrice] = useState<number>(0);
  const [priceChange, setPriceChange] = useState<number>(0);
  const [isLoading, setIsLoading] = useState(true);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();

  /**
   * Gera dados simulados de preço
   */
  const generateMockData = (count: number = 50): PricePoint[] => {
    const data: PricePoint[] = [];
    const basePrice = 45000 + Math.random() * 10000;
    const now = Date.now();
    
    for (let i = 0; i < count; i++) {
      const timestamp = now - (count - i) * 5 * 60 * 1000; // 5 minutos entre pontos
      const volatility = 0.02; // 2% de volatilidade
      const change = (Math.random() - 0.5) * volatility;
      const price = i === 0 ? basePrice : data[i - 1].price * (1 + change);
      const volume = Math.random() * 1000000 + 500000;
      
      data.push({ timestamp, price, volume });
    }
    
    return data;
  };

  /**
   * Adiciona um novo ponto de dados
   */
  const addNewDataPoint = () => {
    setPriceData(prevData => {
      if (prevData.length === 0) return prevData;
      
      const lastPoint = prevData[prevData.length - 1];
      const volatility = 0.01;
      const change = (Math.random() - 0.5) * volatility;
      const newPrice = lastPoint.price * (1 + change);
      const newVolume = Math.random() * 1000000 + 500000;
      
      const newPoint: PricePoint = {
        timestamp: Date.now(),
        price: newPrice,
        volume: newVolume
      };
      
      setCurrentPrice(newPrice);
      setPriceChange(((newPrice - prevData[0].price) / prevData[0].price) * 100);
      
      // Mantém apenas os últimos 50 pontos
      const newData = [...prevData.slice(-49), newPoint];
      return newData;
    });
  };

  /**
   * Desenha o gráfico no canvas
   */
  const drawChart = () => {
    const canvas = canvasRef.current;
    if (!canvas || priceData.length === 0) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    const { width, height } = canvas;
    
    // Limpa o canvas
    ctx.clearRect(0, 0, width, height);
    
    // Configurações
    const padding = 40;
    const chartWidth = width - padding * 2;
    const chartHeight = height - padding * 2;
    
    // Encontra min/max dos preços
    const prices = priceData.map(d => d.price);
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    const priceRange = maxPrice - minPrice;
    
    // Desenha o fundo do gráfico
    ctx.fillStyle = 'rgba(15, 42, 68, 0.8)';
    ctx.fillRect(padding, padding, chartWidth, chartHeight);
    
    // Desenha linhas de grade
    ctx.strokeStyle = 'rgba(100, 255, 218, 0.1)';
    ctx.lineWidth = 1;
    
    // Linhas horizontais
    for (let i = 0; i <= 5; i++) {
      const y = padding + (chartHeight / 5) * i;
      ctx.beginPath();
      ctx.moveTo(padding, y);
      ctx.lineTo(padding + chartWidth, y);
      ctx.stroke();
    }
    
    // Linhas verticais
    for (let i = 0; i <= 10; i++) {
      const x = padding + (chartWidth / 10) * i;
      ctx.beginPath();
      ctx.moveTo(x, padding);
      ctx.lineTo(x, padding + chartHeight);
      ctx.stroke();
    }
    
    // Desenha a linha de preço
    ctx.strokeStyle = priceChange >= 0 ? '#4CAF50' : '#E53E3E';
    ctx.lineWidth = 2;
    ctx.beginPath();
    
    priceData.forEach((point, index) => {
      const x = padding + (index / (priceData.length - 1)) * chartWidth;
      const y = padding + chartHeight - ((point.price - minPrice) / priceRange) * chartHeight;
      
      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    
    ctx.stroke();
    
    // Desenha área sob a curva
    ctx.fillStyle = priceChange >= 0 ? 'rgba(76, 175, 80, 0.1)' : 'rgba(229, 62, 62, 0.1)';
    ctx.beginPath();
    
    priceData.forEach((point, index) => {
      const x = padding + (index / (priceData.length - 1)) * chartWidth;
      const y = padding + chartHeight - ((point.price - minPrice) / priceRange) * chartHeight;
      
      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    
    ctx.lineTo(padding + chartWidth, padding + chartHeight);
    ctx.lineTo(padding, padding + chartHeight);
    ctx.closePath();
    ctx.fill();
    
    // Desenha ponto atual
    if (priceData.length > 0) {
      const lastPoint = priceData[priceData.length - 1];
      const x = padding + chartWidth;
      const y = padding + chartHeight - ((lastPoint.price - minPrice) / priceRange) * chartHeight;
      
      ctx.fillStyle = priceChange >= 0 ? '#4CAF50' : '#E53E3E';
      ctx.beginPath();
      ctx.arc(x, y, 4, 0, 2 * Math.PI);
      ctx.fill();
      
      // Efeito de pulso
      ctx.strokeStyle = priceChange >= 0 ? '#4CAF50' : '#E53E3E';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(x, y, 8, 0, 2 * Math.PI);
      ctx.stroke();
    }
    
    // Labels de preço
    ctx.fillStyle = '#A0AEC0';
    ctx.font = '12px Arial';
    ctx.textAlign = 'right';
    
    for (let i = 0; i <= 5; i++) {
      const price = minPrice + (priceRange / 5) * (5 - i);
      const y = padding + (chartHeight / 5) * i + 4;
      ctx.fillText(`$${price.toFixed(0)}`, padding - 10, y);
    }
  };

  /**
   * Redimensiona o canvas
   */
  const resizeCanvas = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const container = canvas.parentElement;
    if (!container) return;
    
    canvas.width = container.clientWidth;
    canvas.height = height;
    
    drawChart();
  };

  /**
   * Loop de animação
   */
  const animate = () => {
    drawChart();
    animationRef.current = requestAnimationFrame(animate);
  };

  /**
   * Inicialização
   */
  useEffect(() => {
    const initialData = generateMockData();
    setPriceData(initialData);
    setCurrentPrice(initialData[initialData.length - 1].price);
    setPriceChange(0);
    setIsLoading(false);
    
    // Adiciona novos pontos a cada 5 segundos
    const interval = setInterval(addNewDataPoint, 5000);
    
    return () => clearInterval(interval);
  }, []);

  /**
   * Configuração do canvas
   */
  useEffect(() => {
    resizeCanvas();
    animate();
    
    window.addEventListener('resize', resizeCanvas);
    
    return () => {
      window.removeEventListener('resize', resizeCanvas);
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [priceData]);

  if (isLoading) {
    return (
      <div className={styles.chartContainer}>
        <div className={styles.loadingSpinner}>
          <div className={styles.spinner}></div>
          <span>Carregando gráfico...</span>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.chartContainer}>
      <div className={styles.chartHeader}>
        <div className={styles.symbolInfo}>
          <h3 className={styles.symbol}>{symbol}</h3>
          <div className={styles.timeframe}>{timeframe}</div>
        </div>
        <div className={styles.priceInfo}>
          <div className={styles.currentPrice}>
            ${currentPrice.toFixed(2)}
          </div>
          <div className={`${styles.priceChange} ${priceChange >= 0 ? styles.positive : styles.negative}`}>
            {priceChange >= 0 ? '+' : ''}{priceChange.toFixed(2)}%
          </div>
        </div>
      </div>
      
      <div className={styles.chartWrapper}>
        <canvas 
          ref={canvasRef}
          className={styles.chart}
        />
      </div>
      
      <div className={styles.chartFooter}>
        <div className={styles.indicators}>
          <div className={styles.indicator}>
            <span className={styles.indicatorLabel}>Volume 24h:</span>
            <span className={styles.indicatorValue}>
              ${(priceData[priceData.length - 1]?.volume || 0).toLocaleString()}
            </span>
          </div>
          <div className={styles.indicator}>
            <span className={styles.indicatorLabel}>Última atualização:</span>
            <span className={styles.indicatorValue}>
              {new Date().toLocaleTimeString('pt-BR')}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PriceChart;