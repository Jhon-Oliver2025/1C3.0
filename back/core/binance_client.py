from typing import Dict, Optional, List, Any
import requests
import time
import json
import logging
import os
from datetime import datetime
from config import server
from logging import Logger

class BinanceClient:
    def __init__(self):
        # Verificar se deve usar a API da Binance
        use_binance_env = os.getenv('USE_BINANCE_API', 'true')
        self.use_binance_api = use_binance_env.lower() == 'true'
        
        print(f"🔍 USE_BINANCE_API env var: '{use_binance_env}' -> {self.use_binance_api}")
        
        if not self.use_binance_api:
            self.logger = self.setup_logging()
            self.logger.info("🔒 BinanceClient inicializado em modo DESABILITADO (USE_BINANCE_API=false)")
            return
            
        # Verificar se as chaves estão configuradas
        api_key = os.getenv('BINANCE_API_KEY', '')
        api_secret = os.getenv('BINANCE_SECRET_KEY', '')
        
        if not api_key or not api_secret:
            self.logger = self.setup_logging()
            self.logger.warning("⚠️ Chaves da API Binance não configuradas. Usando modo DESABILITADO.")
            self.use_binance_api = False
            return
            
        self.config = server.config['BINANCE_FUTURES']
        self.base_url = self.config['api_url']
        self.ws_base_url = self.config['ws_url']
        self.api_key = api_key
        self.api_secret = api_secret
        self.logger: Logger = self.setup_logging()
        self.time_offset = 0
        self._init_time_offset()
        self.logger.info("BinanceClient inicializado com sucesso")

    def _check_api_enabled(self) -> bool:
        """Verifica se a API está habilitada antes de fazer chamadas"""
        if not hasattr(self, 'use_binance_api') or not self.use_binance_api:
            if hasattr(self, 'logger'):
                self.logger.warning("🚫 Tentativa de usar API Binance com USE_BINANCE_API=false")
            return False
        return True

    def _init_time_offset(self) -> None:
        """Inicializa o offset de tempo com o servidor da Binance"""
        if not self._check_api_enabled():
            return
            
        try:
            success = False
            for attempt in range(5):
                try:
                    server_time = requests.get(f"{self.base_url}/fapi/v1/time", timeout=10).json()
                    if 'serverTime' not in server_time:
                        self.logger.warning(f"Resposta inválida do servidor de tempo: {server_time}")
                        time.sleep(1)
                        continue
                        
                    local_time = int(time.time() * 1000)
                    self.time_offset = server_time['serverTime'] - local_time
                    self.logger.info(f"Time offset set to {self.time_offset}ms (attempt {attempt+1})")
                    success = True
                    break
                except Exception as e:
                    self.logger.warning(f"Falha na tentativa {attempt+1} de sincronização: {e}")
                    time.sleep(1)
            
            if not success:
                self.logger.error("Todas as tentativas de sincronização falharam. Usando offset zero.")
                self.time_offset = 0
                
        except Exception as e:
            self.logger.error(f"Erro crítico ao configurar offset de tempo: {e}")
            self.time_offset = 0
    
    def get_timestamp(self) -> int:
        """Retorna o timestamp correto considerando o offset"""
        if not self._check_api_enabled():
            return int(time.time() * 1000)
            
        # Adiciona verificação periódica do offset a cada 30 minutos
        current_time = time.time()
        if not hasattr(self, '_last_sync_time') or current_time - getattr(self, '_last_sync_time', 0) > 1800:
            self._init_time_offset()
            self._last_sync_time = current_time
            
        return int(time.time() * 1000) + self.time_offset

    def setup_logging(self) -> Logger:
        """Configura o logger para a classe"""
        logger = logging.getLogger('BinanceClient')
        logger.setLevel(logging.INFO)
        
        # Evitar duplicação de handlers
        if logger.handlers:
            return logger
        
        # Criar handler para arquivo
        file_handler = logging.FileHandler('binance_client.log')
        file_handler.setLevel(logging.INFO)
        
        # Criar handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Criar formatador
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Adicionar handlers ao logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger

    def _generate_signature(self, params: Dict) -> str:
        """Gera assinatura para requisições autenticadas"""
        if not self._check_api_enabled():
            return ""
            
        import hmac
        import hashlib
        from urllib.parse import urlencode
        
        query_string = urlencode(params)
        return hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def make_request(self, endpoint: str, method: str = 'GET', params: Optional[Dict] = None, auth: bool = False) -> Optional[Dict]:
        """Faz requisição para API Binance com rate limiting otimizado"""
        if not self._check_api_enabled():
            return None
            
        max_retries = 3
        retry_delay = 1
        
        # Rate limiting otimizado: reduzir delay entre requests
        time.sleep(0.02)  # 20ms entre requests (era 50ms)
        
        for attempt in range(max_retries):
            try:
                url = f"{self.base_url}{endpoint}"
                headers = {'X-MBX-APIKEY': self.api_key} if auth else {}
                
                # Preparar parâmetros
                request_params = params or {}
                if auth:
                    if 'recvWindow' not in request_params:
                        request_params['recvWindow'] = 10000  # Aumentar para 10 segundos
                    
                    request_params['timestamp'] = self.get_timestamp()
                    request_params['signature'] = self._generate_signature(request_params)
                
                # Fazer a requisição com timeout maior
                # No método make_request, linha ~165
                if method == 'GET':
                    response = requests.get(url, params=request_params, headers=headers, timeout=60)  # Aumentar de 30s para 60s
                else:
                    response = requests.post(url, json=request_params, headers=headers, timeout=60)
                
                # Também otimizar o rate limiting
                time.sleep(0.01)  # Reduzir de 0.02 para 0.01 (10ms)
                
                # Verificar resposta
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:  # Rate limit
                    retry_after = int(response.headers.get('Retry-After', retry_delay))
                    self.logger.warning(f"Rate limit atingido. Aguardando {retry_after}s")
                    time.sleep(retry_after)
                elif response.status_code == 400 and 'Timestamp for this request' in response.text:
                    # Erro de timestamp, resincronizar e tentar novamente
                    self.logger.warning("Erro de timestamp detectado, resincronizando...")
                    self._init_time_offset()
                    time.sleep(0.5)
                else:
                    self.logger.error(f"Erro na API: {response.status_code} - {response.text}")
                    if attempt == max_retries - 1:  # Último retry
                        return None
                    time.sleep(retry_delay * (attempt + 1))
                    
            except requests.exceptions.Timeout:
                self.logger.error(f"Timeout na requisição para {endpoint}")
                time.sleep(retry_delay * (attempt + 1))
            except Exception as e:
                self.logger.error(f"Erro na requisição: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    
        return None
        
    def get_exchange_info(self) -> Optional[Dict]:
        """Get exchange information with validation"""
        if not self._check_api_enabled():
            return {}
            
        try:
            data = self.make_request('/fapi/v1/exchangeInfo')
            if not data or 'symbols' not in data:
                self.logger.error("Invalid exchange info response")
                return {}
            return data
        except Exception as e:
            self.logger.error(f"Exchange info error: {e}")
            return {}
            
    def get_leverage_brackets(self, symbol: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Obtém informações sobre alavancagem dos pares"""
        if not self._check_api_enabled():
            return {}
            
        try:
            params: Dict[str, Any] = {'timestamp': self.get_timestamp()}
            if symbol is not None:
                params['symbol'] = str(symbol)
            
            response = self.make_request(
                '/fapi/v1/leverageBracket',
                params=params,
                auth=True
            )
            
            if not response:
                self.logger.error("Resposta inválida de leverage brackets")
                return {}
            
            if symbol is not None:
                brackets = response if isinstance(response, list) else [response]
                return {symbol: brackets}
            
            return {
                str(item['symbol']): item['brackets'] if isinstance(item['brackets'], list) else [item['brackets']]
                for item in response
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter leverage brackets: {e}")
            return {}

    def get_all_usdt_perpetual_pairs(self) -> List[str]:
        """Obtém todos os pares USDT perpétuos ativos"""
        if not self._check_api_enabled():
            return []
            
        try:
            exchange_info = self.get_exchange_info()
            if not exchange_info:
                return []
                
            perpetual_pairs = [
                symbol['symbol'] for symbol in exchange_info['symbols']
                if (symbol['symbol'].endswith('USDT') and 
                    symbol['status'] == 'TRADING' and 
                    symbol['contractType'] == 'PERPETUAL')
            ]
            
            self.logger.info(f"Total de pares USDT perpétuos encontrados: {len(perpetual_pairs)}")
            return perpetual_pairs
            
        except Exception as e:
            self.logger.error(f"Erro ao obter pares perpétuos: {e}")
            return []
            
    def get_24h_ticker_data(self, symbols: List[str]) -> Dict[str, Dict]:
        """Obtém dados de volume e variação 24h dos pares"""
        if not self._check_api_enabled():
            return {}
            
        try:
            response = self.make_request('/fapi/v1/ticker/24hr')
            if not response:
                return {}
                
            return {
                item['symbol']: {
                    'volume': float(item['volume']) * float(item['lastPrice']),
                    'priceChangePercent': float(item['priceChangePercent']),
                    'volatility': abs(float(item['highPrice']) - float(item['lowPrice'])) / float(item['lastPrice']) * 100
                }
                for item in response
                if item['symbol'] in symbols
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter dados 24h: {e}")
            return {}
            
    def filter_high_leverage_pairs(self, pairs: List[str]) -> List[str]:
        """Filtra pares com alavancagem >= 50x"""
        if not self._check_api_enabled():
            return []
            
        try:
            leverage_info = self.get_leverage_brackets()
            if not leverage_info:
                return []
                
            filtered_pairs = [
                symbol for symbol in pairs
                if symbol in leverage_info and 
                float(leverage_info[symbol][0]['initialLeverage']) >= 50
            ]
            
            self.logger.info(f"Pares com alavancagem 50x: {len(filtered_pairs)}")
            return filtered_pairs
            
        except Exception as e:
            self.logger.error(f"Erro ao filtrar por alavancagem: {e}")
            return []
            
    def get_top_pairs(self, limit: int = 100) -> List[str]:
        """Obtém os top pares baseado em volume e volatilidade"""
        if not self._check_api_enabled():
            return []
            
        try:
            # 1. Obter todos os pares USDT perpétuos
            all_pairs = self.get_all_usdt_perpetual_pairs()
            if not all_pairs:
                return []
                
            # 2. Filtrar por alavancagem >= 50x
            high_leverage_pairs = self.filter_high_leverage_pairs(all_pairs)
            if not high_leverage_pairs:
                return []
                
            # 3. Obter dados de volume e volatilidade
            ticker_data = self.get_24h_ticker_data(high_leverage_pairs)
            if not ticker_data:
                return []
                
            # 4. Calcular score final
            scored_pairs = []
            for symbol, data in ticker_data.items():
                volume_score = min(data['volume'] / 1000000, 10)
                volatility_score = min(data['volatility'], 10)
                final_score = (volume_score * 0.6) + (volatility_score * 0.4)
                
                scored_pairs.append((symbol, final_score))
            
            # 5. Ordenar e retornar top pairs
            top_pairs = sorted(scored_pairs, key=lambda x: x[1], reverse=True)[:limit]
            selected_pairs = [pair[0] for pair in top_pairs]
            
            self.logger.info(f"Top {len(selected_pairs)} pares selecionados")
            return selected_pairs
            
        except Exception as e:
            self.logger.error(f"Erro ao selecionar top pares: {e}")
            return []

    def get_klines(self, symbol, interval='1h', limit=100):
        """Obtém dados históricos (klines) para um símbolo"""
        if not self._check_api_enabled():
            return []
            
        try:
            endpoint = '/fapi/v1/klines'
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            
            response = self.make_request(endpoint, 'GET', params)
            
            if not response:
                return []
            
            # Converter para formato mais legível
            klines_data = []
            for kline in response:
                klines_data.append({
                    'open_time': kline[0],
                    'open': float(kline[1]),
                    'high': float(kline[2]),
                    'low': float(kline[3]),
                    'close': float(kline[4]),
                    'volume': float(kline[5]),
                    'close_time': kline[6]
                })
            
            return klines_data
        except Exception as e:
            self.logger.error(f"Erro ao obter klines para {symbol}: {e}")
            return []