# Imports necessários
from typing import Dict, Optional, List, Any, TypedDict
from datetime import datetime, timedelta
import time
import threading
import uuid
from .database import Database
from .binance_client import BinanceClient
from .btc_correlation_analyzer import BTCCorrelationAnalyzer
from .telegram_notifier import TelegramNotifier
from config import server
import traceback

class SignalState:
    """Estados possíveis de um sinal"""
    PENDING = "pending"           # Aguardando confirmação
    CONFIRMED = "confirmed"       # Confirmado e enviado para dashboard
    REJECTED = "rejected"         # Rejeitado por algum motivo
    EXPIRED = "expired"           # Expirou sem confirmação

class ConfirmationReason:
    """Motivos de confirmação ou rejeição"""
    # Confirmação
    BREAKOUT_CONFIRMED = "breakout_confirmed"
    VOLUME_CONFIRMED = "volume_confirmed"
    BTC_ALIGNED = "btc_aligned"
    MOMENTUM_SUSTAINED = "momentum_sustained"
    
    # Rejeição
    BTC_OPPOSITE = "btc_opposite"
    VOLUME_INSUFFICIENT = "volume_insufficient"
    REVERSAL_DETECTED = "reversal_detected"
    TIMEOUT_EXPIRED = "timeout_expired"
    SUPPORT_RESISTANCE_HOLD = "support_resistance_hold"

class PendingSignal(TypedDict):
    """Estrutura de um sinal pendente"""
    id: str
    symbol: str
    type: str  # COMPRA ou VENDA
    entry_price: float
    target_price: float
    projection_percentage: float
    quality_score: float
    signal_class: str
    created_at: datetime
    expires_at: datetime
    confirmation_attempts: int
    last_check: datetime
    btc_correlation: float
    btc_trend: str
    original_data: Dict[str, Any]

