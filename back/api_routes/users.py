from flask import Blueprint, request, jsonify, current_app
from middleware.auth_middleware import jwt_required

users_bp = Blueprint('users', __name__)

@users_bp.route('/profile', methods=['GET'])
@jwt_required
def get_profile():
    """Obtém perfil do usuário"""
    try:
        # Implementar lógica do perfil
        return jsonify({
            'success': True,
            'message': 'Perfil do usuário'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500