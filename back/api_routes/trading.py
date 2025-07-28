from flask import Blueprint, request, jsonify, current_app
from middleware.auth_middleware import jwt_required
from core.binance_client import BinanceClient
from core.technical_analysis import TechnicalAnalysis
from core.gerenciar_sinais import GerenciadorSinais
from core.database import Database

trading_bp = Blueprint('trading', __name__)

# Inicializar componentes com dependências corretas
db_instance = Database()
binance_client = BinanceClient()
technical_analysis = TechnicalAnalysis(db_instance)
gerenciador_sinais = GerenciadorSinais(db_instance)

@trading_bp.route('/analyze_and_generate_signals', methods=['POST'])
@jwt_required
def analyze_and_generate_signals():
    """Analisa pares e gera sinais de trading"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
            
        symbol = data.get('symbol')
        timeframe = data.get('timeframe', '1h')
        
        # Corrigir: definir symbols corretamente
        symbols = data.get('symbols', [symbol]) if symbol else []
        if not symbols:
            return jsonify({'error': 'Nenhum símbolo fornecido'}), 400
        
        results = []
        for symbol in symbols:
            # Obter dados históricos
            klines = binance_client.get_klines(symbol, timeframe, limit=100)
            
            # Análise técnica - corrigir chamada
            analysis = technical_analysis.analyze_symbol(symbol)
            
            # Gerar sinal se condições forem atendidas
            if analysis and analysis.get('quality_score', 0) >= 80:
                # Corrigir: usar save_signal ao invés de create_signal
                signal_data = {
                    'symbol': symbol,
                    'type': analysis.get('type', 'COMPRA'),
                    'entry_price': analysis.get('entry_price', 0),
                    'target_price': analysis.get('target_price', 0),
                    'quality_score': analysis.get('quality_score', 0)
                }
                
                if gerenciador_sinais.save_signal(signal_data):
                    results.append(signal_data)
        
        return jsonify({
            'success': True,
            'signals': results,
            'count': len(results)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@trading_bp.route('/get_top_pairs', methods=['GET'])
@jwt_required
def get_top_pairs():
    """Obtém os principais pares de trading"""
    try:
        data = request.get_json() or {}
        limit = data.get('limit', 100)
        
        # Corrigir nome do método
        pairs = binance_client.get_top_pairs(limit)
        
        return jsonify({
            'success': True,
            'pairs': pairs,
            'count': len(pairs)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@trading_bp.route('/analyze_pair/<symbol>', methods=['GET'])
@jwt_required
def analyze_pair(symbol):
    """Analisa um par específico"""
    try:
        timeframe = request.args.get('timeframe', '1h')
        
        # Obter dados
        klines = binance_client.get_klines(symbol, timeframe, limit=100)
        
        # Análise técnica - corrigir chamada
        analysis = technical_analysis.analyze_symbol(symbol)
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'analysis': analysis
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500