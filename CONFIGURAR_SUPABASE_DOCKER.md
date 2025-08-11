# 🗄️ Configuração Supabase para Docker Desktop

## 📋 Pré-requisitos

Antes de executar o sistema Docker, você precisa configurar as credenciais do Supabase.

### 1. 🔑 Obter Credenciais do Supabase

1. **Acesse** [supabase.com](https://supabase.com)
2. **Faça login** na sua conta
3. **Selecione** seu projeto 1Crypten
4. **Vá em** Settings > API
5. **Copie** as seguintes informações:
   - **Project URL** (ex: `https://seu-projeto.supabase.co`)
   - **anon public** (chave anônima)
   - **service_role** (chave de serviço)

### 2. 🔗 Obter URL do Banco de Dados

1. **Vá em** Settings > Database
2. **Copie** a **Connection string** no formato:
   ```
   postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres
   ```
3. **Substitua** `[PASSWORD]` pela sua senha do banco

### 3. 📝 Criar Arquivo .env

1. **Copie** o arquivo `.env.docker.example` para `.env`:
   ```bash
   copy .env.docker.example .env
   ```

2. **Edite** o arquivo `.env` com suas credenciais:
   ```env
   # === SUPABASE CONFIGURATION ===
   SUPABASE_URL=https://seu-projeto.supabase.co
   SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   SUPABASE_DATABASE_URL=postgresql://postgres:sua-senha@db.seu-projeto.supabase.co:5432/postgres
   
   # === BINANCE API ===
   BINANCE_API_KEY=sua_binance_api_key
   BINANCE_SECRET_KEY=sua_binance_secret_key
   
   # === TELEGRAM BOT ===
   TELEGRAM_BOT_TOKEN=1234567890:AAAA...
   TELEGRAM_CHAT_ID=1249100206
   ```

### 4. ✅ Verificar Configuração

**Execute** o teste de configuração:
```bash
python -c "from back.supabase_config import supabase_config; print('✅ Supabase configurado!' if supabase_config.is_configured else '❌ Configuração incompleta')"
```

## 🚀 Executar Sistema Docker

Após configurar o Supabase:

```bash
python start_docker_test.py
```

## 🔧 Troubleshooting

### ❌ "Supabase não configurado"

1. **Verifique** se o arquivo `.env` existe
2. **Confirme** se todas as variáveis estão preenchidas
3. **Teste** a conexão manualmente

### ❌ "Erro de conexão com banco"

1. **Verifique** se a URL do banco está correta
2. **Confirme** se a senha está correta
3. **Teste** no Supabase Dashboard se o banco está ativo

### ❌ "Tabelas não encontradas"

1. **Execute** as migrações no Supabase:
   ```sql
   -- No SQL Editor do Supabase
   CREATE TABLE IF NOT EXISTS users (
       id SERIAL PRIMARY KEY,
       email VARCHAR(255) UNIQUE NOT NULL,
       name VARCHAR(255) NOT NULL,
       password_hash VARCHAR(255) NOT NULL,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   
   CREATE TABLE IF NOT EXISTS signals (
       id SERIAL PRIMARY KEY,
       symbol VARCHAR(50) NOT NULL,
       type VARCHAR(10) NOT NULL,
       entry_price DECIMAL(20,8) NOT NULL,
       target_price DECIMAL(20,8) NOT NULL,
       projection_percentage DECIMAL(5,2) NOT NULL,
       quality_score DECIMAL(5,2) NOT NULL,
       signal_class VARCHAR(20) NOT NULL,
       status VARCHAR(20) DEFAULT 'OPEN',
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   
   CREATE TABLE IF NOT EXISTS user_sessions (
       id SERIAL PRIMARY KEY,
       user_id INTEGER REFERENCES users(id),
       session_token VARCHAR(255) NOT NULL,
       expires_at TIMESTAMP NOT NULL,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   ```

## 📊 Vantagens do Supabase

✅ **Banco em produção**: Mesmo ambiente que a VPS  
✅ **Dados persistentes**: Não perde dados ao reiniciar Docker  
✅ **Escalabilidade**: Suporta múltiplas conexões  
✅ **Backup automático**: Supabase faz backup automaticamente  
✅ **Monitoramento**: Dashboard com métricas em tempo real  
✅ **Sem conflitos**: Evita problemas de porta e configuração local  

## 🎯 Próximos Passos

Após configurar o Supabase e executar o Docker:

1. ✅ **Testes automatizados** serão executados
2. ✅ **PWA** será testado e validado
3. ✅ **Integrações** (Telegram, Binance) serão verificadas
4. ✅ **Performance** será medida
5. ✅ **Relatório** será gerado

**Sistema estará pronto para produção na VPS!** 🚀