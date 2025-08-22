from flask import Blueprint, request, jsonify, current_app
from middleware.auth_middleware import jwt_required, get_current_user
from core.database import Database
import os
import json
from datetime import datetime

customers_bp = Blueprint('customers', __name__)

# Inicializar componentes
db_instance = Database()

@customers_bp.route('/save', methods=['POST'])
def save_customer_data():
    """
    Salva dados do cliente capturados durante o checkout
    Para automações e disparos de email futuros
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        # Validar campos obrigatórios
        required_fields = ['email', 'courseId']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        # Preparar dados do cliente
        customer_data = {
            'email': data.get('email', '').strip().lower(),
            'first_name': data.get('firstName', '').strip(),
            'last_name': data.get('lastName', '').strip(),
            'full_name': f"{data.get('firstName', '').strip()} {data.get('lastName', '').strip()}".strip(),
            'phone': data.get('phone', ''),
            'identification_type': data.get('identification', {}).get('type', ''),
            'identification_number': data.get('identification', {}).get('number', ''),
            'address': json.dumps(data.get('address', {})),
            'course_id': data.get('courseId'),
            'course_name': data.get('courseName', ''),
            'course_price': data.get('coursePrice', 0),
            'payment_method': data.get('paymentMethod', ''),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'source': 'checkout_form',
            'status': 'lead' # lead, customer, completed
        }
        
        # Verificar se cliente já existe
        existing_customer = db_instance.fetch_one(
            "SELECT id, email FROM customers WHERE email = %s",
            (customer_data['email'],)
        )
        
        if existing_customer:
            # Atualizar dados existentes
            customer_data['updated_at'] = datetime.now().isoformat()
            
            update_fields = []
            update_values = []
            
            for key, value in customer_data.items():
                if key not in ['email', 'created_at']:
                    update_fields.append(f"{key} = %s")
                    update_values.append(value)
            
            update_values.append(customer_data['email'])
            
            query = f"UPDATE customers SET {', '.join(update_fields)} WHERE email = %s"
            db_instance.execute_query(query, tuple(update_values))
            
            customer_id = existing_customer['id']
            action = 'updated'
        else:
            # Inserir novo cliente
            fields = ', '.join(customer_data.keys())
            placeholders = ', '.join(['%s'] * len(customer_data))
            
            query = f"INSERT INTO customers ({fields}) VALUES ({placeholders})"
            customer_id = db_instance.execute_query(query, tuple(customer_data.values()))
            action = 'created'
        
        # Log da ação
        current_app.logger.info(f"Cliente {action}: {customer_data['email']} - Curso: {customer_data['course_id']}")
        
        # Salvar evento de checkout iniciado
        event_data = {
            'customer_id': customer_id,
            'event_type': 'checkout_started',
            'event_data': json.dumps({
                'course_id': customer_data['course_id'],
                'course_name': customer_data['course_name'],
                'course_price': customer_data['course_price'],
                'payment_method': customer_data['payment_method']
            }),
            'created_at': datetime.now().isoformat()
        }
        
        db_instance.execute_query(
            "INSERT INTO customer_events (customer_id, event_type, event_data, created_at) VALUES (%s, %s, %s, %s)",
            (event_data['customer_id'], event_data['event_type'], event_data['event_data'], event_data['created_at'])
        )
        
        return jsonify({
            'success': True,
            'message': f'Dados do cliente {action} com sucesso',
            'customer_id': customer_id,
            'action': action
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao salvar dados do cliente: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@customers_bp.route('/list', methods=['GET'])
@jwt_required
def list_customers():
    """
    Lista clientes cadastrados (apenas para admins)
    """
    try:
        current_user = get_current_user()
        if not current_user or current_user.get('role') != 'admin':
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Parâmetros de paginação
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        offset = (page - 1) * limit
        
        # Filtros
        course_id = request.args.get('course_id')
        status = request.args.get('status')
        
        # Construir query
        where_conditions = []
        params = []
        
        if course_id:
            where_conditions.append("course_id = %s")
            params.append(course_id)
        
        if status:
            where_conditions.append("status = %s")
            params.append(status)
        
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        # Buscar clientes
        query = f"""
            SELECT id, email, full_name, phone, course_id, course_name, 
                   course_price, payment_method, status, created_at, updated_at
            FROM customers 
            {where_clause}
            ORDER BY created_at DESC 
            LIMIT %s OFFSET %s
        """
        
        params.extend([limit, offset])
        customers = db_instance.fetch_all(query, tuple(params))
        
        # Contar total
        count_query = f"SELECT COUNT(*) as total FROM customers {where_clause}"
        count_params = params[:-2] if where_conditions else []
        total = db_instance.fetch_one(count_query, tuple(count_params))['total']
        
        return jsonify({
            'success': True,
            'customers': customers,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar clientes: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@customers_bp.route('/events/<int:customer_id>', methods=['GET'])
@jwt_required
def get_customer_events(customer_id):
    """
    Busca eventos de um cliente específico
    """
    try:
        current_user = get_current_user()
        if not current_user or current_user.get('role') != 'admin':
            return jsonify({'error': 'Acesso negado'}), 403
        
        events = db_instance.fetch_all(
            "SELECT * FROM customer_events WHERE customer_id = %s ORDER BY created_at DESC",
            (customer_id,)
        )
        
        return jsonify({
            'success': True,
            'events': events
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar eventos do cliente: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500