# Imports necessários
from binance.client import Client
from binance.exceptions import BinanceAPIException
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any, TypedDict
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange
from config import server
import time
import traceback
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from .database import Database
from colorama import Fore, Style, init
from .binance_client import BinanceClient
from .gerenciar_sinais import GerenciadorSinais
from .telegram_notifier import TelegramNotifier
from .btc_correlation_analyzer import BTCCorrelationAnalyzer
from .klines_cache import CacheManager
# from .coin_ranking import coin_ranking  # Removido - sistema de ranking desabilitado

# Initialize colorama
init()

class TechnicalAnalysisConfig(TypedDict):
    trend_timeframe: str
    entry_timeframe: str
    quality_score_minimum: float
    scan_interval: int
    pairs_update_interval: int

class TechnicalAnalysis:
    """Sistema principal de análise técnica e monitoramento de mercado"""
    
    def __init__(self, db_instance: Database):
        """Inicializa o sistema de análise técnica"""
        print("📊 Inicializando TechnicalAnalysis...")
        
        # Dependências principais
        self.db = db_instance
        self.binance = BinanceClient()
        self.gerenciador = GerenciadorSinais(db_instance)
        
        # Configurações do sistema
        self.config = {
            'trend_timeframe': '4h',
            'entry_timeframe': '1h',
            'quality_score_minimum': 65.0,  # Mínimo 65 pontos para sinais de qualidade
            'scan_interval': 60,  # 60 segundos
            'pairs_update_interval': 1200,  # 20 minutos
            'target_percentage_min': 6.0,
            'max_pairs': 100
        }
        
        # Estado do sistema
        self.top_pairs: List[str] = []
        self.all_usdt_pairs: List[str] = []
        self.pairs_last_update: float = 0
        self.is_monitoring: bool = False
        self.monitoring_thread: Optional[threading.Thread] = None
        
        # Configurar notificações (opcional)
        self.notifier = self._setup_telegram_notifier()
        
        # Inicializar sistema de cache
        self.cache_manager = CacheManager()
        
        # Inicializar sistema de confirmação BTC
        from .btc_signal_manager import BTCSignalManager
        self.btc_signal_manager = BTCSignalManager(db_instance)
        
        print("✅ TechnicalAnalysis inicializado com sucesso!")
    
    def _setup_telegram_notifier(self) -> Optional[TelegramNotifier]:
        """Configura notificações do Telegram (opcional)"""
        try:
            telegram_token = server.config.get('TELEGRAM_TOKEN')
            telegram_chat_id = server.config.get('TELEGRAM_CHAT_ID')
            
            if telegram_token and telegram_chat_id:
                notifier = TelegramNotifier(telegram_token, telegram_chat_id)
                if notifier.test_connection():
                    print("✅ Telegram configurado com sucesso!")
                    return notifier
            
            print("⚠️ Telegram não configurado")
            return None
        except Exception as e:
            print(f"⚠️ Erro ao configurar Telegram: {e}")
            return None
    
    def start_monitoring(self) -> bool:
        """Inicia o monitoramento contínuo do mercado"""
        if self.is_monitoring:
            print("⚠️ Monitoramento já está ativo")
            return False
        
        print("🚀 Iniciando monitoramento de mercado...")
        self.is_monitoring = True
        
        # Iniciar monitoramento do BTCSignalManager
        self.btc_signal_manager.start_monitoring()
        
        # Pular inicialização de pares para permitir Flask iniciar rapidamente
        # Os pares serão carregados no primeiro ciclo do monitoring_loop
        
        # Iniciar thread de monitoramento
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop, 
            daemon=True
        )
        self.monitoring_thread.start()
        
        print("✅ Monitoramento iniciado com sucesso!")
        print(f"🔍 Thread de monitoramento ativa: {self.monitoring_thread.is_alive()}")
        print(f"🔍 Thread ID: {self.monitoring_thread.ident}")
        return True
    
    def stop_monitoring(self) -> None:
        """Para o monitoramento"""
        print("🛑 Parando monitoramento...")
        self.is_monitoring = False
        
        # Parar monitoramento do BTCSignalManager
        self.btc_signal_manager.stop_monitoring()
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        
        print("✅ Monitoramento parado")
    
    def _monitoring_loop(self) -> None:
        """Loop principal de monitoramento"""
        print("\n" + "="*70)
        print("🤖 INICIANDO MONITORAMENTO DE MERCADO")
        print(f"🔍 Thread atual: {threading.current_thread().name}")
        print(f"🔍 Thread ID: {threading.current_thread().ident}")
        print("="*70)
        
        while self.is_monitoring:
            try:
                cycle_start = time.time()
                current_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                
                print(f"\n⏰ {current_time}")
                print("🔍 Iniciando nova varredura...")
                
                # Executar varredura do mercado
                signals = self.scan_market(verbose=True)
                
                # Processar sinais encontrados
                if signals:
                    self._process_new_signals(signals)
                else:
                    print("📊 Nenhum sinal encontrado neste ciclo")
                
                # Calcular tempo de espera
                cycle_duration = time.time() - cycle_start
                wait_time = max(0, self.config['scan_interval'] - cycle_duration)
                
                print(f"⏳ Próxima varredura em {wait_time:.0f}s")
                print("="*70)
                
                # Aguardar próximo ciclo (interrompível)
                self._interruptible_sleep(wait_time)
                
            except Exception as e:
                print(f"❌ Erro no ciclo de monitoramento: {e}")
                traceback.print_exc()
                self._interruptible_sleep(5)  # Aguardar 5s antes de tentar novamente
    
    def _interruptible_sleep(self, duration: float) -> None:
        """Sleep que pode ser interrompido"""
        end_time = time.time() + duration
        while time.time() < end_time and self.is_monitoring:
            time.sleep(0.1)
    
    def _process_new_signals(self, signals: List[Dict[str, Any]]) -> None:
        """Processa novos sinais encontrados"""
        print(f"\n✨ {len(signals)} NOVOS SINAIS ENCONTRADOS!")
        print("-" * 50)
        
        for signal in signals:
            # Exibir informações do sinal
            print(f"📊 {signal['symbol']} - {signal['type']}")
            print(f"   💰 Entrada: {signal['entry_price']:.8f}")
            print(f"   🎯 Alvo: {signal['target_price']:.8f}")
            print(f"   📈 Projeção: {signal.get('projection_percentage', 6.0):.1f}%")
            print(f"   ⭐ Qualidade: {signal['quality_score']:.1f} ({signal['signal_class']})")
            print(f"   ₿ BTC Correlação: {signal.get('btc_correlation', 0):.2f} | Tendência: {signal.get('btc_trend', 'N/A')}")
            print(f"   🔗 Score BTC: {signal.get('btc_correlation_score', 0):.1f}pts")
            
            # Enviar notificação se configurado
            if self.notifier:
                try:
                    self.notifier.send_signal(
                        signal['symbol'],
                        signal['type'],
                        float(signal['entry_price']),
                        signal.get('quality_score', 0),
                        signal.get('entry_timeframe', '1h'),
                        signal.get('target_price')
                    )
                except Exception as e:
                    print(f"⚠️ Erro ao enviar notificação: {e}")
        
        print("-" * 50)
    
    def _initialize_pairs(self) -> bool:
        """Inicializa a lista de pares (lazy loading)"""
        try:
            print("🔍 Identificando pares USDT disponíveis...")
            if not self._load_all_usdt_pairs():
                return False
            
            print("📊 Criando lista dos top 100 pares...")
            return self._create_top_pairs()
            
        except Exception as e:
            print(f"❌ Erro na inicialização de pares: {e}")
            traceback.print_exc()
            return False
    
    def _load_all_usdt_pairs(self) -> bool:
        """Carrega todos os pares USDT perpétuos"""
        try:
            print("🔄 Obtendo informações da exchange...")
            exchange_info = self.binance.get_exchange_info()
            if not exchange_info:
                print("❌ Falha ao obter informações da exchange")
                return False
            print(f"✅ Informações da exchange obtidas: {len(exchange_info.get('symbols', []))} símbolos")
            
            # Filtrar pares USDT perpétuos
            self.all_usdt_pairs = [
                symbol['symbol'] for symbol in exchange_info['symbols']
                if (symbol['symbol'].endswith('USDT') and 
                    symbol['status'] == 'TRADING' and 
                    symbol['contractType'] == 'PERPETUAL')
            ]
            
            print(f"✅ {len(self.all_usdt_pairs)} pares USDT identificados")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar pares USDT: {e}")
            return False
    
    def _create_top_pairs(self) -> bool:
        """Cria lista dos top 100 pares baseado em critérios"""
        try:
            # Filtrar por alavancagem >= 50x
            print("🔄 Filtrando por alavancagem >= 50x...")
            leverage_info = self.binance.get_leverage_brackets()
            if not leverage_info:
                return False
            
            valid_pairs = []
            for symbol in self.all_usdt_pairs:
                if symbol in leverage_info:
                    try:
                        max_leverage = float(leverage_info[symbol][0]['initialLeverage'])
                        if max_leverage >= 50:
                            valid_pairs.append(symbol)
                    except (KeyError, IndexError, ValueError):
                        continue
            
            print(f"✅ {len(valid_pairs)} pares com alavancagem >= 50x")
            
            # Obter dados de ticker 24h
            print("📊 Analisando volume e volatilidade...")
            ticker_data = self.binance.get_24h_ticker_data(valid_pairs)
            if not ticker_data:
                return False
            
            # Calcular score e selecionar top 100
            pair_scores = []
            for symbol, data in ticker_data.items():
                try:
                    volume = float(data['volume'])
                    volatility = abs(float(data['priceChangePercent']))
                    
                    # Score: Volume (70%) + Volatilidade (30%)
                    volume_score = np.log10(volume + 1) if volume > 0 else 0
                    final_score = (volume_score * 0.7) + (volatility * 0.3)
                    
                    pair_scores.append({
                        'symbol': symbol,
                        'score': final_score,
                        'volume': volume,
                        'volatility': volatility
                    })
                except (ValueError, KeyError):
                    continue
            
            # Selecionar top 100
            sorted_pairs = sorted(pair_scores, key=lambda x: x['score'], reverse=True)
            self.top_pairs = [pair['symbol'] for pair in sorted_pairs[:self.config['max_pairs']]]
            
            print(f"✅ Top {len(self.top_pairs)} pares selecionados")
            self.pairs_last_update = time.time()
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar top pares: {e}")
            traceback.print_exc()
            return False
    
    def scan_market(self, verbose: bool = False) -> List[Dict[str, Any]]:
        """Executa varredura completa do mercado com processamento paralelo"""
        try:
            scan_start_time = time.time()
            current_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            
            print(f"\n{'='*80}")
            print(f"🔍 INICIANDO ESCANEAMENTO DE MERCADO - {current_time}")
            print(f"{'='*80}")
            
            # Carregar pares se ainda não estiverem carregados (primeira execução)
            if not self.top_pairs:
                print("🔄 Carregando pares iniciais...")
                print(f"🔍 Estado atual: top_pairs={len(self.top_pairs)}, all_usdt_pairs={len(self.all_usdt_pairs)}")
                if not self._initialize_pairs():
                    print("❌ Falha ao carregar pares iniciais")
                    return []
                print(f"✅ Pares carregados: {len(self.top_pairs)} pares disponíveis")
            
            print(f"📊 Analisando {len(self.top_pairs)} pares de criptomoedas...")
            print(f"⚡ Processamento paralelo: Máximo 10 threads")
            
            # Verificar se precisa atualizar lista de pares
            if time.time() - self.pairs_last_update >= self.config['pairs_update_interval']:
                print("🔄 Atualizando lista de pares top 100...")
                self._create_top_pairs()
            
            # Processamento paralelo com ThreadPoolExecutor
            signals = []
            analyzed_pairs = []
            rejected_pairs = []
            max_workers = min(10, len(self.top_pairs))  # Máximo 10 threads
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submeter todas as análises para execução paralela
                future_to_symbol = {
                    executor.submit(self._analyze_symbol_safe, symbol): symbol 
                    for symbol in self.top_pairs
                }
                
                # Processar resultados conforme completam
                completed = 0
                for future in as_completed(future_to_symbol):
                    symbol = future_to_symbol[future]
                    completed += 1
                    
                    try:
                        signal = future.result()
                        analyzed_pairs.append(symbol)
                        
                        if signal:
                            # Sinal foi enviado para confirmação BTC
                            print(f"⏳ PRÉ-SINAL DETECTADO: {symbol} - {signal['type']} - Score: {signal['quality_score']:.1f} - Classe: {signal['signal_class']} (Aguardando confirmação BTC)")
                            # Não adicionar à lista de sinais - será processado pelo BTCSignalManager
                        else:
                            rejected_pairs.append(symbol)
                        
                        # Mostrar progresso a cada 25 pares
                        if completed % 25 == 0:
                            print(f"📈 Progresso: {completed}/{len(self.top_pairs)} pares analisados ({(completed/len(self.top_pairs)*100):.1f}%)")
                            
                    except Exception as e:
                        print(f"❌ Erro ao analisar {symbol}: {e}")
                        rejected_pairs.append(symbol)
                        continue
            
            # Estatísticas finais
            scan_duration = time.time() - scan_start_time
            cache_stats = self.cache_manager.get_performance_stats()
            
            print(f"\n{'='*80}")
            print(f"📊 RESULTADO DO ESCANEAMENTO")
            print(f"{'='*80}")
            print(f"⏱️ Tempo total: {scan_duration:.2f}s")
            print(f"📊 Pares analisados: {len(analyzed_pairs)}/{len(self.top_pairs)}")
            print(f"✨ Sinais encontrados: {len(signals)}")
            print(f"❌ Pares rejeitados: {len(rejected_pairs)}")
            print(f"⚡ Threads utilizadas: {max_workers}")
            print(f"🗄️ Cache Hit Rate: {cache_stats['cache_hit_rate']:.1f}%")
            print(f"💾 API Calls Saved: {cache_stats['api_calls_saved']}")
            print(f"🚀 Performance: {len(self.top_pairs)/scan_duration:.1f} pares/segundo")
            
            # Obter estatísticas do BTCSignalManager
            btc_stats = self.btc_signal_manager.get_confirmation_metrics()
            
            print(f"\n🎯 ESTATÍSTICAS BTC:")
            print(f"   ⏳ Sinais Pendentes: {btc_stats['pending_signals']}")
            print(f"   ✅ Taxa Confirmação: {btc_stats['confirmation_rate']}%")
            print(f"   ⏱️ Tempo Médio: {btc_stats['average_confirmation_time_minutes']:.1f}min")
            
            if not signals:
                print(f"\n📭 Nenhum pré-sinal detectado neste ciclo")
            
            print(f"{'='*80}\n")
            
            return signals
            
        except Exception as e:
            print(f"❌ Erro na varredura paralela: {e}")
            traceback.print_exc()
            return []
    
    def _analyze_symbol_safe(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Versão thread-safe do analyze_symbol para processamento paralelo"""
        try:
            return self.analyze_symbol(symbol)
        except Exception as e:
            print(f"❌ Erro thread-safe ao analisar {symbol}: {e}")
            return None
    
    def analyze_symbol(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Analisa um símbolo específico e retorna sinal se qualificado"""
        try:
            # 1. Análise de Tendência (4H)
            trend_df = self.get_klines(symbol, self.config['trend_timeframe'])
            if trend_df is None or len(trend_df) < 50:
                return None
            
            trend_analysis = self.analyze_trend_df(trend_df)
            if trend_analysis is None:
                return None
            
            # 2. Análise de Entrada (1H)
            entry_df = self.get_klines(symbol, self.config['entry_timeframe'])
            if entry_df is None or len(entry_df) < 50:
                return None
            
            entry_analysis = self.analyze_entry_df(entry_df)
            
            # 3. Determinar tipo de sinal
            signal_type = 'COMPRA' if trend_analysis['is_uptrend'] else 'VENDA'
            entry_price = float(entry_df['close'].iloc[-1])
            
            # 4. Sistema de Pontuação (100 pontos total - sem BTC)
            scores = self._calculate_signal_scores(
                trend_analysis, entry_analysis, signal_type, entry_df
            )
            
            quality_score = sum(scores.values())
            
            # 4.5. Sistema de ranking removido - todas as moedas são elegíveis
            # Mantendo apenas a pontuação base da análise técnica
            print(f"   📊 {symbol}: Pontuação base: {quality_score:.1f} pts (sem filtro de ranking)")
            
            # 5. Filtro de qualidade básico (AJUSTADO PARA EQUILIBRIO)
            if quality_score < 65.0:  # Threshold ajustado para 65 pontos
                return None
            
            # 6. Classificação (ajustada para maior rigor)
            if quality_score >= 90:
                signal_class = 'ELITE'
            elif quality_score >= 85:
                signal_class = 'PREMIUM+'
            elif quality_score >= 80:
                signal_class = 'PREMIUM'
            else:
                signal_class = 'STANDARD'
            
            # 7. Calcular alvo
            target_price = self.calculate_target_price(
                entry_price, signal_type, trend_analysis, entry_analysis, quality_score
            )
            
            # 8. Calcular projeção
            if signal_type == 'COMPRA':
                projection = ((target_price - entry_price) / entry_price) * 100
            else:
                projection = ((entry_price - target_price) / entry_price) * 100
            
            # 9. Calcular correlação e tendência BTC
            btc_analyzer = self.btc_signal_manager.btc_analyzer
            btc_correlation = btc_analyzer.calculate_symbol_btc_correlation(symbol)
            btc_analysis = btc_analyzer.get_current_btc_analysis()
            btc_trend = btc_analysis.get('trend', 'NEUTRAL')
            
            # 10. Capturar motivos detalhados de geração
            generation_reasons = self._capture_generation_reasons(
                symbol, signal_type, scores, trend_analysis, entry_analysis, quality_score
            )
            
            # 11. Montar sinal para confirmação BTC
            signal = {
                'symbol': symbol,
                'type': signal_type,
                'entry_price': entry_price,
                'target_price': target_price,
                'projection_percentage': projection,
                'quality_score': quality_score,
                'signal_class': signal_class,
                'rsi': entry_analysis.get('rsi', 50),
                'trend_score': scores['trend'],
                'entry_score': scores['entry'],
                'rsi_score': scores['rsi'],
                'pattern_score': scores['pattern'],
                'timestamp': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                'trend_timeframe': self.config['trend_timeframe'],
                'entry_timeframe': self.config['entry_timeframe'],
                'trend_analysis': trend_analysis,
                'entry_analysis': entry_analysis,
                'btc_correlation': btc_correlation,
                'btc_trend': btc_trend,
                'generation_reasons': generation_reasons  # Adicionar motivos de geração
            }
            
            # 12. Enviar para sistema de confirmação BTC
            signal_id = self.btc_signal_manager.add_pending_signal(signal)
            
            # Não retornar sinal diretamente - será confirmado pelo BTCSignalManager
            return None
            
        except Exception as e:
            print(f"❌ Erro ao analisar {symbol}: {e}")
            return None
    
    def _capture_generation_reasons(self, symbol: str, signal_type: str, scores: Dict[str, float],
                                   trend_analysis: Dict, entry_analysis: Dict, quality_score: float) -> Dict[str, Any]:
        """
        Captura motivos detalhados de por que um sinal foi gerado
        
        Args:
            symbol: Símbolo da moeda
            signal_type: Tipo do sinal (COMPRA/VENDA)
            scores: Pontuações técnicas
            trend_analysis: Análise de tendência
            entry_analysis: Análise de entrada
            quality_score: Pontuação final de qualidade
            
        Returns:
            Dicionário com motivos detalhados de geração
        """
        try:
            # Obter zona do RSI
            rsi_value = entry_analysis.get('rsi', 50)
            rsi_zone = self._get_rsi_zone(rsi_value)
            
            # Determinar condições que dispararam o sinal
            trigger_conditions = []
            
            # Condições de tendência
            if scores['trend'] >= 20:
                trend_strength = abs(trend_analysis.get('trend_strength', 0))
                trigger_conditions.append(f"Tendência {signal_type.lower()} forte ({trend_strength:.1f})")
            elif scores['trend'] >= 10:
                trigger_conditions.append(f"Tendência {signal_type.lower()} moderada")
            
            # Condições de entrada
            if scores['entry'] >= 15:
                volume_ratio = entry_analysis.get('volume_ratio', 1.0)
                trigger_conditions.append(f"Volume elevado ({volume_ratio:.1f}x média)")
            
            # Condições de RSI
            if scores['rsi'] >= 15:
                trigger_conditions.append(f"RSI {rsi_value:.0f} em zona {rsi_zone}")
            
            # Condições de padrões
            if scores['pattern'] >= 10:
                trigger_conditions.append("Padrões técnicos favoráveis")
            
            # MACD
            macd_signal = trend_analysis.get('macd_signal', 0)
            if macd_signal != 0:
                macd_direction = 'positivo' if macd_signal > 0 else 'negativo'
                trigger_conditions.append(f"MACD {macd_direction}")
            
            # Sistema de ranking removido - todas as moedas são elegíveis
            coin_name = symbol.replace('USDT', '').replace('BUSD', '').replace('USDC', '')
            
            return {
                'timestamp': datetime.now(),
                'symbol': symbol,
                'signal_type': signal_type,
                'technical_scores': {
                    'trend_score': scores['trend'],
                    'entry_score': scores['entry'],
                    'rsi_score': scores['rsi'],
                    'pattern_score': scores['pattern'],
                    'base_total': sum(scores.values())
                },
                'key_indicators': {
                    'rsi_value': rsi_value,
                    'rsi_zone': rsi_zone,
                    'trend_strength': abs(trend_analysis.get('trend_strength', 0)),
                    'volume_ratio': entry_analysis.get('volume_ratio', 1.0),
                    'macd_signal': macd_signal,
                    'price_change': entry_analysis.get('price_change', 0)
                },
                'trigger_conditions': trigger_conditions,
                'ranking_info': {
                    'coin': coin_name,
                    'position': None,
                    'tier': 'N/A',
                    'description': 'Sistema de ranking removido',
                    'bonus_applied': 0
                },
                'quality_breakdown': {
                    'base_score': sum(scores.values()),
                    'ranking_bonus': 0,
                    'final_score': quality_score,
                    'classification': self._get_signal_classification(quality_score),
                    'threshold_passed': quality_score >= 65.0
                },
                'market_context': {
                    'timeframe_trend': self.config['trend_timeframe'],
                    'timeframe_entry': self.config['entry_timeframe'],
                    'btc_trend': trend_analysis.get('btc_trend', 'NEUTRAL'),
                    'market_session': self._get_market_session()
                }
            }
            
        except Exception as e:
            print(f"❌ Erro ao capturar motivos de geração: {e}")
            return {
                'timestamp': datetime.now(),
                'error': str(e),
                'basic_info': {
                    'symbol': symbol,
                    'signal_type': signal_type,
                    'quality_score': quality_score
                }
            }
    
    def _get_rsi_zone(self, rsi_value: float) -> str:
        """Determina a zona do RSI"""
        if rsi_value <= 30:
            return 'sobrevenda'
        elif rsi_value >= 70:
            return 'sobrecompra'
        elif 30 < rsi_value <= 45:
            return 'baixa'
        elif 55 <= rsi_value < 70:
            return 'alta'
        else:
            return 'neutra'
    
    def _get_signal_classification(self, quality_score: float) -> str:
        """Retorna a classificação baseada na pontuação"""
        if quality_score >= 90:
            return 'ELITE'
        elif quality_score >= 85:
            return 'PREMIUM+'
        elif quality_score >= 80:
            return 'PREMIUM'
        else:
            return 'STANDARD'
    
    def _get_market_session(self) -> str:
        """Determina a sessão de mercado atual"""
        from datetime import datetime
        hour = datetime.now().hour
        
        if 0 <= hour < 8:
            return 'Asiática'
        elif 8 <= hour < 16:
            return 'Europeia'
        else:
            return 'Americana'
    
    def _calculate_signal_scores(self, trend_analysis: Dict, entry_analysis: Dict, 
                           signal_type: str, entry_df: pd.DataFrame) -> Dict[str, float]:
        """Calcula pontuação detalhada do sinal (100 pontos total - sem BTC)"""
        scores = {'trend': 0.0, 'entry': 0.0, 'rsi': 0.0, 'pattern': 0.0}  # Usar float
        
        # 1. TENDÊNCIA 4H (35 pontos)
        trend_strength = abs(trend_analysis.get('trend_strength', 0))
        scores['trend'] += min(trend_strength * 50.0, 15.0)  # Força da tendência (15 pts)
        
        # Alinhamento EMAs (10 pts)
        if signal_type == 'COMPRA' and trend_analysis['close'] >= trend_analysis['ema20'] * 0.98:
            scores['trend'] += 10.0
        elif signal_type == 'VENDA' and trend_analysis['close'] <= trend_analysis['ema20'] * 1.02:
            scores['trend'] += 10.0
        
        # MACD alinhado (10 pts)
        macd_signal = trend_analysis.get('macd_signal', 0)
        if (signal_type == 'COMPRA' and macd_signal > 0) or (signal_type == 'VENDA' and macd_signal < 0):
            scores['trend'] += 10.0
        
        # 2. CONFIRMAÇÃO 1H (25 pontos)
        # Momentum (15 pts)
        if signal_type == 'COMPRA':
            if entry_analysis.get('momentum_positive', False):
                scores['entry'] += 15.0
            elif entry_analysis.get('price_change', 0) > 0.002:
                scores['entry'] += 10.0
        else:
            if not entry_analysis.get('momentum_positive', True):
                scores['entry'] += 15.0
            elif entry_analysis.get('price_change', 0) < -0.002:
                scores['entry'] += 10.0
        
        # Volume (10 pts)
        volume_ratio = entry_analysis.get('volume_ratio', 1.0)
        if volume_ratio > 1.2:
            scores['entry'] += 10.0
        elif volume_ratio > 1.0:
            scores['entry'] += 5.0
        
        # 3. RSI (20 pontos)
        rsi_value = entry_analysis.get('rsi', 50)
        if 30 <= rsi_value <= 70:
            if (signal_type == 'COMPRA' and 30 <= rsi_value <= 50) or \
               (signal_type == 'VENDA' and 50 <= rsi_value <= 70):
                scores['rsi'] += 20.0
            else:
                scores['rsi'] += 15.0
        else:
            scores['rsi'] += 5.0  # Penalizar extremos
        
        # 4. PADRÕES TÉCNICOS (20 pontos)
        # Suporte/Resistência (10 pts)
        support_resistance = self.calculate_support_resistance_levels(
            entry_df, float(entry_df['close'].iloc[-1])
        )
        
        if signal_type == 'COMPRA':
            distance = support_resistance.get('support_distance', 0)
        else:
            distance = support_resistance.get('resistance_distance', 0)
        
        if 2 <= distance <= 5:
            scores['pattern'] += 10.0
        elif distance <= 8:
            scores['pattern'] += 5.0
        
        # Padrões de candlestick (10 pts)
        if len(entry_df) >= 3:
            candle_score = self._analyze_candlestick_patterns(entry_df, signal_type)
            scores['pattern'] += float(candle_score)  # Garantir que é float
        
        return scores
    
    def _analyze_candlestick_patterns(self, df: pd.DataFrame, signal_type: str) -> float:
        """Analisa padrões de candlestick"""
        try:
            if len(df) < 3:
                return 0.0
                
            last_candle = df.iloc[-1]
            prev_candle = df.iloc[-2]
            
            last_open = float(last_candle['open'])
            last_close = float(last_candle['close'])
            last_high = float(last_candle['high'])
            last_low = float(last_candle['low'])
            
            body_size = abs(last_close - last_open)
            candle_range = last_high - last_low
            
            if candle_range == 0:
                return 0.0
                
            score = 0.0
            
            if signal_type == 'COMPRA':
                # Martelo ou padrão de alta
                lower_shadow = min(last_close, last_open) - last_low
                if lower_shadow > body_size * 2:  # Martelo
                    score += 10.0
                elif body_size < candle_range * 0.3:  # Doji
                    score += 5.0
            else:  # VENDA
                # Estrela cadente ou padrão de baixa
                upper_shadow = last_high - max(last_close, last_open)
                if upper_shadow > body_size * 2:  # Estrela cadente
                    score += 10.0
                elif body_size < candle_range * 0.3:  # Doji
                    score += 5.0
            
            return score
            
        except Exception as e:
            print(f"❌ Erro na análise de candlestick: {e}")
            return 0.0

    def calculate_target_price(self, entry_price: float, signal_type: str, 
                             trend_data: Dict, entry_data: Dict, quality_score: float) -> float:
        """Calcula preço alvo com garantia mínima de 6%"""
        try:
            base_percentage = self.config['target_percentage_min']  # 6% mínimo
            
            # Bônus por volatilidade (0-8%)
            atr_ratio = entry_data.get('atr_ratio', 0.02)
            volatility_bonus = min(atr_ratio * 400, 8.0)  # Máximo 8%
            
            # Bônus por força da tendência (0-3%)
            trend_strength = abs(trend_data.get('trend_strength', 0))
            trend_bonus = min(trend_strength * 100, 3.0)  # Máximo 3%
            
            # Bônus por qualidade (0-1%)
            quality_bonus = min((quality_score - 80) / 20, 1.0)  # Máximo 1%
            
            # Calcular porcentagem total
            total_percentage = base_percentage + volatility_bonus + trend_bonus + quality_bonus
            total_percentage = min(total_percentage, 20.0)  # Máximo 20%
            
            # Calcular preço alvo
            if signal_type == 'COMPRA':
                target_price = entry_price * (1 + total_percentage / 100)
            else:
                target_price = entry_price * (1 - total_percentage / 100)
            
            # Validação final
            if signal_type == 'COMPRA' and target_price <= entry_price:
                target_price = entry_price * 1.06  # Forçar 6% mínimo
            elif signal_type == 'VENDA' and target_price >= entry_price:
                target_price = entry_price * 0.94  # Forçar 6% mínimo
            
            return target_price
            
        except Exception as e:
            print(f"❌ Erro no cálculo do alvo: {e}")
            # Fallback para 6% mínimo
            if signal_type == 'COMPRA':
                return entry_price * 1.06
            else:
                return entry_price * 0.94

    def calculate_support_resistance_levels(self, df: pd.DataFrame, current_price: float) -> Dict[str, float]:
        """Calcula níveis de suporte e resistência"""
        try:
            if df.empty or len(df) < 20:
                return {
                    'support': current_price * 0.98,
                    'resistance': current_price * 1.02,
                    'support_strength': 1.0,
                    'resistance_strength': 1.0,
                    'support_distance': 2.0,
                    'resistance_distance': 2.0
                }
                
            # Calcular níveis baseados em máximas e mínimas locais
            highs = df['high'].rolling(window=5, center=True).max()
            lows = df['low'].rolling(window=5, center=True).min()
            
            # Encontrar níveis de resistência (máximas locais)
            resistance_levels = []
            for i in range(2, len(df) - 2):
                if (df['high'].iloc[i] == highs.iloc[i] and 
                    df['high'].iloc[i] > df['high'].iloc[i-1] and 
                    df['high'].iloc[i] > df['high'].iloc[i+1]):
                    resistance_levels.append(df['high'].iloc[i])
            
            # Encontrar níveis de suporte (mínimas locais)
            support_levels = []
            for i in range(2, len(df) - 2):
                if (df['low'].iloc[i] == lows.iloc[i] and 
                    df['low'].iloc[i] < df['low'].iloc[i-1] and 
                    df['low'].iloc[i] < df['low'].iloc[i+1]):
                    support_levels.append(df['low'].iloc[i])
            
            # Encontrar o suporte e resistência mais próximos do preço atual
            if resistance_levels:
                resistance = min([r for r in resistance_levels if r > current_price], 
                               default=current_price * 1.02)
            else:
                resistance = current_price * 1.02
            
            if support_levels:
                support = max([s for s in support_levels if s < current_price], 
                            default=current_price * 0.98)
            else:
                support = current_price * 0.98
            
            # Calcular força dos níveis (quantas vezes foram testados)
            support_strength = len([s for s in support_levels if abs(s - support) / support < 0.01])
            resistance_strength = len([r for r in resistance_levels if abs(r - resistance) / resistance < 0.01])
            
            # Calcular distâncias em porcentagem
            support_distance = abs(current_price - support) / current_price * 100
            resistance_distance = abs(resistance - current_price) / current_price * 100
            
            return {
                'support': support,
                'resistance': resistance,
                'support_strength': max(float(support_strength), 1.0),
                'resistance_strength': max(float(resistance_strength), 1.0),
                'support_distance': support_distance,
                'resistance_distance': resistance_distance
            }
                
        except Exception as e:
            print(f"❌ Erro ao calcular suporte/resistência: {e}")
            return {
                'support': current_price * 0.98,
                'resistance': current_price * 1.02,
                'support_strength': 1.0,
                'resistance_strength': 1.0,
                'support_distance': 2.0,
                'resistance_distance': 2.0
            }

    def get_klines(self, symbol: str, interval: str, limit: int = 100) -> Optional[pd.DataFrame]:
        """Obtém dados de klines (candlesticks) com cache inteligente"""
        try:
            # Tentar obter do cache primeiro
            cached_data, is_cache_hit = self.cache_manager.get_klines(symbol, interval, limit)
            
            if is_cache_hit:
                return cached_data
            
            # Cache miss - buscar da API
            klines_data = self.binance.get_klines(symbol, interval, limit)
            if not klines_data:
                return None
                
            # Converter para DataFrame
            df = pd.DataFrame(klines_data)
            
            # Converter tipos de dados
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Garantir que retornamos apenas DataFrame ou None
            if all(col in df.columns for col in numeric_columns):
                # Usar to_frame() se for Series, senão usar copy() diretamente
                result = df[numeric_columns].copy()
                # Garantir que é sempre DataFrame
                if isinstance(result, pd.Series):
                    result = result.to_frame().T
                
                # Armazenar no cache para próximas consultas
                self.cache_manager.set_klines(symbol, interval, result, limit)
                
                return result
            else:
                return None
            
        except Exception as e:
            print(f"❌ Erro ao obter klines para {symbol}: {e}")
            return None
    
    def analyze_trend_df(self, df: pd.DataFrame) -> Optional[Dict]:
        """Analisa tendência do DataFrame"""
        try:
            # Calcular indicadores
            close_series = pd.Series(df['close'].values, dtype=float)
            ema20 = EMAIndicator(close=close_series, window=20).ema_indicator()
            ema50 = EMAIndicator(close=close_series, window=50).ema_indicator()
            macd_line = MACD(close=close_series).macd()
            macd_signal = MACD(close=close_series).macd_signal()
            
            current_price = df['close'].iloc[-1]
            current_ema20 = ema20.iloc[-1]
            current_ema50 = ema50.iloc[-1]
            
            # Detectar tendências
            is_uptrend = (
                current_price > current_ema20 * 0.995 and
                current_ema20 > current_ema50 * 1.005
            )
            
            is_downtrend = (
                current_price < current_ema20 * 1.005 and
                current_ema20 < current_ema50 * 0.995
            )
            
            # Calcular força da tendência
            trend_strength = abs(current_price - current_ema20) / current_price
            
            return {
                'is_uptrend': is_uptrend,
                'is_downtrend': is_downtrend,
                'trend_strength': trend_strength,
                'close': current_price,
                'ema20': current_ema20,
                'ema50': current_ema50,
                'macd_signal': macd_line.iloc[-1] - macd_signal.iloc[-1]
            }
            
        except Exception as e:
            print(f"❌ Erro na análise de tendência: {e}")
            return None
    
    def analyze_entry_df(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analisa condições de entrada no timeframe menor"""
        try:
            # Calcular indicadores
            close_series = pd.Series(df['close'].values, dtype=float)
            high_series = pd.Series(df['high'].values, dtype=float)
            low_series = pd.Series(df['low'].values, dtype=float)
            
            ema20 = EMAIndicator(close=close_series, window=20).ema_indicator()
            ema50 = EMAIndicator(close=close_series, window=50).ema_indicator()
            rsi = RSIIndicator(close=close_series, window=14).rsi()
            atr = AverageTrueRange(high=high_series, low=low_series, close=close_series, window=14).average_true_range()
            
            current_price = df['close'].iloc[-1]
            current_ema20 = ema20.iloc[-1]
            current_ema50 = ema50.iloc[-1]
            current_rsi = rsi.iloc[-1]
            current_atr = atr.iloc[-1]
            
            # Calcular ATR ratio para volatilidade
            atr_ratio = current_atr / current_price if current_price > 0 else 0.02
            
            # Condições de tendência
            is_uptrend = current_price > current_ema20 * 0.99 and current_ema20 > current_ema50 * 1.002
            is_downtrend = current_price < current_ema20 * 1.01 and current_ema20 < current_ema50 * 0.998
            
            # Momentum
            price_change = (current_price - df['close'].iloc[-3]) / df['close'].iloc[-3] if len(df) >= 3 else 0
            momentum_positive = price_change > 0
            
            # Volume ratio
            volume_ratio = df['volume'].tail(5).mean() / df['volume'].tail(20).mean() if len(df) >= 20 else 1.0
            
            return {
                'is_uptrend': is_uptrend,
                'is_downtrend': is_downtrend,
                'rsi': current_rsi,
                'price_change': price_change,
                'momentum_positive': momentum_positive,
                'volume_ratio': volume_ratio,
                'atr_ratio': atr_ratio
            }
            
        except Exception as e:
            print(f"❌ Erro na análise de entrada: {e}")
            return {
                'is_uptrend': False,
                'is_downtrend': False,
                'rsi': 50.0,
                'price_change': 0.0,
                'momentum_positive': False,
                'volume_ratio': 1.0
            }