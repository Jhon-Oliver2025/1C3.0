from flask import Blueprint, request, jsonify, current_app
from middleware.auth_middleware import jwt_required, get_current_user
from core.database import Database
from core.payments import PaymentManager
import os

payments_bp = Blueprint('payments', __name__)

# Inicializar componentes
db_instance = Database()
payment_manager = PaymentManager(db_instance)

@payments_bp.route('/courses', methods=['GET'])
@jwt_required
def get_available_courses():
    """Retorna lista de cursos disponíveis para compra"""
    try:
        courses = payment_manager.get_available_courses()
        return jsonify({
            'success': True,
            'courses': courses
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar cursos: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@payments_bp.route('/user-courses', methods=['GET'])
@jwt_required
def get_user_courses():
    """Retorna cursos que o usuário tem acesso"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        user_id = str(current_user.get('id'))
        courses = payment_manager.get_user_courses(user_id)
        
        return jsonify({
            'success': True,
            'courses': courses
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar cursos do usuário: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@payments_bp.route('/create-preference', methods=['POST'])
def create_payment_preference():
    """
    Cria preferência de pagamento no Mercado Pago
    Suporte para checkout público (sem autenticação obrigatória)
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        course_id = data.get('course_id')
        if not course_id:
            return jsonify({'error': 'ID do curso é obrigatório'}), 400
        
        # Obter usuário se autenticado (opcional para checkout público)
        current_user = None
        user_id = None
        
        try:
            current_user = get_current_user()
            if current_user:
                user_id = str(current_user.get('id'))
                
                # Verificar se usuário já tem acesso ao curso
                if payment_manager.check_course_access(user_id, course_id):
                    return jsonify({'error': 'Usuário já tem acesso a este curso'}), 400
        except:
            # Usuário não autenticado - checkout público
            pass
        
        # URLs de retorno personalizadas (opcionais)
        success_url = data.get('success_url')
        failure_url = data.get('failure_url')
        
        # Dados do curso para checkout público
        course_name = data.get('course_name')
        course_price = data.get('course_price')
        course_description = data.get('course_description')
        
        # Criar preferência de pagamento
        preference = payment_manager.create_payment_preference(
            user_id=user_id,  # Pode ser None para checkout público
            course_id=course_id,
            success_url=success_url,
            failure_url=failure_url,
            course_name=course_name,
            course_price=course_price,
            course_description=course_description
        )
        
        if preference:
            return jsonify({
                'success': True,
                'preference': preference
            }), 201
        else:
            return jsonify({'error': 'Erro ao criar preferência de pagamento'}), 500
        
    except Exception as e:
        current_app.logger.error(f"Erro ao criar preferência: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@payments_bp.route('/webhook', methods=['POST'])
def payment_webhook():
    """Webhook para receber notificações do Mercado Pago"""
    try:
        # Verificar se é uma requisição válida do Mercado Pago
        webhook_data = request.get_json()
        
        if not webhook_data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        # Processar webhook
        success = payment_manager.process_webhook(webhook_data)
        
        if success:
            return jsonify({'status': 'ok'}), 200
        else:
            return jsonify({'error': 'Erro ao processar webhook'}), 500
        
    except Exception as e:
        current_app.logger.error(f"Erro no webhook: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@payments_bp.route('/check-access/<course_id>', methods=['GET'])
@jwt_required
def check_course_access(course_id):
    """Verifica se o usuário tem acesso ao curso"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        user_id = str(current_user.get('id'))
        has_access = payment_manager.check_course_access(user_id, course_id)
        
        return jsonify({
            'success': True,
            'has_access': has_access,
            'course_id': course_id
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao verificar acesso: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@payments_bp.route('/check-lesson-access/<lesson_id>', methods=['GET'])
@jwt_required
def check_lesson_access(lesson_id):
    """Verifica se o usuário tem acesso à aula específica"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        user_id = str(current_user.get('id'))
        has_access = payment_manager.check_lesson_access(user_id, lesson_id)
        
        return jsonify({
            'success': True,
            'has_access': has_access,
            'lesson_id': lesson_id
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao verificar acesso à aula: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@payments_bp.route('/payment-status/<payment_id>', methods=['GET'])
@jwt_required
def get_payment_status(payment_id):
    """Consulta status de um pagamento específico"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Buscar informações do pagamento
        payment_info = payment_manager._get_payment_info(payment_id)
        
        if payment_info:
            return jsonify({
                'success': True,
                'payment': {
                    'id': payment_info.get('id'),
                    'status': payment_info.get('status'),
                    'status_detail': payment_info.get('status_detail'),
                    'transaction_amount': payment_info.get('transaction_amount'),
                    'currency_id': payment_info.get('currency_id'),
                    'date_created': payment_info.get('date_created'),
                    'date_approved': payment_info.get('date_approved')
                }
            }), 200
        else:
            return jsonify({'error': 'Pagamento não encontrado'}), 404
        
    except Exception as e:
        current_app.logger.error(f"Erro ao consultar pagamento: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@payments_bp.route('/config', methods=['GET'])
def get_payment_config():
    """Retorna configurações públicas do Mercado Pago"""
    try:
        return jsonify({
            'success': True,
            'config': {
                'public_key': payment_manager.public_key,
                'currency': 'BRL',
                'country': 'BR'
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar configurações: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

# Middleware para verificar acesso a aulas
def require_lesson_access(lesson_id):
    """Decorator para verificar acesso a aulas específicas"""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            try:
                current_user = get_current_user()
                if not current_user:
                    return jsonify({'error': 'Usuário não autenticado'}), 401
                
                user_id = str(current_user.get('id'))
                has_access = payment_manager.check_lesson_access(user_id, lesson_id)
                
                if not has_access:
                    return jsonify({
                        'error': 'Acesso negado',
                        'message': 'Você precisa comprar este curso para acessar esta aula',
                        'lesson_id': lesson_id
                    }), 403
                
                return f(*args, **kwargs)
                
            except Exception as e:
                current_app.logger.error(f"Erro na verificação de acesso: {str(e)}")
                return jsonify({'error': 'Erro interno do servidor'}), 500
        
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator