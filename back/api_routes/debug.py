from flask import Blueprint, jsonify, current_app
import os
import pandas as pd
from datetime import datetime

debug_bp = Blueprint('debug', __name__)

@debug_bp.route('/system-status', methods=['GET'])
def system_status():
    """Endpoint de diagnóstico para verificar o status do sistema em produção"""
    try:
        bot_instance = getattr(current_app, 'bot_instance', None)
        if not bot_instance:
            return jsonify({'error': 'Sistema não inicializado'}), 500
            
        status = {
            'timestamp': datetime.now().isoformat(),
            'files': {},
            'database': {},
            'environment': {
                'flask_env': os.environ.get('FLASK_ENV', 'not_set'),
                'flask_debug': os.environ.get('FLASK_DEBUG', 'not_set')
            }
        }
        
        # Verificar arquivos CSV
        csv_files = {
            'auth_tokens': bot_instance.db.auth_tokens_file,
            'users': bot_instance.db.users_file,
            'signals_list': bot_instance.db.signals_list_file,
            'config': bot_instance.db.config_file
        }
        
        for name, file_path in csv_files.items():
            file_info = {
                'exists': os.path.exists(file_path),
                'path': file_path,
                'size': 0,
                'rows': 0,
                'readable': False,
                'error': None
            }
            
            if file_info['exists']:
                try:
                    file_info['size'] = os.path.getsize(file_path)
                    df = pd.read_csv(file_path)
                    file_info['rows'] = len(df)
                    file_info['readable'] = True
                    
                    # Informações específicas para auth_tokens
                    if name == 'auth_tokens' and not df.empty:
                        now = datetime.now()
                        df['expires_at'] = pd.to_datetime(df['expires_at'])
                        valid_tokens = df[df['expires_at'] > now]
                        file_info['valid_tokens'] = len(valid_tokens)
                        file_info['expired_tokens'] = len(df) - len(valid_tokens)
                        
                except Exception as e:
                    file_info['error'] = str(e)
                    
            status['files'][name] = file_info
            
        # Verificar conexão com banco
        try:
            users = bot_instance.db.get_all_users()
            status['database']['users_count'] = len(users) if users else 0
            status['database']['connection'] = 'ok'
        except Exception as e:
            status['database']['connection'] = 'error'
            status['database']['error'] = str(e)
            
        return jsonify(status), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro no diagnóstico: {e}")
        return jsonify({'error': f'Erro no diagnóstico: {str(e)}'}), 500

@debug_bp.route('/test-token/<token>', methods=['GET'])
def test_token(token):
    """Endpoint para testar um token específico"""
    try:
        bot_instance = getattr(current_app, 'bot_instance', None)
        if not bot_instance:
            return jsonify({'error': 'Sistema não inicializado'}), 500
            
        user_data = bot_instance.db.get_user_by_token(token)
        
        result = {
            'token': token[:10] + '...',
            'valid': user_data is not None,
            'user_data': user_data if user_data else None,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro no teste de token: {e}")
        return jsonify({'error': f'Erro no teste de token: {str(e)}'}), 500