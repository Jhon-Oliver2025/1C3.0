from flask import Blueprint, request, jsonify, current_app
from middleware.auth_middleware import jwt_required, get_current_user
from core.database import Database
from core.payments import PaymentManager
import os
from datetime import datetime

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
        print(f"🔄 [PAYMENTS] Recebendo requisição POST /create-preference")
        print(f"📋 [PAYMENTS] Headers: {dict(request.headers)}")
        print(f"📦 [PAYMENTS] Content-Type: {request.content_type}")
        
        data = request.get_json()
        print(f"📊 [PAYMENTS] Dados recebidos: {data}")
        
        if not data:
            print(f"❌ [PAYMENTS] Nenhum dado JSON recebido")
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
                'preference_id': preference['preference_id'],
                'init_point': preference['init_point'],
                'sandbox_init_point': preference.get('sandbox_init_point'),
                'public_key': preference['public_key']
            }), 201
        else:
            return jsonify({'error': 'Erro ao criar preferência de pagamento'}), 500
        
    except Exception as e:
        print(f"❌ [PAYMENTS] Erro na criação de preferência: {str(e)}")
        print(f"🔍 [PAYMENTS] Tipo do erro: {type(e).__name__}")
        import traceback
        print(f"📋 [PAYMENTS] Traceback completo: {traceback.format_exc()}")
        current_app.logger.error(f"Erro ao criar preferência: {str(e)}")
        return jsonify({'error': f'Erro interno do servidor: {str(e)}'}), 500

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
        print(f"🔧 [CONFIG] Verificando configurações do Mercado Pago...")
        print(f"📋 [CONFIG] Public Key: {payment_manager.public_key}")
        print(f"📋 [CONFIG] Access Token configurado: {'Sim' if payment_manager.access_token else 'Não'}")
        
        if not payment_manager.public_key:
            print(f"❌ [CONFIG] Public Key não encontrada!")
            return jsonify({
                'success': False,
                'error': 'Public Key não configurada',
                'debug': {
                    'public_key_exists': bool(payment_manager.public_key),
                    'access_token_exists': bool(payment_manager.access_token)
                }
            }), 500
        
        return jsonify({
            'success': True,
            'config': {
                'public_key': payment_manager.public_key,
                'currency': 'BRL',
                'country': 'BR'
            }
        }), 200
        
    except Exception as e:
        print(f"❌ [CONFIG] Erro ao buscar configurações: {str(e)}")
        current_app.logger.error(f"Erro ao buscar configurações: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'details': str(e)
        }), 500

@payments_bp.route('/debug', methods=['GET'])
def debug_payment_config():
    """Endpoint de debug para verificar configurações em produção"""
    try:
        import os
        
        # Verificar variáveis de ambiente
        env_vars = {
            'MERCADO_PAGO_ACCESS_TOKEN': bool(os.getenv('MERCADO_PAGO_ACCESS_TOKEN')),
            'MERCADO_PAGO_PUBLIC_KEY': bool(os.getenv('MERCADO_PAGO_PUBLIC_KEY')),
            'MERCADO_PAGO_WEBHOOK_SECRET': bool(os.getenv('MERCADO_PAGO_WEBHOOK_SECRET')),
            'FRONTEND_URL': os.getenv('FRONTEND_URL', 'Não configurado'),
            'BACKEND_URL': os.getenv('BACKEND_URL', 'Não configurado')
        }
        
        # Verificar instância do payment_manager
        manager_config = {
            'access_token_exists': bool(payment_manager.access_token),
            'public_key_exists': bool(payment_manager.public_key),
            'webhook_secret_exists': bool(payment_manager.webhook_secret),
            'base_url': payment_manager.base_url,
            'available_courses_count': len(payment_manager.available_courses)
        }
        
        # Logs detalhados
        print(f"🔍 [DEBUG] Variáveis de ambiente: {env_vars}")
        print(f"🔍 [DEBUG] Configuração do manager: {manager_config}")
        
        return jsonify({
            'success': True,
            'environment_variables': env_vars,
            'payment_manager_config': manager_config,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"❌ [DEBUG] Erro no debug: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@payments_bp.route('/process-card', methods=['POST'])
def process_card_payment():
    """Processa pagamento com cartão de crédito via Mercado Pago"""
    try:
        print(f"🔄 [CARD_PAYMENT] Recebendo requisição POST /process-card")
        print(f"📋 [CARD_PAYMENT] Headers: {dict(request.headers)}")
        
        data = request.get_json()
        print(f"📊 [CARD_PAYMENT] Dados recebidos: {data}")
        
        if not data:
            print(f"❌ [CARD_PAYMENT] Nenhum dado JSON recebido")
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        # Validar dados obrigatórios
        required_fields = ['token', 'payment_method_id', 'transaction_amount', 'installments']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo obrigatório: {field}'}), 400
        
        # Processar pagamento
        result = payment_manager.process_card_payment(data)
        
        if result and result.get('success'):
            print(f"✅ [CARD_PAYMENT] Pagamento processado com sucesso: {result.get('payment_id')}")
            return jsonify(result), 200
        else:
            print(f"❌ [CARD_PAYMENT] Falha no processamento: {result}")
            return jsonify({
                'success': False,
                'error': result.get('error', 'Erro no processamento do pagamento')
            }), 400
        
    except Exception as e:
        print(f"❌ [CARD_PAYMENT] Erro no processamento: {str(e)}")
        import traceback
        print(f"📋 [CARD_PAYMENT] Traceback: {traceback.format_exc()}")
        current_app.logger.error(f"Erro ao processar pagamento com cartão: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

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