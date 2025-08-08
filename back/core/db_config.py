import os
import redis
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, Dict, Any, List
import logging
from contextlib import contextmanager

class DatabaseConfig:
    """Configuração e conexão com PostgreSQL e Redis"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Configurações do PostgreSQL
        self.database_url = os.getenv('DATABASE_URL', 'sqlite:///data/trading_signals.db')
        
        # Configurações do Redis
        self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        
        # Inicializar conexões
        self.redis_client = None
        self._init_redis()
        
    def _init_redis(self):
        """Inicializa conexão com Redis"""
        try:
            if self.redis_url.startswith('redis://'):
                self.redis_client = redis.from_url(self.redis_url)
                # Testar conexão
                self.redis_client.ping()
                self.logger.info("✅ Redis conectado com sucesso")
            else:
                self.logger.warning("⚠️ Redis URL não configurada, usando fallback")
        except Exception as e:
            self.logger.warning(f"⚠️ Redis não disponível: {e}")
            print(f"⚠️ Redis não disponível: {e} - Continuando sem cache...")
            self.redis_client = None
    
    @contextmanager
    def get_db_connection(self):
        """Context manager para conexão com PostgreSQL"""
        conn = None
        try:
            if self.database_url.startswith('postgresql://'):
                conn = psycopg2.connect(self.database_url)
                yield conn
            else:
                # Fallback para SQLite (desenvolvimento)
                import sqlite3
                db_path = self.database_url.replace('sqlite:///', '')
                os.makedirs(os.path.dirname(db_path), exist_ok=True)
                conn = sqlite3.connect(db_path)
                conn.row_factory = sqlite3.Row
                yield conn
        except Exception as e:
            self.logger.error(f"❌ Erro de conexão com banco: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Executa query SELECT e retorna resultados"""
        try:
            with self.get_db_connection() as conn:
                if self.database_url.startswith('postgresql://'):
                    cursor = conn.cursor(cursor_factory=RealDictCursor)
                else:
                    cursor = conn.cursor()
                
                cursor.execute(query, params or ())
                
                if self.database_url.startswith('postgresql://'):
                    results = [dict(row) for row in cursor.fetchall()]
                else:
                    columns = [description[0] for description in cursor.description]
                    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                
                return results
        except Exception as e:
            self.logger.error(f"❌ Erro ao executar query: {e}")
            return []
    
    def execute_insert_update(self, query: str, params: tuple = None) -> bool:
        """Executa query INSERT/UPDATE/DELETE"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params or ())
                conn.commit()
                return True
        except Exception as e:
            self.logger.error(f"❌ Erro ao executar insert/update: {e}")
            return False
    
    def cache_get(self, key: str) -> Optional[str]:
        """Obtém valor do cache Redis"""
        try:
            if self.redis_client:
                value = self.redis_client.get(key)
                return value.decode('utf-8') if value else None
            return None
        except Exception as e:
            self.logger.error(f"❌ Erro ao obter cache: {e}")
            return None
    
    def cache_set(self, key: str, value: str, expire: int = 3600) -> bool:
        """Define valor no cache Redis"""
        try:
            if self.redis_client:
                return self.redis_client.setex(key, expire, value)
            return False
        except Exception as e:
            self.logger.error(f"❌ Erro ao definir cache: {e}")
            return False
    
    def cache_delete(self, key: str) -> bool:
        """Remove valor do cache Redis"""
        try:
            if self.redis_client:
                return bool(self.redis_client.delete(key))
            return False
        except Exception as e:
            self.logger.error(f"❌ Erro ao deletar cache: {e}")
            return False

# Instância global
db_config = DatabaseConfig()