# -*- coding: utf-8 -*-
"""
Sistema de Ranking de Moedas - Top 40 Criptomoedas
Implementa filtros de qualidade baseados no market cap e ranking das moedas
"""

from typing import Dict, List, Optional
from datetime import datetime

class CoinRanking:
    """
    Gerencia o ranking das principais criptomoedas e aplica filtros de qualidade
    """
    
    def __init__(self):
        """Inicializa o sistema de ranking com as top 40 moedas"""
        print("🏆 Inicializando CoinRanking...")
        
        # Lista das 40 maiores criptomoedas por market cap (atualizada 2024)
        self.TOP_40_COINS = [
            # Top 10 - Bonus máximo
            'BTC', 'ETH', 'USDT', 'BNB', 'SOL', 'USDC', 'XRP', 'DOGE', 'ADA', 'AVAX',
            
            # Top 11-20 - Bonus alto
            'TRX', 'LINK', 'MATIC', 'WBTC', 'DOT', 'LTC', 'SHIB', 'DAI', 'BCH', 'UNI',
            
            # Top 21-30 - Bonus médio
            'LEO', 'ATOM', 'ETC', 'XLM', 'XMR', 'ALGO', 'FIL', 'HBAR', 'VET', 'ICP',
            
            # Top 31-40 - Bonus baixo
            'APE', 'SAND', 'MANA', 'AAVE', 'MKR', 'FTM', 'GRT', 'AXS', 'THETA', 'EOS'
        ]
        
        # Configurações de bonus/penalização
        self.RANKING_BONUS = {
            'top_10': 15,      # Top 10: +15 pontos
            'top_20': 10,      # Top 11-20: +10 pontos
            'top_40': 5,       # Top 21-40: +5 pontos
            'outside_top_40': -15  # Fora do top 40: -15 pontos
        }
        
        # Filtros de qualidade de mercado
        self.MARKET_FILTERS = {
            'min_24h_volume_usdt': 5_000_000,    # Mínimo $5M volume 24h
            'max_spread_percentage': 1.0,         # Máximo 1% spread
            'min_price_stability': 0.7            # Estabilidade mínima
        }
        
        print(f"✅ CoinRanking inicializado com {len(self.TOP_40_COINS)} moedas")
    
    def get_coin_from_symbol(self, symbol: str) -> str:
        """
        Extrai o nome da moeda do símbolo de trading
        
        Args:
            symbol: Símbolo como 'BTCUSDT', 'ETHUSDT.P', etc.
            
        Returns:
            Nome da moeda limpo (ex: 'BTC', 'ETH')
        """
        # Remover sufixos comuns
        coin = symbol.upper()
        coin = coin.replace('USDT', '').replace('BUSD', '').replace('USDC', '')
        coin = coin.replace('.P', '')  # Futuros perpétuos
        coin = coin.replace('PERP', '')  # Outros futuros
        
        return coin
    
    def get_coin_ranking_position(self, symbol: str) -> Optional[int]:
        """
        Retorna a posição da moeda no ranking (1-40) ou None se não estiver
        
        Args:
            symbol: Símbolo de trading
            
        Returns:
            Posição no ranking (1-40) ou None
        """
        coin = self.get_coin_from_symbol(symbol)
        
        try:
            return self.TOP_40_COINS.index(coin) + 1  # +1 porque index começa em 0
        except ValueError:
            return None
    
    def calculate_ranking_bonus(self, symbol: str) -> int:
        """
        Calcula o bonus/penalização baseado no ranking da moeda
        
        Args:
            symbol: Símbolo de trading
            
        Returns:
            Pontos de bonus (positivo) ou penalização (negativo)
        """
        position = self.get_coin_ranking_position(symbol)
        
        if position is None:
            # Moeda fora do top 40 - penalização
            return self.RANKING_BONUS['outside_top_40']
        elif position <= 10:
            # Top 10 - bonus máximo
            return self.RANKING_BONUS['top_10']
        elif position <= 20:
            # Top 11-20 - bonus alto
            return self.RANKING_BONUS['top_20']
        elif position <= 40:
            # Top 21-40 - bonus baixo
            return self.RANKING_BONUS['top_40']
        else:
            # Não deveria acontecer, mas por segurança
            return 0
    
    def is_top_coin(self, symbol: str, top_n: int = 40) -> bool:
        """
        Verifica se a moeda está entre as top N
        
        Args:
            symbol: Símbolo de trading
            top_n: Número de posições a considerar (padrão: 40)
            
        Returns:
            True se estiver no top N, False caso contrário
        """
        position = self.get_coin_ranking_position(symbol)
        return position is not None and position <= top_n
    
    def get_coin_tier(self, symbol: str) -> str:
        """
        Retorna o tier da moeda baseado no ranking
        
        Args:
            symbol: Símbolo de trading
            
        Returns:
            Tier da moeda ('TIER_1', 'TIER_2', 'TIER_3', 'UNRANKED')
        """
        position = self.get_coin_ranking_position(symbol)
        
        if position is None:
            return 'UNRANKED'
        elif position <= 10:
            return 'TIER_1'  # Top 10
        elif position <= 20:
            return 'TIER_2'  # Top 11-20
        elif position <= 40:
            return 'TIER_3'  # Top 21-40
        else:
            return 'UNRANKED'
    
    def get_ranking_info(self, symbol: str) -> Dict[str, any]:
        """
        Retorna informações completas sobre o ranking da moeda
        
        Args:
            symbol: Símbolo de trading
            
        Returns:
            Dicionário com informações de ranking
        """
        coin = self.get_coin_from_symbol(symbol)
        position = self.get_coin_ranking_position(symbol)
        bonus = self.calculate_ranking_bonus(symbol)
        tier = self.get_coin_tier(symbol)
        
        return {
            'symbol': symbol,
            'coin': coin,
            'position': position,
            'tier': tier,
            'ranking_bonus': bonus,
            'is_top_40': position is not None,
            'is_top_20': position is not None and position <= 20,
            'is_top_10': position is not None and position <= 10
        }
    
    def should_prioritize_symbol(self, symbol: str) -> bool:
        """
        Determina se um símbolo deve ser priorizado baseado no ranking
        
        Args:
            symbol: Símbolo de trading
            
        Returns:
            True se deve ser priorizado, False caso contrário
        """
        return self.is_top_coin(symbol, top_n=20)  # Priorizar apenas top 20
    
    def filter_symbols_by_ranking(self, symbols: List[str], 
                                 min_tier: str = 'TIER_3') -> List[str]:
        """
        Filtra lista de símbolos baseado no tier mínimo
        
        Args:
            symbols: Lista de símbolos para filtrar
            min_tier: Tier mínimo aceito ('TIER_1', 'TIER_2', 'TIER_3')
            
        Returns:
            Lista filtrada de símbolos
        """
        tier_order = {'TIER_1': 1, 'TIER_2': 2, 'TIER_3': 3, 'UNRANKED': 4}
        min_tier_value = tier_order.get(min_tier, 4)
        
        filtered = []
        for symbol in symbols:
            tier = self.get_coin_tier(symbol)
            tier_value = tier_order.get(tier, 4)
            
            if tier_value <= min_tier_value:
                filtered.append(symbol)
        
        return filtered
    
    def get_top_symbols_from_list(self, symbols: List[str], 
                                 limit: int = 10) -> List[str]:
        """
        Retorna os símbolos com melhor ranking de uma lista
        
        Args:
            symbols: Lista de símbolos
            limit: Número máximo de símbolos a retornar
            
        Returns:
            Lista ordenada por ranking (melhores primeiro)
        """
        # Criar lista com posições
        symbol_positions = []
        for symbol in symbols:
            position = self.get_coin_ranking_position(symbol)
            if position is not None:
                symbol_positions.append((symbol, position))
        
        # Ordenar por posição (menor = melhor)
        symbol_positions.sort(key=lambda x: x[1])
        
        # Retornar apenas os símbolos, limitado
        return [symbol for symbol, _ in symbol_positions[:limit]]
    
    def get_ranking_stats(self) -> Dict[str, any]:
        """
        Retorna estatísticas do sistema de ranking
        
        Returns:
            Dicionário com estatísticas
        """
        return {
            'total_ranked_coins': len(self.TOP_40_COINS),
            'tier_1_count': 10,  # Top 10
            'tier_2_count': 10,  # Top 11-20
            'tier_3_count': 20,  # Top 21-40
            'bonus_structure': self.RANKING_BONUS,
            'market_filters': self.MARKET_FILTERS,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

# Instância global para uso em outros módulos
coin_ranking = CoinRanking()