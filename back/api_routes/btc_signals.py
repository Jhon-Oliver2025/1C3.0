# API Routes para Sistema BTC de Confirmação de Sinais
from flask import Blueprint, jsonify, request
from middleware.auth_middleware import jwt_required, get_current_user
from core.database import Database
from core.btc_signal_manager import BTCSignalManager
from core.signal_confirmation_system import SignalConfirmationSystem
from core.binance_client import BinanceClient
from core.btc_correlation_analyzer import BTCCorrelationAnalyzer
import traceback
from datetime import datetime

# Criar blueprint
btc_signals_bp = Blueprint('btc_signals', __name__, url_prefix='/api/btc-signals')

# Instâncias globais (serão inicializadas no app principal)
btc_signal_manager = None
confirmation_system = None
btc_analyzer = None

def init_btc_signals_routes(db_instance: Database, btc_manager: BTCSignalManager):
    """Inicializa as rotas com as instâncias necessárias"""
    global btc_signal_manager, confirmation_system, btc_analyzer
    btc_signal_manager = btc_manager
    
    # Inicializar sistemas auxiliares
    binance_client = BinanceClient()
    confirmation_system = SignalConfirmationSystem(binance_client)
    btc_analyzer = BTCCorrelationAnalyzer(binance_client)
    
    print("✅ Rotas BTC Signals inicializadas!")

