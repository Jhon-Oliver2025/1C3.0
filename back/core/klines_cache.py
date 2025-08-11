# -*- coding: utf-8 -*-
"""
Klines Cache - Sistema de Cache para Dados Históricos
Reduz chamadas à API Binance cachando DataFrames de klines
"""

import pandas as pd
import time
import threading
from typing import Dict, Optional, Tuple
from datetime import datetime

class KlinesCache:
    """
    Cache thread-safe para dados de klines (candlesticks)
    Reduz significativamente as chamadas à API Binance
    """
    
    def __init__(self, default_ttl: int = 300):
        """Inicializa o cache de klines
        
        Args:
            default_ttl: Tempo de vida padrão em segundos (5 minutos)
        """
        self.default_ttl = default_ttl
        self.cache: Dict[str, Dict] = {}
        self.lock = threading.RLock()  # Lock para thread safety
        
        print(f"🗄️ KlinesCache inicializado com TTL padrão: {default_ttl}s")
    
    def _generate_key(self, symbol: str, interval: str, limit: int) -> str:
        """Gera chave única para o cache"""
        return f"{symbol}_{interval}_{limit}"
    
    def get(self, symbol: str, interval: str, limit: int = 100) -> Optional[pd.DataFrame]:
        """Obtém dados do cache se válidos
        
        Args:
            symbol: Símbolo do par (ex: BTCUSDT)
            interval: Intervalo (ex: 1h, 4h)
            limit: Número de períodos
            
        Returns:
            DataFrame se encontrado e válido, None caso contrário
        """
        key = self._generate_key(symbol, interval, limit)
        
        with self.lock:
            if key not in self.cache:
                return None
            
            cache_entry = self.cache[key]
            current_time = time.time()
            
            # Verificar se ainda é válido
            if current_time - cache_entry['timestamp'] > cache_entry['ttl']:
                # Cache expirado, remover
                del self.cache[key]
                return None
            
            # Cache válido, retornar cópia do DataFrame
            return cache_entry['data'].copy()
    
    def set(self, symbol: str, interval: str, data: pd.DataFrame, 
            limit: int = 100, ttl: Optional[int] = None) -> None:
        """Armazena dados no cache
        
        Args:
            symbol: Símbolo do par
            interval: Intervalo
            data: DataFrame com dados de klines
            limit: Número de períodos
            ttl: Tempo de vida customizado (usa default se None)
        """
        if data is None or data.empty:
            return
        
        key = self._generate_key(symbol, interval, limit)
        cache_ttl = ttl or self.default_ttl
        
        with self.lock:
            self.cache[key] = {
                'data': data.copy(),
                'timestamp': time.time(),
                'ttl': cache_ttl,
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
    
    def invalidate(self, symbol: Optional[str] = None, interval: Optional[str] = None) -> int:
        """Invalida entradas do cache
        
        Args:
            symbol: Se especificado, invalida apenas este símbolo
            interval: Se especificado, invalida apenas este intervalo
            
        Returns:
            Número de entradas removidas
        """
        removed_count = 0
        
        with self.lock:
            keys_to_remove = []
            
            for key, entry in self.cache.items():
                should_remove = True
                
                if symbol and entry['symbol'] != symbol:
                    should_remove = False
                
                if interval and entry['interval'] != interval:
                    should_remove = False
                
                if should_remove:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self.cache[key]
                removed_count += 1
        
        return removed_count
    
    def cleanup_expired(self) -> int:
        """Remove entradas expiradas do cache
        
        Returns:
            Número de entradas removidas
        """
        current_time = time.time()
        removed_count = 0
        
        with self.lock:
            keys_to_remove = []
            
            for key, entry in self.cache.items():
                if current_time - entry['timestamp'] > entry['ttl']:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self.cache[key]
                removed_count += 1
        
        return removed_count
    
    def get_stats(self) -> Dict[str, any]:
        """Retorna estatísticas do cache
        
        Returns:
            Dict com estatísticas do cache
        """
        with self.lock:
            current_time = time.time()
            total_entries = len(self.cache)
            expired_entries = 0
            
            intervals = {}
            symbols = set()
            
            for entry in self.cache.values():
                # Contar expirados
                if current_time - entry['timestamp'] > entry['ttl']:
                    expired_entries += 1
                
                # Contar por intervalo
                interval = entry['interval']
                intervals[interval] = intervals.get(interval, 0) + 1
                
                # Contar símbolos únicos
                symbols.add(entry['symbol'])
            
            return {
                'total_entries': total_entries,
                'expired_entries': expired_entries,
                'valid_entries': total_entries - expired_entries,
                'unique_symbols': len(symbols),
                'intervals': intervals,
                'cache_efficiency': (
                    (total_entries - expired_entries) / total_entries * 100 
                    if total_entries > 0 else 0
                )
            }
    
    def clear(self) -> int:
        """Limpa todo o cache
        
        Returns:
            Número de entradas removidas
        """
        with self.lock:
            count = len(self.cache)
            self.cache.clear()
            return count
    
    def get_cache_hit_info(self, symbol: str, interval: str, limit: int = 100) -> Dict[str, any]:
        """Retorna informações sobre hit/miss do cache para debug
        
        Args:
            symbol: Símbolo do par
            interval: Intervalo
            limit: Número de períodos
            
        Returns:
            Dict com informações de cache
        """
        key = self._generate_key(symbol, interval, limit)
        
        with self.lock:
            if key not in self.cache:
                return {
                    'status': 'MISS',
                    'reason': 'NOT_FOUND',
                    'key': key
                }
            
            cache_entry = self.cache[key]
            current_time = time.time()
            age = current_time - cache_entry['timestamp']
            
            if age > cache_entry['ttl']:
                return {
                    'status': 'MISS',
                    'reason': 'EXPIRED',
                    'key': key,
                    'age': age,
                    'ttl': cache_entry['ttl']
                }
            
            return {
                'status': 'HIT',
                'key': key,
                'age': age,
                'ttl': cache_entry['ttl'],
                'remaining_ttl': cache_entry['ttl'] - age
            }

class CacheManager:
    """
    Gerenciador global de cache para diferentes tipos de dados
    """
    
    def __init__(self):
        """Inicializa o gerenciador de cache"""
        # Cache para diferentes timeframes com TTLs otimizados
        self.klines_1h = KlinesCache(default_ttl=180)    # 3 minutos para 1h
        self.klines_4h = KlinesCache(default_ttl=600)    # 10 minutos para 4h
        self.klines_1d = KlinesCache(default_ttl=1800)   # 30 minutos para 1d
        
        # Estatísticas de performance
        self.stats = {
            'total_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'api_calls_saved': 0
        }
        
        print("🗄️ CacheManager inicializado com múltiplos caches")
    
    def get_cache_for_interval(self, interval: str) -> KlinesCache:
        """Retorna o cache apropriado para o intervalo"""
        if interval in ['1h', '2h', '3h']:
            return self.klines_1h
        elif interval in ['4h', '6h', '8h', '12h']:
            return self.klines_4h
        else:
            return self.klines_1d
    
    def get_klines(self, symbol: str, interval: str, limit: int = 100) -> Tuple[Optional[pd.DataFrame], bool]:
        """Obtém klines do cache apropriado
        
        Returns:
            Tuple (DataFrame, is_cache_hit)
        """
        self.stats['total_requests'] += 1
        
        cache = self.get_cache_for_interval(interval)
        data = cache.get(symbol, interval, limit)
        
        if data is not None:
            self.stats['cache_hits'] += 1
            self.stats['api_calls_saved'] += 1
            return data, True
        else:
            self.stats['cache_misses'] += 1
            return None, False
    
    def set_klines(self, symbol: str, interval: str, data: pd.DataFrame, limit: int = 100) -> None:
        """Armazena klines no cache apropriado"""
        cache = self.get_cache_for_interval(interval)
        cache.set(symbol, interval, data, limit)
    
    def get_performance_stats(self) -> Dict[str, any]:
        """Retorna estatísticas de performance do cache"""
        total_requests = self.stats['total_requests']
        cache_hit_rate = (
            self.stats['cache_hits'] / total_requests * 100 
            if total_requests > 0 else 0
        )
        
        return {
            **self.stats,
            'cache_hit_rate': cache_hit_rate,
            'cache_efficiency': cache_hit_rate,
            'individual_caches': {
                '1h': self.klines_1h.get_stats(),
                '4h': self.klines_4h.get_stats(),
                '1d': self.klines_1d.get_stats()
            }
        }
    
    def cleanup_all_expired(self) -> int:
        """Limpa entradas expiradas de todos os caches"""
        total_removed = 0
        total_removed += self.klines_1h.cleanup_expired()
        total_removed += self.klines_4h.cleanup_expired()
        total_removed += self.klines_1d.cleanup_expired()
        return total_removed