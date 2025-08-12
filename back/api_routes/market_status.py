from flask import Blueprint, jsonify
from datetime import datetime
import pytz

market_status_bp = Blueprint('market_status', __name__)

def get_market_status():
    """
    Determina o status (aberto/fechado) dos mercados de New York e da Ásia.
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

    # Mercado Ásia (Tóquio) - 09:00 às 15:00, Seg-Sex (horário real)
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
    try:
        status = get_market_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500