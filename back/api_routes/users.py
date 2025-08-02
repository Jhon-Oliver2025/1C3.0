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


@users_bp.route('/pending', methods=['GET'])
def get_pending_users():
    """Retorna usuários pendentes de aprovação (apenas admin)"""
    try:
        # Verificar se é admin (implementar middleware de autenticação)
        bot_instance = getattr(current_app, 'bot_instance', None)
        if not bot_instance:
            return jsonify({'error': 'Sistema não inicializado'}), 500
            
        pending_users = bot_instance.db.get_pending_users()
        return jsonify({
            'success': True,
            'users': pending_users
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar usuários pendentes: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@users_bp.route('/approve/<user_id>', methods=['POST'])
def approve_user(user_id):
    """Aprova um usuário pendente (apenas admin)"""
    try:
        bot_instance = getattr(current_app, 'bot_instance', None)
        if not bot_instance:
            return jsonify({'error': 'Sistema não inicializado'}), 500
            
        success = bot_instance.db.approve_user(user_id)
        if success:
            return jsonify({
                'success': True,
                'message': 'Usuário aprovado com sucesso!'
            }), 200
        else:
            return jsonify({'error': 'Erro ao aprovar usuário'}), 500
            
    except Exception as e:
        current_app.logger.error(f"Erro ao aprovar usuário: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@users_bp.route('/suspend/<user_id>', methods=['POST'])
def suspend_user(user_id):
    """Suspende um usuário (apenas admin)"""
    try:
        bot_instance = getattr(current_app, 'bot_instance', None)
        if not bot_instance:
            return jsonify({'error': 'Sistema não inicializado'}), 500
            
        success = bot_instance.db.suspend_user(user_id)
        if success:
            return jsonify({
                'success': True,
                'message': 'Usuário suspenso com sucesso!'
            }), 200
        else:
            return jsonify({'error': 'Erro ao suspender usuário'}), 500
            
    except Exception as e:
        current_app.logger.error(f"Erro ao suspender usuário: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500