#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Detecção de Alavancagem Máxima
Detecta a alavancagem máxima disponível para cada par de moedas na Binance
"""

import requests
import time
from typing import Dict, Optional
from .binance_client import BinanceClient
import traceback

class LeverageDetector:
    """
    Classe responsável por detectar e cachear informações de alavancagem máxima
    para pares de criptomoedas na Binance Futures
    """
    
    def __init__(self, binance_client: BinanceClient):
        """
        Inicializa o detector de alavancagem
        
        Args:
            binance_client: Instância do cliente Binance
        """
        self.binance = binance_client
        self.leverage_cache: Dict[str, int] = {}  # Cache de alavancagem por símbolo
        self.cache_timestamp: Dict[str, float] = {}  # Timestamp do cache
        self.cache_duration = 3600  # Cache válido por 1 hora
        
        print("🔧 LeverageDetector inicializado")
    
    def get_max_leverage(self, symbol: str) -> int:
        """
        Obtém a alavancagem máxima para um símbolo específico
        
        Args:
            symbol: Símbolo da moeda (ex: BTCUSDT)
            
        Returns:
            int: Alavancagem máxima (50, 75, 100, etc.)
        """
        try:
            # Verificar cache
            if self._is_cache_valid(symbol):
                return self.leverage_cache[symbol]
            
            # Buscar alavancagem via API
            leverage = self._fetch_leverage_from_api(symbol)
            
            # Armazenar no cache
            if leverage:
                self.leverage_cache[symbol] = leverage
                self.cache_timestamp[symbol] = time.time()
                return leverage
            
            # Fallback para alavancagem padrão
            return self._get_default_leverage(symbol)
            
        except Exception as e:
            print(f"❌ Erro ao obter alavancagem para {symbol}: {e}")
            return self._get_default_leverage(symbol)
    
    def _is_cache_valid(self, symbol: str) -> bool:
        """
        Verifica se o cache para um símbolo ainda é válido
        
        Args:
            symbol: Símbolo da moeda
            
        Returns:
            bool: True se o cache é válido
        """
        if symbol not in self.leverage_cache:
            return False
        
        if symbol not in self.cache_timestamp:
            return False
        
        elapsed = time.time() - self.cache_timestamp[symbol]
        return elapsed < self.cache_duration
    
    def _fetch_leverage_from_api(self, symbol: str) -> Optional[int]:
        """
        Busca a alavancagem máxima via API da Binance
        
        Args:
            symbol: Símbolo da moeda
            
        Returns:
            Optional[int]: Alavancagem máxima ou None se erro
        """
        try:
            # Usar API de Exchange Info para Futures
            exchange_info = self.binance.client.futures_exchange_info()
            
            # Procurar o símbolo específico
            for symbol_info in exchange_info['symbols']:
                if symbol_info['symbol'] == symbol:
                    # Verificar se há informações de alavancagem
                    if 'filters' in symbol_info:
                        for filter_info in symbol_info['filters']:
                            if filter_info['filterType'] == 'MARKET_LOT_SIZE':
                                # Buscar alavancagem máxima nos metadados
                                max_leverage = self._extract_max_leverage(symbol_info)
                                if max_leverage:
                                    return max_leverage
            
            # Método alternativo: usar endpoint específico de alavancagem
            return self._fetch_leverage_brackets(symbol)
            
        except Exception as e:
            print(f"⚠️ Erro na API para {symbol}: {e}")
            return None
    
    def _fetch_leverage_brackets(self, symbol: str) -> Optional[int]:
        """
        Busca informações de alavancagem via endpoint de brackets
        
        Args:
            symbol: Símbolo da moeda
            
        Returns:
            Optional[int]: Alavancagem máxima
        """
        try:
            # Endpoint para obter brackets de alavancagem
            brackets = self.binance.client.futures_leverage_bracket(symbol=symbol)
            
            if brackets and len(brackets) > 0:
                # Pegar o primeiro bracket que geralmente tem a alavancagem máxima
                first_bracket = brackets[0]
                if 'brackets' in first_bracket and len(first_bracket['brackets']) > 0:
                    max_leverage = first_bracket['brackets'][0].get('initialLeverage', 50)
                    return int(max_leverage)
            
            return None
            
        except Exception as e:
            print(f"⚠️ Erro ao buscar brackets para {symbol}: {e}")
            return None
    
    def _extract_max_leverage(self, symbol_info: Dict) -> Optional[int]:
        """
        Extrai alavancagem máxima das informações do símbolo
        
        Args:
            symbol_info: Informações do símbolo da API
            
        Returns:
            Optional[int]: Alavancagem máxima
        """
        try:
            # Verificar se há campo de alavancagem diretamente
            if 'maxLeverage' in symbol_info:
                return int(symbol_info['maxLeverage'])
            
            # Verificar em outros campos possíveis
            if 'leverageFilter' in symbol_info:
                return int(symbol_info['leverageFilter'].get('maxLeverage', 50))
            
            return None
            
        except Exception as e:
            print(f"⚠️ Erro ao extrair alavancagem: {e}")
            return None
    
    def _get_default_leverage(self, symbol: str) -> int:
        """
        Retorna alavancagem padrão baseada no tipo de moeda
        
        Args:
            symbol: Símbolo da moeda
            
        Returns:
            int: Alavancagem padrão
        """
        # Moedas principais geralmente têm alavancagem maior
        major_coins = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT', 'SOLUSDT']
        
        if symbol in major_coins:
            return 125  # Alavancagem alta para moedas principais
        
        # Moedas de alta capitalização
        high_cap = ['DOGEUSDT', 'MATICUSDT', 'DOTUSDT', 'AVAXUSDT', 'LINKUSDT']
        if symbol in high_cap:
            return 100
        
        # Moedas de média capitalização
        mid_cap = ['UNIUSDT', 'LTCUSDT', 'BCHUSDT', 'FILUSDT', 'TRXUSDT']
        if symbol in mid_cap:
            return 75
        
        # Padrão para outras moedas
        return 50
    
    def get_required_percentage_for_300_profit(self, symbol: str) -> float:
        """
        Calcula o percentual necessário para atingir 300% de lucro
        baseado na alavancagem máxima da moeda
        
        Args:
            symbol: Símbolo da moeda
            
        Returns:
            float: Percentual necessário (ex: 6.0 para 6%)
        """
        max_leverage = self.get_max_leverage(symbol)
        
        # Fórmula: Para 300% de lucro, precisamos de 3% de movimento com alavancagem
        # Percentual necessário = 3% / alavancagem * 100
        required_percentage = (3.0 / max_leverage) * 100
        
        return round(required_percentage, 2)
    
    def get_leverage_info(self, symbol: str) -> Dict[str, any]:
        """
        Retorna informações completas de alavancagem para um símbolo
        
        Args:
            symbol: Símbolo da moeda
            
        Returns:
            Dict: Informações de alavancagem
        """
        max_leverage = self.get_max_leverage(symbol)
        required_percentage = self.get_required_percentage_for_300_profit(symbol)
        
        return {
            'symbol': symbol,
            'max_leverage': max_leverage,
            'required_percentage': required_percentage,
            'target_profit': 300.0,
            'cached': symbol in self.leverage_cache,
            'cache_age': time.time() - self.cache_timestamp.get(symbol, 0)
        }
    
    def clear_cache(self):
        """
        Limpa o cache de alavancagem
        """
        self.leverage_cache.clear()
        self.cache_timestamp.clear()
        print("🧹 Cache de alavancagem limpo")
    
    def preload_common_symbols(self):
        """
        Pré-carrega alavancagem para símbolos comuns
        """
        common_symbols = [
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT',
            'SOLUSDT', 'DOGEUSDT', 'MATICUSDT', 'DOTUSDT', 'AVAXUSDT',
            'LINKUSDT', 'UNIUSDT', 'LTCUSDT', 'BCHUSDT', 'TRXUSDT'
        ]
        
        print("🔄 Pré-carregando alavancagem para símbolos comuns...")
        
        for symbol in common_symbols:
            try:
                leverage = self.get_max_leverage(symbol)
                print(f"   {symbol}: {leverage}x")
            except Exception as e:
                print(f"   ❌ {symbol}: Erro - {e}")
        
        print(f"✅ Pré-carregamento concluído: {len(self.leverage_cache)} símbolos")