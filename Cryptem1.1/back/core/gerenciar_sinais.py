import pandas as pd
import os
import csv
import traceback  # Adicionando import do traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
from pandas import DataFrame, Series
from .database import Database

class GerenciadorSinais:
    # --- Início da Edição ---
    def __init__(self, db_instance): # Adicione um parâmetro para a instância do banco de dados
        self.db = db_instance # Armazene a instância do banco de dados
        self.signals_file = 'sinais_lista.csv'
        self.history_file = 'historico_sinais.csv'
        self.SIGNAL_COLUMNS = pd.Index([
            'symbol', 'type', 'entry_price', 'entry_time',
            'target_price', 'target_exit_time', 'status', 'exit_price',
            'variation', 'result', 'quality_score', 'signal_class',
            'trend_score', 'alignment_score', 'market_score'
        ])
        
        self._empty_df = DataFrame(columns=self.SIGNAL_COLUMNS)

    def _get_signal_class(self, quality_score: float) -> str:
        """Retorna a classificação do sinal baseado no quality_score"""
        # --- Início da Edição ---
        # Simplificado para Sinais Premium se o score for >= 90
        if quality_score >= 90:
            return "Sinais Premium"
        else:
            # Esta parte não deve ser alcançada se o filtro quality_score_minimum estiver ativo
            return "❌ Score Insuficiente"
        # --- Fim da Edição ---

    def save_signal(self, signal_data: Dict) -> bool:
        try:
            print(f"Tentando salvar sinal: {signal_data}")  # Debug
            
            # Formatar o sinal antes de salvar
            formatted_signal = {
                'symbol': signal_data['symbol'],
                'type': signal_data['type'],
                'entry_price': float(signal_data['entry_price']),
                'entry_time': signal_data['entry_time'],
                'target_price': float(signal_data['target_price']),
                'target_exit_time': signal_data['target_exit_time'],
                'status': 'OPEN',
                'exit_price': '',
                'variation': '',
                'result': '',
                'quality_score': float(signal_data['quality_score']),
                'signal_class': self._get_signal_class(float(signal_data['quality_score'])),
                'trend_score': float(signal_data.get('trend_score', 0)),
                'alignment_score': float(signal_data.get('alignment_score', 0)),
                'market_score': float(signal_data.get('market_score', 0)),
                'strategy_info': str(signal_data.get('strategy_info', '')),
                'trend_timeframe': str(signal_data.get('trend_timeframe', '4h')),
                'entry_timeframe': str(signal_data.get('entry_timeframe', '1h')),
                'trend_strength': float(signal_data.get('trend_strength', 0)),
                'confluence_count': float(signal_data.get('confluence_count', 0)),
                'leverage': float(signal_data.get('leverage', 50.0)),
                'max_exit_time': signal_data.get('max_exit_time', ''),
                'expected_duration': signal_data.get('expected_duration', '1-3 dias (típico), até 7 dias (normal), máximo 15 dias')
            }
            
            # Converter valores NaN para string vazia
            for key in formatted_signal:
                if pd.isna(formatted_signal[key]):
                    formatted_signal[key] = ''
            
            print(f"Sinal formatado para salvar: {formatted_signal}")
            
            result = self.db.add_signal(formatted_signal)
            if result:
                print(f"✅ Sinal salvo com sucesso: {formatted_signal['symbol']}")
            else:
                print(f"❌ Falha ao salvar sinal: {formatted_signal['symbol']}")
            return result
            
        except Exception as e:
            print(f"❌ Erro detalhado ao salvar sinal: {str(e)}")
            traceback.print_exc()
            return False

    def clean_scalping_signals(self):
        """Limpa todos os sinais de scalping à meia-noite"""
        try:
            df = pd.read_csv(self.signals_file)
            
            # Manter apenas sinais não-scalping
            df = df[~df['is_scalping']]
            
            # Salvar arquivo atualizado
            df.to_csv(self.signals_file, index=False)
            print("✨ Sinais de scalping limpos com sucesso")
            
        except Exception as e:
            print(f"❌ Erro ao limpar sinais de scalping: {e}")

    # Adicionar este método para ser chamado por um agendador
    def schedule_cleanup(self):
        """Agenda a limpeza dos sinais de scalping para meia-noite"""
        now = datetime.now()
        midnight = (now + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        
        # Calcular tempo até meia-noite
        wait_seconds = (midnight - now).total_seconds()
        
        # Aqui você pode usar um agendador como schedule ou APScheduler
        # Para executar clean_scalping_signals() à meia-noite

    def processar_sinais_abertos(self) -> DataFrame:
        try:
            df = pd.read_csv(self.signals_file)
            df['entry_time'] = pd.to_datetime(df['entry_time'])
            
            # --- Início da Edição ---
            # Converter colunas numéricas para float, tratando erros
            # Removido .astype(float) pois pd.to_numeric(errors='coerce') já retorna float64 se necessário
            numeric_cols = [
                'entry_price', 'target_price', 'exit_price', 'variation',
                'quality_score', 'trend_score', 'alignment_score', 'market_score',
                'trend_strength', 'confluence_count', 'leverage'
            ]
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            # --- Fim da Edição ---
            
            # Pegar a data atual
            hoje = datetime.now().date()
            
            # Filtrar sinais do dia atual e com status OPEN
            result_df = df[
                (df['entry_time'].dt.date == hoje) & 
                (df['status'] == 'OPEN')
            ]
            
            # Agrupar por symbol e pegar o primeiro sinal do dia
            result_df = (result_df
                        .assign(entry_time=pd.to_datetime(result_df['entry_time']))
                        .sort_values('entry_time')
                        .groupby('symbol')
                        .first()
                        .reset_index())
            
            # Ordenar o resultado final por horário
            result_df = result_df.sort_values('entry_time')
            
            if isinstance(result_df, pd.Series):
                result_df = result_df.to_frame().T
            return result_df if not result_df.empty else self._empty_df.copy()
        except Exception as e:
            print(f"❌ Erro ao processar sinais abertos: {e}")
            return self._empty_df.copy()

    def gerar_relatorio(self) -> dict:
        try:
            df = pd.read_csv(self.signals_file)
            df['entry_time'] = pd.to_datetime(df['entry_time'])
            
            cutoff = datetime.now() - timedelta(hours=24)
            recentes = df[
                (df['status'] == 'CLOSED') & 
                (df['entry_time'] >= cutoff)
            ]
            
            total = len(recentes)
            if total == 0:
                return {'total_trades': 0, 'win_rate': 0, 'avg_gain': 0}
                
            wins = len(recentes[recentes['result'] == 'WIN'])
            win_rate = (wins / total) * 100
            
            recentes['variation'] = pd.to_numeric(recentes['variation'], errors='coerce')
            avg_gain = recentes['variation'].mean() if len(recentes) > 0 else 0.0
            
            return {
                'total_trades': total,
                'win_rate': round(win_rate, 2),
                'avg_gain': round(float(avg_gain), 2)
            }
            
        except Exception as e:
            print(f"❌ Erro ao gerar relatório: {e}")
            return {'total_trades': 0, 'win_rate': 0, 'avg_gain': 0}

    def atualizar_sinal(self, symbol: str, exit_price: float, variation: float) -> bool:
        """Atualiza um sinal com informações de saída"""
        try:
            df = pd.read_csv(self.signals_file)
            mask = (df['symbol'] == symbol) & (df['status'] == 'OPEN')
            
            if not mask.any():
                print(f"⚠️ Nenhum sinal aberto encontrado para {symbol}")
                return False
                
            df.loc[mask, 'exit_price'] = str(exit_price)
            df.loc[mask, 'variation'] = str(variation)
            df.loc[mask, 'status'] = 'CLOSED'
            df.loc[mask, 'result'] = 'WIN' if variation > 0 else 'LOSS'
            df.loc[mask, 'exit_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            df.to_csv(self.signals_file, index=False)
            print(f"✅ Sinal atualizado: {symbol}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao atualizar sinal: {e}")
            return False

    def verificar_integridade(self) -> bool:
        try:
            if not os.path.exists(self.signals_file):
                df = pd.DataFrame(columns=self.SIGNAL_COLUMNS)
                df.to_csv(self.signals_file, index=False)
                print("✅ Arquivo de sinais criado")
            return True
        except Exception as e:
            print(f"❌ Erro na verificação de integridade: {e}")
            return False
    
    def limpar_sinais_abertos_do_dia_anterior(self) -> None:
        """Remove todos os sinais com status 'OPEN' do dia anterior."""
        try:
            if not os.path.exists(self.signals_file):
                print("⚠️ Arquivo de sinais não encontrado para limpeza.")
                return

            df = pd.read_csv(self.signals_file)
            
            # Converter entry_time para datetime
            df['entry_time'] = pd.to_datetime(df['entry_time'])
            
            # Definir a data de corte como o início do dia atual
            hoje_inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Manter apenas sinais que NÃO estão 'OPEN' OU que são de HOJE
            df_cleaned = df[
                (df['status'] != 'OPEN') | 
                (df['entry_time'] >= hoje_inicio)
            ].copy() # Use .copy() para evitar SettingWithCopyWarning

            # Opcional: Migrar sinais 'OPEN' antigos para o histórico antes de deletar
            # Se você quiser manter um registro dos sinais 'OPEN' que foram fechados pela limpeza diária
            # old_open_signals = df[
            #     (df['status'] == 'OPEN') & 
            #     (df['entry_time'] < hoje_inicio)
            # ].copy()
            # if not old_open_signals.empty:
            #     old_open_signals['status'] = 'CLEANED_DAILY' # Marcar como limpo pela rotina
            #     old_open_signals['exit_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            #     old_open_signals.to_csv(self.history_file, mode='a', header=not os.path.exists(self.history_file), index=False)
            #     print(f"✨ {len(old_open_signals)} sinais 'OPEN' antigos migrados para histórico.")

            # Salvar o DataFrame limpo de volta no arquivo de sinais
            df_cleaned.to_csv(self.signals_file, index=False)
            print("✨ Sinais 'OPEN' do dia anterior limpos com sucesso.")

        except Exception as e:
            print(f"❌ Erro ao limpar sinais 'OPEN' do dia anterior: {e}")
            traceback.print_exc()

    def limpar_sinais_antigos(self, dias: int = 7) -> None:
        try:
            df = pd.read_csv(self.signals_file)
            df['entry_time'] = pd.to_datetime(df['entry_time'])
            cutoff_date = datetime.now() - timedelta(days=dias)
            df = df[df['entry_time'] >= cutoff_date]
            df.to_csv(self.signals_file, index=False)
        except Exception as e:
            print(f"❌ Erro ao limpar sinais antigos: {e}")
    
    def migrar_sinais(self) -> None:
        try:
            if not os.path.exists(self.signals_file):
                return
            df = pd.read_csv(self.signals_file)
            df['entry_time'] = pd.to_datetime(df['entry_time'])
            cutoff_date = datetime.now() - timedelta(days=30)
            old_signals = df[df['entry_time'] < cutoff_date]
            if not old_signals.empty:
                old_signals.to_csv(self.history_file, mode='a', header=False, index=False)
                df = df[df['entry_time'] >= cutoff_date]
                df.to_csv(self.signals_file, index=False)
        except Exception as e:
            print(f"❌ Erro ao migrar sinais: {e}")

    # Adicionar este método para limpar sinais manualmente
    def clear_signals(self, status_to_clear: Optional[str] = None):
        """
        Limpa sinais do arquivo CSV.
        Se status_to_clear for None, limpa todos os sinais.
        Se for 'CLOSED' ou 'OPEN', limpa apenas sinais com esse status.
        """
        try:
            if not os.path.exists(self.signals_file):
                print(f"Arquivo de sinais não encontrado: {self.signals_file}")
                # Criar um arquivo vazio com cabeçalhos se não existir
                self._empty_df.to_csv(self.signals_file, index=False)
                print(f"Arquivo de sinais vazio criado: {self.signals_file}")
                return

            df = pd.read_csv(self.signals_file)

            initial_count = len(df)
            cleaned_count = 0
            df_cleaned = df.copy() # Começa com uma cópia do dataframe original

            if status_to_clear is None:
                # Limpar todos os sinais
                df_cleaned = self._empty_df.copy()
                cleaned_count = initial_count
                print("🧹 Limpando TODOS os sinais...")
            elif status_to_clear.upper() == 'CLOSED':
                # Manter apenas sinais que NÃO são 'CLOSED'
                df_cleaned = df[df['status'] != 'CLOSED'].copy()
                cleaned_count = initial_count - len(df_cleaned)
                print("🧹 Limpando sinais com status 'CLOSED'...")
            elif status_to_clear.upper() == 'OPEN':
                 # Manter apenas sinais que NÃO são 'OPEN'
                df_cleaned = df[df['status'] != 'OPEN'].copy()
                cleaned_count = initial_count - len(df_cleaned)
                print("🧹 Limpando sinais com status 'OPEN'...")
            else:
                print(f"⚠️ Status '{status_to_clear}' inválido para limpeza. Use 'CLOSED', 'OPEN' ou deixe vazio para limpar todos.")
                return # Não salva se o status for inválido

            # Salvar arquivo atualizado
            df_cleaned.to_csv(self.signals_file, index=False)

            print(f"✅ Limpeza concluída. {cleaned_count} sinais removidos.")

        except Exception as e:
            print(f"❌ Erro ao limpar sinais: {e}")