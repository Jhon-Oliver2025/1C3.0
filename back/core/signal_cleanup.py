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
    
    def cleanup_old_signals(self) -> None:
        """Remove sinais antigos do banco de dados"""
        try:
            if not self.supabase_url or not self.supabase_key:
                print("⚠️ Supabase não configurado para limpeza")
                return
            
            supabase: Client = create_client(self.supabase_url, self.supabase_key)
            now_sp = datetime.now(self.sao_paulo_tz)
            
            print(f"🧹 Iniciando limpeza de sinais - {now_sp.strftime('%d/%m/%Y %H:%M:%S')} (SP)")
            
            # Determinar horário de corte baseado no horário atual
            if now_sp.hour == 10:
                # Limpeza das 10:00 - remover sinais desde a última limpeza (21:00 de ontem)
                yesterday = now_sp - timedelta(days=1)
                cutoff_time = yesterday.replace(hour=21, minute=0, second=0, microsecond=0)
                cleanup_type = "Preparação Mercado Americano"
            elif now_sp.hour == 21:
                # Limpeza das 21:00 - remover sinais desde a última limpeza (10:00 de hoje)
                cutoff_time = now_sp.replace(hour=10, minute=0, second=0, microsecond=0)
                cleanup_type = "Preparação Mercado Asiático"
            else:
                print(f"⚠️ Limpeza executada fora do horário programado: {now_sp.hour}:00")
                return
            
            # Converter para UTC
            cutoff_time_utc = cutoff_time.astimezone(pytz.UTC)
            
            print(f"🎯 {cleanup_type}")
            print(f"🗑️ Removendo sinais anteriores a: {cutoff_time.strftime('%d/%m/%Y %H:%M')} (SP)")
            
            # Buscar sinais para remoção
            old_signals = supabase.table('signals').select('id, symbol, created_at').lt('created_at', cutoff_time_utc.isoformat()).execute()
            
            if old_signals.data:
                signal_count = len(old_signals.data)
                print(f"📊 Encontrados {signal_count} sinais para remoção")
                
                # Remover sinais antigos
                for signal in old_signals.data:
                    try:
                        supabase.table('signals').delete().eq('id', signal['id']).execute()
                        print(f"🗑️ Removido: {signal['symbol']} (ID: {signal['id']})")
                    except Exception as e:
                        print(f"❌ Erro ao remover sinal {signal['id']}: {e}")
                
                print(f"✅ Limpeza concluída: {signal_count} sinais removidos")
            else:
                print("📭 Nenhum sinal antigo encontrado para remoção")
            
            # Estatísticas finais
            remaining_signals = supabase.table('signals').select('id', count='exact').execute()
            total_remaining = remaining_signals.count if remaining_signals.count else 0
            
            print(f"📊 Sinais restantes no sistema: {total_remaining}")
            print(f"🧹 Limpeza finalizada - {datetime.now(self.sao_paulo_tz).strftime('%d/%m/%Y %H:%M:%S')} (SP)")
            
        except Exception as e:
            print(f"❌ Erro na limpeza de sinais: {e}")
            import traceback
            traceback.print_exc()
    
    def schedule_cleanup(self) -> None:
        """Agenda limpezas automáticas"""
        # Agendar limpeza às 10:00 (preparação mercado americano)
        schedule.every().day.at("10:00").do(self.cleanup_old_signals)
        
        # Agendar limpeza às 21:00 (preparação mercado asiático)
        schedule.every().day.at("21:00").do(self.cleanup_old_signals)
        
        print("📅 Limpezas agendadas:")
        print("   🇺🇸 10:00 - Preparação Mercado Americano")
        print("   🇯🇵 21:00 - Preparação Mercado Asiático")
        print("   🌍 Timezone: America/Sao_Paulo")
    
    def start_scheduler(self) -> None:
        """Inicia o agendador de limpeza em thread separada"""
        if self.is_running:
            print("⚠️ Sistema de limpeza já está rodando")
            return
        
        self.is_running = True
        self.schedule_cleanup()
        
        def run_scheduler():
            print("🚀 Sistema de limpeza automática iniciado")
            while self.is_running:
                try:
                    schedule.run_pending()
                    time.sleep(60)  # Verificar a cada minuto
                except Exception as e:
                    print(f"❌ Erro no agendador de limpeza: {e}")
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
    
    def get_next_cleanup_time(self) -> str:
        """Retorna o horário da próxima limpeza"""
        now_sp = datetime.now(self.sao_paulo_tz)
        
        # Próxima limpeza às 10:00
        next_10 = now_sp.replace(hour=10, minute=0, second=0, microsecond=0)
        if next_10 <= now_sp:
            next_10 += timedelta(days=1)
        
        # Próxima limpeza às 21:00
        next_21 = now_sp.replace(hour=21, minute=0, second=0, microsecond=0)
        if next_21 <= now_sp:
            next_21 += timedelta(days=1)
        
        # Retornar a próxima mais próxima
        next_cleanup = min(next_10, next_21)
        
        return next_cleanup.strftime('%d/%m/%Y %H:%M:%S')

# Instância global para uso em outros módulos
cleanup_system = SignalCleanup()

if __name__ == "__main__":
    # Teste do sistema
    cleanup = SignalCleanup()
    print(f"📅 Próxima limpeza: {cleanup.get_next_cleanup_time()}")
    
    # Para teste manual, descomente a linha abaixo:
    # cleanup.manual_cleanup()