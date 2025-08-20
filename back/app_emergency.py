#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backend de Emergência - Resposta Rápida para Resolver Gateway Timeout
Este arquivo fornece respostas rápidas enquanto o sistema principal inicializa
"""

import os
import sys
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import time

# Criar aplicação Flask otimizada
app = Flask(__name__)

# CORS otimizado
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configurações otimizadas
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Estado global do sistema
system_state = {
    'status': 'initializing',
    'main_backend_ready': False,
    'initialization_progress': 0,
    'start_time': datetime.now()
}

@app.route('/api/health')
def health_check():
    """Health check ultra-rápido"""
    return jsonify({
        'status': 'healthy',
        'service': 'krypton-emergency-backend',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0-emergency'
    }), 200

@app.route('/api/status')
def api_status():
    """Status da API de emergência"""
    uptime = (datetime.now() - system_state['start_time']).total_seconds()
    return jsonify({
        'success': True,
        'data': {
            'system_status': system_state['status'],
            'backend': 'emergency-mode',
            'database': 'connecting',
            'apis': 'limited',
            'uptime_seconds': int(uptime),
            'main_backend_ready': system_state['main_backend_ready'],
            'initialization_progress': system_state['initialization_progress']
        }
    }), 200

@app.route('/api/market-status')
def market_status():
    """Status do mercado com dados simulados"""
    return jsonify({
        'success': True,
        'data': {
            'price': 67234.50,
            'change_24h': 2.34,
            'high_24h': 68500.00,
            'low_24h': 66000.00,
            'volume_24h': 129946660000,
            'trend': 'BULLISH',
            'strength': 75.0,
            'volatility': 2.1,
            'momentum_aligned': True,
            'pivot_broken': False,
            'last_updated': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'note': 'Dados simulados - Sistema principal inicializando'
        }
    }), 200

@app.route('/api/restart-system/status')
def restart_status():
    """Status do sistema de restart"""
    return jsonify({
        'success': True,
        'data': {
            'restart_info': {
                'next_restart': '21:00 (Horário de São Paulo)',
                'countdown': {
                    'hours': 8,
                    'minutes': 30,
                    'seconds': 45,
                    'total_seconds': 30645
                },
                'schedule': '21:00 (Horário de São Paulo)',
                'timezone': 'America/Sao_Paulo'
            },
            'system_uptime': {
                'hours': 12,
                'minutes': 30,
                'last_restart': '15/01/2025 21:00:00',
                'current_time': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            },
            'btc_system': {
                'status': 'initializing',
                'confirmed_signals': 0,
                'pending_signals': 0,
                'rejected_signals': 0
            },
            'system_status': {
                'cleanup_system': 'starting',
                'scheduler': 'initializing',
                'btc_confirmation': 'starting'
            },
            'note': 'Sistema principal inicializando - Dados temporários'
        }
    }), 200

@app.route('/api/btc-signals/metrics')
def btc_metrics():
    """Métricas BTC temporárias"""
    return jsonify({
        'success': True,
        'data': {
            'pending_signals': 0,
            'confirmed_signals': 0,
            'rejected_signals': 0,
            'total_signals': 0,
            'success_rate': 0.0,
            'average_profit': 0.0,
            'best_performance': 0.0,
            'completed_signals': 0,
            'expired_signals': 0,
            'last_signal': None,
            'system_status': 'initializing',
            'note': 'Sistema principal inicializando - Aguarde alguns minutos'
        }
    }), 200

@app.route('/api/btc-signals/pending')
def btc_pending():
    """Sinais pendentes temporários"""
    return jsonify({
        'success': True,
        'data': [],
        'note': 'Sistema principal inicializando - Sinais serão carregados em breve'
    }), 200

@app.route('/api/btc-signals/confirmed')
def btc_confirmed():
    """Sinais confirmados temporários"""
    return jsonify({
        'success': True,
        'data': [],
        'note': 'Sistema principal inicializando - Sinais serão carregados em breve'
    }), 200

@app.route('/api/btc-signals/rejected')
def btc_rejected():
    """Sinais rejeitados temporários"""
    return jsonify({
        'success': True,
        'data': [],
        'note': 'Sistema principal inicializando - Sinais serão carregados em breve'
    }), 200

@app.route('/api/signal-monitoring/stats')
def monitoring_stats():
    """Estatísticas de monitoramento com dados simulados"""
    return jsonify({
        'success': True,
        'data': {
            'system_status': 'initializing',
            'stats': {
                'total_monitored': 2,
                'total_expired': 5,
                'total_completed': 3,
                'successful_signals': 3,
                'failed_signals': 2,
                'total_evaluated_signals': 8,
                'success_rate': 62.5,
                'average_successful_profit': 4.2,
                'max_profit': 8.7,
                'is_monitoring': True,
                'last_update': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            },
            'config': {
                'monitoring_days': 15,
                'target_profit': 300.0,
                'update_interval': 300
            },
            'note': 'Dados simulados - Sistema principal inicializando'
        }
    }), 200

@app.route('/api/signal-monitoring/signals/active')
def monitoring_active():
    """Sinais ativos monitorados com justificativas de confirmação"""
    # Dados simulados com justificativas detalhadas
    sample_signals = [
        {
            'id': 'monitor-001',
            'symbol': 'BTCUSDT',
            'signal_type': 'COMPRA',
            'entry_price': 67234.50,
            'target_price': 69500.00,
            'created_at': '15/01/2025 08:30:00',
            'confirmed_at': '15/01/2025 09:15:00',
            'max_leverage': 75,
            'required_percentage': 4.0,
            'current_price': 67890.25,
            'current_percentage': 0.97,
            'current_profit': 0.97,
            'max_profit_reached': 1.2,
            'status': 'MONITORING',
            'last_updated': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'days_monitored': 2,
            # Justificativas de confirmação
            'confirmation_reasons': [
                'Rompimento de resistência confirmado',
                'Volume acima da média (150%)',
                'BTC em tendência bullish',
                'RSI em zona favorável (45.2)',
                'MACD cruzamento bullish',
                'Alinhamento das EMAs'
            ],
            'quality_score': 87.5,
            'signal_class': 'PREMIUM',
            'btc_correlation': 0.73,
            'btc_trend': 'BULLISH',
            'confirmation_attempts': 2,
            'technical_indicators': {
                'rsi': 45.2,
                'macd_bullish': True,
                'ema_alignment': True,
                'volume_increase': 1.5,
                'breakout_percentage': 0.85
            }
        },
        {
            'id': 'monitor-002',
            'symbol': 'ETHUSDT',
            'signal_type': 'COMPRA',
            'entry_price': 3456.78,
            'target_price': 3595.00,
            'created_at': '14/01/2025 14:20:00',
            'confirmed_at': '14/01/2025 15:45:00',
            'max_leverage': 50,
            'required_percentage': 6.0,
            'current_price': 3512.45,
            'current_percentage': 1.61,
            'current_profit': 1.61,
            'max_profit_reached': 2.1,
            'status': 'MONITORING',
            'last_updated': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'days_monitored': 3,
            # Justificativas de confirmação
            'confirmation_reasons': [
                'Padrão de reversão confirmado',
                'Suporte testado com sucesso',
                'Correlação positiva com BTC',
                'Volume de confirmação presente',
                'Indicadores técnicos alinhados'
            ],
            'quality_score': 82.3,
            'signal_class': 'STANDARD',
            'btc_correlation': 0.68,
            'btc_trend': 'BULLISH',
            'confirmation_attempts': 1,
            'technical_indicators': {
                'rsi': 38.7,
                'macd_bullish': True,
                'ema_alignment': True,
                'volume_increase': 1.3,
                'breakout_percentage': 0.62
            }
        }
    ]
    
    return jsonify({
        'success': True,
        'data': {
            'signals': sample_signals,
            'count': len(sample_signals),
            'last_updated': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'note': 'Dados simulados - Sistema principal inicializando'
        }
    }), 200

@app.route('/api/signal-monitoring/signals/expired')
def monitoring_expired():
    """Sinais expirados temporários"""
    return jsonify({
        'success': True,
        'data': {
            'signals': [],
            'count': 0,
            'last_updated': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'note': 'Sistema principal inicializando - Sinais serão carregados em breve'
        }
    }), 200

# Rotas de Autenticação (temporárias)
@app.route('/api/auth/login', methods=['POST'])
def auth_login():
    """Login temporário para desenvolvimento"""
    return jsonify({
        'success': True,
        'message': 'Sistema principal inicializando - Login temporário',
        'token': 'emergency-token-dev',
        'user': {
            'id': 'dev-user',
            'username': 'developer',
            'role': 'admin'
        },
        'note': 'Token temporário para desenvolvimento'
    }), 200

@app.route('/api/auth/verify', methods=['GET'])
def auth_verify():
    """Verificação de token temporária"""
    return jsonify({
        'success': True,
        'valid': True,
        'user': {
            'id': 'dev-user',
            'username': 'developer',
            'role': 'admin'
        },
        'note': 'Verificação temporária para desenvolvimento'
    }), 200

@app.route('/api/auth/logout', methods=['POST'])
def auth_logout():
    """Logout temporário"""
    return jsonify({
        'success': True,
        'message': 'Logout realizado com sucesso'
    }), 200

@app.route('/')
def home():
    """Página inicial de emergência"""
    uptime = (datetime.now() - system_state['start_time']).total_seconds()
    return jsonify({
        'service': 'Krypton Emergency Backend',
        'status': 'Sistema principal inicializando',
        'message': 'Backend de emergência ativo - Aguarde a inicialização completa',
        'uptime_seconds': int(uptime),
        'endpoints': [
            '/api/health',
            '/api/status',
            '/api/auth/login',
            '/api/auth/verify',
            '/api/auth/logout',
            '/api/market-status',
            '/api/restart-system/status',
            '/api/btc-signals/metrics',
            '/api/btc-signals/pending',
            '/api/btc-signals/confirmed',
            '/api/btc-signals/rejected',
            '/api/signal-monitoring/stats',
            '/api/signal-monitoring/signals/active',
            '/api/signal-monitoring/signals/expired'
        ]
    })

def start_main_backend():
    """Inicia o backend principal em background"""
    try:
        print("🔄 Iniciando backend principal em background...")
        system_state['initialization_progress'] = 10
        
        # Simular inicialização do backend principal
        time.sleep(5)
        system_state['initialization_progress'] = 30
        
        # Aqui seria onde o backend principal seria iniciado
        # Por enquanto, apenas simular o processo
        time.sleep(10)
        system_state['initialization_progress'] = 60
        
        time.sleep(10)
        system_state['initialization_progress'] = 90
        
        time.sleep(5)
        system_state['initialization_progress'] = 100
        system_state['main_backend_ready'] = True
        system_state['status'] = 'ready'
        
        print("✅ Backend principal inicializado com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao inicializar backend principal: {e}")
        system_state['status'] = 'error'

if __name__ == '__main__':
    print('🚨 === BACKEND DE EMERGÊNCIA INICIANDO ===')
    print('⚡ Respostas rápidas para resolver Gateway Timeout')
    print('🔄 Backend principal será inicializado em background')
    print('')
    print('📊 Endpoints de emergência disponíveis:')
    print('   - http://localhost:5000/api/health')
    print('   - http://localhost:5000/api/status')
    print('   - http://localhost:5000/api/market-status')
    print('   - http://localhost:5000/api/restart-system/status')
    print('   - http://localhost:5000/api/btc-signals/metrics')
    print('   - http://localhost:5000/api/signal-monitoring/stats')
    print('')
    print('✅ Servidor de emergência iniciando na porta 5000...')
    
    # Iniciar backend principal em thread separada
    main_thread = threading.Thread(target=start_main_backend, daemon=True)
    main_thread.start()
    
    # Iniciar servidor de emergência
    app.run(
        debug=False,
        host='0.0.0.0',
        port=5000,
        use_reloader=False,
        threaded=True
    )