from flask import Blueprint, jsonify
from middleware.auth_middleware import jwt_required
from datetime import datetime, timedelta
import pytz

market_times_bp = Blueprint('market_times', __name__)

@market_times_bp.route('/market-countdown', methods=['GET'])
@jwt_required
def get_market_countdown():
    """Retorna contagem regressiva para abertura dos mercados"""
    try:
        now = datetime.now(pytz.timezone('America/Sao_Paulo'))
        
        # Próximo horário New York (10:30)
        ny_time = now.replace(hour=10, minute=30, second=0, microsecond=0)
        if now >= ny_time:
            ny_time += timedelta(days=1)
        
        # Próximo horário ÁSIA (21:00)
        asia_time = now.replace(hour=21, minute=0, second=0, microsecond=0)
        if now >= asia_time:
            asia_time += timedelta(days=1)
        
        ny_countdown = int((ny_time - now).total_seconds())
        asia_countdown = int((asia_time - now).total_seconds())
        
        return jsonify({
            'new_york_countdown': ny_countdown,
            'asia_countdown': asia_countdown,
            'new_york_time': ny_time.strftime('%d/%m/%Y %H:%M:%S'),
            'asia_time': asia_time.strftime('%d/%m/%Y %H:%M:%S'),
            'current_time': now.strftime('%d/%m/%Y %H:%M:%S')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500