from flask import Blueprint, request, jsonify, current_app, g
import csv
import os
from middleware.auth_middleware import jwt_required

signals_bp = Blueprint('signals', __name__)

def get_signals_from_csv():
    """Função para ler sinais do arquivo CSV"""
    signals_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sinais_lista.csv')
    signals_list = []
    
    try:
        with open(signals_file, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            row_count = 0
            
            for row in csv_reader:
                row_count += 1
                
                # Initialize variables with default values
                entry_price = 0.0
                target_price = 0.0
                change_percentage = 0.0
                
                try:
                    entry_price = float(row.get('entry_price', 0))
                    target_price = float(row.get('target_price', 0))
                    
                    if entry_price != 0:
                        change_percentage = ((target_price / entry_price) - 1) * 100
                except (ValueError, ZeroDivisionError):
                    pass
                
                # Usar a classificação que já existe no CSV
                signal_class = row.get('signal_class', '')
                
                # Só incluir sinais PREMIUM e ELITE
                if signal_class not in ['PREMIUM', 'ELITE']:
                    continue
                
                signal_type = "LONG" if row.get('type') == 'COMPRA' else "SHORT"
                
                # Create signal object
                signal_obj = {
                    "symbol": row.get('symbol', ''),
                    "type": signal_type,
                    "entry_price": entry_price,
                    "entry_time": row.get('entry_time', ''),
                    "target_price": target_price,
                    "projection_percentage": round(change_percentage, 2),
                    "status": row.get('status', ''),
                    "quality_score": round(float(row.get('projection_percentage', 0)), 1),  # Usar projeção como score
                    "signal_class": signal_class
                }
                
                # Ensure no undefined values
                for key, value in signal_obj.items():
                    if value is None:
                        signal_obj[key] = ''
                
                signals_list.append(signal_obj)
    
        # Sort by entry_time
        signals_list.sort(key=lambda x: x['entry_time'], reverse=True)
        current_app.logger.debug(f"Processed {row_count} signals successfully")
        
        return signals_list

    except Exception as e:
        current_app.logger.error(f"Error reading CSV: {str(e)}", exc_info=True)
        return []

@signals_bp.route('/', methods=['GET'])
@jwt_required
def get_signals():
    """Endpoint para obter a lista de sinais do arquivo CSV"""
    current_app.logger.debug("Rota /api/signals foi acessada!")
    try:
        # Acessa os dados do usuário do objeto g
        user_data = g.user_data
        
        # Verificar se o usuário é admin para ver sinais premium
        is_admin = user_data.get('isAdmin', False)

        # Obter sinais do CSV
        all_signals = get_signals_from_csv()
        
        # Retornar todos os sinais (temporariamente para depuração)
        signals_to_return = all_signals

        current_app.logger.debug(f"DEBUG: Sinais antes de jsonify: {len(signals_to_return)}")
        return jsonify(signals_to_return), 200

    except Exception as e:
        current_app.logger.error(f"Erro ao obter sinais: {e}", exc_info=True)
        return jsonify({"error": "Erro interno do servidor ao obter sinais"}), 500