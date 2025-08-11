#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para limpeza manual de sinais antigos
Remove sinais com mais de 1 dia para resolver problema de interface
"""

import os
import sys
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Adicionar o diretório back ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'back'))

def cleanup_old_signals():
    """
    Executa limpeza manual de sinais antigos
    """
    try:
        print("🧹 INICIANDO LIMPEZA MANUAL DE SINAIS ANTIGOS")
        print("="*60)
        
        # Importar componentes necessários
        from core.database import Database
        from core.gerenciar_sinais import GerenciadorSinais
        
        # Inicializar componentes
        print("📊 Inicializando componentes...")
        db = Database()
        gerenciador = GerenciadorSinais(db)
        
        # Obter horário atual
        tz = pytz.timezone('America/Sao_Paulo')
        now = datetime.now(tz)
        
        print(f"⏰ Horário atual: {now.strftime('%d/%m/%Y %H:%M:%S')}")
        
        # Contar sinais antes da limpeza
        try:
            count_query = "SELECT COUNT(*) as total FROM signals WHERE status = 'OPEN'"
            result = db.execute_query(count_query)
            total_before = result[0]['total'] if result else 0
            print(f"📊 Sinais OPEN antes da limpeza: {total_before}")
        except Exception as e:
            print(f"⚠️ Erro ao contar sinais: {e}")
            total_before = 0
        
        # Executar limpeza de sinais antigos (mais de 24 horas)
        print("\n🧹 Removendo sinais com mais de 24 horas...")
        try:
            # Calcular data limite (24 horas atrás)
            limit_date = now - timedelta(hours=24)
            
            # Query para deletar sinais antigos
            delete_query = """
            DELETE FROM signals 
            WHERE status = 'OPEN' 
            AND created_at < %s
            """
            
            # Executar deleção
            cursor = db.get_cursor()
            cursor.execute(delete_query, (limit_date,))
            deleted_count = cursor.rowcount
            db.connection.commit()
            
            print(f"✅ {deleted_count} sinais antigos removidos")
            
        except Exception as e:
            print(f"❌ Erro na limpeza de sinais antigos: {e}")
            deleted_count = 0
        
        # Executar limpezas específicas
        print("\n🧹 Executando limpezas específicas...")
        
        # Limpeza matinal (antes das 10:00)
        try:
            gerenciador.limpar_sinais_antes_das_10h()
            print("✅ Limpeza matinal executada")
        except Exception as e:
            print(f"⚠️ Erro na limpeza matinal: {e}")
        
        # Limpeza noturna (antes das 21:00)
        try:
            gerenciador.limpar_sinais_antes_das_21h()
            print("✅ Limpeza noturna executada")
        except Exception as e:
            print(f"⚠️ Erro na limpeza noturna: {e}")
        
        # Limpeza de sinais futuros
        try:
            gerenciador.limpar_sinais_futuros()
            print("✅ Limpeza de sinais futuros executada")
        except Exception as e:
            print(f"⚠️ Erro na limpeza de sinais futuros: {e}")
        
        # Contar sinais após a limpeza
        try:
            result = db.execute_query(count_query)
            total_after = result[0]['total'] if result else 0
            print(f"\n📊 Sinais OPEN após a limpeza: {total_after}")
            print(f"🗑️ Total removido: {total_before - total_after}")
        except Exception as e:
            print(f"⚠️ Erro ao contar sinais finais: {e}")
        
        print("\n" + "="*60)
        print("✅ LIMPEZA MANUAL CONCLUÍDA COM SUCESSO!")
        print("🔄 O frontend agora deve mostrar apenas sinais recentes")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na limpeza manual: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🚀 Script de Limpeza Manual de Sinais")
    print("Removendo sinais antigos para atualizar interface...\n")
    
    success = cleanup_old_signals()
    
    if success:
        print("\n🎉 Limpeza concluída! O frontend deve atualizar automaticamente.")
    else:
        print("\n❌ Falha na limpeza. Verifique os logs acima.")
    
    input("\nPressione Enter para sair...")