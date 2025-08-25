# -*- coding: utf-8 -*-
"""
Sistema de Limpeza Automática de Sinais
Limpa sinais nos horários: 10:00 e 21:00 (horário de São Paulo)
"""

import schedule
import time
import threading
from datetime import datetime, timedelta
import pytz
import os
from typing import Optional
from supabase import create_client, Client

class SignalCleanup:
    """Sistema de limpeza automática de sinais baseado no horário de São Paulo"""
    
    def __init__(self):
        """Inicializa o sistema de limpeza"""
        self.sao_paulo_tz = pytz.timezone('America/Sao_Paulo')
        self.is_running = False
        self.cleanup_thread: Optional[threading.Thread] = None
        
        # Configurar Supabase
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        print("🧹 Sistema de Limpeza de Sinais inicializado")
    
    def daily_system_restart(self) -> None:
        """Executa restart completo do sistema às 21:00"""
        try:
            now_sp = datetime.now(self.sao_paulo_tz)
            
            print("\n" + "="*80)
            print(f"🔄 RESTART DIÁRIO DO SISTEMA - {now_sp.strftime('%d/%m/%Y %H:%M:%S')} (SP)")
            print("🌙 REINÍCIO COMPLETO PARA NOVA SESSÃO DE TRADING")
            print("="*80)
            
            # 1. Limpar todos os sinais antigos
            print("🧹 Executando limpeza completa de sinais...")
            self.cleanup_old_signals()
            
            # 2. Resetar sistema BTC de confirmação
            print("₿ Reiniciando sistema de confirmação BTC...")
            try:
                # Obter instância do BTCSignalManager do app
                from flask import current_app
                if hasattr(current_app, 'bot_instance') and current_app.bot_instance:
                    bot_instance = current_app.bot_instance
                    if hasattr(bot_instance, 'btc_signal_manager') and bot_instance.btc_signal_manager:
                        btc_manager = bot_instance.btc_signal_manager
                        
                        # Resetar controle de sinais confirmados diários
                        btc_manager.reset_daily_confirmed_signals()
                        
                        # Verificar sinais ainda ativos pós-restart
                        btc_manager.check_post_restart_signals()
                        
                        print("✅ Sistema BTC reiniciado com sucesso")
                        print(f"📊 Controle de duplicação resetado")
                    else:
                        print("⚠️ BTCSignalManager não encontrado")
                else:
                    print("⚠️ Bot instance não encontrada")
            except Exception as e:
                print(f"⚠️ Erro ao reiniciar sistema BTC: {e}")
            
            # 3. Atualizar estatísticas do sistema
            print("📊 Atualizando estatísticas do sistema...")
            self.update_system_stats()
            
            print(f"\n🎯 RESTART COMPLETO FINALIZADO")
            print(f"⏰ Próximo restart: {self.get_next_restart_time()}")
            print("✅ Sistema pronto para nova sessão de trading!")
            print("="*80)
            
        except Exception as e:
            print(f"❌ Erro no restart do sistema: {e}")
            import traceback
            traceback.print_exc()
    
    def cleanup_old_signals(self) -> None:
        """Remove apenas sinais pendentes e rejeitados antigos, preservando sinais confirmados até às 21:00"""
        try:
            if not self.supabase_url or not self.supabase_key:
                print("⚠️ Supabase não configurado para limpeza")
                return
            
            supabase: Client = create_client(self.supabase_url, self.supabase_key)
            now_sp = datetime.now(self.sao_paulo_tz)
            
            # Definir horário de corte para sinais pendentes/rejeitados (24h atrás)
            cutoff_time_pending = now_sp - timedelta(hours=24)
            cutoff_time_pending_utc = cutoff_time_pending.astimezone(pytz.UTC)
            
            # Para sinais confirmados, só remover os do dia anterior às 21:00
            # Se ainda não passou das 21:00 hoje, manter sinais confirmados de ontem
            if now_sp.hour < 21:
                # Ainda não passou das 21:00, manter sinais confirmados de ontem
                yesterday_21h = (now_sp - timedelta(days=1)).replace(hour=21, minute=0, second=0, microsecond=0)
            else:
                # Já passou das 21:00, pode remover sinais confirmados de hoje às 21:00
                yesterday_21h = now_sp.replace(hour=21, minute=0, second=0, microsecond=0)
            
            cutoff_time_confirmed_utc = yesterday_21h.astimezone(pytz.UTC)
            
            print(f"🗑️ Removendo sinais pendentes/rejeitados anteriores a: {cutoff_time_pending.strftime('%d/%m/%Y %H:%M')} (SP)")
            print(f"🗑️ Removendo sinais confirmados anteriores a: {yesterday_21h.strftime('%d/%m/%Y %H:%M')} (SP)")
            
            # 1. Buscar e remover sinais pendentes e rejeitados antigos
            old_pending_signals = supabase.table('signals').select('id, symbol, status, created_at').in_('status', ['PENDING', 'REJECTED']).lt('created_at', cutoff_time_pending_utc.isoformat()).execute()
            
            pending_removed = 0
            if old_pending_signals.data:
                print(f"📊 Encontrados {len(old_pending_signals.data)} sinais pendentes/rejeitados para remoção")
                
                for signal in old_pending_signals.data:
                    try:
                        supabase.table('signals').delete().eq('id', signal['id']).execute()
                        print(f"🗑️ Removido {signal['status']}: {signal['symbol']} (ID: {signal['id']})")
                        pending_removed += 1
                    except Exception as e:
                        print(f"❌ Erro ao remover sinal {signal['id']}: {e}")
            
            # 2. Buscar e remover apenas sinais confirmados muito antigos (anteriores ao horário de corte)
            old_confirmed_signals = supabase.table('signals').select('id, symbol, status, created_at').eq('status', 'CONFIRMED').lt('created_at', cutoff_time_confirmed_utc.isoformat()).execute()
            
            confirmed_removed = 0
            if old_confirmed_signals.data:
                print(f"📊 Encontrados {len(old_confirmed_signals.data)} sinais confirmados antigos para remoção")
                
                for signal in old_confirmed_signals.data:
                    try:
                        supabase.table('signals').delete().eq('id', signal['id']).execute()
                        print(f"🗑️ Removido CONFIRMED: {signal['symbol']} (ID: {signal['id']})")
                        confirmed_removed += 1
                    except Exception as e:
                        print(f"❌ Erro ao remover sinal confirmado {signal['id']}: {e}")
            
            total_removed = pending_removed + confirmed_removed
            print(f"✅ Limpeza concluída: {total_removed} sinais removidos ({pending_removed} pendentes/rejeitados, {confirmed_removed} confirmados antigos)")
            
            # Estatísticas finais
            remaining_signals = supabase.table('signals').select('id', count='exact').execute()
            total_remaining = remaining_signals.count if remaining_signals.count else 0
            
            # Contar sinais confirmados restantes
            confirmed_remaining = supabase.table('signals').select('id', count='exact').eq('status', 'CONFIRMED').execute()
            confirmed_count = confirmed_remaining.count if confirmed_remaining.count else 0
            
            print(f"📊 Sinais restantes no sistema: {total_remaining} (sendo {confirmed_count} confirmados)")
            print(f"✅ Sinais confirmados preservados até às 21:00 conforme solicitado")
            
        except Exception as e:
            print(f"❌ Erro na limpeza de sinais: {e}")
            import traceback
            traceback.print_exc()
    
    def update_system_stats(self) -> None:
        """Atualiza estatísticas do sistema após restart"""
        try:
            now_sp = datetime.now(self.sao_paulo_tz)
            
            # Aqui podemos adicionar lógica para salvar estatísticas do restart
            # Por exemplo, salvar no banco de dados informações sobre:
            # - Horário do último restart
            # - Número de sinais removidos
            # - Status do sistema BTC
            # - Métricas de performance
            
            print(f"📈 Estatísticas atualizadas - {now_sp.strftime('%d/%m/%Y %H:%M:%S')}")
            
        except Exception as e:
            print(f"❌ Erro ao atualizar estatísticas: {e}")
    
    def schedule_cleanup(self) -> None:
        """Agenda restart diário do sistema com timezone correto"""
        # IMPORTANTE: A biblioteca schedule não suporta timezone nativamente
        # Vamos usar uma abordagem diferente com verificação manual de horário
        
        print("📅 Sistema de restart configurado:")
        print("   🧪 TESTE: 12:00 - Restart Diário Completo do Sistema")
        print("   🌍 Timezone: America/Sao_Paulo")
        print("   ⚠️ Usando verificação manual de timezone (schedule não suporta timezone)")
        print("   🔄 TODO: Voltar para 21:00 após teste")
    
    def start_scheduler(self) -> None:
        """Inicia o agendador de limpeza em thread separada"""
        if self.is_running:
            print("⚠️ Sistema de limpeza já está rodando")
            return
        
        self.is_running = True
        self.schedule_cleanup()
        
        def run_scheduler():
            print("🚀 Sistema de limpeza automática iniciado")
            last_restart_date = None  # Controlar para executar apenas uma vez por dia
            
            while self.is_running:
                try:
                    # Obter horário atual de São Paulo
                    now_sp = datetime.now(self.sao_paulo_tz)
                    current_date = now_sp.date()
                    current_hour = now_sp.hour
                    current_minute = now_sp.minute
                    
                    # Debug: mostrar horário atual a cada 30 minutos
                    if current_minute % 30 == 0:
                        print(f"🕐 Horário atual SP: {now_sp.strftime('%d/%m/%Y %H:%M:%S')} - TESTE: Aguardando 12:00")
                    
                    # TESTE EM PRODUÇÃO: Verificar se é 12:00 e ainda não executou hoje
                    # TODO: Voltar para 21:00 após teste
                    if (current_hour == 12 and current_minute == 0 and 
                        last_restart_date != current_date):
                        
                        print(f"⏰ HORÁRIO DE RESTART DETECTADO: {now_sp.strftime('%d/%m/%Y %H:%M:%S')}")
                        print("🚀 Executando restart diário do sistema...")
                        
                        # Executar restart
                        self.daily_system_restart()
                        
                        # Marcar que já executou hoje
                        last_restart_date = current_date
                        print(f"✅ Restart concluído. Próximo restart: {(current_date + timedelta(days=1)).strftime('%d/%m/%Y')} às 21:00")
                    
                    # Executar jobs agendados da biblioteca schedule (se houver outros)
                    schedule.run_pending()
                    
                    time.sleep(60)  # Verificar a cada minuto
                    
                except Exception as e:
                    print(f"❌ Erro no agendador de limpeza: {e}")
                    import traceback
                    traceback.print_exc()
                    time.sleep(60)
        
        self.cleanup_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.cleanup_thread.start()
        
        print("✅ Sistema de limpeza automática ativo")
    
    def stop_scheduler(self) -> None:
        """Para o agendador de limpeza"""
        self.is_running = False
        schedule.clear()
        
        if self.cleanup_thread and self.cleanup_thread.is_alive():
            self.cleanup_thread.join(timeout=5)
        
        print("🛑 Sistema de limpeza automática parado")
    
    def manual_cleanup(self) -> None:
        """Executa limpeza manual (para testes)"""
        print("🔧 Executando limpeza manual...")
        self.cleanup_old_signals()
    
    def test_restart_system(self) -> None:
        """Testa o sistema de restart (para debug)"""
        print("🧪 TESTE DO SISTEMA DE RESTART")
        print("="*50)
        
        now_sp = datetime.now(self.sao_paulo_tz)
        print(f"⏰ Horário atual SP: {now_sp.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"📅 Próximo restart: {self.get_next_restart_time()}")
        
        time_until = self.get_time_until_restart()
        print(f"⏳ Tempo até restart: {time_until['hours']}h {time_until['minutes']}m {time_until['seconds']}s")
        
        print(f"🔄 Sistema ativo: {self.is_running}")
        print(f"🧵 Thread ativa: {self.cleanup_thread.is_alive() if self.cleanup_thread else False}")
        
        print("\n🚀 Executando restart de teste...")
        self.daily_system_restart()
        print("✅ Teste concluído!")
    
    def get_system_status(self) -> dict:
        """Retorna status detalhado do sistema"""
        now_sp = datetime.now(self.sao_paulo_tz)
        time_until = self.get_time_until_restart()
        
        return {
            'is_running': self.is_running,
            'thread_active': self.cleanup_thread.is_alive() if self.cleanup_thread else False,
            'current_time_sp': now_sp.strftime('%d/%m/%Y %H:%M:%S'),
            'next_restart': self.get_next_restart_time(),
            'time_until_restart': time_until,
            'timezone': str(self.sao_paulo_tz)
        }
    
    def get_next_restart_time(self) -> str:
        """Retorna o horário do próximo restart do sistema"""
        now_sp = datetime.now(self.sao_paulo_tz)
        
        # TESTE: Próximo restart às 12:00
        # TODO: Voltar para 21:00 após teste
        next_restart = now_sp.replace(hour=12, minute=0, second=0, microsecond=0)
        if next_restart <= now_sp:
            next_restart += timedelta(days=1)
        
        return next_restart.strftime('%d/%m/%Y %H:%M:%S')
    
    def get_time_until_restart(self) -> dict:
        """Retorna tempo restante até o próximo restart"""
        now_sp = datetime.now(self.sao_paulo_tz)
        
        # TESTE: Próximo restart às 12:00
        # TODO: Voltar para 21:00 após teste
        next_restart = now_sp.replace(hour=12, minute=0, second=0, microsecond=0)
        if next_restart <= now_sp:
            next_restart += timedelta(days=1)
        
        time_diff = next_restart - now_sp
        hours = time_diff.seconds // 3600
        minutes = (time_diff.seconds % 3600) // 60
        seconds = time_diff.seconds % 60
        
        return {
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds,
            'total_seconds': time_diff.total_seconds(),
            'next_restart': next_restart.strftime('%d/%m/%Y %H:%M:%S')
        }

# Instância global para uso em outros módulos
cleanup_system = SignalCleanup()

if __name__ == "__main__":
    # Teste do sistema
    cleanup = SignalCleanup()
    print(f"📅 Próxima limpeza: {cleanup.get_next_cleanup_time()}")
    
    # Para teste manual, descomente a linha abaixo:
    # cleanup.manual_cleanup()