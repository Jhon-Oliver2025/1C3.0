from flask import Blueprint, jsonify
from datetime import datetime
import pytz
import traceback

market_status_bp = Blueprint('market_status', __name__)

# Instâncias globais (serão inicializadas no app principal)
btc_analyzer = None

def init_market_status_routes(btc_analyzer_instance):
    """Inicializa as rotas com as instâncias necessárias"""
    global btc_analyzer
    btc_analyzer = btc_analyzer_instance
    print("✅ Rotas Market Status inicializadas!")

def get_market_status():
    """
    Determina o status (aberto/fechado) dos mercados de New York e de Tóquio.
    Sistema de limpeza baseado em horário de São Paulo: 10:00 e 21:00.
    """
    now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)

    # Mercado New York - 09:30 às 16:00, Seg-Sex (horário real)
    tz_ny = pytz.timezone('America/New_York')
    now_ny = now_utc.astimezone(tz_ny)
    ny_open_time = now_ny.replace(hour=9, minute=30, second=0, microsecond=0).time()
    ny_close_time = now_ny.replace(hour=16, minute=0, second=0, microsecond=0).time()
    ny_is_weekday = now_ny.weekday() < 5  # 0=Seg, 4=Sex
    ny_is_open = ny_is_weekday and ny_open_time <= now_ny.time() < ny_close_time
    ny_status = 'ABERTO' if ny_is_open else 'FECHADO'

    # Mercado Tóquio - 09:00 às 15:00, Seg-Sex (horário real)
    tz_tokyo = pytz.timezone('Asia/Tokyo')
    now_tokyo = now_utc.astimezone(tz_tokyo)
    asia_open_time = now_tokyo.replace(hour=9, minute=0, second=0, microsecond=0).time()
    asia_close_time = now_tokyo.replace(hour=15, minute=0, second=0, microsecond=0).time()
    asia_is_weekday = now_tokyo.weekday() < 5  # 0=Seg, 4=Sex
    asia_is_open = asia_is_weekday and asia_open_time <= now_tokyo.time() < asia_close_time
    asia_status = 'ABERTO' if asia_is_open else 'FECHADO'
    
    return {
        'new_york': {'status': ny_status, 'time': now_ny.strftime('%H:%M:%S')},
        'asia': {'status': asia_status, 'time': now_tokyo.strftime('%H:%M:%S')}
    }

@market_status_bp.route('/market-status', methods=['GET'])
def market_status():
    """Retorna status dos mercados e dados completos do BTC"""
    try:
        # Status dos mercados tradicionais
        market_data = get_market_status()
        
        # Dados do BTC (se disponível)
        btc_data = get_btc_market_data()
        
        return jsonify({
            'success': True,
            'data': {
                **btc_data,  # Dados do BTC como dados principais
                'markets': market_data  # Mercados tradicionais como sub-seção
            }
        })
        
    except Exception as e:
        print(f"❌ Erro na API market-status: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

def get_btc_market_data():
    """Obtém dados completos do BTC para os cards"""
    try:
        if not btc_analyzer:
            print("⚠️ BTCAnalyzer não inicializado, retornando dados padrão")
            return get_default_btc_data()
        
        # Obter dados de preço do BTC
        btc_price_data = btc_analyzer.get_btc_price_data()
        
        # Obter análise técnica atual do BTC
        btc_analysis = btc_analyzer.get_current_btc_analysis()
        
        # Combinar dados de preço e análise
        combined_data = {
            # Dados de preço
            'price': btc_price_data.get('price', 50000.0),
            'change_24h': btc_price_data.get('change_24h', 0.0),
            'high_24h': btc_price_data.get('high_24h', 50000.0),
            'low_24h': btc_price_data.get('low_24h', 50000.0),
            'volume_24h': btc_price_data.get('volume_24h', 0.0),
            
            # Dados de análise técnica
            'trend': btc_analysis.get('trend', 'NEUTRAL'),
            'strength': btc_analysis.get('strength', 50.0),
            'volatility': btc_analysis.get('volatility', 2.0),
            'momentum_aligned': btc_analysis.get('momentum_aligned', False),
            'pivot_broken': btc_analysis.get('pivot_broken', False),
            
            # Timeframes detalhados
            'timeframes': btc_analysis.get('timeframes', {}),
            
            # Timestamp
            'last_updated': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        }
        
        return combined_data
        
    except Exception as e:
        print(f"❌ Erro ao obter dados BTC: {e}")
        return get_default_btc_data()

def get_default_btc_data():
    """Retorna dados padrão do BTC em caso de erro"""
    return {
        'price': 50000.0,
        'change_24h': 0.0,
        'high_24h': 50000.0,
        'low_24h': 50000.0,
        'volume_24h': 0.0,
        'trend': 'NEUTRAL',
        'strength': 50.0,
        'volatility': 2.0,
        'momentum_aligned': False,
        'pivot_broken': False,
        'timeframes': {},
        'last_updated': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    }