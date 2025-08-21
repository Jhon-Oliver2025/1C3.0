from flask import Blueprint, jsonify
from core.binance_client import BinanceClient
import os

binance_prices_bp = Blueprint('binance_prices', __name__)

# Inicializar cliente Binance
use_binance = os.getenv('USE_BINANCE_API', 'true').lower() == 'true'

if use_binance:
    try:
        binance_client = BinanceClient()
        print("✅ BinanceClient carregado para preços em tempo real")
    except Exception as e:
        print(f"⚠️ Erro ao carregar BinanceClient: {e}")
        binance_client = None
else:
    print("🔒 Binance API desabilitada para preços")
    binance_client = None

@binance_prices_bp.route('/api/binance/price/<symbol>')
def get_symbol_price(symbol):
    """
    Obtém o preço atual de um símbolo da Binance
    
    Args:
        symbol: Símbolo da moeda (ex: ETHUSDT)
        
    Returns:
        JSON com o preço atual
    """
    try:
        if not binance_client or not hasattr(binance_client, 'use_binance_api') or not binance_client.use_binance_api:
            return jsonify({
                'success': False,
                'error': 'Binance API não disponível',
                'price': None
            }), 503
        
        # Buscar preço atual via API da Binance
        response = binance_client.make_request(f'/fapi/v1/ticker/price?symbol={symbol}')
        
        if response and 'price' in response:
            price = float(response['price'])
            return jsonify({
                'success': True,
                'symbol': symbol,
                'price': price,
                'timestamp': response.get('timestamp', None)
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Preço não encontrado para {symbol}',
                'price': None
            }), 404
            
    except Exception as e:
        print(f"❌ Erro ao buscar preço de {symbol}: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'price': None
        }), 500

@binance_prices_bp.route('/api/binance/prices')
def get_multiple_prices():
    """
    Obtém preços de múltiplos símbolos da Binance
    
    Returns:
        JSON com preços de todos os símbolos
    """
    try:
        if not binance_client or not hasattr(binance_client, 'use_binance_api') or not binance_client.use_binance_api:
            return jsonify({
                'success': False,
                'error': 'Binance API não disponível',
                'prices': {}
            }), 503
        
        # Buscar todos os preços via API da Binance
        response = binance_client.make_request('/fapi/v1/ticker/price')
        
        if response and isinstance(response, list):
            prices = {}
            for item in response:
                if 'symbol' in item and 'price' in item:
                    prices[item['symbol']] = float(item['price'])
            
            return jsonify({
                'success': True,
                'prices': prices,
                'count': len(prices)
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Erro ao buscar preços',
                'prices': {}
            }), 500
            
    except Exception as e:
        print(f"❌ Erro ao buscar preços múltiplos: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'prices': {}
        }), 500