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
        
        # Job diário às 10:00 - Atualização geral do sistema
        self.scheduler.add_job(
            func=self._daily_system_update,
            trigger=CronTrigger(hour=10, minute=0),
            id='daily_system_update',
            name='Atualização Diária do Sistema',
            replace_existing=True
        )
        
        # Job diário às 21:00 - Preparação para mercados asiáticos
        self.scheduler.add_job(
            func=self._asian_market_preparation,
            trigger=CronTrigger(hour=21, minute=0),
            id='asian_market_prep',
            name='Preparação Mercados Asiáticos',
            replace_existing=True
        )
        
        print("✅ Jobs agendados configurados:")
        print("   📅 10:00 - Atualização geral do sistema")
        print("   📅 21:00 - Preparação mercados asiáticos")
        # Remover esta linha: print("   📅 00:00 - Limpeza de sinais antigos")
    
    def _daily_system_update(self):
        """Atualização geral do sistema às 10:00"""
        try:
            print("\n" + "="*70)
            print("🌅 INICIANDO ATUALIZAÇÃO DIÁRIA DO SISTEMA - 10:00")
            print("="*70)
            
            # 1. Limpar sinais antigos (antes das 10:00)
            print("🧹 Limpando sinais antigos...")
            self.gerenciador.limpar_sinais_antes_das_10h()
            
            # 2. Atualizar lista de pares top 100
            print("📊 Atualizando lista de top 100 pares...")
            self.technical_analysis._update_pairs_list()
            
            # 3. Executar varredura completa
            print("🔍 Executando varredura completa do mercado...")
            signals = self.technical_analysis.scan_market(verbose=True)
            
            if signals:
                print(f"✨ {len(signals)} novos sinais encontrados na varredura matinal!")
            else:
                print("📊 Nenhum sinal encontrado na varredura matinal")
            
            print("✅ Atualização diária concluída com sucesso!")
            print("="*70)
            
        except Exception as e:
            self.logger.error(f"Erro na atualização diária: {e}")
            print(f"❌ Erro na atualização diária: {e}")
    
    def _asian_market_preparation(self):
        """Preparação para abertura dos mercados asiáticos às 21:00"""
        try:
            print("\n" + "="*70)
            print("🌏 PREPARAÇÃO PARA MERCADOS ASIÁTICOS - 21:00")
            print("="*70)
            
            # 1. Limpar sinais antigos (antes das 21:00)
            print("🧹 Limpando sinais antigos...")
            self.gerenciador.limpar_sinais_antes_das_21h()
            
            # 2. Executar varredura focada em pares asiáticos
            print("🔍 Executando varredura para mercados asiáticos...")
            signals = self.technical_analysis.scan_market(verbose=True)
            
            if signals:
                print(f"✨ {len(signals)} sinais encontrados para sessão asiática!")
            else:
                print("📊 Nenhum sinal encontrado para sessão asiática")
            
            print("✅ Preparação para mercados asiáticos concluída!")
            print("="*70)
            
        except Exception as e:
            self.logger.error(f"Erro na preparação asiática: {e}")
            print(f"❌ Erro na preparação asiática: {e}")
    
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
        
        # Próximo horário USA (10:30)
        usa_time = now.replace(hour=10, minute=30, second=0, microsecond=0)
        if now >= usa_time:
            usa_time += timedelta(days=1)
        
        # Próximo horário ÁSIA (21:00)
        asia_time = now.replace(hour=21, minute=0, second=0, microsecond=0)
        if now >= asia_time:
            asia_time += timedelta(days=1)
        
        return {
            'usa_countdown': int((usa_time - now).total_seconds()),
            'asia_countdown': int((asia_time - now).total_seconds()),
            'usa_time': usa_time.strftime('%d/%m/%Y %H:%M:%S'),
            'asia_time': asia_time.strftime('%d/%m/%Y %H:%M:%S')
        }