@btc_signals_bp.route('/pending', methods=['GET'])
@jwt_required
def get_pending_signals():
    """Retorna lista de sinais aguardando confirmação"""
    try:
        # Verificar se usuário é admin
        user_data = get_current_user()
        print(f"DEBUG BTC: user_data = {user_data}")
        print(f"DEBUG BTC: is_admin = {user_data.get('is_admin') if user_data else None} (type: {type(user_data.get('is_admin')) if user_data else None})")
        if not user_data or not user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Apenas administradores podem acessar esta funcionalidade.'
            }), 403
        
        if not btc_signal_manager:
            return jsonify({
                'success': False,
                'message': 'Sistema BTC não inicializado'
            }), 500
        
        # Obter sinais pendentes
        pending_signals = btc_signal_manager.get_pending_signals()
        
        return jsonify({
            'success': True,
            'data': {
                'pending_signals': pending_signals,
                'count': len(pending_signals),
                'last_updated': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            }
        })
        
    except Exception as e:
        print(f"❌ Erro ao obter sinais pendentes: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@btc_signals_bp.route('/daily-status', methods=['GET'])
@jwt_required
def get_daily_signals_status():
    """Retorna status do controle de sinais confirmados diários"""
    try:
        # Verificar se usuário é admin
        user_data = get_current_user()
        if not user_data or not user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Apenas administradores podem acessar esta funcionalidade.'
            }), 403
        
        if not btc_signal_manager:
            return jsonify({
                'success': False,
                'message': 'Sistema BTC não inicializado'
            }), 500
        
        # Obter informações do controle diário
        daily_count = btc_signal_manager.get_daily_confirmed_count()
        daily_list = btc_signal_manager.get_daily_confirmed_list()
        last_reset_date = btc_signal_manager.last_reset_date
        
        return jsonify({
            'success': True,
            'data': {
                'daily_confirmed_count': daily_count,
                'daily_confirmed_signals': [
                    {'symbol': signal[0], 'type': signal[1]} 
                    for signal in daily_list
                ],
                'last_reset_date': last_reset_date.strftime('%d/%m/%Y'),
                'current_date': datetime.now().strftime('%d/%m/%Y'),
                'duplicate_prevention': {
                    'enabled': True,
                    'description': 'Sinais do mesmo símbolo e tipo não podem ser confirmados mais de uma vez por dia',
                    'reset_time': '21:00 (Horário de São Paulo)'
                },
                'system_info': {
                    'pending_signals': len(btc_signal_manager.get_pending_signals()),
                    'total_confirmed': len(btc_signal_manager.get_confirmed_signals()),
                    'total_rejected': len(btc_signal_manager.get_rejected_signals())
                }
            }
        })
        
    except Exception as e:
        print(f"❌ Erro ao obter status diário: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

# Função duplicada removida - já existe acima

@btc_signals_bp.route('/rejected', methods=['GET'])
@jwt_required
def get_rejected_signals():
    """Retorna lista de sinais rejeitados"""
    try:
        # Verificar se usuário é admin
        user_data = get_current_user()
        if not user_data or not user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Apenas administradores podem acessar esta funcionalidade.'
            }), 403
        
        if not btc_signal_manager:
            return jsonify({
                'success': False,
                'message': 'Sistema BTC não inicializado'
            }), 500
        
        # Obter parâmetros opcionais
        limit = request.args.get('limit', 50, type=int)
        limit = min(limit, 200)  # Máximo 200 registros
        
        # Obter sinais rejeitados
        rejected_signals = btc_signal_manager.get_rejected_signals(limit=limit)
        
        return jsonify({
            'success': True,
            'data': {
                'rejected_signals': rejected_signals,
                'count': len(rejected_signals),
                'limit': limit,
                'last_updated': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            }
        })
        
    except Exception as e:
        print(f"❌ Erro ao obter sinais rejeitados: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@btc_signals_bp.route('/confirmed', methods=['GET'])
@jwt_required
def get_confirmed_signals():
    """Retorna lista de sinais confirmados"""
    try:
        # Verificar se usuário é admin
        user_data = get_current_user()
        if not user_data or not user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Apenas administradores podem acessar esta funcionalidade.'
            }), 403
        
        if not btc_signal_manager:
            return jsonify({
                'success': False,
                'message': 'Sistema BTC não inicializado'
            }), 500
        
        # Obter parâmetros opcionais
        limit = request.args.get('limit', 50, type=int)
        limit = min(limit, 200)  # Máximo 200 registros
        
        # Obter sinais confirmados
        confirmed_signals = btc_signal_manager.get_confirmed_signals(limit=limit)
        
        return jsonify({
            'success': True,
            'data': {
                'confirmed_signals': confirmed_signals,
                'count': len(confirmed_signals),
                'limit': limit,
                'last_updated': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            }
        })
        
    except Exception as e:
        print(f"❌ Erro ao obter sinais confirmados: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@btc_signals_bp.route('/metrics', methods=['GET'])
@jwt_required
def get_btc_metrics():
    """Retorna métricas do sistema BTC"""
    try:
        # Verificar se usuário é admin
        user_data = get_current_user()
        if not user_data or not user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Apenas administradores podem acessar esta funcionalidade.'
            }), 403
        
        if not btc_signal_manager or not btc_analyzer:
            return jsonify({
                'success': False,
                'message': 'Sistema BTC não inicializado'
            }), 500
        
        # Obter métricas de confirmação
        confirmation_metrics = btc_signal_manager.get_confirmation_metrics()
        
        # Obter análise atual do BTC
        btc_analysis = btc_analyzer.get_current_btc_analysis()
        
        # Obter dados de preço do BTC
        btc_price_data = btc_analyzer.get_btc_price_data()
        
        # Converter todos os valores para tipos serializáveis
        def make_serializable(obj):
            """Converte objetos para tipos serializáveis JSON"""
            import numpy as np
            import pandas as pd
            
            if isinstance(obj, dict):
                return {k: make_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [make_serializable(item) for item in obj]
            elif isinstance(obj, tuple):
                return [make_serializable(item) for item in obj]
            elif isinstance(obj, (np.integer, np.floating)):
                return obj.item()
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, (np.bool_, bool)):
                return bool(obj)
            elif isinstance(obj, (pd.Timestamp, datetime)):
                return obj.strftime('%d/%m/%Y %H:%M:%S') if hasattr(obj, 'strftime') else str(obj)
            elif hasattr(obj, 'item'):  # outros tipos numpy
                return obj.item()
            elif isinstance(obj, (int, float, str, type(None))):
                return obj
            else:
                return str(obj)
        
        return jsonify({
            'success': True,
            'data': {
                'confirmation_metrics': make_serializable(confirmation_metrics),
                'btc_analysis': make_serializable(btc_analysis),
                'btc_price_data': make_serializable(btc_price_data),
                'system_status': {
                    'btc_manager_active': bool(btc_signal_manager.is_monitoring),
                    'last_updated': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                }
            }
        })
        
    except Exception as e:
        print(f"❌ Erro ao obter métricas BTC: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@btc_signals_bp.route('/confirm/<signal_id>', methods=['POST'])
@jwt_required
def confirm_signal_manually(signal_id):
    """Confirma um sinal manualmente"""
    try:
        # Verificar se usuário é admin
        user_data = get_current_user()
        if not user_data or not user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Apenas administradores podem confirmar sinais.'
            }), 403
        
        if not btc_signal_manager:
            return jsonify({
                'success': False,
                'message': 'Sistema BTC não inicializado'
            }), 500
        
        # Confirmar sinal
        success = btc_signal_manager.manual_confirm_signal(signal_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Sinal {signal_id[:8]} confirmado com sucesso!',
                'data': {
                    'signal_id': signal_id,
                    'confirmed_by': user_data.get('email', 'admin'),
                    'confirmed_at': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Sinal {signal_id[:8]} não encontrado ou já processado'
            }), 404
        
    except Exception as e:
        print(f"❌ Erro ao confirmar sinal: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@btc_signals_bp.route('/reject/<signal_id>', methods=['POST'])
@jwt_required
def reject_signal_manually(signal_id):
    """Rejeita um sinal manualmente"""
    try:
        # Verificar se usuário é admin
        user_data = get_current_user()
        if not user_data or not user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Apenas administradores podem rejeitar sinais.'
            }), 403
        
        if not btc_signal_manager:
            return jsonify({
                'success': False,
                'message': 'Sistema BTC não inicializado'
            }), 500
        
        # Obter motivo da rejeição (opcional)
        data = request.get_json() or {}
        reason = data.get('reason', 'MANUAL_REJECTION_BY_ADMIN')
        
        # Rejeitar sinal
        success = btc_signal_manager.manual_reject_signal(signal_id, reason)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Sinal {signal_id[:8]} rejeitado com sucesso!',
                'data': {
                    'signal_id': signal_id,
                    'rejected_by': user_data.get('email', 'admin'),
                    'rejected_at': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                    'reason': reason
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Sinal {signal_id[:8]} não encontrado ou já processado'
            }), 404
        
    except Exception as e:
        print(f"❌ Erro ao rejeitar sinal: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@btc_signals_bp.route('/analysis/<symbol>', methods=['GET'])
@jwt_required
def get_symbol_btc_analysis(symbol):
    """Retorna análise detalhada de um símbolo em relação ao BTC"""
    try:
        # Verificar se usuário é admin
        user_data = get_current_user()
        if not user_data or not user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Apenas administradores podem acessar esta funcionalidade.'
            }), 403
        
        if not btc_analyzer or not confirmation_system:
            return jsonify({
                'success': False,
                'message': 'Sistema BTC não inicializado'
            }), 500
        
        # Validar símbolo
        symbol = symbol.upper()
        if not symbol.endswith('USDT'):
            return jsonify({
                'success': False,
                'message': 'Símbolo deve terminar com USDT'
            }), 400
        
        # Obter correlação com BTC
        btc_correlation = btc_analyzer.calculate_symbol_btc_correlation(symbol)
        
        # Obter análise atual do BTC
        btc_analysis = btc_analyzer.get_current_btc_analysis()
        
        # Obter thresholds do sistema de confirmação
        confirmation_thresholds = confirmation_system.get_confirmation_thresholds()
        
        return jsonify({
            'success': True,
            'data': {
                'symbol': symbol,
                'btc_correlation': btc_correlation,
                'btc_analysis': btc_analysis,
                'confirmation_thresholds': confirmation_thresholds,
                'analysis_timestamp': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            }
        })
        
    except Exception as e:
        print(f"❌ Erro na análise do símbolo {symbol}: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@btc_signals_bp.route('/config', methods=['GET'])
@jwt_required
def get_btc_config():
    """Retorna configurações do sistema BTC"""
    try:
        # Verificar se usuário é admin
        user_data = get_current_user()
        if not user_data or not user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Apenas administradores podem acessar esta funcionalidade.'
            }), 403
        
        if not btc_signal_manager or not confirmation_system:
            return jsonify({
                'success': False,
                'message': 'Sistema BTC não inicializado'
            }), 500
        
        # Obter configurações
        btc_config = btc_signal_manager.config
        confirmation_thresholds = confirmation_system.get_confirmation_thresholds()
        
        return jsonify({
            'success': True,
            'data': {
                'btc_signal_manager_config': btc_config,
                'confirmation_system_config': confirmation_thresholds,
                'system_info': {
                    'version': '1.0',
                    'last_updated': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                }
            }
        })
        
    except Exception as e:
        print(f"❌ Erro ao obter configurações BTC: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@btc_signals_bp.route('/config', methods=['PUT'])
@jwt_required
def update_btc_config():
    """Atualiza configurações do sistema BTC"""
    try:
        # Verificar se usuário é admin
        user_data = get_current_user()
        if not user_data or not user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Apenas administradores podem alterar configurações.'
            }), 403
        
        if not confirmation_system:
            return jsonify({
                'success': False,
                'message': 'Sistema BTC não inicializado'
            }), 500
        
        # Obter dados da requisição
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'Dados não fornecidos'
            }), 400
        
        # Atualizar thresholds se fornecidos
        if 'confirmation_thresholds' in data:
            success = confirmation_system.update_confirmation_thresholds(
                data['confirmation_thresholds']
            )
            
            if not success:
                return jsonify({
                    'success': False,
                    'message': 'Erro ao atualizar thresholds'
                }), 500
        
        return jsonify({
            'success': True,
            'message': 'Configurações atualizadas com sucesso!',
            'data': {
                'updated_by': user_data.get('email', 'admin'),
                'updated_at': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            }
        })
        
    except Exception as e:
        print(f"❌ Erro ao atualizar configurações BTC: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@btc_signals_bp.route('/status', methods=['GET'])
@jwt_required
def get_system_status():
    """Retorna status geral do sistema BTC"""
    try:
        # Verificar se usuário é admin
        user_data = get_current_user()
        if not user_data or not user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Apenas administradores podem acessar esta funcionalidade.'
            }), 403
        
        status_data = {
            'btc_signal_manager': {
                'initialized': btc_signal_manager is not None,
                'monitoring': btc_signal_manager.is_monitoring if btc_signal_manager else False,
                'pending_count': len(btc_signal_manager.pending_signals) if btc_signal_manager else 0
            },
            'confirmation_system': {
                'initialized': confirmation_system is not None
            },
            'btc_analyzer': {
                'initialized': btc_analyzer is not None
            },
            'system_timestamp': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        }
        
        return jsonify({
            'success': True,
            'data': status_data
        })
        
    except Exception as e:
        print(f"❌ Erro ao obter status do sistema: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

# Rota de teste para verificar se o sistema está funcionando
@btc_signals_bp.route('/test', methods=['GET'])
@jwt_required
def test_btc_system():
    """Testa o sistema BTC"""
    try:
        # Verificar se usuário é admin
        user_data = get_current_user()
        if not user_data or not user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Apenas administradores podem acessar esta funcionalidade.'
            }), 403
        
        test_results = {
            'btc_signal_manager': 'OK' if btc_signal_manager else 'NOT_INITIALIZED',
            'confirmation_system': 'OK' if confirmation_system else 'NOT_INITIALIZED',
            'btc_analyzer': 'OK' if btc_analyzer else 'NOT_INITIALIZED',
            'test_timestamp': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        }
        
        all_ok = all(status == 'OK' for status in test_results.values() if status != test_results['test_timestamp'])
        
        return jsonify({
            'success': all_ok,
            'message': 'Sistema BTC funcionando corretamente!' if all_ok else 'Alguns componentes não estão inicializados',
            'data': test_results
        })
        
    except Exception as e:
        print(f"❌ Erro no teste do sistema BTC: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500