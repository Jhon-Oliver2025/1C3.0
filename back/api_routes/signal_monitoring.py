#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Routes para Sistema de Monitoramento de Sinais
Endpoints para gerenciar e visualizar sinais monitorados
"""

from flask import Blueprint, jsonify, request
from middleware.auth_middleware import jwt_required, get_current_user
from core.signal_monitoring_system import SignalMonitoringSystem
from core.binance_client import BinanceClient
from core.database import Database
import traceback
from datetime import datetime

# Criar blueprint
signal_monitoring_bp = Blueprint('signal_monitoring', __name__, url_prefix='/api/signal-monitoring')

# Instâncias globais (serão inicializadas no app principal)
monitoring_system = None

def init_signal_monitoring_routes(db_instance: Database, binance_client: BinanceClient):
    """
    Inicializa as rotas de monitoramento com as instâncias necessárias
    
    Args:
        db_instance: Instância do banco de dados
        binance_client: Cliente da Binance
    """
    global monitoring_system
    
    try:
        monitoring_system = SignalMonitoringSystem(binance_client, db_instance)
        print("✅ Rotas de Monitoramento de Sinais inicializadas!")
    except Exception as e:
        print(f"❌ Erro ao inicializar rotas de monitoramento: {e}")
        traceback.print_exc()

@signal_monitoring_bp.route('/status', methods=['GET'])
@jwt_required
def get_monitoring_status():
    """
    Retorna o status do sistema de monitoramento
    """
    try:
        # Verificar se usuário é admin
        user_data = get_current_user()
        if not user_data or not user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Apenas administradores podem acessar esta funcionalidade.'
            }), 403
        
        if not monitoring_system:
            return jsonify({
                'success': False,
                'message': 'Sistema de monitoramento não inicializado'
            }), 500
        
        # Obter estatísticas do sistema
        stats = monitoring_system.get_monitoring_stats()
        
        return jsonify({
            'success': True,
            'data': {
                'system_status': 'active' if monitoring_system.is_monitoring else 'inactive',
                'stats': stats,
                'config': {
                    'monitoring_days': monitoring_system.config['monitoring_days'],
                    'target_profit': monitoring_system.config['target_profit_percentage'],
                    'update_interval': monitoring_system.config['update_interval']
                }
            }
        })
        
    except Exception as e:
        print(f"❌ Erro ao obter status do monitoramento: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@signal_monitoring_bp.route('/signals/active', methods=['GET'])
@jwt_required
def get_active_signals():
    """
    Retorna lista de sinais sendo monitorados ativamente
    """
    try:
        # Verificar se usuário é admin
        user_data = get_current_user()
        if not user_data or not user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Apenas administradores podem acessar esta funcionalidade.'
            }), 403
        
        if not monitoring_system:
            return jsonify({
                'success': False,
                'message': 'Sistema de monitoramento não inicializado'
            }), 500
        
        # Obter sinais monitorados
        monitored_signals = monitoring_system.get_monitored_signals()
        
        # Ordenar por lucro atual (maior primeiro)
        monitored_signals.sort(key=lambda x: x.get('current_profit', 0), reverse=True)
        
        return jsonify({
            'success': True,
            'data': {
                'signals': monitored_signals,
                'count': len(monitored_signals),
                'last_updated': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            }
        })
        
    except Exception as e:
        print(f"❌ Erro ao obter sinais ativos: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@signal_monitoring_bp.route('/signals/expired', methods=['GET'])
@jwt_required
def get_expired_signals():
    """
    Retorna lista de sinais expirados (após 15 dias)
    """
    try:
        # Verificar se usuário é admin
        user_data = get_current_user()
        if not user_data or not user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Apenas administradores podem acessar esta funcionalidade.'
            }), 403
        
        if not monitoring_system:
            return jsonify({
                'success': False,
                'message': 'Sistema de monitoramento não inicializado'
            }), 500
        
        # Obter sinais expirados
        expired_signals = monitoring_system.get_expired_signals()
        
        # Ordenar por lucro máximo atingido (maior primeiro)
        expired_signals.sort(key=lambda x: x.get('max_profit_reached', 0), reverse=True)
        
        # Separar por status
        completed_signals = [s for s in expired_signals if s.get('status') == 'COMPLETED']
        expired_only = [s for s in expired_signals if s.get('status') == 'EXPIRED']
        
        return jsonify({
            'success': True,
            'data': {
                'completed_signals': completed_signals,
                'expired_signals': expired_only,
                'total_completed': len(completed_signals),
                'total_expired': len(expired_only),
                'success_rate': (len(completed_signals) / len(expired_signals) * 100) if expired_signals else 0,
                'last_updated': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            }
        })
        
    except Exception as e:
        print(f"❌ Erro ao obter sinais expirados: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@signal_monitoring_bp.route('/signals/add', methods=['POST'])
@jwt_required
def add_signal_to_monitoring():
    """
    Adiciona um sinal confirmado ao sistema de monitoramento
    """
    try:
        # Verificar se usuário é admin
        user_data = get_current_user()
        if not user_data or not user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Apenas administradores podem acessar esta funcionalidade.'
            }), 403
        
        if not monitoring_system:
            return jsonify({
                'success': False,
                'message': 'Sistema de monitoramento não inicializado'
            }), 500
        
        # Obter dados do sinal
        signal_data = request.get_json()
        
        if not signal_data:
            return jsonify({
                'success': False,
                'message': 'Dados do sinal não fornecidos'
            }), 400
        
        # Validar campos obrigatórios
        required_fields = ['id', 'symbol', 'type', 'entry_price']
        for field in required_fields:
            if field not in signal_data:
                return jsonify({
                    'success': False,
                    'message': f'Campo obrigatório ausente: {field}'
                }), 400
        
        # Adicionar ao monitoramento
        success = monitoring_system.add_signal_to_monitoring(signal_data)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Sinal {signal_data["symbol"]} adicionado ao monitoramento com sucesso!',
                'data': {
                    'signal_id': signal_data['id'],
                    'symbol': signal_data['symbol'],
                    'added_at': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Falha ao adicionar sinal ao monitoramento'
            }), 500
        
    except Exception as e:
        print(f"❌ Erro ao adicionar sinal ao monitoramento: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@signal_monitoring_bp.route('/start', methods=['POST'])
@jwt_required
def start_monitoring():
    """
    Inicia o sistema de monitoramento
    """
    try:
        # Verificar se usuário é admin
        user_data = get_current_user()
        if not user_data or not user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Apenas administradores podem acessar esta funcionalidade.'
            }), 403
        
        if not monitoring_system:
            return jsonify({
                'success': False,
                'message': 'Sistema de monitoramento não inicializado'
            }), 500
        
        # Verificar se já está monitorando
        if monitoring_system.is_monitoring:
            return jsonify({
                'success': True,
                'message': 'Monitoramento já está ativo',
                'data': {
                    'status': 'already_active',
                    'stats': monitoring_system.get_monitoring_stats()
                }
            })
        
        # Iniciar monitoramento
        success = monitoring_system.start_monitoring()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Monitoramento iniciado com sucesso!',
                'data': {
                    'status': 'started',
                    'started_at': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                    'stats': monitoring_system.get_monitoring_stats()
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Falha ao iniciar monitoramento'
            }), 500
        
    except Exception as e:
        print(f"❌ Erro ao iniciar monitoramento: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@signal_monitoring_bp.route('/stop', methods=['POST'])
@jwt_required
def stop_monitoring():
    """
    Para o sistema de monitoramento
    """
    try:
        # Verificar se usuário é admin
        user_data = get_current_user()
        if not user_data or not user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Apenas administradores podem acessar esta funcionalidade.'
            }), 403
        
        if not monitoring_system:
            return jsonify({
                'success': False,
                'message': 'Sistema de monitoramento não inicializado'
            }), 500
        
        # Parar monitoramento
        monitoring_system.stop_monitoring()
        
        return jsonify({
            'success': True,
            'message': 'Monitoramento parado com sucesso!',
            'data': {
                'status': 'stopped',
                'stopped_at': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            }
        })
        
    except Exception as e:
        print(f"❌ Erro ao parar monitoramento: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@signal_monitoring_bp.route('/leverage/<symbol>', methods=['GET'])
@jwt_required
def get_symbol_leverage(symbol):
    """
    Retorna informações de alavancagem para um símbolo específico
    """
    try:
        # Verificar se usuário é admin
        user_data = get_current_user()
        if not user_data or not user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Apenas administradores podem acessar esta funcionalidade.'
            }), 403
        
        if not monitoring_system:
            return jsonify({
                'success': False,
                'message': 'Sistema de monitoramento não inicializado'
            }), 500
        
        # Validar símbolo
        symbol = symbol.upper()
        if not symbol.endswith('USDT'):
            return jsonify({
                'success': False,
                'message': 'Símbolo deve terminar com USDT'
            }), 400
        
        # Obter informações de alavancagem
        leverage_info = monitoring_system.leverage_detector.get_leverage_info(symbol)
        
        return jsonify({
            'success': True,
            'data': leverage_info
        })
        
    except Exception as e:
        print(f"❌ Erro ao obter alavancagem para {symbol}: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@signal_monitoring_bp.route('/stats', methods=['GET'])
@jwt_required
def get_monitoring_stats():
    """
    Retorna estatísticas detalhadas do monitoramento
    """
    try:
        # Verificar se usuário é admin
        user_data = get_current_user()
        if not user_data or not user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Apenas administradores podem acessar esta funcionalidade.'
            }), 403
        
        if not monitoring_system:
            return jsonify({
                'success': False,
                'message': 'Sistema de monitoramento não inicializado'
            }), 500
        
        # Obter estatísticas
        stats = monitoring_system.get_monitoring_stats()
        
        # Adicionar informações extras
        monitored_signals = monitoring_system.get_monitored_signals()
        expired_signals = monitoring_system.get_expired_signals()
        
        # Calcular estatísticas por alavancagem
        leverage_stats = {}
        for signal in monitored_signals + expired_signals:
            leverage = signal.get('max_leverage', 50)
            if leverage not in leverage_stats:
                leverage_stats[leverage] = {'count': 0, 'avg_profit': 0, 'profits': []}
            
            leverage_stats[leverage]['count'] += 1
            leverage_stats[leverage]['profits'].append(signal.get('current_profit', 0))
        
        # Calcular médias
        for leverage, data in leverage_stats.items():
            if data['profits']:
                data['avg_profit'] = sum(data['profits']) / len(data['profits'])
        
        return jsonify({
            'success': True,
            'data': {
                'general_stats': stats,
                'leverage_breakdown': leverage_stats,
                'system_info': {
                    'monitoring_days': monitoring_system.config['monitoring_days'],
                    'target_profit': monitoring_system.config['target_profit_percentage'],
                    'update_interval': monitoring_system.config['update_interval']
                }
            }
        })
        
    except Exception as e:
        print(f"❌ Erro ao obter estatísticas: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@signal_monitoring_bp.route('/quantitative-report', methods=['GET'])
@jwt_required
def get_quantitative_report():
    """
    Retorna relatório quantitativo completo para avaliação do sistema
    """
    try:
        # Verificar se usuário é admin
        user_data = get_current_user()
        if not user_data or not user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Apenas administradores podem acessar esta funcionalidade.'
            }), 403
        
        if not monitoring_system:
            return jsonify({
                'success': False,
                'message': 'Sistema de monitoramento não inicializado'
            }), 500
        
        # Obter relatório quantitativo
        report = monitoring_system.get_quantitative_report()
        
        return jsonify({
            'success': True,
            'data': report,
            'message': 'Relatório quantitativo gerado com sucesso'
        })
        
    except Exception as e:
        print(f"❌ Erro ao gerar relatório quantitativo: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500