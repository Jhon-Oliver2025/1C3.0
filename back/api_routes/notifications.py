from flask import Blueprint, request, jsonify
from middleware.auth_middleware import jwt_required

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/send', methods=['POST'])
@jwt_required
def send_notification():
    """Envia notificação via Telegram"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
            
        message = data.get('message', 'Mensagem de teste')
        
        # Aqui você integraria com o TelegramNotifier
        # telegram_notifier.send_message(message)
        
        return jsonify({
            'success': True,
            'message': 'Notificação enviada'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/send_test', methods=['POST'])
def send_test_notification():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
            
        message = data.get('message', 'Mensagem de teste')
        
        # Aqui você integraria com o TelegramNotifier
        # telegram_notifier.send_message(message)
        
        return jsonify({
            'success': True,
            'message': 'Notificação enviada'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500