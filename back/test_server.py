#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor de teste simples para verificar comunicação frontend-backend
"""

from flask import Flask, jsonify
from flask_cors import CORS
import os
from datetime import datetime

# Criar aplicação Flask simples
app = Flask(__name__)

# Configurar CORS para permitir comunicação com frontend
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "http://localhost:3001"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configurações básicas
app.config['SECRET_KEY'] = 'test-secret-key'
app.config['JWT_SECRET'] = 'test-jwt-secret'

@app.route('/')
def index():
    """Rota raiz"""
    return jsonify({
        'message': 'Backend de teste funcionando!',
        'timestamp': datetime.now().isoformat(),
        'status': 'online'
    })

@app.route('/api/health')
def health():
    """Endpoint de health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'test-backend',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/status')
def status():
    """Endpoint de status do sistema"""
    return jsonify({
        'success': True,
        'data': {
            'system_status': 'active',
            'backend': 'running',
            'database': 'connected',
            'apis': 'operational'
        }
    })

@app.route('/api/market-status')
def market_status():
    """Endpoint de status do mercado BTC"""
    return jsonify({
        'success': True,
        'data': {
            'current_price': 67234.50,
            'volume_24h': '129946.66B',
            'change_24h': '+2.34%',
            'market_cap': '1.32T',
            'last_updated': datetime.now().isoformat()
        }
    })

@app.route('/api/btc-signals/metrics')
def btc_metrics():
    """Endpoint de métricas BTC"""
    return jsonify({
        'success': True,
        'data': {
            'pending_signals': 14,
            'confirmed_signals': 30,
            'rejected_signals': 5,
            'total_signals': 49,
            'success_rate': '85.7%',
            'last_signal': datetime.now().isoformat()
        }
    })

@app.route('/api/btc-signals/pending')
def btc_pending():
    """Endpoint de sinais pendentes"""
    return jsonify({
        'success': True,
        'data': [
            {
                'id': 'test-001',
                'symbol': 'BTCUSDT',
                'type': 'COMPRA',
                'entry_price': 67234.50,
                'target_price': 69000.00,
                'created_at': datetime.now().isoformat(),
                'status': 'PENDING'
            },
            {
                'id': 'test-002', 
                'symbol': 'ETHUSDT',
                'type': 'VENDA',
                'entry_price': 3456.78,
                'target_price': 3200.00,
                'created_at': datetime.now().isoformat(),
                'status': 'PENDING'
            }
        ]
    })

@app.route('/api/btc-signals/confirmed')
def btc_confirmed():
    """Endpoint de sinais confirmados"""
    return jsonify({
        'success': True,
        'data': [
            {
                'id': 'confirmed-001',
                'symbol': 'ADAUSDT',
                'type': 'COMPRA',
                'entry_price': 0.45,
                'target_price': 0.52,
                'confirmed_at': datetime.now().isoformat(),
                'status': 'CONFIRMED'
            }
        ]
    })

@app.route('/api/restart-system/status')
def restart_status():
    """Endpoint de status do sistema de restart"""
    return jsonify({
        'success': True,
        'data': {
            'system_status': {
                'btc_confirmation': 'active',
                'cleanup_system': 'active',
                'scheduler': 'running'
            },
            'uptime_hours': 24,
            'next_restart': '21:00 (Horário de São Paulo)',
            'last_restart': datetime.now().isoformat()
        }
    })

if __name__ == '__main__':
    print('🚀 Iniciando servidor de teste...')
    print('📊 Endpoints disponíveis:')
    print('   - http://localhost:5000/')
    print('   - http://localhost:5000/api/health')
    print('   - http://localhost:5000/api/status')
    print('   - http://localhost:5000/api/market-status')
    print('   - http://localhost:5000/api/btc-signals/metrics')
    print('   - http://localhost:5000/api/btc-signals/pending')
    print('   - http://localhost:5000/api/btc-signals/confirmed')
    print('   - http://localhost:5000/api/restart-system/status')
    print('')
    print('✅ Servidor iniciando na porta 5000...')
    
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        use_reloader=False
    )