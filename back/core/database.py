import pandas as pd
# --- Início da Edição ---
# Importar 'cast' do módulo typing
from typing import Dict, Any, Optional, List, cast
import math # Importar math para usar math.isnan
import os
from datetime import datetime, timedelta # Adicionado timedelta
import traceback
import csv # Importa o módulo csv
import numpy as np # Adicione esta importação para usar numpy.nan_to_num
import uuid # Adicionado para gerar tokens únicos

def snake_to_camel_case(snake_str: str) -> str:
    """Converte uma string de snake_case para camelCase."""
    components = snake_str.split('_')
    # Capitaliza a primeira letra de cada componente, exceto o primeiro, e os une
    return components[0] + ''.join(x.title() for x in components[1:])

class Database:
    def __init__(self):
        # Define os caminhos dos arquivos CSV
        self.signals_list_file = os.path.join(os.path.dirname(__file__), '..', 'sinais_lista.csv')
        self.signals_history_file = os.path.join(os.path.dirname(__file__), '..', 'signals_history.csv')
        self.config_file = os.path.join(os.path.dirname(__file__), '..', 'config.csv')
        self.users_file = os.path.join(os.path.dirname(__file__), '..', 'users.csv')
        self.tickers_file = os.path.join(os.path.dirname(__file__), '..', 'tickers.csv') # Adicionado caminho para tickers.csv
        self.password_reset_tokens_file = os.path.join(os.path.dirname(__file__), '..', 'password_reset_tokens.csv') # Novo arquivo para tokens de redefinição
        self.auth_tokens_file = os.path.join(os.path.dirname(__file__), '..', 'auth_tokens.csv') # Adicionado caminho para auth_tokens.csv

        # Define os cabeçalhos para cada arquivo CSV
        self.files_to_check = {
            self.signals_list_file: [
                'symbol', 'type', 'entry_price', 'entry_time', 
                'target_price', 'projection_percentage', 'signal_class', 'status',
                'confirmed_at', 'confirmation_reasons', 'confirmation_attempts',
                'quality_score', 'btc_correlation', 'btc_trend'
            ],
            self.signals_history_file: [
                'symbol', 'type', 'entry_price', 'entry_time', 
                'target_price', 'projection_percentage', 'signal_class', 'status', 
                'exit_price', 'result', 'confirmed_at', 'confirmation_reasons', 
                'confirmation_attempts', 'quality_score', 'btc_correlation', 'btc_trend'
            ],
            self.config_file: ['key', 'value'],
            self.users_file: ['username', 'password', 'email', 'is_admin', 'id', 'status'], # Adicionado 'status'
            self.tickers_file: ['symbol', 'baseAsset', 'quoteAsset'], # Colunas para tickers
            self.password_reset_tokens_file: ['user_id', 'token', 'expiration_time', 'used'], # Colunas para tokens de redefinição
            self.auth_tokens_file: ['token', 'user_id', 'created_at', 'expires_at'] # Colunas para tokens de autenticação
        }

        # Garante que os arquivos existam
        self._ensure_files_exist()

        # Carrega configurações iniciais
        self.config = self._load_config()

    def _ensure_files_exist(self):
        """Garante que os arquivos CSV necessários existam, criando-os se não."""
        for file_path, headers in self.files_to_check.items(): # Usar self.files_to_check
            if not os.path.exists(file_path):
                try:
                    with open(file_path, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(headers)
                    print(f"✅ Arquivo criado: {file_path}")
                except Exception as e:
                    print(f"❌ Erro ao criar arquivo {file_path}: {e}")
                    traceback.print_exc()

    def _load_config(self) -> Dict[str, str]:
        """Carrega as configurações do arquivo config.csv."""
        config_data = {}
        if os.path.exists(self.config_file):
            try:
                df = pd.read_csv(self.config_file)
                if not df.empty:
                    # Converte o DataFrame para um dicionário
                    # Garante que não há NaNs antes de converter para int/str
                    for index, row in df.iterrows():
                        # --- Início da Edição ---
                        # Usar 'bool()' para garantir um booleano escalar para a condição, satisfazendo o Pyright
                        key = str(row['key']) if not bool(pd.isna(row['key'])) else None
                        value = str(row['value']) if not bool(pd.isna(row['value'])) else None
                        # --- Fim da Edição ---
                        if key is not None:
                            config_data[key] = value
            except Exception as e:
                print(f"❌ Erro ao carregar configurações do {self.config_file}: {e}")
                traceback.print_exc()
        return config_data

    def get_config(self) -> Dict[str, str]:
        """Obtém todas as configurações."""
        return self.config

    def get_config_value(self, key: str) -> Optional[str]:
        """Obtém um valor de configuração pela chave."""
        return self.config.get(key)

    def set_config(self, key: str, value: str) -> None:
        """Define ou atualiza um valor de configuração e salva no arquivo."""
        self.config[key] = value
        try:
            # Converte o dicionário de volta para DataFrame e salva
            # Explicitamente criar um pd.Index para as colunas para satisfazer o type checker
            df = pd.DataFrame(list(self.config.items()), columns=pd.Index(['key', 'value']))
            df.to_csv(self.config_file, index=False)
            print(f"✅ Configuração '{key}' salva.")
        except Exception as e:
            print(f"❌ Erro ao salvar configuração no {self.config_file}: {e}")
            traceback.print_exc()

    def add_signal(self, signal_data: Dict[str, Any]) -> bool: # Adicionado tipo de retorno bool
        """Adiciona um novo sinal ao arquivo sinais_lista.csv e ao Supabase, verificando duplicatas por dia."""
        try:
            # Padronizar tipos de sinal
            signal_type = signal_data.get('type', '').upper()
            if signal_type in ['LONG', 'BUY']:
                signal_data['type'] = 'COMPRA'
            elif signal_type in ['SHORT', 'SELL']:
                signal_data['type'] = 'VENDA'
            
            # Tentar salvar no Supabase primeiro
            supabase_success = self._save_to_supabase(signal_data)
            if supabase_success:
                print(f"✅ Sinal salvo no Supabase: {signal_data.get('symbol')}")
            
            # Cria um DataFrame com o novo sinal
            new_signal_df = pd.DataFrame([signal_data])

            # Converte a entry_time do novo sinal para datetime para comparação
            new_signal_time = datetime.strptime(signal_data['entry_time'], '%Y-%m-%d %H:%M:%S')
            new_signal_date = new_signal_time.date() # Extrai apenas a data (dia, mês, ano)

            # Inicializa updated_df com o novo sinal por padrão
            updated_df = new_signal_df

            # Verifica se o arquivo existe e tem conteúdo
            if os.path.exists(self.signals_list_file) and os.path.getsize(self.signals_list_file) > 0:
                # Lê o arquivo existente
                existing_df = pd.read_csv(self.signals_list_file)

                # Converte a coluna entry_time do DataFrame existente para datetime
                existing_df['entry_time'] = pd.to_datetime(existing_df['entry_time'])

                # Verifica se já existe um sinal para este símbolo no dia atual
                existing_signal_today = existing_df[
                    (existing_df['symbol'] == signal_data['symbol']) &
                    (existing_df['entry_time'].dt.date == new_signal_date) # Esta é a verificação chave
                ]

                if not existing_signal_today.empty:
                    print(f"⚠️ Sinal duplicado para {signal_data.get('symbol')} no dia {new_signal_date}. Não adicionado.")
                    return False # Sinal duplicado, não adiciona

                # Adiciona o novo sinal ao DataFrame existente
                # Garante que as colunas são consistentes antes de concatenar
                # Preenche colunas ausentes no new_signal_df com NaN para evitar erros de concatenação
                updated_df = pd.concat([existing_df, new_signal_df], ignore_index=True)
            
            # Garante que a coluna entry_time é datetime mesmo no primeiro sinal ou se o arquivo estava vazio
            updated_df['entry_time'] = pd.to_datetime(updated_df['entry_time'])

            # Salva o DataFrame atualizado de volta no arquivo
            updated_df.to_csv(self.signals_list_file, index=False)
            print(f"✅ Sinal adicionado para {signal_data.get('symbol')}")
            return True # Sinal adicionado com sucesso

        except Exception as e:
            print(f"❌ Erro ao adicionar sinal: {e}")
            traceback.print_exc()
            return False

    def get_auth_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Busca um token de autenticação no banco de dados"""
        try:
            if not os.path.exists(self.auth_tokens_file):
                return None
                
            df = pd.read_csv(self.auth_tokens_file)
            if df.empty:
                return None
                
            # Buscar token específico
            token_row = df[df['token'] == token]
            if token_row.empty:
                return None
                
            # Converter para dicionário
            token_data = token_row.iloc[0].to_dict()
            return token_data
            
        except Exception as e:
            print(f"❌ Erro ao buscar token de autenticação: {e}")
            traceback.print_exc()
            return None

    def remove_auth_token(self, token: str) -> bool:
        """Remove um token de autenticação do banco de dados"""
        try:
            if not os.path.exists(self.auth_tokens_file):
                return False
                
            df = pd.read_csv(self.auth_tokens_file)
            if df.empty:
                return False
                
            # Remover token específico
            df_filtered = df[df['token'] != token]
            
            # Salvar de volta
            df_filtered.to_csv(self.auth_tokens_file, index=False)
            print(f"✅ Token de autenticação removido: {token[:8]}...")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao remover token de autenticação: {e}")
            traceback.print_exc()
            return False
    
    def _save_to_supabase(self, signal_data: Dict[str, Any]) -> bool:
        """Salva o sinal no banco de dados Supabase"""
        try:
            # Verificar se as variáveis de ambiente do Supabase estão configuradas
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_ANON_KEY')
            
            if not supabase_url or not supabase_key:
                print("⚠️ Supabase não configurado, salvando apenas em CSV")
                return False
            
            # Importar Supabase apenas quando necessário
            try:
                from supabase import create_client, Client
            except ImportError:
                print("⚠️ Biblioteca Supabase não instalada, salvando apenas em CSV")
                return False
            
            # Criar cliente Supabase
            supabase: Client = create_client(supabase_url, supabase_key)
            
            # Preparar dados para o Supabase (apenas campos que existem na tabela)
            from datetime import timezone
            import pytz
            
            # Garantir timestamp UTC para created_at
            entry_time_str = signal_data.get('entry_time')
            if entry_time_str:
                try:
                    # Converter entry_time para UTC se necessário
                    if isinstance(entry_time_str, str):
                        # Assumir que entry_time está em horário de São Paulo
                        sao_paulo_tz = pytz.timezone('America/Sao_Paulo')
                        entry_dt = datetime.strptime(entry_time_str, '%Y-%m-%d %H:%M:%S')
                        entry_dt_sp = sao_paulo_tz.localize(entry_dt)
                        entry_dt_utc = entry_dt_sp.astimezone(timezone.utc)
                        created_at_utc = entry_dt_utc.isoformat()
                    else:
                        created_at_utc = datetime.now(timezone.utc).isoformat()
                except Exception as e:
                    print(f"⚠️ Erro ao converter entry_time: {e}")
                    created_at_utc = datetime.now(timezone.utc).isoformat()
            else:
                created_at_utc = datetime.now(timezone.utc).isoformat()
            
            supabase_data = {
                'symbol': signal_data.get('symbol'),
                'type': signal_data.get('type'),
                'entry_price': float(signal_data.get('entry_price', 0)),
                'target_price': float(signal_data.get('target_price', 0)),
                'status': signal_data.get('status', 'OPEN'),
                'entry_time': signal_data.get('entry_time'),
                'created_at': created_at_utc,  # Garantir created_at em UTC
                'quality_score': float(signal_data.get('quality_score', 0))
            }
            
            # Inserir no Supabase
            result = supabase.table('signals').insert(supabase_data).execute()
            
            if result.data:
                return True
            else:
                print(f"⚠️ Falha ao salvar no Supabase: {result}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao salvar no Supabase: {e}")
            traceback.print_exc()
            return False

    def verify_auth_token(self, token: str) -> Optional[str]:
        """Verifica se um token de autenticação é válido e retorna o user_id"""
        try:
            if os.path.exists(self.auth_tokens_file):
                df = pd.read_csv(self.auth_tokens_file)
                
                # Buscar token
                token_row = df[df['token'] == token]
                
                if len(token_row) > 0:
                    token_data = token_row.iloc[0]
                    expires_at = pd.to_datetime(token_data['expires_at'])
                    
                    # Verificar se não expirou
                    if datetime.now() < expires_at:
                        return str(token_data['user_id'])
                    else:
                        # Token expirado, remover
                        self.remove_auth_token(token)
                        
            return None
            
        except Exception as e:
            print(f"Erro ao verificar token de autenticação: {e}")
            return None

    def save_auth_token(self, token: str, user_id: int, expires_at: datetime):
        """Salva um token de autenticação no arquivo CSV"""
        try:
            # Lê o arquivo existente ou cria um DataFrame vazio
            try:
                tokens_df = pd.read_csv(self.auth_tokens_file)
            except (pd.errors.EmptyDataError, FileNotFoundError):
                tokens_df = pd.DataFrame(columns=['token', 'user_id', 'created_at', 'expires_at'])
            
            # Remove tokens antigos para o mesmo usuário
            tokens_df = tokens_df[tokens_df['user_id'] != user_id]
            
            # Adiciona o novo token
            new_token_data = pd.DataFrame([{
                'token': token,
                'user_id': user_id,
                'created_at': datetime.now().isoformat(),
                'expires_at': expires_at.isoformat()
            }])
            
            tokens_df = pd.concat([tokens_df, new_token_data], ignore_index=True)
            tokens_df.to_csv(self.auth_tokens_file, index=False)
            
            print(f"✅ Token de autenticação salvo para usuário {user_id}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar token de autenticação: {e}")
            traceback.print_exc()
            return False # Indica que ocorreu um erro

    def update_signal_status(self, symbol: str, entry_time: str, status: str, exit_price: Optional[float] = None, variation: Optional[float] = None, result: Optional[str] = None) -> None:
        """Atualiza o status de um sinal no sinais_lista.csv e move para signals_history.csv se fechado."""
        try:
            if not os.path.exists(self.signals_list_file):
                print(f"❌ Arquivo de sinais {self.signals_list_file} não encontrado.")
                return

            df = pd.read_csv(self.signals_list_file)

            # Encontra a linha do sinal a ser atualizado
            # Usamos symbol e entry_time para identificar unicamente o sinal
            signal_index = df[(df['symbol'] == symbol) & (df['entry_time'] == entry_time)].index

            if signal_index.empty:
                print(f"❌ Sinal não encontrado para atualização: {symbol} @ {entry_time}")
                return

            # Atualiza os campos
            df.loc[signal_index, 'status'] = status
            if exit_price is not None:
                df.loc[signal_index, 'exit_price'] = exit_price
            if variation is not None:
                df.loc[signal_index, 'variation'] = variation
            if result is not None:
                df.loc[signal_index, 'result'] = result

            # Se o status for 'CLOSED', move o sinal para o histórico
            if status == 'CLOSED':
                closed_signal = df.loc[signal_index].copy()

                # Adiciona ao arquivo de histórico
                if os.path.exists(self.signals_history_file) and os.path.getsize(self.signals_history_file) > 0:
                    history_df = pd.read_csv(self.signals_history_file)
                    # Garante que as colunas do histórico correspondem
                    # Pode ser necessário mapear colunas se forem diferentes
                    # Exemplo simples:
                    # history_df = pd.concat([history_df, closed_signal[history_df.columns]], ignore_index=True)
                    # Para garantir que todas as colunas esperadas no history_df estejam presentes no closed_signal
                    # e vice-versa, preenchendo com NaN se necessário.
                    # Primeiro, garanta que as colunas do closed_signal correspondam às do history_df
                    # e adicione colunas ausentes com NaN
                    for col in history_df.columns:
                        if col not in closed_signal.columns:
                            closed_signal[col] = np.nan
                    # Em seguida, selecione apenas as colunas que existem no history_df
                    closed_signal_for_history = closed_signal[history_df.columns]
                    history_df = pd.concat([history_df, closed_signal_for_history], ignore_index=True)
                else:
                    # Se o arquivo de histórico não existe ou está vazio, cria um novo com o sinal fechado
                    # Assegura que as colunas do closed_signal são um subconjunto ou mapeáveis para as do history
                    history_headers = self.files_to_check[self.signals_history_file] # Usar self.files_to_check
                    for col in history_headers:
                        if col not in closed_signal.columns:
                            closed_signal[col] = np.nan
                    history_df = closed_signal[history_headers]

                history_df.to_csv(self.signals_history_file, index=False)
                print(f"✅ Sinal {symbol} movido para histórico.")

                # Remove o sinal do arquivo de sinais ativos
                df = df.drop(index=signal_index.to_list()) # Alterado para usar index=signal_index.to_list()
                print(f"✅ Sinal {symbol} removido da lista de sinais ativos.")

            # Salva o DataFrame atualizado de volta no sinais_lista.csv
            df.to_csv(self.signals_list_file, index=False)
            print(f"✅ Status do sinal {symbol} atualizado para '{status}'.")

        except Exception as e:
            print(f"❌ Erro ao atualizar status do sinal: {e}")
            traceback.print_exc()

    def get_all_signals(self) -> List[Dict[str, Any]]:
        """Retorna todos os sinais do sinais_lista.csv."""
        if not os.path.exists(self.signals_list_file) or os.path.getsize(self.signals_list_file) == 0:
            return []
        try:
            df = pd.read_csv(self.signals_list_file)
            # Converte o DataFrame para uma lista de dicionários
            # Substitui NaN por None para melhor representação em JSON
            return df.replace({np.nan: None}).to_dict(orient='records')
        except Exception as e:
            print(f"❌ Erro ao carregar sinais: {e}")
            traceback.print_exc()
            return []

    def get_signal_by_symbol(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Retorna um sinal específico pelo símbolo."""
        signals = self.get_all_signals()
        for signal in signals:
            if signal.get('symbol') == symbol:
                return signal
        return None

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Retorna todos os usuários do users.csv."""
        if not os.path.exists(self.users_file) or os.path.getsize(self.users_file) == 0:
            return []
        try:
            df = pd.read_csv(self.users_file)
            # Garante que a coluna 'id' é tratada como string para evitar problemas com UUIDs
            df['id'] = df['id'].astype(str)
            # Converte is_admin para boolean explicitamente
            if 'is_admin' in df.columns:
                df['is_admin'] = df['is_admin'].map(lambda x: str(x).lower() == 'true' if pd.notna(x) else False)
            return df.replace({np.nan: None}).to_dict(orient='records')
        except Exception as e:
            print(f"❌ Erro ao carregar usuários: {e}")
            traceback.print_exc()
            return []

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Retorna um usuário pelo nome de usuário."""
        users = self.get_all_users()
        for user in users:
            if user.get('username') == username:
                return user
        return None

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Retorna um usuário pelo e-mail."""
        users = self.get_all_users()
        for user in users:
            if user.get('email') == email:
                return user
        return None

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retorna um usuário pelo ID."""
        users = self.get_all_users()
        for user in users:
            if user.get('id') == user_id:
                return user
        return None

    def add_user(self, user_data: Dict[str, Any]) -> bool:
        """Adiciona um novo usuário ao users.csv."""
        try:
            # Garante que o ID é uma string
            user_data['id'] = str(user_data.get('id', uuid.uuid4())) # Gera um novo UUID se não fornecido
            new_user_df = pd.DataFrame([user_data])

            if os.path.exists(self.users_file) and os.path.getsize(self.users_file) > 0:
                existing_df = pd.read_csv(self.users_file)
                # Verifica se o usuário já existe pelo username ou id
                if user_data['username'] in existing_df['username'].values:
                    print(f"⚠️ Usuário '{user_data['username']}' já existe.")
                    return False
                if user_data['id'] in existing_df['id'].astype(str).values: # Converte para str para comparação
                    print(f"⚠️ ID de usuário '{user_data['id']}' já existe.")
                    return False

                updated_df = pd.concat([existing_df, new_user_df], ignore_index=True)
            else:
                updated_df = new_user_df

            updated_df.to_csv(self.users_file, index=False)
            print(f"✅ Usuário '{user_data['username']}' adicionado.")
            return True
        except Exception as e:
            print(f"❌ Erro ao adicionar usuário: {e}")
            traceback.print_exc()
            return False

    def create_user(self, username: str, email: str, password: str, is_admin: bool = False) -> bool:
        """Cria um novo usuário com hash da senha."""
        try:
            import bcrypt
            
            # Gerar hash da senha
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            user_data = {
                'id': str(uuid.uuid4()),
                'username': username,
                'email': email,
                'password': password_hash,
                'is_admin': is_admin,
                'status': 'pending'  # Usuários criados ficam pendentes por padrão
            }
            
            return self.add_user(user_data)
            
        except Exception as e:
            print(f"❌ Erro ao criar usuário: {e}")
            traceback.print_exc()
            return False

    def update_user_password(self, user_id: str, new_password_hash: str) -> bool:
        """Atualiza a senha de um usuário pelo ID."""
        try:
            # DEBUG DB: Tentando atualizar senha para user_id: '{user_id}' (type: {type(user_id)})" # Removed debug print
            if not os.path.exists(self.users_file):
                print(f"❌ Arquivo de usuários {self.users_file} não encontrado.")
                return False

            df = pd.read_csv(self.users_file)
            # print(f"DEBUG DB: DataFrame de usuários lido. Colunas: {df.columns.tolist()}") # Removed debug print
            # print(f"DEBUG DB: Primeiras linhas do DataFrame:\n{df.head()}") # Removed debug print

            # Garante que a coluna 'id' é tratada como string para comparação
            df['id'] = df['id'].astype(str)
            # print(f"DEBUG DB: Coluna 'id' convertida para string. Tipos de dados:\n{df.dtypes}") # Removed debug print
            # print(f"DEBUG DB: IDs existentes no DataFrame: {df['id'].tolist()}") # Removed debug print

            user_index = df[df['id'] == user_id].index
            # print(f"DEBUG DB: user_index encontrado: {user_index.tolist()}") # Removed debug print

            if user_index.empty:
                print(f"❌ Usuário com ID '{user_id}' não encontrado para atualização de senha.")
                return False

            df.loc[user_index, 'password'] = new_password_hash
            df.to_csv(self.users_file, index=False)
            print(f"✅ Senha do usuário com ID '{user_id}' atualizada com sucesso.")
            return True
        except Exception as e:
            print(f"❌ Erro ao atualizar senha do usuário: {e}")
            traceback.print_exc()
            return False

    def create_password_reset_token(self, user_id: str) -> Optional[str]:
        """
        Cria e armazena um token de redefinição de senha para um user_id.
        Retorna o token gerado ou None em caso de erro.
        """
        try:
            token = str(uuid.uuid4())
            expiration_time = (datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S') # Token válido por 1 hora
            token_data = {
                'user_id': user_id,
                'token': token,
                'expiration_time': expiration_time,
                'used': False
            }
            new_token_df = pd.DataFrame([token_data])

            if os.path.exists(self.password_reset_tokens_file) and os.path.getsize(self.password_reset_tokens_file) > 0:
                existing_df = pd.read_csv(self.password_reset_tokens_file)
                updated_df = pd.concat([existing_df, new_token_df], ignore_index=True)
            else:
                updated_df = new_token_df

            updated_df.to_csv(self.password_reset_tokens_file, index=False)
            print(f"✅ Token de redefinição de senha criado para o usuário {user_id}.")
            return token
        except Exception as e:
            print(f"❌ Erro ao criar token de redefinição de senha: {e}")
            traceback.print_exc()
            return None

    def get_password_reset_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Recupera um token de redefinição de senha e verifica sua validade.
        Retorna os dados do token se válido, caso contrário, None.
        """
        try:
            if not os.path.exists(self.password_reset_tokens_file) or os.path.getsize(self.password_reset_tokens_file) == 0:
                return None

            df = pd.read_csv(self.password_reset_tokens_file)
            # Garante que a coluna 'used' é booleana
            df['used'] = df['used'].astype(bool)
            # Garante que a coluna 'user_id' é tratada como string
            df['user_id'] = df['user_id'].astype(str) # Adicionada esta linha

            token_record = df[(df['token'] == token) & (df['used'] == False)]

            if token_record.empty:
                print(f"❌ Token '{token}' não encontrado ou já utilizado.")
                return None

            token_data = token_record.iloc[0].to_dict()
            expiration_time = datetime.strptime(token_data['expiration_time'], '%Y-%m-%d %H:%M:%S')

            if datetime.now() > expiration_time:
                print(f"❌ Token '{token}' expirado.")
                return None

            return token_data
        except Exception as e:
            print(f"❌ Erro ao obter token de redefinição de senha: {e}")
            traceback.print_exc()
            return None

    def mark_token_as_used(self, token: str) -> bool:
        """
        Marca um token de redefinição de senha como usado.
        """
        try:
            if not os.path.exists(self.password_reset_tokens_file):
                print(f"❌ Arquivo de tokens de redefinição de senha {self.password_reset_tokens_file} não encontrado.")
                return False

            df = pd.read_csv(self.password_reset_tokens_file)
            token_index = df[df['token'] == token].index

            if token_index.empty:
                print(f"❌ Token '{token}' não encontrado para marcar como usado.")
                return False

            df.loc[token_index, 'used'] = True
            df.to_csv(self.password_reset_tokens_file, index=False)
            print(f"✅ Token '{token}' marcado como usado.")
            return True
        except Exception as e:
            print(f"❌ Erro ao marcar token como usado: {e}")
            traceback.print_exc()
            return False

    def get_all_tickers(self) -> List[Dict[str, Any]]:
        """Retorna todos os tickers do tickers.csv."""
        if not os.path.exists(self.tickers_file) or os.path.getsize(self.tickers_file) == 0:
            return []
        try:
            df = pd.read_csv(self.tickers_file)
            return df.replace({np.nan: None}).to_dict(orient='records')
        except Exception as e:
            print(f"❌ Erro ao carregar tickers: {e}")
            traceback.print_exc()
            return []

    def add_ticker(self, ticker_data: Dict[str, Any]) -> bool:
        """Adiciona um novo ticker ao tickers.csv."""
        try:
            new_ticker_df = pd.DataFrame([ticker_data])

            if os.path.exists(self.tickers_file) and os.path.getsize(self.tickers_file) > 0:
                existing_df = pd.read_csv(self.tickers_file)
                if ticker_data['symbol'] in existing_df['symbol'].values:
                    print(f"⚠️ Ticker '{ticker_data['symbol']}' já existe.")
                    return False
                updated_df = pd.concat([existing_df, new_ticker_df], ignore_index=True)
            else:
                updated_df = new_ticker_df

            updated_df.to_csv(self.tickers_file, index=False)
            print(f"✅ Ticker '{ticker_data['symbol']}' adicionado.")
            return True
        except Exception as e:
            print(f"❌ Erro ao adicionar ticker: {e}")
            traceback.print_exc()
            return False

    def delete_ticker(self, symbol: str) -> bool:
        """Deleta um ticker do tickers.csv pelo símbolo."""
        try:
            if not os.path.exists(self.tickers_file):
                print(f"❌ Arquivo de tickers {self.tickers_file} não encontrado.")
                return False

            df = pd.read_csv(self.tickers_file)
            initial_rows = len(df)
            df = df[df['symbol'] != symbol]

            if len(df) == initial_rows:
                print(f"❌ Ticker '{symbol}' não encontrado para exclusão.")
                return False

            df.to_csv(self.tickers_file, index=False)
            print(f"✅ Ticker '{symbol}' excluído com sucesso.")
            return True
        except Exception as e:
            print(f"❌ Erro ao deletar ticker: {e}")
            traceback.print_exc()
            return False


### 2. Adição de métodos em `c:\Users\spcom\Desktop\backend1.1\core\database.py`

### Você precisará adicionar os seguintes métodos à sua classe `Database` no arquivo <mcfile name="database.py" path="c:\Users\spcom\Desktop\backend1.1\core\database.py"></mcfile>. Se o arquivo não existir ou tiver um nome diferente, por favor, me avise

    def store_auth_token(self, user_id: int, token: str, expires_in_minutes: int = 60):
        """
        Armazena um token de autenticação para um usuário com um tempo de expiração.
        Remove tokens antigos para o mesmo usuário para garantir apenas um token ativo por vez.
        """
        try:
            tokens_df = pd.read_csv(self.auth_tokens_file)
        except pd.errors.EmptyDataError:
            # Correção para o erro de tipagem do Pyright: explicitamente usando pd.Index para as colunas
            tokens_df = pd.DataFrame([], columns=pd.Index(['token', 'user_id', 'created_at', 'expires_at']))

        # Remover quaisquer tokens existentes para este user_id para garantir apenas um token ativo por usuário
        tokens_df = tokens_df[tokens_df['user_id'] != user_id]

        created_at = datetime.now()
        expires_at = created_at + timedelta(minutes=expires_in_minutes)

        new_token_data = pd.DataFrame([{
            'token': token,
            'user_id': user_id,
            'created_at': created_at.isoformat(),
            'expires_at': expires_at.isoformat()
        }])
        tokens_df = pd.concat([tokens_df, new_token_data], ignore_index=True)
        tokens_df.to_csv(self.auth_tokens_file, index=False)
        return True
    
    def get_user_by_token(self, token: str):
        """
        Recupera os dados do usuário com base em um token de autenticação, verificando a expiração.
        Retorna os dados do usuário se o token for válido e não expirado, caso contrário, None.
        """
        # print(f"DEBUG DB: get_user_by_token chamado com token: {token}") # Removido
        try:
            tokens_df = pd.read_csv(self.auth_tokens_file)
            # print(f"DEBUG DB: auth_tokens.csv lido. Conteúdo:\n{tokens_df}") # Removido
        except pd.errors.EmptyDataError:
            # print("DEBUG DB: auth_tokens.csv está vazio.") # Removido
            return None
        except FileNotFoundError:
            # print("DEBUG DB: auth_tokens.csv não encontrado.") # Removido
            return None
        except Exception as e:
            print(f"❌ Erro ao ler auth_tokens.csv: {e}") # Mantido para erros críticos
            traceback.print_exc()
            return None

        now = datetime.now()
        # print(f"DEBUG DB: Hora atual para verificação de expiração: {now}") # Removido
        
        # Garante que 'expires_at' é do tipo datetime para comparação
        tokens_df['expires_at'] = pd.to_datetime(tokens_df['expires_at'])

        # Filtrar pelo token e garantir que não está expirado
        valid_tokens = tokens_df[
            (tokens_df['token'] == token) &
            (tokens_df['expires_at'] > now)
        ]
        # print(f"DEBUG DB: Tokens válidos encontrados após filtragem:\n{valid_tokens}") # Removido

        if not valid_tokens.empty:
            token_record = valid_tokens.iloc[0]
            user_id = str(token_record['user_id']) # Converte explicitamente para string
            # print(f"DEBUG DB: Token válido encontrado. user_id associado: {user_id} (type: {type(user_id)})") # Removido
            
            user_data = self.get_user_by_id(user_id)
            # print(f"DEBUG DB: Resultado de get_user_by_id para user_id {user_id}: {user_data}") # Removido
            return user_data 
        else:
            # print(f"DEBUG DB: Nenhum token válido encontrado para '{token}' ou token expirado.") # Removido
            pass # Não é necessário imprimir nada aqui se o token não for encontrado/válido
        return None

    def save_signal_to_database(self, signal_data):
        """
        Salva um sinal no banco de dados (CSV)
        """
        try:
            # Adicionar o sinal à lista de sinais
            return self.add_signal(signal_data)
        except Exception as e:
            print(f"Erro ao salvar sinal no banco: {e}")
            return False
    
    def execute_query(self, query: str, params: tuple = None) -> Any:
        """
        Método de compatibilidade para execução de queries SQL
        Como estamos usando CSV, este método apenas simula a execução
        Para um banco real, implementar a lógica SQL apropriada
        """
        try:
            print(f"📝 Simulando execução de query: {query[:100]}...")
            # Para CSV, não executamos queries SQL reais
            # Este método existe apenas para compatibilidade
            return True
        except Exception as e:
            print(f"❌ Erro na simulação de query: {e}")
            return False
    
    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """
        Método de compatibilidade para buscar um registro
        """
        print(f"🔍 Simulando fetch_one: {query[:50]}...")
        return None
    
    def fetch_all(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        Método de compatibilidade para buscar múltiplos registros
        """
        print(f"🔍 Simulando fetch_all: {query[:50]}...")
        return []