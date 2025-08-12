from flask import Blueprint, jsonify
from middleware.auth_middleware import jwt_required
from datetime import datetime, timedelta
import pytz
import os

cleanup_status_bp = Blueprint('cleanup_status', __name__)

@cleanup_status_bp.route('/cleanup-status', methods=['GET'])
@jwt_required
def get_cleanup_status():
    """Retorna o status das limpezas automáticas (ATIVO/INATIVO)"""
    try:
        # Timezone de São Paulo
        tz = pytz.timezone('America/Sao_Paulo')
        now = datetime.now(tz)
        
        # Verificar arquivo de log do scheduler
        log_file = os.path.join(os.getcwd(), 'scheduler_log.txt')
        
        # Status padrão
        morning_status = 'INATIVO'
        evening_status = 'INATIVO'
        last_morning_cleanup = None
        last_evening_cleanup = None
        
        # Ler logs se o arquivo existir
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Procurar pelas últimas execuções
                for line in reversed(lines):
                    if 'MORNING_CLEANUP_EXECUTED:' in line:
                        if last_morning_cleanup is None:
                            timestamp_str = line.split('MORNING_CLEANUP_EXECUTED: ')[1].strip()
                            last_morning_cleanup = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    
                    elif 'EVENING_CLEANUP_EXECUTED:' in line:
                        if last_evening_cleanup is None:
                            timestamp_str = line.split('EVENING_CLEANUP_EXECUTED: ')[1].strip()
                            last_evening_cleanup = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    
                    # Parar quando encontrar ambos
                    if last_morning_cleanup and last_evening_cleanup:
                        break
                        
            except Exception as e:
                print(f"Erro ao ler log: {e}")
        
        # Verificar se as limpezas aconteceram hoje
        today = now.date()
        
        # Limpeza matinal (10:00)
        if last_morning_cleanup:
            if last_morning_cleanup.date() == today and last_morning_cleanup.hour == 10:
                morning_status = 'ATIVO'
        
        # Limpeza noturna (21:00)
        if last_evening_cleanup:
            if last_evening_cleanup.date() == today and last_evening_cleanup.hour == 21:
                evening_status = 'ATIVO'
            # Se for ontem à noite e ainda não passou das 10h de hoje
            elif (last_evening_cleanup.date() == (today - timedelta(days=1)) and 
                  last_evening_cleanup.hour == 21 and now.hour < 10):
                evening_status = 'ATIVO'
        
        # Próximas execuções
        next_morning = now.replace(hour=10, minute=0, second=0, microsecond=0)
        if now.hour >= 10:
            next_morning += timedelta(days=1)
            
        next_evening = now.replace(hour=21, minute=0, second=0, microsecond=0)
        if now.hour >= 21:
            next_evening += timedelta(days=1)
        
        return jsonify({
            'morning_cleanup': {
                'status': morning_status,
                'time': '10:00',
                'description': 'Limpeza matinal (pré-mercado New York)',
                'last_execution': last_morning_cleanup.strftime('%Y-%m-%d %H:%M:%S') if last_morning_cleanup else None,
                'next_execution': next_morning.strftime('%Y-%m-%d %H:%M:%S')
            },
            'evening_cleanup': {
                'status': evening_status,
                'time': '21:00', 
                'description': 'Limpeza noturna (pré-mercado Ásia)',
                'last_execution': last_evening_cleanup.strftime('%Y-%m-%d %H:%M:%S') if last_evening_cleanup else None,
                'next_execution': next_evening.strftime('%Y-%m-%d %H:%M:%S')
            },
            'current_time': now.strftime('%Y-%m-%d %H:%M:%S'),
            'timezone': 'America/Sao_Paulo'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cleanup_status_bp.route('/force-cleanup', methods=['POST'])
@jwt_required
def force_cleanup():
    """Força uma limpeza manual dos sinais"""
    return _execute_cleanup()

@cleanup_status_bp.route('/public-cleanup', methods=['POST'])
def public_cleanup():
    """Limpeza pública temporária (sem autenticação)"""
    return _execute_cleanup()

def _execute_cleanup():
    try:
        from core.database import Database
        from core.gerenciar_sinais import GerenciadorSinais
        
        # Inicializar gerenciador
        db = Database()
        gerenciador = GerenciadorSinais(db)
        
        # Executar limpeza baseada no horário atual
        tz = pytz.timezone('America/Sao_Paulo')
        now = datetime.now(tz)
        
        if now.hour < 15:  # Antes das 15h, fazer limpeza matinal
            gerenciador.limpar_sinais_antes_das_10h()
            cleanup_type = 'matinal'
        else:  # Após 15h, fazer limpeza noturna
            gerenciador.limpar_sinais_antes_das_21h()
            cleanup_type = 'noturna'
        
        # Registrar no log
        log_file = os.path.join(os.getcwd(), 'scheduler_log.txt')
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"MANUAL_CLEANUP_EXECUTED: {now.strftime('%Y-%m-%d %H:%M:%S')} - {cleanup_type}\n")
        
        return jsonify({
            'success': True,
            'message': f'Limpeza {cleanup_type} executada com sucesso',
            'timestamp': now.strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500