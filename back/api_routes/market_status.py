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
    Determina o status (aberto/fechado) do mercado asiático.
    Sistema de limpeza baseado em horário de São Paulo: 21:00.
    """
    now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)

    # Mercado Asiático - Das 21:30 (abertura Tóquio) até 08:00 (fechamento China)
    # Usando horário de São Paulo como referência para facilitar o cálculo
    tz_sao_paulo = pytz.timezone('America/Sao_Paulo')
    now_sp = now_utc.astimezone(tz_sao_paulo)
    
    # Mercado asiático funciona das 21:30 às 08:00 (horário de São Paulo)
    # Isso corresponde ao período de Tóquio (09:00) até China (20:00 horário local)
    current_time = now_sp.time()
    current_weekday = now_sp.weekday()  # 0=Seg, 6=Dom
    
    # Lógica para horário que cruza meia-noite (21:30 até 08:00)
    asia_open_time = now_sp.replace(hour=21, minute=30, second=0, microsecond=0).time()
    asia_close_time = now_sp.replace(hour=8, minute=0, second=0, microsecond=0).time()
    
    # Verificar se está em horário de funcionamento
    is_in_operating_hours = current_time >= asia_open_time or current_time < asia_close_time
    
    # Verificar se é dia útil (Seg-Sex)
    # Para mercado que cruza meia-noite, considerar tanto o dia atual quanto o anterior
    is_weekday = current_weekday < 5  # 0-4 = Seg-Sex
    
    # Se estamos na madrugada (00:00-08:00), verificar se ontem era dia útil
    if current_time < asia_close_time:  # Madrugada
        yesterday_weekday = (current_weekday - 1) % 7
        is_weekday = yesterday_weekday < 5
    
    # Mercado está aberto se está em horário de funcionamento E é dia útil
    asia_is_open = is_in_operating_hours and is_weekday
    
    asia_status = 'ABERTO' if asia_is_open else 'FECHADO'
    
    return {
        'asia': {'status': asia_status, 'time': now_sp.strftime('%H:%M:%S')}
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