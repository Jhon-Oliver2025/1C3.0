#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Monitoramento de Sinais
Acompanha sinais por até 15 dias calculando lucros baseados na alavancagem máxima
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from .leverage_detector import LeverageDetector
from .binance_client import BinanceClient
from .database import Database
import json
import traceback

@dataclass
class MonitoredSignal:
    """
    Classe que representa um sinal sendo monitorado com simulação de trading de $1.000 USD
    """
    id: str
    symbol: str
    signal_type: str  # 'COMPRA' ou 'VENDA'
    entry_price: float
    target_price: float
    created_at: str
    confirmed_at: str
    max_leverage: int
    required_percentage: float
    current_price: float = 0.0
    current_percentage: float = 0.0
    current_profit: float = 0.0
    max_profit_reached: float = 0.0
    status: str = 'MONITORING'  # MONITORING, COMPLETED, EXPIRED
    last_updated: str = ''
    days_monitored: int = 0
    price_history: List[Dict] = None
    
    # Campos de simulação financeira com $1.000 USD
    simulation_investment: float = 1000.0  # Investimento fixo de $1.000
    simulation_current_value: float = 1000.0  # Valor atual da posição
    simulation_pnl_usd: float = 0.0  # P&L em dólares
    simulation_pnl_percentage: float = 0.0  # P&L em percentual
    simulation_max_value_reached: float = 1000.0  # Maior valor atingido
    simulation_target_value: float = 4000.0  # Meta de $4.000 (300% de lucro)
    simulation_position_size: float = 0.0  # Tamanho da posição (quantidade de moedas)
    
    def __post_init__(self):
        if self.price_history is None:
            self.price_history = []
        if not self.last_updated:
            self.last_updated = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

