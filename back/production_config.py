# -*- coding: utf-8 -*-
"""
Configuração de Produção Otimizada para Resolver Gateway Timeout
Este arquivo contém configurações específicas para produção que ajudam a resolver
problemas de timeout e melhorar a performance do backend.
"""

import os
from datetime import timedelta

class ProductionConfig:
    """
    Configurações otimizadas para produção
    Foco em resolver Gateway Timeout e melhorar performance
    """
    
    # ===== CONFIGURAÇÕES DE TIMEOUT =====
    
    # Timeout para requisições HTTP (em segundos)
    REQUEST_TIMEOUT = 120
    
    # Timeout para conexões com banco de dados
    DATABASE_TIMEOUT = 60
    
    # Timeout para operações de I/O
    IO_TIMEOUT = 90
    
    # Timeout para cache Redis
    REDIS_TIMEOUT = 30
    
    # ===== CONFIGURAÇÕES DE PERFORMANCE =====
    
    # Número máximo de workers para processamento
    MAX_WORKERS = 4
    
    # Tamanho do pool de conexões do banco
    DATABASE_POOL_SIZE = 20
    DATABASE_MAX_OVERFLOW = 30
    
    # Configurações de cache
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutos
    CACHE_THRESHOLD = 1000
    
    # ===== CONFIGURAÇÕES FLASK =====
    
    # Timeout para sessões
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Tamanho máximo de upload
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    
    # Configurações de JSON
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = False
    
    # ===== CONFIGURAÇÕES DE LOGGING =====
    
    # Nível de log para produção
    LOG_LEVEL = 'INFO'
    
    # Formato de log otimizado
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # ===== CONFIGURAÇÕES DE SEGURANÇA =====
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'memory://')
    RATELIMIT_DEFAULT = '100 per hour'
    
    # CORS
    CORS_ORIGINS = ['https://seu-dominio.com', 'https://www.seu-dominio.com']
    
    # ===== CONFIGURAÇÕES DE BANCO DE DADOS =====
    
    @staticmethod
    def get_database_config():
        """
        Retorna configurações otimizadas para o banco de dados
        """
        return {
            'pool_size': ProductionConfig.DATABASE_POOL_SIZE,
            'max_overflow': ProductionConfig.DATABASE_MAX_OVERFLOW,
            'pool_timeout': ProductionConfig.DATABASE_TIMEOUT,
            'pool_recycle': 3600,  # Reciclar conexões a cada hora
            'pool_pre_ping': True,  # Verificar conexões antes de usar
            'connect_args': {
                'connect_timeout': ProductionConfig.DATABASE_TIMEOUT,
                'application_name': 'KryptonBot_Production'
            }
        }
    
    # ===== CONFIGURAÇÕES DE REDIS =====
    
    @staticmethod
    def get_redis_config():
        """
        Retorna configurações otimizadas para Redis
        """
        return {
            'socket_timeout': ProductionConfig.REDIS_TIMEOUT,
            'socket_connect_timeout': ProductionConfig.REDIS_TIMEOUT,
            'socket_keepalive': True,
            'socket_keepalive_options': {},
            'health_check_interval': 30,
            'retry_on_timeout': True,
            'max_connections': 50
        }
    
    # ===== CONFIGURAÇÕES DE BINANCE API =====
    
    @staticmethod
    def get_binance_config():
        """
        Retorna configurações otimizadas para Binance API
        """
        return {
            'timeout': 30,  # Timeout para requisições à Binance
            'max_retries': 3,
            'retry_delay': 1,
            'rate_limit': True,
            'requests_per_second': 10
        }
    
    # ===== CONFIGURAÇÕES DE THREADING =====
    
    # Configurações para threads de background
    BACKGROUND_THREAD_TIMEOUT = 300  # 5 minutos
    MAX_BACKGROUND_THREADS = 5
    
    # ===== CONFIGURAÇÕES DE MONITORAMENTO =====
    
    # Intervalo para health checks (em segundos)
    HEALTH_CHECK_INTERVAL = 60
    
    # Timeout para health checks
    HEALTH_CHECK_TIMEOUT = 10
    
    # ===== CONFIGURAÇÕES DE OTIMIZAÇÃO =====
    
    # Configurações para otimizar performance
    OPTIMIZE_FOR_PRODUCTION = True
    
    # Desabilitar debug em produção
    DEBUG = False
    TESTING = False
    
    # Configurações de compressão
    COMPRESS_MIMETYPES = [
        'text/html',
        'text/css',
        'text/xml',
        'application/json',
        'application/javascript'
    ]
    
    # ===== MÉTODOS UTILITÁRIOS =====
    
    @staticmethod
    def apply_to_app(app):
        """
        Aplica todas as configurações de produção ao app Flask
        """
        # Aplicar configurações básicas
        app.config['REQUEST_TIMEOUT'] = ProductionConfig.REQUEST_TIMEOUT
        app.config['PERMANENT_SESSION_LIFETIME'] = ProductionConfig.PERMANENT_SESSION_LIFETIME
        app.config['MAX_CONTENT_LENGTH'] = ProductionConfig.MAX_CONTENT_LENGTH
        app.config['JSON_SORT_KEYS'] = ProductionConfig.JSON_SORT_KEYS
        app.config['JSONIFY_PRETTYPRINT_REGULAR'] = ProductionConfig.JSONIFY_PRETTYPRINT_REGULAR
        
        # Configurações de segurança
        app.config['DEBUG'] = ProductionConfig.DEBUG
        app.config['TESTING'] = ProductionConfig.TESTING
        
        print("✅ Configurações de produção aplicadas ao Flask app")
    
    @staticmethod
    def setup_logging():
        """
        Configura logging otimizado para produção
        """
        import logging
        
        # Configurar nível de log
        logging.basicConfig(
            level=getattr(logging, ProductionConfig.LOG_LEVEL),
            format=ProductionConfig.LOG_FORMAT,
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('/var/log/app/backend.log', mode='a')
            ]
        )
        
        # Reduzir verbosidade de bibliotecas externas
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('requests').setLevel(logging.WARNING)
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
        
        print("✅ Logging de produção configurado")
    
    @staticmethod
    def optimize_flask_app(app):
        """
        Aplica otimizações específicas para Flask em produção
        """
        # Desabilitar reloader em produção
        app.config['USE_RELOADER'] = False
        
        # Configurar threading
        app.config['THREADED'] = True
        
        # Otimizar templates
        app.jinja_env.auto_reload = False
        app.jinja_env.cache_size = 400
        
        print("✅ Otimizações Flask aplicadas")

