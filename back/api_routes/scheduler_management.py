# -*- coding: utf-8 -*-
"""
Gerenciamento do Scheduler de Limpeza de Sinais
Endpoints para diagnóstico, monitoramento e controle manual do sistema de limpeza
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import pytz
import os
import traceback
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler_management_bp = Blueprint('scheduler_management', __name__)

@scheduler_management_bp.route('/api/scheduler/status', methods=['GET'])
def get_detailed_scheduler_status():
    """
    Retorna status detalhado do sistema de limpeza de sinais
    Inclui informações sobre execuções, próximas limpezas e diagnósticos
    """
    try:
        from market_scheduler import get_scheduler_status, is_scheduler_running
        
        # Obter timezone de São Paulo
        tz = pytz.timezone('America/Sao_Paulo')
        now = datetime.now(tz)
        
        # Status básico do scheduler
        scheduler_status = get_scheduler_status()
        
        # Verificar arquivo de log
        log_file = os.path.join(os.getcwd(), 'scheduler_log.txt')
        log_exists = os.path.exists(log_file)
        last_execution = None
        
        if log_exists:
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        last_line = lines[-1].strip()
                        if ':' in last_line:
                            last_execution = last_line.split(': ')[1] if len(last_line.split(': ')) > 1 else None
            except Exception as e:
                logger.error(f"Erro ao ler log: {e}")
        
        # Calcular próximas execuções
        next_10am = now.replace(hour=10, minute=0, second=0, microsecond=0)
        next_9pm = now.replace(hour=21, minute=0, second=0, microsecond=0)
        
        if now.hour >= 21:
            next_10am += timedelta(days=1)
        elif now.hour >= 10:
            pass  # próximo 21:00 é hoje
        else:
            next_9pm = next_9pm  # próximo 21:00 é hoje
            
        if now.hour >= 21:
            next_9pm += timedelta(days=1)
        
        # Verificar se deveria ter executado
        should_have_run_10am = now.hour > 10 or (now.hour == 10 and now.minute > 0)
        should_have_run_9pm = now.hour > 21 or (now.hour == 21 and now.minute > 0)
        
        # Status detalhado
        detailed_status = {
            'scheduler_running': is_scheduler_running(),
            'current_time': now.strftime('%Y-%m-%d %H:%M:%S'),
            'timezone': 'America/Sao_Paulo',
            'log_file_exists': log_exists,
            'last_execution': last_execution,
            'next_executions': {
                'morning_cleanup': next_10am.strftime('%Y-%m-%d %H:%M:%S'),
                'evening_cleanup': next_9pm.strftime('%Y-%m-%d %H:%M:%S')
            },
            'execution_status': {
                'should_have_run_10am_today': should_have_run_10am,
                'should_have_run_9pm_today': should_have_run_9pm,
                'current_hour': now.hour
            },
            'scheduler_info': scheduler_status
        }
        
        return jsonify({
            'success': True,
            'status': detailed_status,
            'message': 'Status do scheduler obtido com sucesso'
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter status do scheduler: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erro ao obter status do scheduler'
        }), 500

@scheduler_management_bp.route('/api/scheduler/manual-cleanup', methods=['POST'])
def execute_manual_cleanup():
    """
    Executa limpeza manual de sinais
    Permite especificar o tipo de limpeza (morning, evening, ou both)
    """
    try:
        data = request.get_json() or {}
        cleanup_type = data.get('type', 'both')  # morning, evening, ou both
        
        # Importar dependências
        from core.database import Database
        from core.gerenciar_sinais import GerenciadorSinais
        
        # Inicializar componentes
        db = Database()
        gerenciador = GerenciadorSinais(db)
        
        results = []
        
        # Executar limpeza matinal
        if cleanup_type in ['morning', 'both']:
            try:
                logger.info("🌅 Executando limpeza matinal manual...")
                gerenciador.limpar_sinais_antes_das_10h()
                gerenciador.limpar_sinais_futuros()
                results.append({
                    'type': 'morning',
                    'success': True,
                    'message': 'Limpeza matinal executada com sucesso'
                })
            except Exception as e:
                results.append({
                    'type': 'morning',
                    'success': False,
                    'error': str(e)
                })
        
        # Executar limpeza noturna
        if cleanup_type in ['evening', 'both']:
            try:
                logger.info("🌙 Executando limpeza noturna manual...")
                gerenciador.limpar_sinais_antes_das_21h()
                gerenciador.limpar_sinais_futuros()
                results.append({
                    'type': 'evening',
                    'success': True,
                    'message': 'Limpeza noturna executada com sucesso'
                })
            except Exception as e:
                results.append({
                    'type': 'evening',
                    'success': False,
                    'error': str(e)
                })
        
        # Registrar execução manual no log
        log_file = os.path.join(os.getcwd(), 'scheduler_log.txt')
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"MANUAL_CLEANUP_EXECUTED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Type: {cleanup_type}\n")
        
        success_count = sum(1 for r in results if r['success'])
        total_count = len(results)
        
        return jsonify({
            'success': success_count == total_count,
            'results': results,
            'summary': f'{success_count}/{total_count} limpezas executadas com sucesso',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        logger.error(f"Erro na limpeza manual: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erro ao executar limpeza manual'
        }), 500

@scheduler_management_bp.route('/api/scheduler/restart', methods=['POST'])
def restart_scheduler():
    """
    Reinicia o scheduler de limpeza
    Útil quando o scheduler para de funcionar
    """
    try:
        from market_scheduler import restart_scheduler as restart_func
        from core.database import Database
        from core.gerenciar_sinais import GerenciadorSinais
        
        # Inicializar componentes
        db = Database()
        gerenciador = GerenciadorSinais(db)
        
        # Reiniciar scheduler
        scheduler_instance = restart_func(db, gerenciador)
        
        # Registrar restart no log
        log_file = os.path.join(os.getcwd(), 'scheduler_log.txt')
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"SCHEDULER_RESTARTED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        return jsonify({
            'success': True,
            'message': 'Scheduler reiniciado com sucesso',
            'scheduler_running': scheduler_instance.running if scheduler_instance else False,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        logger.error(f"Erro ao reiniciar scheduler: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erro ao reiniciar scheduler'
        }), 500

@scheduler_management_bp.route('/api/scheduler/logs', methods=['GET'])
def get_scheduler_logs():
    """
    Retorna os logs do scheduler
    Permite ver histórico de execuções e erros
    """
    try:
        log_file = os.path.join(os.getcwd(), 'scheduler_log.txt')
        
        if not os.path.exists(log_file):
            return jsonify({
                'success': True,
                'logs': [],
                'message': 'Arquivo de log não encontrado - scheduler pode não ter executado ainda'
            })
        
        # Ler últimas 50 linhas do log
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            recent_lines = lines[-50:] if len(lines) > 50 else lines
        
        # Processar logs
        processed_logs = []
        for line in recent_lines:
            line = line.strip()
            if line:
                processed_logs.append({
                    'timestamp': line.split(': ')[1] if ': ' in line else 'Unknown',
                    'type': line.split(': ')[0] if ': ' in line else 'Unknown',
                    'raw': line
                })
        
        return jsonify({
            'success': True,
            'logs': processed_logs,
            'total_lines': len(lines),
            'showing_recent': len(recent_lines),
            'log_file_path': log_file
        })
        
    except Exception as e:
        logger.error(f"Erro ao ler logs: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erro ao ler logs do scheduler'
        }), 500

@scheduler_management_bp.route('/api/scheduler/delete-signals', methods=['POST'])
def delete_signals_manually():
    """
    Deleta sinais manualmente do sistema
    Permite deletar todos os sinais ou sinais específicos por critérios
    """
    try:
        data = request.get_json() or {}
        delete_type = data.get('type', 'all')  # all, by_status, by_symbol, by_ids
        criteria = data.get('criteria', {})
        
        # Importar dependências
        from core.database import Database
        from core.gerenciar_sinais import GerenciadorSinais
        
        # Inicializar componentes
        db = Database()
        gerenciador = GerenciadorSinais(db)
        
        deleted_count = 0
        results = []
        
        if delete_type == 'all':
            # Deletar todos os sinais
            try:
                logger.info("🗑️ Deletando todos os sinais...")
                # Usar método do gerenciador para limpar todos os sinais
                import os
                import pandas as pd
                
                signals_file = gerenciador.signals_file
                if os.path.exists(signals_file):
                    df = pd.read_csv(signals_file)
                    deleted_count = len(df)
                    
                    # Criar DataFrame vazio com as mesmas colunas
                    empty_df = pd.DataFrame(columns=df.columns)
                    empty_df.to_csv(signals_file, index=False)
                    
                    results.append({
                        'type': 'all_signals',
                        'success': True,
                        'deleted_count': deleted_count,
                        'message': f'Todos os {deleted_count} sinais foram deletados'
                    })
                else:
                    results.append({
                        'type': 'all_signals',
                        'success': True,
                        'deleted_count': 0,
                        'message': 'Arquivo de sinais não encontrado - nenhum sinal para deletar'
                    })
                
                # Também deletar do Supabase
                try:
                    from supabase import create_client, Client
                    supabase_url = os.getenv('SUPABASE_URL')
                    supabase_key = os.getenv('SUPABASE_ANON_KEY')
                    
                    if supabase_url and supabase_key:
                        supabase: Client = create_client(supabase_url, supabase_key)
                        
                        # Buscar todos os sinais
                        all_signals = supabase.table('signals').select('id').execute()
                        supabase_count = len(all_signals.data)
                        
                        if supabase_count > 0:
                            # Deletar todos os sinais do Supabase
                            for signal in all_signals.data:
                                supabase.table('signals').delete().eq('id', signal['id']).execute()
                            
                            results.append({
                                'type': 'supabase_signals',
                                'success': True,
                                'deleted_count': supabase_count,
                                'message': f'Todos os {supabase_count} sinais foram deletados do Supabase'
                            })
                        else:
                            results.append({
                                'type': 'supabase_signals',
                                'success': True,
                                'deleted_count': 0,
                                'message': 'Nenhum sinal encontrado no Supabase'
                            })
                    else:
                        results.append({
                            'type': 'supabase_signals',
                            'success': False,
                            'deleted_count': 0,
                            'message': 'Supabase não configurado'
                        })
                except Exception as e:
                    results.append({
                        'type': 'supabase_signals',
                        'success': False,
                        'deleted_count': 0,
                        'message': f'Erro ao deletar do Supabase: {str(e)}'
                    })
                    
            except Exception as e:
                results.append({
                    'type': 'all_signals',
                    'success': False,
                    'error': str(e)
                })
        
        elif delete_type == 'by_status':
            # Deletar sinais por status (ex: OPEN, CLOSED)
            status = criteria.get('status', 'OPEN')
            try:
                logger.info(f"🗑️ Deletando sinais com status: {status}...")
                import os
                import pandas as pd
                
                signals_file = gerenciador.signals_file
                if os.path.exists(signals_file):
                    df = pd.read_csv(signals_file)
                    signals_to_delete = df[df['status'] == status]
                    deleted_count = len(signals_to_delete)
                    
                    # Manter apenas sinais que NÃO têm o status especificado
                    df_cleaned = df[df['status'] != status]
                    df_cleaned.to_csv(signals_file, index=False)
                    
                    results.append({
                        'type': 'by_status',
                        'success': True,
                        'deleted_count': deleted_count,
                        'criteria': {'status': status},
                        'message': f'{deleted_count} sinais com status "{status}" foram deletados'
                    })
                else:
                    results.append({
                        'type': 'by_status',
                        'success': True,
                        'deleted_count': 0,
                        'message': 'Arquivo de sinais não encontrado'
                    })
                    
            except Exception as e:
                results.append({
                    'type': 'by_status',
                    'success': False,
                    'error': str(e)
                })
        
        elif delete_type == 'by_symbol':
            # Deletar sinais de um símbolo específico
            symbol = criteria.get('symbol', '')
            if not symbol:
                return jsonify({
                    'success': False,
                    'error': 'Símbolo é obrigatório para deletar por símbolo',
                    'message': 'Parâmetro "symbol" não fornecido'
                }), 400
            
            try:
                logger.info(f"🗑️ Deletando sinais do símbolo: {symbol}...")
                import os
                import pandas as pd
                
                signals_file = gerenciador.signals_file
                if os.path.exists(signals_file):
                    df = pd.read_csv(signals_file)
                    signals_to_delete = df[df['symbol'] == symbol]
                    deleted_count = len(signals_to_delete)
                    
                    # Manter apenas sinais que NÃO são do símbolo especificado
                    df_cleaned = df[df['symbol'] != symbol]
                    df_cleaned.to_csv(signals_file, index=False)
                    
                    results.append({
                        'type': 'by_symbol',
                        'success': True,
                        'deleted_count': deleted_count,
                        'criteria': {'symbol': symbol},
                        'message': f'{deleted_count} sinais do símbolo "{symbol}" foram deletados'
                    })
                else:
                    results.append({
                        'type': 'by_symbol',
                        'success': True,
                        'deleted_count': 0,
                        'message': 'Arquivo de sinais não encontrado'
                    })
                    
            except Exception as e:
                results.append({
                    'type': 'by_symbol',
                    'success': False,
                    'error': str(e)
                })
        
        # Registrar operação no log
        log_file = os.path.join(os.getcwd(), 'scheduler_log.txt')
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"MANUAL_DELETE_EXECUTED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Type: {delete_type}, Deleted: {sum(r.get('deleted_count', 0) for r in results)}\n")
        
        success_count = sum(1 for r in results if r.get('success', False))
        total_deleted = sum(r.get('deleted_count', 0) for r in results)
        
        return jsonify({
            'success': success_count > 0,
            'results': results,
            'summary': f'{total_deleted} sinais deletados com sucesso',
            'delete_type': delete_type,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        logger.error(f"Erro na deleção manual de sinais: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erro ao deletar sinais manualmente'
        }), 500

@scheduler_management_bp.route('/api/scheduler/health-check', methods=['GET'])
def scheduler_health_check():
    """
    Verifica a saúde do sistema de limpeza
    Retorna diagnóstico completo e recomendações
    """
    try:
        from market_scheduler import is_scheduler_running
        
        tz = pytz.timezone('America/Sao_Paulo')
        now = datetime.now(tz)
        
        # Verificações de saúde
        health_checks = {
            'scheduler_running': is_scheduler_running(),
            'log_file_exists': os.path.exists(os.path.join(os.getcwd(), 'scheduler_log.txt')),
            'current_hour': now.hour,
            'timezone_correct': str(now.tzinfo) == 'America/Sao_Paulo'
        }
        
        # Determinar status geral
        critical_issues = []
        warnings = []
        
        if not health_checks['scheduler_running']:
            critical_issues.append('Scheduler não está rodando')
        
        if not health_checks['log_file_exists']:
            warnings.append('Arquivo de log não encontrado - pode indicar que o scheduler nunca executou')
        
        if not health_checks['timezone_correct']:
            critical_issues.append('Timezone incorreto - pode causar execução em horários errados')
        
        # Verificar se deveria ter executado hoje
        should_have_executed = []
        if now.hour > 10:
            should_have_executed.append('Limpeza matinal (10:00)')
        if now.hour > 21:
            should_have_executed.append('Limpeza noturna (21:00)')
        
        # Status geral
        if critical_issues:
            overall_status = 'CRITICAL'
        elif warnings:
            overall_status = 'WARNING'
        else:
            overall_status = 'HEALTHY'
        
        # Recomendações
        recommendations = []
        if not health_checks['scheduler_running']:
            recommendations.append('Execute POST /api/scheduler/restart para reiniciar o scheduler')
        if should_have_executed:
            recommendations.append(f'Execute POST /api/scheduler/manual-cleanup para executar limpezas pendentes: {", ".join(should_have_executed)}')
        if not health_checks['log_file_exists']:
            recommendations.append('Execute uma limpeza manual para criar o arquivo de log')
        
        return jsonify({
            'success': True,
            'overall_status': overall_status,
            'health_checks': health_checks,
            'critical_issues': critical_issues,
            'warnings': warnings,
            'should_have_executed_today': should_have_executed,
            'recommendations': recommendations,
            'timestamp': now.strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        return jsonify({
            'success': False,
            'overall_status': 'ERROR',
            'error': str(e),
            'message': 'Erro ao executar health check'
        }), 500

@scheduler_management_bp.route('/api/scheduler/restart-system-status', methods=['GET'])
def get_restart_system_status():
    """
    Retorna status específico do sistema de restart às 21:00
    Inclui informações detalhadas sobre o sistema de limpeza automática
    """
    try:
        from core.signal_cleanup import cleanup_system
        
        # Obter status detalhado do sistema
        status = cleanup_system.get_system_status()
        
        return jsonify({
            'status': 'success',
            'restart_system': status,
            'message': 'Status do sistema de restart obtido com sucesso'
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter status do sistema de restart: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Erro ao obter status do sistema de restart',
            'error': str(e)
        }), 500

@scheduler_management_bp.route('/api/scheduler/test-restart', methods=['POST'])
def test_restart_system():
    """
    Executa um teste do sistema de restart (para debug)
    ATENÇÃO: Isso executará a limpeza completa de sinais!
    """
    try:
        from core.signal_cleanup import cleanup_system
        
        # Verificar se é uma requisição autorizada (pode adicionar autenticação aqui)
        data = request.get_json() or {}
        confirm = data.get('confirm', False)
        
        if not confirm:
            return jsonify({
                'status': 'error',
                'message': 'Confirmação necessária. Envie {"confirm": true} para executar o teste.',
                'warning': 'ATENÇÃO: Isso executará a limpeza completa de sinais!'
            }), 400
        
        # Executar teste do sistema
        logger.info("🧪 Executando teste do sistema de restart...")
        cleanup_system.test_restart_system()
        
        return jsonify({
            'status': 'success',
            'message': 'Teste do sistema de restart executado com sucesso',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro no teste do sistema de restart: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Erro no teste do sistema de restart',
            'error': str(e)
        }), 500