class BTCSignalManager:
    """Gerenciador central de sinais BTC e sistema de confirmação"""
    
    def __init__(self, db_instance: Database):
        """Inicializa o gerenciador de sinais BTC"""
        print("₿ Inicializando BTCSignalManager...")
        
        # Dependências principais
        self.db = db_instance
        self.binance = BinanceClient()
        self.btc_analyzer = BTCCorrelationAnalyzer(self.binance)
        
        # Configurações do sistema
        self.config = {
            'confirmation_timeout': 14400,  # 4 horas em segundos
            'check_interval': 300,          # 5 minutos
            'max_confirmation_attempts': 12, # Máximo 12 tentativas (1 hora)
            'min_breakout_percentage': 0.5,  # 0.5% mínimo para rompimento
            'min_volume_increase': 1.2,      # 20% aumento mínimo no volume
            'btc_alignment_threshold': 0.3   # Threshold para alinhamento BTC
        }
        
        # Estados dos sinais
        self.pending_signals: List[PendingSignal] = []
        self.confirmed_signals: List[Dict[str, Any]] = []
        self.rejected_signals: List[Dict[str, Any]] = []
        
        # Controle de sinais duplicados diários
        self.daily_confirmed_signals: set = set()  # (symbol, type) confirmados hoje
        self.last_reset_date = datetime.now().date()  # Data do último reset
        
        # Controle de thread
        self.is_monitoring: bool = False
        self.monitoring_thread: Optional[threading.Thread] = None
        
        # Configurar notificações (opcional)
        self.notifier = self._setup_telegram_notifier()
        
        print("✅ BTCSignalManager inicializado com sucesso!")
        
        # Limpar sinais duplicados na inicialização
        self._cleanup_duplicate_signals()
    
    def _cleanup_duplicate_signals(self) -> None:
        """Remove sinais duplicados da lista de pendentes"""
        try:
            if not self.pending_signals:
                return
            
            original_count = len(self.pending_signals)
            seen_signals = set()
            unique_signals = []
            
            for signal in self.pending_signals:
                signal_key = (signal['symbol'], signal['type'])
                if signal_key not in seen_signals:
                    seen_signals.add(signal_key)
                    unique_signals.append(signal)
                else:
                    print(f"🗑️ Removendo sinal duplicado: {signal['symbol']} ({signal['type']}) - ID: {signal['id'][:8]}")
            
            self.pending_signals = unique_signals
            removed_count = original_count - len(unique_signals)
            
            if removed_count > 0:
                print(f"🧹 Limpeza concluída: {removed_count} sinais duplicados removidos ({original_count} → {len(unique_signals)})")
            else:
                print("✅ Nenhum sinal duplicado encontrado")
                
        except Exception as e:
            print(f"❌ Erro na limpeza de sinais duplicados: {e}")
            traceback.print_exc()
    
    def _setup_telegram_notifier(self) -> Optional[TelegramNotifier]:
        """Configura notificações do Telegram (opcional)"""
        try:
            telegram_token = server.config.get('TELEGRAM_TOKEN')
            telegram_chat_id = server.config.get('TELEGRAM_CHAT_ID')
            
            if telegram_token and telegram_chat_id:
                notifier = TelegramNotifier(telegram_token, telegram_chat_id)
                if notifier.test_connection():
                    return notifier
            return None
        except Exception as e:
            print(f"⚠️ Erro ao configurar Telegram no BTCSignalManager: {e}")
            return None
    
    def start_monitoring(self) -> bool:
        """Inicia o monitoramento de confirmações"""
        if self.is_monitoring:
            print("⚠️ Monitoramento de confirmações já está ativo")
            return False
        
        print("🚀 Iniciando monitoramento de confirmações BTC...")
        self.is_monitoring = True
        
        # Iniciar thread de monitoramento
        self.monitoring_thread = threading.Thread(
            target=self._confirmation_loop,
            daemon=True
        )
        self.monitoring_thread.start()
        
        print("✅ Monitoramento de confirmações iniciado!")
        return True
    
    def reset_daily_confirmed_signals(self) -> None:
        """Reseta o controle de sinais confirmados diários (chamado no restart às 21:00)"""
        try:
            previous_count = len(self.daily_confirmed_signals)
            previous_date = self.last_reset_date
            
            # Limpar lista de sinais confirmados hoje
            self.daily_confirmed_signals.clear()
            
            # Atualizar data do último reset
            self.last_reset_date = datetime.now().date()
            
            print("\n" + "="*60)
            print("🔄 RESET DO CONTROLE DE SINAIS CONFIRMADOS DIÁRIOS")
            print("="*60)
            print(f"📅 Data anterior: {previous_date.strftime('%d/%m/%Y')}")
            print(f"📅 Nova data: {self.last_reset_date.strftime('%d/%m/%Y')}")
            print(f"🧹 Sinais únicos confirmados limpos: {previous_count}")
            print(f"✅ Sistema pronto para detectar novos sinais únicos")
            print("="*60)
            
        except Exception as e:
            print(f"❌ Erro ao resetar controle de sinais diários: {e}")
            traceback.print_exc()
    
    def check_post_restart_signals(self) -> None:
        """Verifica quais sinais ainda estão ativos após o restart e permite nova geração"""
        try:
            print("\n🔍 VERIFICANDO SINAIS AINDA ATIVOS PÓS-RESTART...")
            
            # Aqui podemos implementar lógica para verificar se sinais antigos ainda são válidos
            # Por exemplo, verificar se o preço ainda está em uma condição favorável
            # Se sim, o sinal pode ser gerado novamente
            
            print("✅ Verificação de sinais pós-restart concluída")
            print("🎯 Sinais ainda válidos poderão ser gerados novamente")
            
        except Exception as e:
            print(f"❌ Erro na verificação pós-restart: {e}")
            traceback.print_exc()
    
    def get_daily_confirmed_count(self) -> int:
        """Retorna o número de sinais únicos confirmados hoje"""
        return len(self.daily_confirmed_signals)
    
    def get_daily_confirmed_list(self) -> List[tuple]:
        """Retorna a lista de sinais confirmados hoje"""
        return list(self.daily_confirmed_signals)
    
    def stop_monitoring(self) -> None:
        """Para o monitoramento de confirmações"""
        print("🛑 Parando monitoramento de confirmações...")
        self.is_monitoring = False
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        
        print("✅ Monitoramento de confirmações parado")
    
    def add_pending_signal(self, signal_data: Dict[str, Any]) -> str:
        """Adiciona um sinal para aguardar confirmação"""
        try:
            symbol = signal_data['symbol']
            signal_type = signal_data['type']
            
            # Verificar se já foi confirmado hoje (regra de não duplicação)
            signal_key = (symbol, signal_type)
            if signal_key in self.daily_confirmed_signals:
                print(f"🚫 Sinal {symbol} ({signal_type}) já confirmado hoje - ignorando duplicata")
                print(f"   📅 Sinais confirmados hoje: {len(self.daily_confirmed_signals)}")
                return ""
            
            # Verificar se já existe um sinal pendente para o mesmo símbolo e tipo
            existing_signal = next(
                (s for s in self.pending_signals 
                 if s['symbol'] == symbol and s['type'] == signal_type), 
                None
            )
            
            if existing_signal:
                print(f"⚠️ Sinal {symbol} ({signal_type}) já existe pendente (ID: {existing_signal['id'][:8]}) - ignorando duplicata")
                return existing_signal['id']
            
            # Gerar ID único para o sinal
            signal_id = str(uuid.uuid4())
            
            # Criar sinal pendente
            pending_signal: PendingSignal = {
                'id': signal_id,
                'symbol': symbol,
                'type': signal_type,
                'entry_price': signal_data['entry_price'],
                'target_price': signal_data['target_price'],
                'projection_percentage': signal_data['projection_percentage'],
                'quality_score': signal_data['quality_score'],
                'signal_class': signal_data['signal_class'],
                'created_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(seconds=self.config['confirmation_timeout']),
                'confirmation_attempts': 0,
                'last_check': datetime.now(),
                'btc_correlation': signal_data.get('btc_correlation', 0),
                'btc_trend': signal_data.get('btc_trend', 'NEUTRAL'),
                'original_data': signal_data
            }
            
            # Adicionar à lista de pendentes
            self.pending_signals.append(pending_signal)
            
            print(f"⏳ Sinal {symbol} ({signal_type}) adicionado para confirmação (ID: {signal_id[:8]})")
            
            # Salvar no banco de dados
            self._save_pending_signal_to_db(pending_signal)
            
            return signal_id
            
        except Exception as e:
            print(f"❌ Erro ao adicionar sinal pendente: {e}")
            traceback.print_exc()
            return ""
    
    def _confirmation_loop(self) -> None:
        """Loop principal de verificação de confirmações"""
        print("\n" + "="*60)
        print("🔄 INICIANDO MONITORAMENTO DE CONFIRMAÇÕES BTC")
        print("="*60)
        
        while self.is_monitoring:
            try:
                cycle_start = time.time()
                current_time = datetime.now()
                
                if self.pending_signals:
                    print(f"\n⏰ {current_time.strftime('%d/%m/%Y %H:%M:%S')}")
                    print(f"🔍 Verificando {len(self.pending_signals)} sinais pendentes...")
                    
                    # Verificar cada sinal pendente
                    signals_to_remove = []
                    
                    for signal in self.pending_signals:
                        try:
                            result = self._check_signal_confirmation(signal)
                            
                            if result['action'] == 'confirm':
                                self._confirm_signal(signal, result['reasons'])
                                signals_to_remove.append(signal)
                            elif result['action'] == 'reject':
                                self._reject_signal(signal, result['reasons'])
                                signals_to_remove.append(signal)
                            elif result['action'] == 'expire':
                                self._expire_signal(signal)
                                signals_to_remove.append(signal)
                            # Se action == 'wait', continua pendente
                            
                        except Exception as e:
                            print(f"❌ Erro ao verificar sinal {signal['symbol']}: {e}")
                            continue
                    
                    # Remover sinais processados
                    for signal in signals_to_remove:
                        if signal in self.pending_signals:
                            self.pending_signals.remove(signal)
                
                # Calcular tempo de espera
                cycle_duration = time.time() - cycle_start
                wait_time = max(0, self.config['check_interval'] - cycle_duration)
                
                # Aguardar próximo ciclo
                self._interruptible_sleep(wait_time)
                
            except Exception as e:
                print(f"❌ Erro no ciclo de confirmação: {e}")
                traceback.print_exc()
                self._interruptible_sleep(30)  # Aguardar 30s em caso de erro
    
    def _check_signal_confirmation(self, signal: PendingSignal) -> Dict[str, Any]:
        """Verifica se um sinal deve ser confirmado, rejeitado ou continuar pendente"""
        try:
            current_time = datetime.now()
            
            # Verificar se expirou
            if current_time > signal['expires_at']:
                return {
                    'action': 'expire',
                    'reasons': [ConfirmationReason.TIMEOUT_EXPIRED]
                }
            
            # Incrementar tentativas
            signal['confirmation_attempts'] += 1
            signal['last_check'] = current_time
            
            # Verificar se excedeu máximo de tentativas
            if signal['confirmation_attempts'] > self.config['max_confirmation_attempts']:
                return {
                    'action': 'expire',
                    'reasons': [ConfirmationReason.TIMEOUT_EXPIRED]
                }
            
            # Obter dados atuais do símbolo
            current_data = self._get_current_symbol_data(signal['symbol'])
            if not current_data:
                return {'action': 'wait', 'reasons': []}
            
            # Verificar confirmações
            confirmations = []
            rejections = []
            
            # 1. Verificar rompimento de preço
            breakout_result = self._check_price_breakout(signal, current_data)
            if breakout_result['confirmed']:
                confirmations.append(ConfirmationReason.BREAKOUT_CONFIRMED)
            elif breakout_result['rejected']:
                rejections.append(ConfirmationReason.REVERSAL_DETECTED)
            
            # 2. Verificar volume
            volume_result = self._check_volume_confirmation(signal, current_data)
            if volume_result['confirmed']:
                confirmations.append(ConfirmationReason.VOLUME_CONFIRMED)
            elif volume_result['rejected']:
                rejections.append(ConfirmationReason.VOLUME_INSUFFICIENT)
            
            # 3. Verificar alinhamento BTC
            btc_result = self._check_btc_alignment(signal)
            if btc_result['confirmed']:
                confirmations.append(ConfirmationReason.BTC_ALIGNED)
            elif btc_result['rejected']:
                rejections.append(ConfirmationReason.BTC_OPPOSITE)
            
            # 4. Verificar momentum sustentado
            momentum_result = self._check_momentum_sustainability(signal, current_data)
            if momentum_result['confirmed']:
                confirmations.append(ConfirmationReason.MOMENTUM_SUSTAINED)
            
            # Decidir ação baseada nas confirmações
            if len(rejections) >= 2:  # 2+ rejeições = rejeitar
                return {
                    'action': 'reject',
                    'reasons': rejections
                }
            elif len(confirmations) >= 3:  # 3+ confirmações = confirmar
                return {
                    'action': 'confirm',
                    'reasons': confirmations
                }
            else:  # Continuar aguardando
                return {
                    'action': 'wait',
                    'reasons': confirmations + rejections
                }
            
        except Exception as e:
            print(f"❌ Erro na verificação de confirmação: {e}")
            return {'action': 'wait', 'reasons': []}
    
    def _get_current_symbol_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Obtém dados atuais do símbolo"""
        try:
            # Obter dados de klines recentes (últimas 5 velas de 1h)
            klines_data = self.binance.get_klines(symbol, '1h', 5)
            if not klines_data:
                return None
            
            # Obter ticker 24h
            ticker_data = self.binance.get_24h_ticker_data([symbol])
            if not ticker_data or symbol not in ticker_data:
                return None
            
            return {
                'klines': klines_data,
                'ticker': ticker_data[symbol],
                'current_price': float(klines_data[-1]['close']),
                'volume_24h': float(ticker_data[symbol]['volume'])
            }
            
        except Exception as e:
            print(f"❌ Erro ao obter dados do símbolo {symbol}: {e}")
            return None
    
    def _check_price_breakout(self, signal: PendingSignal, current_data: Dict[str, Any]) -> Dict[str, bool]:
        """Verifica se houve rompimento de preço confirmado"""
        try:
            current_price = current_data['current_price']
            entry_price = signal['entry_price']
            signal_type = signal['type']
            
            min_breakout = self.config['min_breakout_percentage'] / 100
            
            if signal_type == 'COMPRA':
                # Para compra, verificar se rompeu para cima
                breakout_price = entry_price * (1 + min_breakout)
                reversal_price = entry_price * (1 - min_breakout * 2)  # 2x para reversão
                
                if current_price >= breakout_price:
                    return {'confirmed': True, 'rejected': False}
                elif current_price <= reversal_price:
                    return {'confirmed': False, 'rejected': True}
            
            else:  # VENDA
                # Para venda, verificar se rompeu para baixo
                breakout_price = entry_price * (1 - min_breakout)
                reversal_price = entry_price * (1 + min_breakout * 2)  # 2x para reversão
                
                if current_price <= breakout_price:
                    return {'confirmed': True, 'rejected': False}
                elif current_price >= reversal_price:
                    return {'confirmed': False, 'rejected': True}
            
            return {'confirmed': False, 'rejected': False}
            
        except Exception as e:
            print(f"❌ Erro na verificação de breakout: {e}")
            return {'confirmed': False, 'rejected': False}
    
    def _check_volume_confirmation(self, signal: PendingSignal, current_data: Dict[str, Any]) -> Dict[str, bool]:
        """Verifica se há confirmação de volume"""
        try:
            klines = current_data['klines']
            if len(klines) < 3:
                return {'confirmed': False, 'rejected': False}
            
            # Volume das últimas 2 velas vs média das 3 anteriores
            recent_volume = (float(klines[-1]['volume']) + float(klines[-2]['volume'])) / 2
            avg_volume = sum(float(k['volume']) for k in klines[-5:-2]) / 3
            
            volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
            
            if volume_ratio >= self.config['min_volume_increase']:
                return {'confirmed': True, 'rejected': False}
            elif volume_ratio < 0.8:  # Volume muito baixo
                return {'confirmed': False, 'rejected': True}
            
            return {'confirmed': False, 'rejected': False}
            
        except Exception as e:
            print(f"❌ Erro na verificação de volume: {e}")
            return {'confirmed': False, 'rejected': False}
    
    def _check_btc_alignment(self, signal: PendingSignal) -> Dict[str, bool]:
        """Verifica alinhamento com BTC"""
        try:
            btc_analysis = self.btc_analyzer.get_current_btc_analysis()
            signal_type = signal['type']
            
            # Verificar se BTC está alinhado com o sinal
            if signal_type == 'COMPRA':
                if btc_analysis['trend'] == 'BULLISH':
                    return {'confirmed': True, 'rejected': False}
                elif btc_analysis['trend'] == 'BEARISH' and btc_analysis['strength'] > 0.5:
                    return {'confirmed': False, 'rejected': True}
            
            else:  # VENDA
                if btc_analysis['trend'] == 'BEARISH':
                    return {'confirmed': True, 'rejected': False}
                elif btc_analysis['trend'] == 'BULLISH' and btc_analysis['strength'] > 0.5:
                    return {'confirmed': False, 'rejected': True}
            
            return {'confirmed': False, 'rejected': False}
            
        except Exception as e:
            print(f"❌ Erro na verificação de alinhamento BTC: {e}")
            return {'confirmed': False, 'rejected': False}
    
    def _check_momentum_sustainability(self, signal: PendingSignal, current_data: Dict[str, Any]) -> Dict[str, bool]:
        """Verifica se o momentum está se sustentando"""
        try:
            klines = current_data['klines']
            if len(klines) < 3:
                return {'confirmed': False, 'rejected': False}
            
            signal_type = signal['type']
            
            # Verificar últimas 3 velas
            last_3_closes = [float(k['close']) for k in klines[-3:]]
            
            if signal_type == 'COMPRA':
                # Para compra, verificar se pelo menos 2 das 3 últimas velas são de alta
                bullish_candles = sum(1 for i in range(1, len(last_3_closes)) 
                                    if last_3_closes[i] > last_3_closes[i-1])
                if bullish_candles >= 2:
                    return {'confirmed': True, 'rejected': False}
            
            else:  # VENDA
                # Para venda, verificar se pelo menos 2 das 3 últimas velas são de baixa
                bearish_candles = sum(1 for i in range(1, len(last_3_closes)) 
                                    if last_3_closes[i] < last_3_closes[i-1])
                if bearish_candles >= 2:
                    return {'confirmed': True, 'rejected': False}
            
            return {'confirmed': False, 'rejected': False}
            
        except Exception as e:
            print(f"❌ Erro na verificação de momentum: {e}")
            return {'confirmed': False, 'rejected': False}
    
    def _confirm_signal(self, signal: PendingSignal, reasons: List[str]) -> None:
        """Confirma um sinal e o envia para o dashboard"""
        try:
            print(f"✅ CONFIRMANDO SINAL: {signal['symbol']} - {signal['type']}")
            print(f"   🎯 Motivos: {', '.join(reasons)}")
            
            # Adicionar à lista de sinais confirmados hoje (controle de duplicação)
            signal_key = (signal['symbol'], signal['type'])
            self.daily_confirmed_signals.add(signal_key)
            print(f"   📅 Adicionado à lista de confirmados hoje: {signal_key}")
            print(f"   📊 Total de sinais únicos confirmados hoje: {len(self.daily_confirmed_signals)}")
            
            # Criar sinal confirmado
            confirmed_signal = signal['original_data'].copy()
            confirmed_signal.update({
                'confirmation_id': signal['id'],
                'confirmed_at': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                'confirmation_reasons': reasons,
                'confirmation_attempts': signal['confirmation_attempts']
            })
            
            # Adicionar à lista de confirmados
            self.confirmed_signals.append(confirmed_signal)
            
            # Salvar sinal confirmado no banco (usando o sistema existente)
            from .gerenciar_sinais import GerenciadorSinais
            gerenciador = GerenciadorSinais(self.db)
            gerenciador.save_signal(confirmed_signal)
            
            # Enviar notificação se configurado
            if self.notifier:
                try:
                    self.notifier.send_signal(
                        signal['symbol'],
                        signal['type'],
                        signal['entry_price'],
                        signal['quality_score'],
                        '1h',
                        signal['target_price']
                    )
                except Exception as e:
                    print(f"⚠️ Erro ao enviar notificação de confirmação: {e}")
            
            # Salvar no banco como confirmado
            self._save_confirmed_signal_to_db(signal, confirmed_signal, reasons)
            
            print(f"✅ Sinal {signal['symbol']} confirmado e enviado para dashboard!")
            
        except Exception as e:
            print(f"❌ Erro ao confirmar sinal: {e}")
            traceback.print_exc()
    
    def _reject_signal(self, signal: PendingSignal, reasons: List[str]) -> None:
        """Rejeita um sinal"""
        try:
            print(f"❌ REJEITANDO SINAL: {signal['symbol']} - {signal['type']}")
            print(f"   🚫 Motivos: {', '.join(reasons)}")
            
            # Criar sinal rejeitado
            rejected_signal = {
                'id': signal['id'],
                'symbol': signal['symbol'],
                'type': signal['type'],
                'entry_price': signal['entry_price'],
                'quality_score': signal['quality_score'],
                'signal_class': signal['signal_class'],
                'created_at': signal['created_at'],
                'rejected_at': datetime.now(),
                'rejection_reasons': reasons,
                'confirmation_attempts': signal['confirmation_attempts'],
                'original_data': signal['original_data']
            }
            
            # Adicionar à lista de rejeitados
            self.rejected_signals.append(rejected_signal)
            
            # Salvar no banco como rejeitado
            self._save_rejected_signal_to_db(rejected_signal)
            
        except Exception as e:
            print(f"❌ Erro ao rejeitar sinal: {e}")
            traceback.print_exc()
    
    def _expire_signal(self, signal: PendingSignal) -> None:
        """Expira um sinal por timeout"""
        try:
            print(f"⏰ EXPIRANDO SINAL: {signal['symbol']} - {signal['type']} (Timeout)")
            
            # Tratar como rejeição por timeout
            self._reject_signal(signal, [ConfirmationReason.TIMEOUT_EXPIRED])
            
        except Exception as e:
            print(f"❌ Erro ao expirar sinal: {e}")
            traceback.print_exc()
    
    def _interruptible_sleep(self, duration: float) -> None:
        """Sleep que pode ser interrompido"""
        end_time = time.time() + duration
        while time.time() < end_time and self.is_monitoring:
            time.sleep(0.1)
    
    def _save_pending_signal_to_db(self, signal: PendingSignal) -> None:
        """Salva sinal pendente no banco de dados"""
        try:
            # Implementar salvamento no banco se necessário
            # Por enquanto, apenas log
            pass
        except Exception as e:
            print(f"❌ Erro ao salvar sinal pendente no DB: {e}")
    
    def _save_confirmed_signal_to_db(self, original_signal: PendingSignal, 
                                   confirmed_signal: Dict[str, Any], reasons: List[str]) -> None:
        """Salva sinal confirmado no banco de dados"""
        try:
            # Implementar salvamento no banco se necessário
            # Por enquanto, apenas log
            pass
        except Exception as e:
            print(f"❌ Erro ao salvar sinal confirmado no DB: {e}")
    
    def _save_rejected_signal_to_db(self, rejected_signal: Dict[str, Any]) -> None:
        """Salva sinal rejeitado no banco de dados"""
        try:
            # Implementar salvamento no banco se necessário
            # Por enquanto, apenas log
            pass
        except Exception as e:
            print(f"❌ Erro ao salvar sinal rejeitado no DB: {e}")
    
    # Métodos para API
    def get_pending_signals(self) -> List[Dict[str, Any]]:
        """Retorna lista de sinais pendentes para a API"""
        return [{
            'id': signal['id'],
            'symbol': signal['symbol'],
            'type': signal['type'],
            'entry_price': signal['entry_price'],
            'target_price': signal['target_price'],
            'projection_percentage': signal['projection_percentage'],
            'quality_score': signal['quality_score'],
            'signal_class': signal['signal_class'],
            'created_at': signal['created_at'].strftime('%d/%m/%Y %H:%M:%S'),
            'expires_at': signal['expires_at'].strftime('%d/%m/%Y %H:%M:%S'),
            'confirmation_attempts': signal['confirmation_attempts'],
            'btc_correlation': signal['btc_correlation'],
            'btc_trend': signal['btc_trend']
        } for signal in self.pending_signals]
    
    def get_rejected_signals(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retorna lista de sinais rejeitados para a API"""
        # Retornar os mais recentes primeiro
        recent_rejected = sorted(self.rejected_signals, 
                               key=lambda x: x['rejected_at'], reverse=True)[:limit]
        
        return [{
            'id': signal['id'],
            'symbol': signal['symbol'],
            'type': signal['type'],
            'entry_price': signal['entry_price'],
            'quality_score': signal['quality_score'],
            'signal_class': signal['signal_class'],
            'created_at': signal['created_at'].strftime('%d/%m/%Y %H:%M:%S'),
            'rejected_at': signal['rejected_at'].strftime('%d/%m/%Y %H:%M:%S'),
            'rejection_reasons': signal['rejection_reasons'],
            'confirmation_attempts': signal['confirmation_attempts']
        } for signal in recent_rejected]
    
    def get_confirmed_signals(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retorna lista de sinais confirmados para a API"""
        # Retornar os mais recentes primeiro
        recent_confirmed = sorted(self.confirmed_signals, 
                                key=lambda x: x.get('confirmed_at', ''), reverse=True)[:limit]
        
        return [{
            'id': signal.get('confirmation_id', signal.get('id', '')),
            'symbol': signal['symbol'],
            'type': signal['type'],
            'entry_price': signal['entry_price'],
            'target_price': signal['target_price'],
            'projection_percentage': signal['projection_percentage'],
            'quality_score': signal['quality_score'],
            'signal_class': signal['signal_class'],
            'created_at': signal.get('timestamp', signal.get('created_at', '')),
            'confirmed_at': signal.get('confirmed_at', ''),
            'confirmation_reasons': signal.get('confirmation_reasons', []),
            'confirmation_attempts': signal.get('confirmation_attempts', 0),
            'btc_correlation': signal.get('btc_correlation', 0),
            'btc_trend': signal.get('btc_trend', 'NEUTRAL')
        } for signal in recent_confirmed]
    
    def get_confirmation_metrics(self) -> Dict[str, Any]:
        """Retorna métricas de confirmação para a API"""
        try:
            total_signals = len(self.confirmed_signals) + len(self.rejected_signals)
            confirmed_count = len(self.confirmed_signals)
            rejected_count = len(self.rejected_signals)
            pending_count = len(self.pending_signals)
            
            confirmation_rate = (confirmed_count / total_signals * 100) if total_signals > 0 else 0
            
            # Calcular tempo médio de confirmação
            avg_confirmation_time = 0
            if self.confirmed_signals:
                total_attempts = sum(signal.get('confirmation_attempts', 1) for signal in self.confirmed_signals)
                avg_confirmation_time = (total_attempts * self.config['check_interval']) / len(self.confirmed_signals) / 60  # em minutos
            
            return {
                'total_signals_processed': int(total_signals),
                'confirmed_signals': int(confirmed_count),
                'rejected_signals': int(rejected_count),
                'pending_signals': int(pending_count),
                'confirmation_rate': float(round(confirmation_rate, 1)),
                'average_confirmation_time_minutes': float(round(avg_confirmation_time, 1)),
                'system_status': 'active' if bool(self.is_monitoring) else 'inactive'
            }
            
        except Exception as e:
            print(f"❌ Erro ao calcular métricas: {e}")
            return {
                'total_signals_processed': 0,
                'confirmed_signals': 0,
                'rejected_signals': 0,
                'pending_signals': 0,
                'confirmation_rate': 0,
                'average_confirmation_time_minutes': 0,
                'system_status': 'error'
            }
    
    def manual_confirm_signal(self, signal_id: str) -> bool:
        """Confirma um sinal manualmente (para interface admin)"""
        try:
            # Encontrar sinal pendente
            signal = next((s for s in self.pending_signals if s['id'] == signal_id), None)
            if not signal:
                return False
            
            # Confirmar sinal
            self._confirm_signal(signal, ['MANUAL_CONFIRMATION'])
            
            # Remover da lista de pendentes
            self.pending_signals.remove(signal)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro na confirmação manual: {e}")
            return False
    
    def manual_reject_signal(self, signal_id: str, reason: str = 'MANUAL_REJECTION') -> bool:
        """Rejeita um sinal manualmente (para interface admin)"""
        try:
            # Encontrar sinal pendente
            signal = next((s for s in self.pending_signals if s['id'] == signal_id), None)
            if not signal:
                return False
            
            # Rejeitar sinal
            self._reject_signal(signal, [reason])
            
            # Remover da lista de pendentes
            self.pending_signals.remove(signal)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro na rejeição manual: {e}")
            return False