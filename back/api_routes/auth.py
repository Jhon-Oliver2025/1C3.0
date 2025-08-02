@auth_bp.route('/register', methods=['POST'])
def register():
    """Endpoint para registro de usuários (ficam pendentes)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
            
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            return jsonify({'error': 'Username, email e senha são obrigatórios'}), 400
            
        bot_instance = getattr(current_app, 'bot_instance', None)
        if not bot_instance:
            return jsonify({'error': 'Sistema não inicializado'}), 500
            
        # Verificar se usuário já existe
        existing_user = bot_instance.db.get_user_by_username(username)
        if existing_user:
            return jsonify({'error': 'Nome de usuário já existe'}), 409
            
        existing_email = bot_instance.db.get_user_by_email(email)
        if existing_email:
            return jsonify({'error': 'Email já está cadastrado'}), 409
            
        # Criar usuário (status pendente)
        user_created = bot_instance.db.create_user(username, email, password)
        if user_created:
            return jsonify({
                'success': True,
                'message': 'Conta criada com sucesso! Aguarde a aprovação do administrador para acessar o sistema.'
            }), 201
        else:
            return jsonify({'error': 'Erro ao criar usuário'}), 500
            
    except Exception as e:
        current_app.logger.error(f"Erro no registro: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500