# ===== CONFIGURAÇÕES ESPECÍFICAS PARA GUNICORN =====

class GunicornConfig:
    """
    Configurações otimizadas para Gunicorn em produção
    """
    
    # Número de workers (recomendado: 2 * CPU cores + 1)
    workers = 4
    
    # Tipo de worker (async para melhor performance)
    worker_class = 'gevent'
    
    # Conexões simultâneas por worker
    worker_connections = 1000
    
    # Timeout para workers
    timeout = 120
    
    # Timeout para keep-alive
    keepalive = 5
    
    # Máximo de requisições por worker antes de restart
    max_requests = 1000
    max_requests_jitter = 100
    
    # Configurações de bind
    bind = '0.0.0.0:5000'
    
    # Configurações de log
    accesslog = '/var/log/app/gunicorn_access.log'
    errorlog = '/var/log/app/gunicorn_error.log'
    loglevel = 'info'
    
    # Preload da aplicação
    preload_app = True
    
    @staticmethod
    def get_gunicorn_cmd():
        """
        Retorna comando otimizado para executar Gunicorn
        """
        return [
            'gunicorn',
            '--workers', str(GunicornConfig.workers),
            '--worker-class', GunicornConfig.worker_class,
            '--worker-connections', str(GunicornConfig.worker_connections),
            '--timeout', str(GunicornConfig.timeout),
            '--keepalive', str(GunicornConfig.keepalive),
            '--max-requests', str(GunicornConfig.max_requests),
            '--max-requests-jitter', str(GunicornConfig.max_requests_jitter),
            '--bind', GunicornConfig.bind,
            '--access-logfile', GunicornConfig.accesslog,
            '--error-logfile', GunicornConfig.errorlog,
            '--log-level', GunicornConfig.loglevel,
            '--preload',
            'app:app'
        ]

# ===== EXEMPLO DE USO =====

def configure_production_app(app):
    """
    Função para configurar completamente o app para produção
    """
    print("🔧 Configurando aplicação para produção...")
    
    # Aplicar configurações de produção
    ProductionConfig.apply_to_app(app)
    
    # Configurar logging
    ProductionConfig.setup_logging()
    
    # Otimizar Flask
    ProductionConfig.optimize_flask_app(app)
    
    print("✅ Aplicação configurada para produção com otimizações anti-timeout")
    
    return app

# ===== SCRIPT DE INICIALIZAÇÃO OTIMIZADA =====

def start_production_server():
    """
    Inicia o servidor em modo produção com todas as otimizações
    """
    import subprocess
    import sys
    
    print("🚀 Iniciando servidor em modo produção...")
    
    # Comando Gunicorn otimizado
    cmd = GunicornConfig.get_gunicorn_cmd()
    
    try:
        # Executar Gunicorn
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao iniciar Gunicorn: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Servidor interrompido pelo usuário")
        sys.exit(0)

if __name__ == '__main__':
    start_production_server()