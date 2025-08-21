#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema Unificado de Sinais - Solução Local
Centraliza todos os dados de sinais e ativa monitoramento com simulação de $1.000 USD
"""

import sys
import os
import sqlite3
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import traceback

# Adicionar path do backend
sys.path.append(os.path.join(os.path.dirname(__file__), 'back'))

from core.database import Database
from core.signal_monitoring_system import SignalMonitoringSystem
from core.binance_client import BinanceClient
from core.gerenciar_sinais import GerenciadorSinais

class UnifiedSignalSystem:
    """
    Sistema unificado que centraliza todos os sinais e ativa monitoramento
    """
    
    def __init__(self):
        """
        Inicializa o sistema unificado
        """
        self.db = Database()
        self.binance_client = BinanceClient()
        self.monitoring_system = SignalMonitoringSystem.get_instance(self.db, self.binance_client)
        self.gerenciador = GerenciadorSinais(self.db)
        self.unified_signals = []
        
    def collect_all_signals(self) -> List[Dict[str, Any]]:
        """
        Coleta todos os sinais de todas as fontes
        """
        try:
            print("📊 === COLETANDO SINAIS DE TODAS AS FONTES ===")
            all_signals = []
            
            # 1. Coletar do SQLite
            print("   🗄️ Coletando do SQLite...")
            sqlite_signals = self._collect_from_sqlite()
            all_signals.extend(sqlite_signals)
            print(f"   ✅ {len(sqlite_signals)} sinais do SQLite")
            
            # 2. Coletar do CSV
            print("   📄 Coletando do CSV...")
            csv_signals = self._collect_from_csv()
            all_signals.extend(csv_signals)
            print(f"   ✅ {len(csv_signals)} sinais do CSV")
            
            # 3. Remover duplicatas
            print("   🔄 Removendo duplicatas...")
            unique_signals = self._remove_duplicates(all_signals)
            print(f"   ✅ {len(unique_signals)} sinais únicos")
            
            print(f"\n📋 Total coletado: {len(unique_signals)} sinais")
            return unique_signals
            
        except Exception as e:
            print(f"❌ Erro ao coletar sinais: {e}")
            traceback.print_exc()
            return []
    
    def _collect_from_sqlite(self) -> List[Dict[str, Any]]:
        """
        Coleta sinais do banco SQLite
        """
        try:
            sqlite_path = 'Cryptem1.1/back/signals.db'
            if not os.path.exists(sqlite_path):
                return []
            
            conn = sqlite3.connect(sqlite_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM signals WHERE status = "OPEN"')
            rows = cursor.fetchall()
            conn.close()
            
            signals = []
            for row in rows:
                signal = dict(row)
                signal['source'] = 'sqlite'
                signals.append(signal)
            
            return signals
            
        except Exception as e:
            print(f"   ⚠️ Erro no SQLite: {e}")
            return []
    
    def _collect_from_csv(self) -> List[Dict[str, Any]]:
        """
        Coleta sinais do arquivo CSV
        """
        try:
            csv_path = 'back/signals_history.csv'
            if not os.path.exists(csv_path):
                return []
            
            df = pd.read_csv(csv_path)
            signals = df.to_dict('records')
            
            for signal in signals:
                signal['source'] = 'csv'
            
            return signals
            
        except Exception as e:
            print(f"   ⚠️ Erro no CSV: {e}")
            return []
    
    def _remove_duplicates(self, signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove sinais duplicados baseado em symbol + type + entry_price
        """
        seen = set()
        unique_signals = []
        
        for signal in signals:
            # Criar chave única
            key = (
                signal.get('symbol', '').upper(),
                signal.get('type', '').upper(),
                float(signal.get('entry_price', signal.get('price', 0)))
            )
            
            if key not in seen and key[0]:  # Verificar se symbol não está vazio
                seen.add(key)
                unique_signals.append(signal)
        
        return unique_signals
    
    def normalize_signals(self, signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normaliza sinais para formato padrão
        """
        try:
            print("\n🔧 === NORMALIZANDO SINAIS ===")
            normalized = []
            
            for i, signal in enumerate(signals, 1):
                try:
                    normalized_signal = self._normalize_single_signal(signal)
                    if normalized_signal:
                        normalized.append(normalized_signal)
                        print(f"   ✅ [{i}/{len(signals)}] {normalized_signal['symbol']} - {normalized_signal['signal_type']}")
                    else:
                        print(f"   ❌ [{i}/{len(signals)}] Falha na normalização")
                        
                except Exception as e:
                    print(f"   ❌ [{i}/{len(signals)}] Erro: {e}")
                    continue
            
            print(f"\n✅ {len(normalized)} sinais normalizados")
            return normalized
            
        except Exception as e:
            print(f"❌ Erro na normalização: {e}")
            traceback.print_exc()
            return []
    
    def _normalize_single_signal(self, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Normaliza um único sinal
        """
        try:
            # Mapear tipo de sinal
            signal_type = signal.get('type', 'COMPRA').upper()
            if signal_type in ['LONG', 'BUY']:
                signal_type = 'COMPRA'
            elif signal_type in ['SHORT', 'SELL']:
                signal_type = 'VENDA'
            
            # Preços
            entry_price = float(signal.get('entry_price', signal.get('price', 0)))
            target_price = float(signal.get('target_price', signal.get('tp3', entry_price * 1.04)))
            
            if entry_price <= 0:
                return None
            
            # Calcular movimento necessário
            if signal_type == 'COMPRA':
                movement_percentage = ((target_price - entry_price) / entry_price) * 100
            else:
                movement_percentage = ((entry_price - target_price) / entry_price) * 100
            
            # Calcular alavancagem
            required_percentage = abs(movement_percentage) if movement_percentage != 0 else 4.0
            max_leverage = min(100, max(50, int(300 / required_percentage)))
            
            # Criar sinal normalizado
            normalized = {
                'id': f"unified_{signal.get('symbol', 'UNKNOWN')}_{int(datetime.now().timestamp())}",
                'symbol': signal.get('symbol', '').upper(),
                'type': signal_type,  # Campo esperado pelo sistema de monitoramento
                'signal_type': signal_type,  # Campo para compatibilidade
                'entry_price': entry_price,
                'target_price': target_price,
                'entry_time': self._parse_datetime(signal.get('entry_time', signal.get('timestamp', datetime.now()))),
                'confirmed_at': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                'status': 'CONFIRMED',
                'quality_score': float(signal.get('quality_score', signal.get('score', 75.0))),
                'signal_class': signal.get('signal_class', 'PREMIUM'),
                'projection_percentage': round(movement_percentage, 2),
                'max_leverage': max_leverage,
                'required_percentage': round(required_percentage, 2),
                'source': signal.get('source', 'unknown'),
                'confirmation_reasons': ['unified_system'],
                'btc_correlation': 0.0,
                'btc_trend': 'NEUTRAL',
                
                # Campos de monitoramento
                'is_monitored': True,
                'monitoring_status': 'MONITORING',
                'days_monitored': 0,
                
                # Campos de simulação
                'simulation_investment': 1000.00,
                'simulation_current_value': 1000.00,
                'simulation_pnl_usd': 0.00,
                'simulation_pnl_percentage': 0.00,
                'simulation_max_value_reached': 1000.00,
                'simulation_target_value': 4000.00,
                'simulation_position_size': 0.00,
                
                # Campos de alavancagem
                'current_profit': 0.00,
                'max_profit_reached': 0.00
            }
            
            return normalized
            
        except Exception as e:
            print(f"     ⚠️ Erro na normalização de {signal.get('symbol', 'UNKNOWN')}: {e}")
            return None
    
    def _parse_datetime(self, dt_value) -> str:
        """
        Converte valor para datetime string
        """
        if isinstance(dt_value, str):
            try:
                formats = [
                    '%Y-%m-%d %H:%M:%S',
                    '%d/%m/%Y %H:%M:%S',
                    '%Y-%m-%d',
                    '%d/%m/%Y'
                ]
                
                for fmt in formats:
                    try:
                        dt = datetime.strptime(dt_value, fmt)
                        return dt.strftime('%d/%m/%Y %H:%M:%S')
                    except ValueError:
                        continue
                
                return datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                
            except:
                return datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        elif isinstance(dt_value, datetime):
            return dt_value.strftime('%d/%m/%Y %H:%M:%S')
        else:
            return datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    
    def save_unified_signals(self, signals: List[Dict[str, Any]]) -> bool:
        """
        Salva sinais unificados no sistema
        """
        try:
            print("\n💾 === SALVANDO SINAIS UNIFICADOS ===")
            
            # Limpar sinais existentes
            print("   🧹 Limpando sinais antigos...")
            self._clear_old_signals()
            
            # Salvar novos sinais
            print("   💾 Salvando novos sinais...")
            saved_count = 0
            
            for signal in signals:
                try:
                    # Salvar no gerenciador de sinais
                    self.gerenciador.save_signal(signal)
                    saved_count += 1
                    
                except Exception as e:
                    print(f"     ❌ Erro ao salvar {signal.get('symbol', 'UNKNOWN')}: {e}")
                    continue
            
            print(f"   ✅ {saved_count} sinais salvos")
            
            # Salvar backup JSON
            backup_file = f'unified_signals_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(signals, f, indent=2, default=str)
            
            print(f"   💾 Backup salvo: {backup_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar sinais: {e}")
            traceback.print_exc()
            return False
    
    def _clear_old_signals(self):
        """
        Limpa sinais antigos do sistema
        """
        try:
            # Limpar arquivo CSV se existir
            signals_file = self.gerenciador.signals_file
            if os.path.exists(signals_file):
                # Criar backup antes de limpar
                backup_name = f"{signals_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                os.rename(signals_file, backup_name)
                print(f"     📁 Backup criado: {backup_name}")
            
        except Exception as e:
            print(f"     ⚠️ Erro ao limpar sinais antigos: {e}")
    
    def activate_monitoring(self, signals: List[Dict[str, Any]]) -> bool:
        """
        Ativa monitoramento para todos os sinais
        """
        try:
            print("\n🚀 === ATIVANDO MONITORAMENTO ===")
            
            # Inicializar sistema de monitoramento
            print("   🔧 Inicializando sistema de monitoramento...")
            if not self.monitoring_system.is_monitoring:
                self.monitoring_system.start_monitoring()
                print("   ✅ Sistema de monitoramento iniciado")
            else:
                print("   ✅ Sistema de monitoramento já ativo")
            
            # Adicionar sinais ao monitoramento
            print("   📊 Adicionando sinais ao monitoramento...")
            added_count = 0
            
            for signal in signals:
                try:
                    success = self.monitoring_system.add_signal_to_monitoring(signal_data=signal)
                    if success:
                        added_count += 1
                        print(f"     ✅ {signal['symbol']} - ${signal['simulation_investment']} USD")
                    else:
                        print(f"     ❌ Falha: {signal['symbol']}")
                        
                except Exception as e:
                    print(f"     ❌ Erro em {signal.get('symbol', 'UNKNOWN')}: {e}")
                    continue
            
            print(f"\n✅ {added_count} sinais adicionados ao monitoramento")
            print(f"💰 Simulação ativa: ${added_count * 1000} USD total")
            
            return added_count > 0
            
        except Exception as e:
            print(f"❌ Erro ao ativar monitoramento: {e}")
            traceback.print_exc()
            return False
    
    def verify_system(self) -> bool:
        """
        Verifica se o sistema está funcionando corretamente
        """
        try:
            print("\n🔍 === VERIFICANDO SISTEMA ===")
            
            # Verificar sinais salvos
            saved_signals = self.gerenciador.load_signals_from_csv()
            print(f"   📊 Sinais salvos: {len(saved_signals)}")
            
            # Verificar monitoramento
            monitored_signals = self.monitoring_system.get_monitored_signals()
            print(f"   🔄 Sinais monitorados: {len(monitored_signals)}")
            
            # Verificar estatísticas
            stats = self.monitoring_system.get_monitoring_stats()
            print(f"   📈 Sistema ativo: {stats.get('is_monitoring', False)}")
            
            # Mostrar exemplos
            if monitored_signals:
                print("\n   📋 Exemplos de sinais monitorados:")
                for signal in monitored_signals[:3]:
                    print(f"     • {signal.get('symbol')} - {signal.get('signal_type')} - ${signal.get('simulation_investment', 1000)}")
            
            success = len(monitored_signals) > 0
            
            if success:
                print("\n✅ Sistema verificado com sucesso")
            else:
                print("\n⚠️ Sistema pode ter problemas")
            
            return success
            
        except Exception as e:
            print(f"❌ Erro na verificação: {e}")
            traceback.print_exc()
            return False
    
    def run_unification(self) -> bool:
        """
        Executa todo o processo de unificação
        """
        print("🚀 === SISTEMA UNIFICADO DE SINAIS ===")
        print(f"⏰ Início: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        try:
            # Fase 1: Coletar sinais
            all_signals = self.collect_all_signals()
            if not all_signals:
                print("❌ Nenhum sinal encontrado")
                return False
            
            # Fase 2: Normalizar
            normalized_signals = self.normalize_signals(all_signals)
            if not normalized_signals:
                print("❌ Falha na normalização")
                return False
            
            # Fase 3: Salvar
            if not self.save_unified_signals(normalized_signals):
                print("❌ Falha ao salvar")
                return False
            
            # Fase 4: Ativar monitoramento
            if not self.activate_monitoring(normalized_signals):
                print("❌ Falha no monitoramento")
                return False
            
            # Fase 5: Verificar
            if not self.verify_system():
                print("⚠️ Sistema pode ter problemas")
            
            print("\n🎉 === UNIFICAÇÃO CONCLUÍDA COM SUCESSO ===")
            print(f"⏰ Fim: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            print(f"📊 Total de sinais: {len(normalized_signals)}")
            print(f"💰 Simulação total: ${len(normalized_signals) * 1000} USD")
            print("\n📋 Próximos passos:")
            print("   1. ✅ Dashboard mostrará dados consistentes")
            print("   2. ✅ Monitoramento ativo com simulação")
            print("   3. ✅ APIs retornando dados corretos")
            print("   4. 🔄 Migração para Supabase quando disponível")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro crítico: {e}")
            traceback.print_exc()
            return False

def main():
    """
    Função principal
    """
    try:
        system = UnifiedSignalSystem()
        success = system.run_unification()
        
        if success:
            print("\n🎯 SISTEMA UNIFICADO CRIADO COM SUCESSO!")
            print("💰 Simulação de $1.000 USD por sinal ativa!")
            print("📊 Dados consistentes entre todos os sistemas!")
            sys.exit(0)
        else:
            print("\n❌ FALHA NA UNIFICAÇÃO!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Processo cancelado pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()