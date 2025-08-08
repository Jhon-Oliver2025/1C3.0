from flask import Blueprint, jsonify
from datetime import datetime
import pytz

market_status_bp = Blueprint('market_status', __name__)

def get_market_status():
    """
    Determina o status (aberto/fechado) dos mercados dos EUA e da Ásia.
    """
    now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)

    # Mercado EUA (Nova York) - 09:30 às 16:00, Seg-Sex
    tz_ny = pytz.timezone('America/New_York')
    now_ny = now_utc.astimezone(tz_ny)
    usa_open_time = now_ny.replace(hour=9, minute=30, second=0, microsecond=0).time()
    usa_close_time = now_ny.replace(hour=16, minute=0, second=0, microsecond=0).time()
    usa_is_weekday = now_ny.weekday() < 5  # 0=Seg, 4=Sex
    usa_is_open = usa_is_weekday and usa_open_time <= now_ny.time() < usa_close_time
    usa_status = 'ABERTO' if usa_is_open else 'FECHADO'

    # Mercado Ásia (Tóquio) - 09:00 às 15:00, Seg-Sex
    tz_tokyo = pytz.timezone('Asia/Tokyo')
    now_tokyo = now_utc.astimezone(tz_tokyo)
    asia_open_time = now_tokyo.replace(hour=9, minute=0, second=0, microsecond=0).time()
    asia_close_time = now_tokyo.replace(hour=15, minute=0, second=0, microsecond=0).time()
    asia_is_weekday = now_tokyo.weekday() < 5  # 0=Seg, 4=Sex
    asia_is_open = asia_is_weekday and asia_open_time <= now_tokyo.time() < asia_close_time
    asia_status = 'ABERTO' if asia_is_open else 'FECHADO'
    
    return {
        'usa': {'status': usa_status, 'time': now_ny.strftime('%H:%M:%S')},
        'asia': {'status': asia_status, 'time': now_tokyo.strftime('%H:%M:%S')}
    }

@market_status_bp.route('/market-status', methods=['GET'])
def market_status():
    try:
        status = get_market_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500