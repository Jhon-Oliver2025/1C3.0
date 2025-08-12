#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para limpar sinais fracos (< 80 pontos) do Supabase
Mantém apenas sinais de alta qualidade (80+ pontos)
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

# Carregar variáveis de ambiente
load_dotenv()

def cleanup_weak_signals():
    """
    Remove todos os sinais com quality_score < 80 do Supabase
    """
    try:
        print("🧹 INICIANDO LIMPEZA DE SINAIS FRACOS")
        print("="*60)
        
        # Configurar Supabase
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        if not supabase_url or not supabase_key:
            print("❌ Erro: Variáveis SUPABASE_URL ou SUPABASE_ANON_KEY não encontradas")
            return False
        
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Contar sinais antes da limpeza
        print("📊 Contando sinais antes da limpeza...")
        all_signals = supabase.table('signals').select('*').eq('status', 'OPEN').execute()
        total_before = len(all_signals.data)
        print(f"📊 Total de sinais OPEN: {total_before}")
        
        # Contar sinais de alta qualidade (80+)
        quality_signals = [s for s in all_signals.data if float(s.get('quality_score', 0)) >= 80.0]
        quality_count = len(quality_signals)
        weak_count = total_before - quality_count
        
        print(f"✅ Sinais de qualidade (80+): {quality_count}")
        print(f"❌ Sinais fracos (< 80): {weak_count}")
        
        if weak_count == 0:
            print("✨ Nenhum sinal fraco encontrado! Todos os sinais já são de alta qualidade.")
            return True
        
        # Confirmar limpeza
        print(f"\n⚠️ ATENÇÃO: Serão removidos {weak_count} sinais fracos!")
        print(f"✅ Serão mantidos {quality_count} sinais de qualidade.")
        
        # Executar limpeza - deletar sinais com quality_score < 80
        print("\n🧹 Removendo sinais fracos...")
        
        # Buscar IDs dos sinais fracos
        weak_signals = [s for s in all_signals.data if float(s.get('quality_score', 0)) < 80.0]
        
        deleted_count = 0
        for signal in weak_signals:
            try:
                result = supabase.table('signals').delete().eq('id', signal['id']).execute()
                if result.data:
                    deleted_count += 1
                    if deleted_count % 100 == 0:
                        print(f"🗑️ Removidos {deleted_count}/{weak_count} sinais...")
            except Exception as e:
                print(f"⚠️ Erro ao remover sinal {signal.get('symbol', 'N/A')}: {e}")
        
        # Contar sinais após a limpeza
        print("\n📊 Contando sinais após a limpeza...")
        final_signals = supabase.table('signals').select('*').eq('status', 'OPEN').execute()
        total_after = len(final_signals.data)
        
        print(f"\n{'='*60}")
        print(f"✅ LIMPEZA CONCLUÍDA COM SUCESSO!")
        print(f"📊 Sinais antes: {total_before}")
        print(f"📊 Sinais após: {total_after}")
        print(f"🗑️ Sinais removidos: {deleted_count}")
        print(f"✨ Apenas sinais de 80+ pontos permanecem no sistema!")
        print(f"{'='*60}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na limpeza: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🚀 Script de Limpeza de Sinais Fracos")
    print("Removendo sinais < 80 pontos para manter apenas alta qualidade...\n")
    
    success = cleanup_weak_signals()
    
    if success:
        print("\n🎉 Limpeza concluída! Apenas sinais de alta qualidade permanecem.")
        print("📱 O frontend agora exibirá apenas sinais de 80+ pontos.")
    else:
        print("\n❌ Falha na limpeza. Verifique os logs acima.")
    
    input("\nPressione Enter para sair...")