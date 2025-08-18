from flask import Blueprint, request, jsonify, current_app, g
import csv
import os
import threading
import time
from datetime import datetime

from flask import Blueprint, jsonify, g, current_app
from middleware.auth_middleware import jwt_required

def get_btc_confirmed_signals():
    """Função para obter sinais confirmados do sistema BTC e converter para o formato dos cards"""
    current_app.logger.debug("🔍 Iniciando get_btc_confirmed_signals()")
    try:
        # Obter instância do BTCSignalManager do app
        bot_instance = getattr(current_app, 'bot_instance', None)
        current_app.logger.debug(f"Bot instance: {bot_instance}")
        
        if not bot_instance:
            current_app.logger.debug("Bot instance não encontrada")
            return []
            
        current_app.logger.debug(f"Bot instance attributes: {dir(bot_instance)}")
        
        if not hasattr(bot_instance, 'btc_signal_manager'):
            current_app.logger.debug("BTCSignalManager attribute não encontrado")
            return []
        
        btc_signal_manager = bot_instance.btc_signal_manager
        current_app.logger.debug(f"BTCSignalManager: {btc_signal_manager}")
        
        if not btc_signal_manager:
            current_app.logger.debug("BTCSignalManager não inicializado")
            return []
        
        # Obter sinais confirmados do sistema BTC
        confirmed_signals = btc_signal_manager.get_confirmed_signals(limit=20)
        
        # Converter para o formato esperado pelos cards do dashboard
        btc_signals = []
        for signal in confirmed_signals:
            # Converter tipo de COMPRA/VENDA para LONG/SHORT
            signal_type = "LONG" if signal.get('type') == 'COMPRA' else "SHORT"
            
            # Converter sinal para formato dos cards
            btc_signal = {
                "symbol": signal.get('symbol', ''),
                "type": signal_type,
                "entry_price": float(signal.get('entry_price', 0)),
                "entry_time": signal.get('confirmed_at', signal.get('created_at', '')),
                "created_at": signal.get('created_at', ''),
                "confirmed_at": signal.get('confirmed_at', ''),
                "target_price": float(signal.get('target_price', 0)),
                "projection_percentage": round(float(signal.get('projection_percentage', 0)), 2),
                "status": "CONFIRMADO",
                "quality_score": round(float(signal.get('quality_score', 0)), 1),
                "signal_class": "BTC_CONFIRMED"
            }
            
            # Garantir que não há valores None
            for key, value in btc_signal.items():
                if value is None:
                    btc_signal[key] = '' if isinstance(value, str) else 0
            
            btc_signals.append(btc_signal)
        
        current_app.logger.debug(f"Sinais BTC confirmados convertidos: {len(btc_signals)}")
        return btc_signals
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter sinais BTC confirmados: {e}")
        return []

signals_bp = Blueprint('signals', __name__)

# Variável global para status da análise
analysis_status = {
    'running': False,
    'progress': 0,
    'total': 0,
    'current_symbol': '',
    'start_time': None,
    'errors': []
}

def get_signals_from_csv():
    """Função para ler sinais do arquivo CSV"""
    signals_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sinais_lista.csv')
    signals_list = []
    
    current_app.logger.debug(f"Tentando ler arquivo CSV: {signals_file}")
    current_app.logger.debug(f"Arquivo existe: {os.path.exists(signals_file)}")
    
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

@signals_bp.route('/', methods=['OPTIONS'])
def handle_options():
    return '', 200

@signals_bp.route('/', methods=['GET'])
@jwt_required
def get_signals():
    """Endpoint para obter APENAS os sinais confirmados do sistema BTC"""
    current_app.logger.debug("Rota /api/signals foi acessada!")
    try:
        # Acessa os dados do usuário do objeto g
        user_data = g.user_data
        
        # Obter APENAS sinais confirmados do sistema BTC
        btc_confirmed_signals = get_btc_confirmed_signals()
        
        # Ordenar por data de confirmação (mais recentes primeiro)
        btc_confirmed_signals.sort(key=lambda x: x.get('entry_time', ''), reverse=True)
        
        current_app.logger.debug(f"DEBUG: Retornando apenas sinais BTC confirmados: {len(btc_confirmed_signals)}")
        return jsonify(btc_confirmed_signals), 200

    except Exception as e:
        current_app.logger.error(f"Erro ao obter sinais confirmados: {e}", exc_info=True)
        return jsonify({"error": "Erro interno do servidor ao obter sinais confirmados"}), 500

@signals_bp.route('/start-analysis', methods=['POST'])
@jwt_required
def start_analysis():
    """Inicia análise assíncrona de criptomoedas"""
    global analysis_status
    
    if analysis_status['running']:
        return jsonify({
            'success': False,
            'message': 'Análise já está em execução'
        }), 400
    
    # Iniciar análise em thread separada
    thread = threading.Thread(target=run_crypto_analysis)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'message': 'Análise iniciada com sucesso'
    })

@signals_bp.route('/analysis-status', methods=['GET'])
@jwt_required
def get_analysis_status():
    """Retorna status da análise em tempo real"""
    return jsonify(analysis_status)

@signals_bp.route('/stop-analysis', methods=['POST'])
@jwt_required
def stop_analysis():
    """Para a análise em execução"""
    global analysis_status
    analysis_status['running'] = False
    
    return jsonify({
        'success': True,
        'message': 'Análise interrompida'
    })

def run_crypto_analysis():
    """Executa análise de criptomoedas em background"""
    global analysis_status
    
    try:
        analysis_status.update({
            'running': True,
            'progress': 0,
            'total': 100,
            'start_time': datetime.now().isoformat(),
            'errors': []
        })
        
        # Aqui você pode integrar com sua lógica real de análise
        # Por exemplo, chamar o BinanceClient e TechnicalAnalysis
        
        for i in range(100):
            if not analysis_status['running']:  # Permitir cancelamento
                break
                
            analysis_status.update({
                'progress': i + 1,
                'current_symbol': f'SYMBOL{i+1}USDT'
            })
            
            # Simular processamento (substituir pela lógica real)
            time.sleep(0.1)
            
    except Exception as e:
        analysis_status['errors'].append(str(e))
        current_app.logger.error(f"Erro na análise: {e}")
    finally:
        analysis_status['running'] = False