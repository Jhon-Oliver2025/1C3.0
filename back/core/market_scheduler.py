from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import pytz
import logging
from typing import Optional
from .database import Database
from .technical_analysis import TechnicalAnalysis
from .gerenciar_sinais import GerenciadorSinais

class MarketScheduler:
    """Sistema de agendamento para operações de mercado"""
    
    def __init__(self, db_instance: Database, technical_analysis: TechnicalAnalysis):
        self.db = db_instance
        self.technical_analysis = technical_analysis
        self.gerenciador = GerenciadorSinais(db_instance)
        self.scheduler = BackgroundScheduler(timezone=pytz.timezone('America/Sao_Paulo'))
        self.logger = logging.getLogger(__name__)
        
        # Configurar jobs
        self._setup_scheduled_jobs()
    
    def _setup_scheduled_jobs(self):
        """Configura todos os jobs agendados"""
        
        # Job diário às 21:00 - Restart completo do sistema
        self.scheduler.add_job(
            func=self._daily_system_restart,
            trigger=CronTrigger(hour=21, minute=0),
            id='daily_system_restart',
            name='Restart Diário Completo do Sistema',
            replace_existing=True
        )
        
        print("✅ Job de restart agendado configurado:")
        print("   🔄 21:00 - Restart Diário Completo do Sistema")
        print("   🌍 Timezone: America/Sao_Paulo")
    
    def _daily_system_restart(self):
        """Restart completo do sistema às 21:00"""
        try:
            from datetime import datetime
            import pytz
            from .signal_cleanup import cleanup_system
            
            # Obter horário de São Paulo
            tz = pytz.timezone('America/Sao_Paulo')
            now = datetime.now(tz)
            
            print("\n" + "="*80)
            print(f"🔄 RESTART DIÁRIO DO SISTEMA - {now.strftime('%d/%m/%Y %H:%M:%S')}")
            print("🌙 REINÍCIO COMPLETO PARA NOVA SESSÃO DE TRADING")
            print("="*80)
            
            # 1. Executar restart completo via sistema de limpeza
            print("🧹 Executando restart completo do sistema...")
            cleanup_system.daily_system_restart()
            
            # 2. Atualizar lista de pares top 100
            print("📊 Atualizando lista de top 100 pares por volume...")
            try:
                self.technical_analysis._create_top_pairs()
                print("✅ Lista de pares atualizada com sucesso")
            except Exception as e:
                print(f"⚠️ Erro ao atualizar lista de pares: {e}")
            
            # 3. Executar varredura completa pós-restart
            print("🔍 Executando varredura completa pós-restart...")
            signals = self.technical_analysis.scan_market(verbose=True)
            
            if signals:
                print(f"\n🎯 RESULTADO DA VARREDURA PÓS-RESTART:")
                print(f"✨ {len(signals)} novos sinais encontrados!")
                for signal in signals:
                    print(f"   • {signal['symbol']}: {signal['type']} - {signal['signal_class']} (Score: {signal['quality_score']:.1f})")
            else:
                print("\n📊 Nenhum sinal de qualidade encontrado na varredura pós-restart")
            
            print(f"\n🌍 Sistema preparado para nova sessão de trading global")
            print(f"⏰ Próximo restart: {cleanup_system.get_next_restart_time()}")
            print("✅ Restart diário concluído com sucesso!")
            print("="*80)
            
        except Exception as e:
            self.logger.error(f"Erro no restart diário: {e}")
            print(f"❌ Erro no restart diário: {e}")
    
    # Método _cleanup_old_signals removido - não é mais necessário
    
    def start(self):
        """Inicia o agendador"""
        if not self.scheduler.running:
            self.scheduler.start()
            print("🚀 Sistema de agendamento iniciado!")
            
            # Mostrar próximos jobs
            jobs = self.scheduler.get_jobs()
            if jobs:
                print("\n📅 Próximos jobs agendados:")
                for job in jobs:
                    next_run = job.next_run_time
                    if next_run:
                        print(f"   ⏰ {job.name}: {next_run.strftime('%d/%m/%Y %H:%M:%S')}")
    
    def stop(self):
        """Para o agendador"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            print("🛑 Sistema de agendamento parado!")
    
    def get_next_market_times(self) -> dict:
        """Retorna os próximos horários de abertura dos mercados"""
        now = datetime.now(pytz.timezone('America/Sao_Paulo'))
        
        # Próximo horário New York (10:30)
        ny_time = now.replace(hour=10, minute=30, second=0, microsecond=0)
        if now >= ny_time:
            ny_time += timedelta(days=1)
        
        # Próximo horário ÁSIA (21:30)
        asia_time = now.replace(hour=21, minute=30, second=0, microsecond=0)
        if now >= asia_time:
            asia_time += timedelta(days=1)
        
        return {
            'new_york_countdown': int((ny_time - now).total_seconds()),
            'asia_countdown': int((asia_time - now).total_seconds()),
            'new_york_time': ny_time.strftime('%d/%m/%Y %H:%M:%S'),
            'asia_time': asia_time.strftime('%d/%m/%Y %H:%M:%S')
        }