import pandas as pd
import os
import csv
import traceback  # Adicionando import do traceback
from datetime import datetime, timedelta
import pytz  # Adicionar esta importação
from typing import Dict, List, Optional, Union, Any
from pandas import DataFrame, Series
from .database import Database

class GerenciadorSinais:
    def __init__(self, db_instance):
        self.db = db_instance
        # Usar caminhos absolutos para os arquivos CSV
        import os
        base_dir = os.path.dirname(os.path.dirname(__file__))
        self.signals_file = os.path.join(base_dir, 'sinais_lista.csv')
        self.history_file = os.path.join(base_dir, 'historico_sinais.csv')
        # Adicionar timezone
        self.timezone = pytz.timezone('America/Sao_Paulo')
        # Colunas incluindo campos de confirmação
        self.SIGNAL_COLUMNS = pd.Index([
            'symbol', 'type', 'entry_price', 'entry_time',
            'target_price', 'projection_percentage', 'signal_class', 'status',
            'confirmed_at', 'confirmation_reasons', 'confirmation_attempts',
            'quality_score', 'btc_correlation', 'btc_trend'
        ])
        self._empty_df = DataFrame(columns=self.SIGNAL_COLUMNS)

    def _get_signal_class(self, quality_score: float) -> Optional[str]:
        """Retorna a classificação do sinal baseado no quality_score"""
        if quality_score >= 110:
            return "ELITE+"
        elif quality_score >= 95:
            return "ELITE"
        elif quality_score >= 85:
            return "PREMIUM+"
        elif quality_score >= 80:
            return "PREMIUM"
        else:
            return None  # Não retorna classificação para scores baixos

    def save_signal(self, signal_data: Dict) -> bool:
        try:
            # Usar timezone correto
            entry_time = datetime.now(self.timezone)
            
            # Calcular porcentagem de projeção
            entry_price = float(signal_data['entry_price'])
            target_price = float(signal_data['target_price'])
            
            if signal_data['type'] == 'COMPRA':
                projection_percentage = ((target_price - entry_price) / entry_price) * 100
            else:  # VENDA
                projection_percentage = ((entry_price - target_price) / entry_price) * 100
            
            # Formatar o sinal com todos os dados incluindo motivos de confirmação
            formatted_signal = {
                'symbol': signal_data['symbol'],
                'type': signal_data['type'],
                'entry_price': entry_price,
                'entry_time': entry_time.strftime('%Y-%m-%d %H:%M:%S'),
                'target_price': target_price,
                'projection_percentage': round(projection_percentage, 2),
                'signal_class': self._get_signal_class(float(signal_data.get('quality_score', 0))),
                'status': 'OPEN',
                # Adicionar campos de confirmação se existirem
                'confirmed_at': signal_data.get('confirmed_at'),
                'confirmation_reasons': signal_data.get('confirmation_reasons', []),
                'confirmation_attempts': signal_data.get('confirmation_attempts', 0),
                'quality_score': signal_data.get('quality_score', 0),
                'btc_correlation': signal_data.get('btc_correlation'),
                'btc_trend': signal_data.get('btc_trend')
            }
            
            result = self.db.add_signal(formatted_signal)
            if result:
                print(f"✅ Sinal salvo com sucesso: {formatted_signal['symbol']}")
            return result
            
        except Exception as e:
            print(f"❌ Erro ao salvar sinal: {str(e)}")
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
        """Processa sinais abertos baseado no horário atual de limpeza"""
        try:
            df = pd.read_csv(self.signals_file)
            
            # Converter entry_time para datetime
            df['entry_time'] = pd.to_datetime(df['entry_time'])
            
            # Converter colunas numéricas
            numeric_cols = [
                'entry_price', 'target_price', 'exit_price', 'variation',
                'quality_score', 'trend_score', 'alignment_score', 'market_score',
                'trend_strength', 'confluence_count', 'leverage'
            ]
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
        
            # Determinar horário de corte baseado na hora atual (MODO PERMISSIVO)
            agora = datetime.now(self.timezone)  # Usar timezone
            
            # NOVO: Modo mais permissivo para evitar perda de sinais durante restarts
            if agora.hour >= 21:  # Após 21:00 - mostrar sinais gerados após 10:00 de hoje
                corte = agora.replace(hour=10, minute=0, second=0, microsecond=0)
                print(f"🌙 Modo noturno: Exibindo sinais gerados após 10:00 (permissivo)")
            elif agora.hour >= 10:  # Entre 10:00-21:00 - mostrar sinais gerados após 21:00 de ontem
                ontem = agora - timedelta(days=1)
                corte = ontem.replace(hour=21, minute=0, second=0, microsecond=0)
                print(f"☀️ Modo diurno: Exibindo sinais gerados após 21:00 de ontem (permissivo)")
            else:  # Antes das 10:00 - mostrar sinais gerados após 21:00 do dia anterior
                ontem = agora - timedelta(days=1)
                corte = ontem.replace(hour=21, minute=0, second=0, microsecond=0)
                print(f"🌅 Modo madrugada: Exibindo sinais gerados após 21:00 de ontem")
            
            # Filtrar sinais após o horário de corte e com status OPEN
            result_df = df[
                (df['entry_time'] >= corte) & 
                (df['status'] == 'OPEN')
            ]
            
            print(f"📊 Filtro aplicado: {len(result_df)} sinais OPEN encontrados após {corte.strftime('%d/%m/%Y %H:%M')}")
            
            # Agrupar por symbol e pegar o sinal mais recente
            if not result_df.empty:
                result_df = (result_df
                            .sort_values(by='entry_time', ascending=False)
                            .groupby('symbol')
                            .first()
                            .reset_index())
                
                # Ordenar o resultado final por horário
                result_df = result_df.sort_values(by='entry_time', ascending=True)
            
            if isinstance(result_df, pd.Series):
                result_df = result_df.to_frame().T
            return result_df if not result_df.empty else self._empty_df.copy()
        except Exception as e:
            print(f"❌ Erro ao processar sinais abertos: {e}")
            traceback.print_exc()
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
            df.loc[mask, 'exit_time'] = datetime.now(self.timezone).strftime('%Y-%m-%d %H:%M:%S')
            
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
            
            # Define o início do dia atual
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

    def limpar_sinais_antes_das_10h(self) -> None:
        """Remove todos os sinais OPEN gerados antes das 10:00 do dia atual."""
        try:
            if not os.path.exists(self.signals_file):
                print("⚠️ Arquivo de sinais não encontrado para limpeza.")
                return

            df = pd.read_csv(self.signals_file)
            
            # Converter entry_time para datetime
            df['entry_time'] = pd.to_datetime(df['entry_time'])
            
            # Definir o horário de corte (10:00 de hoje)
            hoje = datetime.now(self.timezone).replace(hour=10, minute=0, second=0, microsecond=0)
            # Converter para timestamp do pandas sem timezone para comparação
            hoje = pd.Timestamp(hoje.replace(tzinfo=None))
            
            # Contar sinais que serão removidos
            sinais_para_remover = df[
                (df['status'] == 'OPEN') & 
                (df['entry_time'] < hoje)
            ]
            
            # Manter apenas sinais que NÃO estão 'OPEN' OU que foram gerados após as 10:00
            df_cleaned = df[
                (df['status'] != 'OPEN') | 
                (df['entry_time'] >= hoje)
            ].copy()
    
            # Salvar o DataFrame limpo
            df_cleaned.to_csv(self.signals_file, index=False)
            
            print(f"✨ {len(sinais_para_remover)} sinais OPEN anteriores às 10:00 foram removidos.")
            print(f"📊 {len(df_cleaned[df_cleaned['status'] == 'OPEN'])} sinais OPEN restantes (gerados após 10:00).")
    
        except Exception as e:
            print(f"❌ Erro ao limpar sinais antes das 10:00: {e}")
            traceback.print_exc()

    def limpar_sinais_antes_das_21h(self) -> None:
        """Remove todos os sinais OPEN gerados antes das 21:00 do dia atual."""
        try:
            if not os.path.exists(self.signals_file):
                print("⚠️ Arquivo de sinais não encontrado para limpeza.")
                return

            df = pd.read_csv(self.signals_file)
            
            # Converter entry_time para datetime
            df['entry_time'] = pd.to_datetime(df['entry_time'])
            
            # Definir o horário de corte (21:00 de hoje)
            hoje = datetime.now(self.timezone).replace(hour=21, minute=0, second=0, microsecond=0)
            # Converter para timestamp do pandas sem timezone para comparação
            hoje = pd.Timestamp(hoje.replace(tzinfo=None))
            
            # Contar sinais que serão removidos
            sinais_para_remover = df[
                (df['status'] == 'OPEN') & 
                (df['entry_time'] < hoje)
            ]
            
            # Manter apenas sinais que NÃO estão 'OPEN' OU que foram gerados após as 21:00
            df_cleaned = df[
                (df['status'] != 'OPEN') | 
                (df['entry_time'] >= hoje)
            ].copy()
    
            # Salvar o DataFrame limpo
            df_cleaned.to_csv(self.signals_file, index=False)
            
            print(f"✨ {len(sinais_para_remover)} sinais OPEN anteriores às 21:00 foram removidos.")
            print(f"📊 {len(df_cleaned[df_cleaned['status'] == 'OPEN'])} sinais OPEN restantes (gerados após 21:00).")
    
        except Exception as e:
            print(f"❌ Erro ao limpar sinais antes das 21:00: {e}")
            traceback.print_exc()

    def limpar_sinais_antigos(self) -> None:
        """Remove sinais OPEN de dias anteriores."""
        try:
            df = pd.read_csv(self.signals_file)
            df['entry_time'] = pd.to_datetime(df['entry_time'])
            
            # Define o início do dia atual
            hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Mantém apenas sinais de hoje ou sinais já fechados (CLOSED)
            df_limpo = df[
                (df['entry_time'] >= hoje) |
                (df['status'] != 'OPEN')
            ]
            
            # Salva o DataFrame limpo
            df_limpo.to_csv(self.signals_file, index=False)
            print("✅ Sinais antigos removidos com sucesso")
            
        except Exception as e:
            print(f"❌ Erro ao limpar sinais antigos: {e}")
            traceback.print_exc()

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

    def limpar_sinais_futuros(self) -> None:
        """Remove todos os sinais com datas futuras."""
        try:
            df = pd.read_csv(self.signals_file)
            df['entry_time'] = pd.to_datetime(df['entry_time'])
            
            agora = datetime.now()
            
            # Identificar sinais com datas futuras
            sinais_futuros = df['entry_time'] > agora
            
            if sinais_futuros.any():
                # Manter apenas sinais com datas válidas
                df = df[~sinais_futuros]
                df.to_csv(self.signals_file, index=False)
                print(f"✅ {sinais_futuros.sum()} sinais com datas futuras foram removidos")
            else:
                print("✨ Nenhum sinal com data futura encontrado")
                
        except Exception as e:
            print(f"❌ Erro ao limpar sinais futuros: {e}")
            traceback.print_exc()
    
    def load_signals_from_csv(self) -> List[Dict[str, Any]]:
        """Carrega todos os sinais do arquivo CSV"""
        try:
            if not os.path.exists(self.signals_file):
                print(f"⚠️ Arquivo de sinais não encontrado: {self.signals_file}")
                return []
            
            df = pd.read_csv(self.signals_file)
            
            if df.empty:
                print("📭 Arquivo de sinais está vazio")
                return []
            
            # Converter DataFrame para lista de dicionários
            signals = df.replace({pd.NA: None, float('nan'): None}).to_dict(orient='records')
            
            # Processar confirmation_reasons para garantir formato correto
            for signal in signals:
                reasons = signal.get('confirmation_reasons')
                if reasons and isinstance(reasons, str):
                    # Se é uma string, tentar converter para lista
                    if reasons.startswith('[') and reasons.endswith(']'):
                        # Formato de lista como string
                        try:
                            import ast
                            signal['confirmation_reasons'] = ast.literal_eval(reasons)
                        except:
                            # Se falhar, dividir por vírgula
                            signal['confirmation_reasons'] = [r.strip().strip("'\"") for r in reasons.strip('[]').split(',')]
                    else:
                        # String simples separada por vírgula
                        signal['confirmation_reasons'] = [r.strip() for r in reasons.split(',')]
                elif not reasons:
                    signal['confirmation_reasons'] = []
            
            print(f"📊 Carregados {len(signals)} sinais do CSV")
            return signals
            
        except Exception as e:
            print(f"❌ Erro ao carregar sinais do CSV: {e}")
            traceback.print_exc()
            return []

    # No método onde ocorre o warning
    def save_signal_to_file(self, signal_data):
        """Salva sinal no arquivo CSV com correção do warning pandas"""
        try:
            # ... existing code ...
            
            # Corrigir warning do pandas concat (linha 454)
            if not existing_df.empty and not new_signal_df.empty:
                # Verificar se há colunas vazias antes do concat
                existing_df = existing_df.dropna(how='all', axis=1)
                new_signal_df = new_signal_df.dropna(how='all', axis=1)
                updated_df = pd.concat([existing_df, new_signal_df], ignore_index=True)
            elif not new_signal_df.empty:
                updated_df = new_signal_df.copy()
            else:
                updated_df = existing_df.copy()
                
            df.to_csv(self.signals_file, index=False)
            print(f"✅ Sinal atualizado: {symbol}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao atualizar sinal: {e}")