# -*- coding: utf-8 -*-
"""
API Routes para Sistema de Restart
Fornece informações sobre o restart diário do sistema
"""

from flask import Blueprint, jsonify
from middleware.auth_middleware import jwt_required, get_current_user
from core.signal_cleanup import cleanup_system
from core.btc_signal_manager import BTCSignalManager
from datetime import datetime
import pytz
import traceback

# Criar blueprint
restart_system_bp = Blueprint('restart_system', __name__, url_prefix='/api/restart-system')

@restart_system_bp.route('/status', methods=['GET'])
def get_restart_status():
    """
    Retorna informações sobre o sistema de restart
    Inclui contador, próximo restart e estatísticas
    Rota pública para exibição nos cards do dashboard
    """
    try:
        print('📊 Processando requisição para /api/restart-system/status')
        
        # Obter informações do sistema de restart
        time_until_restart = cleanup_system.get_time_until_restart()
        next_restart_time = cleanup_system.get_next_restart_time()
        
        # Obter horário atual de São Paulo
        sao_paulo_tz = pytz.timezone('America/Sao_Paulo')
        current_time_sp = datetime.now(sao_paulo_tz)
        
        # Calcular uptime desde o último restart (aproximado)
        last_restart = current_time_sp.replace(hour=21, minute=0, second=0, microsecond=0)
        if current_time_sp.hour < 21:
            # Se ainda não passou das 21h hoje, o último restart foi ontem
            from datetime import timedelta
            last_restart = last_restart - timedelta(days=1)
        
        uptime_seconds = (current_time_sp - last_restart).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        
        # Informações do sistema BTC (se disponível)
        btc_system_info = {
            'status': 'unknown',
            'confirmed_signals': 0,
            'pending_signals': 0,
            'rejected_signals': 0
        }
        
        try:
            # Aqui podemos adicionar lógica para obter estatísticas do sistema BTC
            # Por enquanto, valores simulados
            btc_system_info = {
                'status': 'active',
                'confirmed_signals': 0,  # Será atualizado com dados reais
                'pending_signals': 0,    # Será atualizado com dados reais
                'rejected_signals': 0    # Será atualizado com dados reais
            }
        except Exception as e:
            print(f"⚠️ Erro ao obter informações do sistema BTC: {e}")
        
        return jsonify({
            'success': True,
            'data': {
                'restart_info': {
                    'next_restart': next_restart_time,
                    'countdown': {
                        'hours': time_until_restart['hours'],
                        'minutes': time_until_restart['minutes'],
                        'seconds': time_until_restart['seconds'],
                        'total_seconds': int(time_until_restart['total_seconds'])
                    },
                    'schedule': '21:00 (Horário de São Paulo)',
                    'timezone': 'America/Sao_Paulo'
                },
                'system_uptime': {
                    'hours': uptime_hours,
                    'minutes': uptime_minutes,
                    'last_restart': last_restart.strftime('%d/%m/%Y %H:%M:%S'),
                    'current_time': current_time_sp.strftime('%d/%m/%Y %H:%M:%S')
                },
                'btc_system': btc_system_info,
                'restart_features': [
                    'Limpeza completa de sinais antigos',
                    'Reinício do sistema de confirmação BTC',
                    'Atualização de estatísticas do sistema',
                    'Varredura completa do mercado',
                    'Atualização da lista de pares top 100'
                ],
                'system_status': {
                    'cleanup_system': 'active',
                    'scheduler': 'running',
                    'btc_confirmation': btc_system_info['status']
                }
            }
        })
        
    except Exception as e:
        print(f"❌ Erro ao obter status do restart: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@restart_system_bp.route('/trigger', methods=['POST'])
@jwt_required
def trigger_manual_restart():
    """
    Executa restart manual do sistema (apenas para admins)
    """
    try:
        # Verificar se usuário é admin
        user_data = get_current_user()
        if not user_data or not user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Apenas administradores podem executar restart manual.'
            }), 403
        
        # Executar restart manual
        print(f"🔧 Restart manual iniciado por: {user_data.get('email', 'admin')}")
        cleanup_system.daily_system_restart()
        
        return jsonify({
            'success': True,
            'message': 'Restart manual executado com sucesso!',
            'data': {
                'executed_by': user_data.get('email', 'admin'),
                'executed_at': datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%d/%m/%Y %H:%M:%S'),
                'next_scheduled_restart': cleanup_system.get_next_restart_time()
            }
        })
        
    except Exception as e:
        print(f"❌ Erro no restart manual: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@restart_system_bp.route('/history', methods=['GET'])
@jwt_required
def get_restart_history():
    """
    Retorna histórico de restarts (simulado por enquanto)
    """
    try:
        # Verificar se usuário é admin
        user_data = get_current_user()
        if not user_data or not user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Apenas administradores podem acessar histórico de restarts.'
            }), 403
        
        # Por enquanto, retornar histórico simulado
        # No futuro, isso pode vir de um banco de dados
        sao_paulo_tz = pytz.timezone('America/Sao_Paulo')
        current_time = datetime.now(sao_paulo_tz)
        
        history = []
        for i in range(7):  # Últimos 7 dias
            from datetime import timedelta
            restart_date = current_time - timedelta(days=i)
            restart_date = restart_date.replace(hour=21, minute=0, second=0, microsecond=0)
            
            history.append({
                'date': restart_date.strftime('%d/%m/%Y'),
                'time': '21:00:00',
                'status': 'completed' if i > 0 else 'scheduled',
                'signals_cleaned': 15 - i * 2 if i > 0 else 0,
                'duration_seconds': 45 + i * 5 if i > 0 else 0,
                'type': 'automatic'
            })
        
        return jsonify({
            'success': True,
            'data': {
                'history': history,
                'total_restarts': len([h for h in history if h['status'] == 'completed']),
                'average_duration': 50,  # segundos
                'last_restart': history[1] if len(history) > 1 else None
            }
        })
        
    except Exception as e:
        print(f"❌ Erro ao obter histórico de restarts: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500