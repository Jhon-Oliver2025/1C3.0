from apscheduler.schedulers.background import BackgroundScheduler
from core.gerenciar_sinais import GerenciadorSinais
from core.database import Database
from datetime import datetime
import atexit
import logging
import pytz

# Configurar logging para o agendador
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_market_scheduler(db_instance=None, gerenciador_sinais=None):
    """Configura o agendador de tarefas do mercado com limpezas automáticas"""
    # Configurar timezone para São Paulo (UTC-3)
    timezone = pytz.timezone('America/Sao_Paulo')
    scheduler = BackgroundScheduler(timezone=timezone)
    
    # Usar instâncias passadas ou criar novas
    if db_instance is None:
        db_instance = Database()
    if gerenciador_sinais is None:
        gerenciador = GerenciadorSinais(db_instance)
    else:
        gerenciador = gerenciador_sinais
    
    # === LIMPEZA MATINAL ÀS 10:00 ===
    scheduler.add_job(
        func=lambda: execute_morning_cleanup(gerenciador),
        trigger="cron",
        hour=10,
        minute=0,
        timezone=timezone,
        id='morning_cleanup',
        name='Limpeza Matinal - 10:00'
    )
    
    # === LIMPEZA NOTURNA ÀS 21:00 ===
    scheduler.add_job(
        func=lambda: execute_evening_cleanup(gerenciador),
        trigger="cron",
        hour=21,
        minute=0,
        timezone=timezone,
        id='evening_cleanup',
        name='Limpeza Noturna - 21:00'
    )
    
    # REMOVIDO: Job de manutenção à meia-noite (00:00)
    
    logger.info("🕐 Agendador de mercado configurado com sucesso!")
    logger.info("📅 Limpezas programadas:")
    logger.info("   • 10:00 - Limpeza matinal (pré-mercado USA)")
    logger.info("   • 21:00 - Limpeza noturna (pré-mercado ÁSIA)")
    # REMOVIDO: logger.info("   • 00:00 - Manutenção geral")
    
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
    
    return scheduler

def execute_morning_cleanup(gerenciador):
    """Executa limpeza matinal às 10:00 - Preparação para mercado USA"""
    try:
        logger.info("🌅 === INICIANDO LIMPEZA MATINAL (10:00) ===")
        
        # 1. Limpar sinais antigos (antes das 10:00)
        logger.info("🧹 Limpando sinais antes das 10:00...")
        gerenciador.limpar_sinais_antes_das_10h()
        
        # 2. Limpar sinais com datas futuras (erro de sistema)
        logger.info("🔮 Limpando sinais com datas futuras...")
        gerenciador.limpar_sinais_futuros()
        
        logger.info("✅ Limpeza matinal concluída com sucesso!")
        logger.info("🇺🇸 Sistema preparado para abertura do mercado americano (10:30)")
        
    except Exception as e:
        logger.error(f"❌ Erro durante limpeza matinal: {e}")

def execute_evening_cleanup(gerenciador):
    """Executa limpeza noturna às 21:00 - Preparação para mercado ÁSIA"""
    try:
        logger.info("🌙 === INICIANDO LIMPEZA NOTURNA (21:00) ===")
        
        # 1. Limpar sinais antigos (antes das 21:00)
        logger.info("🧹 Limpando sinais antes das 21:00...")
        gerenciador.limpar_sinais_antes_das_21h()
        
        # 2. Verificar e limpar sinais com problemas
        logger.info("🔍 Verificando sinais com problemas...")
        gerenciador.limpar_sinais_futuros()
        
        logger.info("✅ Limpeza noturna concluída com sucesso!")
        logger.info("🌏 Sistema preparado para abertura do mercado asiático (21:00)")
        
    except Exception as e:
        logger.error(f"❌ Erro durante limpeza noturna: {e}")

# REMOVIDO: Função execute_midnight_maintenance

def generate_daily_stats(gerenciador):
    """Gera estatísticas diárias dos sinais"""
    try:
        # Obter sinais do dia
        signals_df = gerenciador.processar_sinais_abertos()
        
        if not signals_df.empty:
            total_signals = len(signals_df)
            long_signals = len(signals_df[signals_df['type'] == 'LONG'])
            short_signals = len(signals_df[signals_df['type'] == 'SHORT'])
            
            logger.info(f"📈 Estatísticas do dia:")
            logger.info(f"   • Total de sinais: {total_signals}")
            logger.info(f"   • Sinais LONG: {long_signals}")
            logger.info(f"   • Sinais SHORT: {short_signals}")
        else:
            logger.info("📭 Nenhum sinal ativo encontrado")
            
    except Exception as e:
        logger.error(f"❌ Erro ao gerar estatísticas: {e}")

def get_scheduler_status():
    """Retorna o status do agendador para monitoramento"""
    from datetime import datetime
    import pytz
    
    # Obter timezone de São Paulo
    tz = pytz.timezone('America/Sao_Paulo')
    now = datetime.now(tz)
    
    return {
        'morning_cleanup': '10:00 - Limpeza matinal (pré-mercado USA)',
        'evening_cleanup': '21:00 - Limpeza noturna (pré-mercado ÁSIA)',
        'status': 'active',
        'timezone': 'America/Sao_Paulo',
        'current_hour': now.hour,
        'current_minute': now.minute,
        'last_check': now.strftime('%Y-%m-%d %H:%M:%S'),
        'jobs_configured': [
            {'id': 'morning_cleanup', 'time': '10:00', 'description': 'Limpeza matinal'},
            {'id': 'evening_cleanup', 'time': '21:00', 'description': 'Limpeza noturna'}
        ]
    }