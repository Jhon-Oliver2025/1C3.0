import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class SupabaseConfig:
    """
    Configuração para conexão com Supabase
    """
    
    def __init__(self):
        # URL do projeto Supabase
        self.SUPABASE_URL = os.getenv('SUPABASE_URL')
        
        # Chave anônima do Supabase (para operações públicas)
        self.SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')
        
        # Chave de serviço do Supabase (para operações administrativas)
        self.SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        # URL de conexão direta com PostgreSQL do Supabase
        self.DATABASE_URL = os.getenv('SUPABASE_DATABASE_URL')
        
        # Validar configurações obrigatórias
        self._validate_config()
    
    def _validate_config(self):
        """
        Valida se todas as configurações necessárias estão presentes
        """
        required_vars = {
            'SUPABASE_URL': self.SUPABASE_URL,
            'SUPABASE_ANON_KEY': self.SUPABASE_ANON_KEY,
            'DATABASE_URL': self.DATABASE_URL
        }
        
        missing_vars = [var for var, value in required_vars.items() if not value]
        
        if missing_vars:
            raise ValueError(f"❌ Variáveis de ambiente obrigatórias não definidas: {', '.join(missing_vars)}")
        
        print("✅ Configuração do Supabase validada com sucesso")
        print(f"✅ Supabase URL: {self.SUPABASE_URL}")
        print(f"✅ Database URL configurada")
    
    def get_database_url(self):
        """
        Retorna a URL de conexão com o banco de dados
        """
        return self.DATABASE_URL
    
    def get_supabase_credentials(self):
        """
        Retorna as credenciais do Supabase para uso com o SDK
        """
        return {
            'url': self.SUPABASE_URL,
            'anon_key': self.SUPABASE_ANON_KEY,
            'service_role_key': self.SUPABASE_SERVICE_ROLE_KEY
        }

# Instância global da configuração
supabase_config = SupabaseConfig()