class SignalMonitoringSystem:
    """
    Sistema principal de monitoramento de sinais
    Acompanha sinais por até 15 dias calculando lucros baseados na alavancagem
    """
    
    _instance = None
    
    @classmethod
    def get_instance(cls, database: Database, binance_client: BinanceClient = None):
        """Retorna instância singleton do sistema de monitoramento"""
        if cls._instance is None:
            if binance_client is None:
                # Criar cliente Binance se não fornecido
                from .binance_client import BinanceClient
                binance_client = BinanceClient()
            cls._instance = cls(binance_client, database)
        return cls._instance
    
    def __init__(self, binance_client: BinanceClient, database: Database):
        """
        Inicializa o sistema de monitoramento
        
        Args:
            binance_client: Cliente da Binance para obter preços
            database: Instância do banco de dados
        """
        self.binance = binance_client
        self.db = database
        self.leverage_detector = LeverageDetector(binance_client)
        
        # Armazenamento em memória dos sinais monitorados
        self.monitored_signals: Dict[str, MonitoredSignal] = {}
        self.expired_signals: Dict[str, MonitoredSignal] = {}
        
        # Controle de thread
        self.is_monitoring = False
        self.monitoring_thread: Optional[threading.Thread] = None
        
        # Configurações
        self.config = {
            'monitoring_days': 15,
            'update_interval': 300,  # 5 minutos
            'target_profit_percentage': 300.0,  # 300% de lucro
            'price_check_interval': 60  # 1 minuto para verificar preços
        }
        
        print("📊 SignalMonitoringSystem inicializado")
        
        # Carregar sinais existentes do banco
        self._load_existing_signals()
    
    def add_signal_to_monitoring(self, signal_id: str = None, symbol: str = None, 
                                signal_type: str = None, entry_price: float = None,
                                target_price: float = None, quality_score: float = None,
                                signal_class: str = None, confirmation_reasons: List[str] = None,
                                btc_correlation: float = None, btc_trend: str = None,
                                signal_data: Dict[str, Any] = None) -> bool:
        """
        Adiciona um novo sinal ao sistema de monitoramento
        
        Args:
            signal_id: ID único do sinal
            symbol: Símbolo da moeda
            signal_type: Tipo do sinal (COMPRA/VENDA)
            entry_price: Preço de entrada
            target_price: Preço alvo
            quality_score: Score de qualidade
            signal_class: Classe do sinal
            confirmation_reasons: Motivos da confirmação
            btc_correlation: Correlação com BTC
            btc_trend: Tendência do BTC
            signal_data: Dados completos do sinal (alternativa aos parâmetros individuais)
            
        Returns:
            bool: True se adicionado com sucesso
        """
        try:
            # Se signal_data foi fornecido, usar seus valores
            if signal_data:
                symbol = signal_data['symbol']
                signal_id = signal_data.get('id', signal_data.get('confirmation_id', ''))
                signal_type = signal_data['type']
                entry_price = float(signal_data['entry_price'])
                target_price = float(signal_data.get('target_price', 0))
                quality_score = signal_data.get('quality_score', 0)
                signal_class = signal_data.get('signal_class', '')
                confirmation_reasons = signal_data.get('confirmation_reasons', [])
                btc_correlation = signal_data.get('btc_correlation', 0)
                btc_trend = signal_data.get('btc_trend', 'NEUTRAL')
            
            # Verificar se já está sendo monitorado
            if signal_id in self.monitored_signals:
                print(f"⚠️ Sinal {signal_id} já está sendo monitorado")
                return False
            
            # Obter informações de alavancagem
            leverage_info = self.leverage_detector.get_leverage_info(symbol)
            
            # Criar objeto de sinal monitorado
            monitored_signal = MonitoredSignal(
                id=signal_id,
                symbol=symbol,
                signal_type=signal_type,
                entry_price=entry_price,
                target_price=target_price,
                created_at=datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                confirmed_at=datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                max_leverage=leverage_info['max_leverage'],
                required_percentage=leverage_info['required_percentage']
            )
            
            # Obter preço atual
            current_price = self._get_current_price(symbol)
            if current_price:
                monitored_signal.current_price = current_price
                self._update_signal_metrics(monitored_signal)
            
            # Adicionar ao monitoramento
            self.monitored_signals[signal_id] = monitored_signal
            
            # Salvar no banco
            self._save_signal_to_database(monitored_signal)
            
            print(f"✅ Sinal {symbol} adicionado ao monitoramento quantitativo")
            print(f"   Alavancagem: {leverage_info['max_leverage']}x")
            print(f"   Percentual necessário para 300%: {leverage_info['required_percentage']}%")
            print(f"   Período de avaliação: 15 dias")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao adicionar sinal ao monitoramento: {e}")
            traceback.print_exc()
            return False
    
    def start_monitoring(self) -> bool:
        """
        Inicia o monitoramento contínuo dos sinais
        
        Returns:
            bool: True se iniciado com sucesso
        """
        if self.is_monitoring:
            print("⚠️ Monitoramento já está ativo")
            return False
        
        print("🚀 Iniciando monitoramento de sinais...")
        self.is_monitoring = True
        
        # Iniciar thread de monitoramento
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()
        
        print("✅ Monitoramento de sinais iniciado!")
        return True
    
    def stop_monitoring(self):
        """
        Para o monitoramento de sinais
        """
        print("🛑 Parando monitoramento de sinais...")
        self.is_monitoring = False
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        
        print("✅ Monitoramento parado")
    
    def _monitoring_loop(self):
        """
        Loop principal de monitoramento
        """
        print("🔄 Loop de monitoramento iniciado")
        
        while self.is_monitoring:
            try:
                cycle_start = time.time()
                
                # Atualizar preços e métricas de todos os sinais
                self._update_all_signals()
                
                # Verificar sinais expirados
                self._check_expired_signals()
                
                # Verificar sinais que atingiram o objetivo
                self._check_completed_signals()
                
                # Salvar estado atual
                self._save_monitoring_state()
                
                # Aguardar próximo ciclo
                cycle_duration = time.time() - cycle_start
                sleep_time = max(0, self.config['update_interval'] - cycle_duration)
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
            except Exception as e:
                print(f"❌ Erro no loop de monitoramento: {e}")
                traceback.print_exc()
                time.sleep(60)  # Aguardar 1 minuto antes de tentar novamente
    
    def _update_all_signals(self):
        """
        Atualiza preços e métricas de todos os sinais monitorados
        """
        if not self.monitored_signals:
            return
        
        print(f"🔄 Atualizando {len(self.monitored_signals)} sinais monitorados...")
        
        for signal_id, signal in self.monitored_signals.items():
            try:
                # Obter preço atual
                current_price = self._get_current_price(signal.symbol)
                if current_price:
                    signal.current_price = current_price
                    self._update_signal_metrics(signal)
                    
                    # Adicionar ao histórico de preços
                    self._add_price_to_history(signal, current_price)
                    
                    # Atualizar timestamp
                    signal.last_updated = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                    
            except Exception as e:
                print(f"❌ Erro ao atualizar sinal {signal.symbol}: {e}")
    
    def _update_signal_metrics(self, signal: MonitoredSignal):
        """
        Atualiza as métricas de um sinal específico incluindo simulação financeira de $1.000 USD
        
        Args:
            signal: Sinal a ser atualizado
        """
        try:
            entry_price = signal.entry_price
            current_price = signal.current_price
            
            # Calcular percentual de movimento
            if signal.signal_type == 'COMPRA':
                percentage_change = ((current_price - entry_price) / entry_price) * 100
            else:  # VENDA
                percentage_change = ((entry_price - current_price) / entry_price) * 100
            
            signal.current_percentage = round(percentage_change, 2)
            
            # Calcular lucro com alavancagem
            leveraged_profit = percentage_change * signal.max_leverage
            signal.current_profit = round(leveraged_profit, 2)
            
            # Atualizar máximo lucro atingido
            if signal.current_profit > signal.max_profit_reached:
                signal.max_profit_reached = signal.current_profit
            
            # === SIMULAÇÃO FINANCEIRA COM $1.000 USD ===
            
            # Calcular tamanho da posição (quantidade de moedas com $1.000)
            if signal.simulation_position_size == 0.0:
                # Primeira vez - calcular posição inicial
                signal.simulation_position_size = signal.simulation_investment / entry_price
            
            # Calcular valor atual da posição
            signal.simulation_current_value = signal.simulation_position_size * current_price
            
            # Calcular P&L em dólares
            signal.simulation_pnl_usd = signal.simulation_current_value - signal.simulation_investment
            
            # Calcular P&L em percentual
            signal.simulation_pnl_percentage = (signal.simulation_pnl_usd / signal.simulation_investment) * 100
            
            # Atualizar maior valor atingido
            if signal.simulation_current_value > signal.simulation_max_value_reached:
                signal.simulation_max_value_reached = signal.simulation_current_value
            
            # Calcular dias monitorados
            if signal.confirmed_at:
                confirmed_date = datetime.strptime(signal.confirmed_at, '%d/%m/%Y %H:%M:%S')
                days_diff = (datetime.now() - confirmed_date).days
                signal.days_monitored = days_diff
            
        except Exception as e:
            print(f"❌ Erro ao calcular métricas para {signal.symbol}: {e}")
    
    def _get_current_price(self, symbol: str) -> Optional[float]:
        """
        Obtém o preço atual de um símbolo
        
        Args:
            symbol: Símbolo da moeda
            
        Returns:
            Optional[float]: Preço atual ou None se erro
        """
        try:
            ticker = self.binance.client.get_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except Exception as e:
            print(f"⚠️ Erro ao obter preço de {symbol}: {e}")
            return None
    
    def _add_price_to_history(self, signal: MonitoredSignal, price: float):
        """
        Adiciona um preço ao histórico do sinal
        
        Args:
            signal: Sinal monitorado
            price: Preço atual
        """
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        
        price_entry = {
            'timestamp': timestamp,
            'price': price,
            'percentage': signal.current_percentage,
            'profit': signal.current_profit
        }
        
        signal.price_history.append(price_entry)
        
        # Manter apenas últimas 100 entradas para economizar memória
        if len(signal.price_history) > 100:
            signal.price_history = signal.price_history[-100:]
    
    def _check_expired_signals(self):
        """
        Verifica e move sinais expirados (15 dias) para lista de expirados
        """
        expired_ids = []
        
        for signal_id, signal in self.monitored_signals.items():
            if signal.days_monitored >= self.config['monitoring_days']:
                signal.status = 'EXPIRED'
                self.expired_signals[signal_id] = signal
                expired_ids.append(signal_id)
                
                print(f"⏰ Sinal {signal.symbol} expirado após {signal.days_monitored} dias")
                print(f"   Lucro máximo atingido: {signal.max_profit_reached:.2f}%")
        
        # Remover da lista de monitoramento
        for signal_id in expired_ids:
            del self.monitored_signals[signal_id]
    
    def _check_completed_signals(self):
        """
        Verifica sinais que atingiram o objetivo de $4.000 (300% de lucro na simulação)
        """
        completed_ids = []
        
        for signal_id, signal in self.monitored_signals.items():
            # Verificar se atingiu $4.000 na simulação OU 300% de alavancagem (backup)
            simulation_target_reached = signal.simulation_current_value >= signal.simulation_target_value
            leverage_target_reached = signal.current_profit >= self.config['target_profit_percentage']
            
            if simulation_target_reached or leverage_target_reached:
                signal.status = 'COMPLETED'
                completed_ids.append(signal_id)
                
                print(f"🎯 Sinal {signal.symbol} atingiu objetivo!")
                print(f"   💰 Valor da simulação: ${signal.simulation_current_value:.2f}")
                print(f"   📈 P&L: ${signal.simulation_pnl_usd:.2f} ({signal.simulation_pnl_percentage:.2f}%)")
                print(f"   ⚡ Lucro alavancado: {signal.current_profit:.2f}%")
                print(f"   📅 Dias para atingir: {signal.days_monitored}")
        
        # Mover para expirados (sinais completados também vão para histórico)
        for signal_id in completed_ids:
            self.expired_signals[signal_id] = self.monitored_signals[signal_id]
            del self.monitored_signals[signal_id]
    
    def _save_signal_to_database(self, signal: MonitoredSignal):
        """
        Salva um sinal no banco de dados
        
        Args:
            signal: Sinal a ser salvo
        """
        try:
            # Converter para dicionário
            signal_dict = asdict(signal)
            signal_dict['price_history'] = json.dumps(signal.price_history)
            
            # Salvar no banco (implementar conforme estrutura do banco)
            # Por enquanto, apenas log
            print(f"💾 Salvando sinal {signal.symbol} no banco")
            
        except Exception as e:
            print(f"❌ Erro ao salvar sinal no banco: {e}")
    
    def _save_monitoring_state(self):
        """
        Salva o estado atual do monitoramento
        """
        try:
            # Salvar estado em arquivo temporário ou banco
            state = {
                'monitored_count': len(self.monitored_signals),
                'expired_count': len(self.expired_signals),
                'last_update': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            }
            
            # Log do estado
            if len(self.monitored_signals) > 0:
                print(f"📊 Estado: {state['monitored_count']} monitorados, {state['expired_count']} expirados")
            
        except Exception as e:
            print(f"❌ Erro ao salvar estado: {e}")
    
    def _load_existing_signals(self):
        """
        Carrega sinais existentes do banco de dados
        """
        try:
            # Implementar carregamento do banco
            print("📂 Carregando sinais existentes do banco...")
            # Por enquanto, apenas log
            print("✅ Sinais carregados")
            
        except Exception as e:
            print(f"❌ Erro ao carregar sinais: {e}")
    
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do monitoramento
        
        Returns:
            Dict: Estatísticas do sistema
        """
        try:
            # Calcular estatísticas dos sinais monitorados
            total_monitored = len(self.monitored_signals)
            total_expired = len(self.expired_signals)
            
            # Estatísticas de lucro
            profits = [s.current_profit for s in self.monitored_signals.values()]
            avg_profit = sum(profits) / len(profits) if profits else 0
            max_profit = max(profits) if profits else 0
            
            # Sinais que atingiram objetivo
            completed_signals = [s for s in self.expired_signals.values() if s.status == 'COMPLETED']
            success_rate = (len(completed_signals) / total_expired * 100) if total_expired > 0 else 0
            
            return {
                'total_monitored': total_monitored,
                'total_expired': total_expired,
                'total_completed': len(completed_signals),
                'success_rate': round(success_rate, 2),
                'average_profit': round(avg_profit, 2),
                'max_profit': round(max_profit, 2),
                'is_monitoring': self.is_monitoring,
                'last_update': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            }
            
        except Exception as e:
            print(f"❌ Erro ao calcular estatísticas: {e}")
            return {}
    
    def get_monitored_signals(self) -> List[Dict[str, Any]]:
        """
        Retorna lista de sinais sendo monitorados
        
        Returns:
            List: Lista de sinais monitorados
        """
        return [asdict(signal) for signal in self.monitored_signals.values()]
    
    def get_expired_signals(self) -> List[Dict[str, Any]]:
        """
        Retorna lista de sinais expirados
        
        Returns:
            List: Lista de sinais expirados
        """
        return [asdict(signal) for signal in self.expired_signals.values()]
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """
        Retorna estatísticas quantitativas completas do sistema de monitoramento
        
        Returns:
            Dict: Estatísticas detalhadas para avaliação quantitativa
        """
        try:
            # Sinais ativos
            active_signals = list(self.monitored_signals.values())
            expired_signals = list(self.expired_signals.values())
            
            # Sinais que atingiram 300% de lucro
            successful_signals = [s for s in expired_signals if s.status == 'COMPLETED']
            failed_signals = [s for s in expired_signals if s.status == 'EXPIRED']
            
            # Cálculos estatísticos
            total_evaluated = len(expired_signals)
            success_count = len(successful_signals)
            failure_count = len(failed_signals)
            
            success_rate = (success_count / total_evaluated * 100) if total_evaluated > 0 else 0
            
            # Lucros médios
            successful_profits = [s.max_profit_reached for s in successful_signals if s.max_profit_reached > 0]
            avg_successful_profit = sum(successful_profits) / len(successful_profits) if successful_profits else 0
            
            # Tempo médio para sucesso
            successful_days = [s.days_monitored for s in successful_signals]
            avg_days_to_success = sum(successful_days) / len(successful_days) if successful_days else 0
            
            # Análise por tipo de sinal
            buy_signals = [s for s in expired_signals if s.signal_type == 'COMPRA']
            sell_signals = [s for s in expired_signals if s.signal_type == 'VENDA']
            
            buy_success_rate = (len([s for s in buy_signals if s.status == 'COMPLETED']) / len(buy_signals) * 100) if buy_signals else 0
            sell_success_rate = (len([s for s in sell_signals if s.status == 'COMPLETED']) / len(sell_signals) * 100) if sell_signals else 0
            
            # Análise por alavancagem
            leverage_analysis = {}
            for signal in expired_signals:
                leverage = signal.max_leverage
                if leverage not in leverage_analysis:
                    leverage_analysis[leverage] = {'total': 0, 'successful': 0, 'avg_profit': 0, 'profits': []}
                
                leverage_analysis[leverage]['total'] += 1
                if signal.status == 'COMPLETED':
                    leverage_analysis[leverage]['successful'] += 1
                leverage_analysis[leverage]['profits'].append(signal.max_profit_reached)
            
            # Calcular médias por alavancagem
            for leverage, data in leverage_analysis.items():
                if data['profits']:
                    data['avg_profit'] = sum(data['profits']) / len(data['profits'])
                data['success_rate'] = (data['successful'] / data['total'] * 100) if data['total'] > 0 else 0
                del data['profits']  # Remover lista para economizar espaço
            
            return {
                # Estatísticas gerais
                'total_active_signals': len(active_signals),
                'total_evaluated_signals': total_evaluated,
                'successful_signals': success_count,
                'failed_signals': failure_count,
                'overall_success_rate': round(success_rate, 2),
                
                # Análise de performance
                'average_successful_profit': round(avg_successful_profit, 2),
                'average_days_to_success': round(avg_days_to_success, 1),
                'max_profit_achieved': max([s.max_profit_reached for s in expired_signals], default=0),
                
                # Análise por tipo
                'buy_signals_success_rate': round(buy_success_rate, 2),
                'sell_signals_success_rate': round(sell_success_rate, 2),
                'buy_signals_count': len(buy_signals),
                'sell_signals_count': len(sell_signals),
                
                # Análise por alavancagem
                'leverage_analysis': leverage_analysis,
                
                # Informações do sistema
                'monitoring_period_days': self.config['monitoring_days'],
                'target_profit_percentage': self.config['target_profit_percentage'],
                'system_status': 'active' if self.is_monitoring else 'inactive',
                'last_update': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            }
            
        except Exception as e:
            print(f"❌ Erro ao calcular estatísticas: {e}")
            return {
                'error': str(e),
                'total_active_signals': 0,
                'total_evaluated_signals': 0,
                'overall_success_rate': 0
            }
    
    def get_quantitative_report(self) -> Dict[str, Any]:
        """
        Gera relatório quantitativo completo para avaliação do sistema
        
        Returns:
            Dict: Relatório detalhado com métricas de avaliação
        """
        stats = self.get_system_statistics()
        
        # Interpretação dos resultados
        interpretation = {
            'system_effectiveness': 'unknown',
            'recommendation': 'insufficient_data',
            'confidence_level': 'low'
        }
        
        if stats['total_evaluated_signals'] >= 10:
            success_rate = stats['overall_success_rate']
            
            if success_rate >= 70:
                interpretation['system_effectiveness'] = 'excellent'
                interpretation['recommendation'] = 'continue_current_strategy'
                interpretation['confidence_level'] = 'high'
            elif success_rate >= 50:
                interpretation['system_effectiveness'] = 'good'
                interpretation['recommendation'] = 'minor_optimizations'
                interpretation['confidence_level'] = 'medium'
            elif success_rate >= 30:
                interpretation['system_effectiveness'] = 'moderate'
                interpretation['recommendation'] = 'significant_improvements_needed'
                interpretation['confidence_level'] = 'medium'
            else:
                interpretation['system_effectiveness'] = 'poor'
                interpretation['recommendation'] = 'major_strategy_revision'
                interpretation['confidence_level'] = 'high'
        
        return {
            'statistics': stats,
            'interpretation': interpretation,
            'generated_at': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'evaluation_criteria': {
                'target_profit': '300%',
                'monitoring_period': '15 days',
                'success_threshold': 'Signal reaches 300% profit within 15 days'
            }
        }