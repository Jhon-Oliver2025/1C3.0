#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para forçar limpeza de sinais antigos em produção
Este script deve ser executado no servidor para limpar sinais de dias anteriores
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta
import pytz
import traceback

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

def force_cleanup_production_signals():
    """
    Força a limpeza de todos os sinais antigos em produção
    Remove sinais OPEN de dias anteriores ao dia atual
    """
    print("🧹 [PRODUÇÃO] Iniciando limpeza forçada de sinais antigos...")
    
    try:
        # Caminho do arquivo de sinais (relativo ao diretório do script)
        signals_file = os.path.join(os.path.dirname(__file__), 'sinais_lista.csv')
        
        print(f"📁 Verificando arquivo: {signals_file}")
        
        if not os.path.exists(signals_file):
            print(f"⚠️ Arquivo de sinais não encontrado: {signals_file}")
            # Criar arquivo vazio se não existir
            with open(signals_file, 'w') as f:
                f.write("symbol,type,entry_price,entry_time,target_price,projection_percentage,signal_class,status\n")
            print("📝 Arquivo de sinais criado com cabeçalho.")
            return
        
        # Ler arquivo de sinais
        df = pd.read_csv(signals_file)
        print(f"📊 Total de sinais no arquivo: {len(df)}")
        
        if df.empty:
            print("📝 Arquivo de sinais está vazio.")
            return
        
        # Mostrar alguns sinais para debug
        print("\n📋 Primeiros 5 sinais no arquivo:")
        for i, row in df.head().iterrows():
            print(f"  {i+1}. {row['symbol']} - {row['entry_time']} - Status: {row['status']}")
        
        # Converter entry_time para datetime
        df['entry_time'] = pd.to_datetime(df['entry_time'])
        
        # Definir timezone e data de corte
        timezone = pytz.timezone('America/Sao_Paulo')
        agora = datetime.now(timezone)
        
        # Data de corte: início do dia atual (00:00:00)
        inicio_hoje = agora.replace(hour=0, minute=0, second=0, microsecond=0)
        inicio_hoje_naive = inicio_hoje.replace(tzinfo=None)
        
        # Data de corte alternativa: 2 dias atrás para ser mais agressivo
        dois_dias_atras = (agora - timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
        dois_dias_atras_naive = dois_dias_atras.replace(tzinfo=None)
        
        print(f"📅 Data atual: {agora}")
        print(f"📅 Início de hoje: {inicio_hoje_naive}")
        print(f"📅 Dois dias atrás: {dois_dias_atras_naive}")
        
        # Identificar sinais antigos (OPEN e anteriores a 2 dias atrás)
        sinais_muito_antigos = df[
            (df['status'] == 'OPEN') & 
            (df['entry_time'] < dois_dias_atras_naive)
        ]
        
        # Identificar sinais de ontem e anteontem
        sinais_antigos = df[
            (df['status'] == 'OPEN') & 
            (df['entry_time'] < inicio_hoje_naive)
        ]
        
        print(f"\n🗑️ Sinais muito antigos (>2 dias): {len(sinais_muito_antigos)}")
        print(f"🗑️ Sinais antigos (dias anteriores): {len(sinais_antigos)}")
        
        if len(sinais_antigos) > 0:
            print("\n📋 Sinais antigos que serão removidos:")
            for i, (_, sinal) in enumerate(sinais_antigos.iterrows()):
                if i < 10:  # Mostrar apenas os primeiros 10
                    print(f"  - {sinal['symbol']} ({sinal['type']}) - {sinal['entry_time']} - Status: {sinal['status']}")
                elif i == 10:
                    print(f"  ... e mais {len(sinais_antigos) - 10} sinais")
                    break
        
        # Estratégia 1: Remover apenas sinais muito antigos (>2 dias)
        df_limpo_conservador = df[
            ~((df['status'] == 'OPEN') & (df['entry_time'] < dois_dias_atras_naive))
        ].copy()
        
        # Estratégia 2: Remover todos os sinais OPEN de dias anteriores
        df_limpo_agressivo = df[
            (df['entry_time'] >= inicio_hoje_naive) |
            (df['status'] != 'OPEN')
        ].copy()
        
        print(f"\n🔄 Opções de limpeza:")
        print(f"   Conservadora (>2 dias): {len(df)} → {len(df_limpo_conservador)} sinais")
        print(f"   Agressiva (dias anteriores): {len(df)} → {len(df_limpo_agressivo)} sinais")
        
        # Usar limpeza agressiva para resolver o problema
        df_final = df_limpo_agressivo
        
        # Backup do arquivo original
        backup_file = signals_file + f".backup_{agora.strftime('%Y%m%d_%H%M%S')}"
        df.to_csv(backup_file, index=False)
        print(f"💾 Backup criado: {backup_file}")
        
        # Salvar arquivo limpo
        df_final.to_csv(signals_file, index=False)
        
        print(f"\n🎉 Limpeza concluída!")
        print(f"   - Sinais originais: {len(df)}")
        print(f"   - Sinais removidos: {len(df) - len(df_final)}")
        print(f"   - Sinais restantes: {len(df_final)}")
        
        # Mostrar sinais restantes
        sinais_open_restantes = df_final[df_final['status'] == 'OPEN']
        print(f"   - Sinais OPEN restantes: {len(sinais_open_restantes)}")
        
        if len(sinais_open_restantes) > 0:
            print("\n📋 Sinais OPEN que permaneceram:")
            for i, (_, sinal) in enumerate(sinais_open_restantes.iterrows()):
                if i < 5:  # Mostrar apenas os primeiros 5
                    print(f"  - {sinal['symbol']} ({sinal['type']}) - {sinal['entry_time']}")
                elif i == 5:
                    print(f"  ... e mais {len(sinais_open_restantes) - 5} sinais")
                    break
        
    except Exception as e:
        print(f"❌ Erro durante a limpeza: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    force_cleanup_production_signals()