# Migração para Supabase 🚀

Este documento descreve como migrar o Krypton Trading Bot do PostgreSQL local para o Supabase.

## Por que Supabase?

- ✅ **Banco gerenciado**: Sem necessidade de manter PostgreSQL local
- ✅ **Escalabilidade**: Infraestrutura robusta e escalável
- ✅ **Integração com Trae AI**: Suporte nativo
- ✅ **Deploy simplificado**: Menos dependências no Docker
- ✅ **Backup automático**: Dados seguros na nuvem

## Pré-requisitos

1. Conta no [Supabase](https://supabase.com)
2. Projeto criado no Supabase
3. Credenciais do projeto (URL, chaves, connection string)

## Passo 1: Configurar Projeto no Supabase

### 1.1 Criar Projeto
1. Acesse [supabase.com](https://supabase.com)
2. Clique em "Start your project"
3. Crie um novo projeto
4. Escolha uma região próxima (ex: South America)
5. Defina uma senha forte para o banco

### 1.2 Obter Credenciais
1. Vá para **Settings > API**
2. Copie:
   - Project URL
   - anon/public key
   - service_role/secret key

### 1.3 Obter Connection String
1. Vá para **Settings > Database**
2. Na seção "Connection string", copie a URI
3. Substitua `[YOUR-PASSWORD]` pela senha do banco

## Passo 2: Configurar Variáveis de Ambiente

### 2.1 Arquivo Local (.env)
```bash
# Copie .env.supabase.example para .env
cp .env.supabase.example .env

# Edite o arquivo .env com suas credenciais
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_DATABASE_URL=postgresql://postgres:your-password@db.your-project-ref.supabase.co:5432/postgres
```

### 2.2 Coolify (Produção)
No painel do Coolify, adicione as variáveis:
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_DATABASE_URL`

## Passo 3: Executar Script de Migração

```bash
# Executar script de verificação e migração
python migrate_to_supabase.py
```

O script irá:
- ✅ Verificar se todas as variáveis estão configuradas
- ✅ Testar conexão com Supabase
- ✅ Criar tabelas necessárias
- ✅ Mostrar instruções de deploy

## Passo 4: Testar Localmente

```bash
# Testar a aplicação com Supabase
python back/app_supabase.py

# Verificar endpoints
curl http://localhost:5000/api/health
curl http://localhost:5000/api/status
```

## Passo 5: Deploy no Coolify

### 5.1 Commit das Alterações
```bash
git add .
git commit -m "feat: migração para Supabase"
git push origin main
```

### 5.2 Configurar Variáveis no Coolify
1. Acesse seu projeto no Coolify
2. Vá para "Environment Variables"
3. Adicione as 4 variáveis do Supabase
4. Salve as configurações

### 5.3 Fazer Deploy
1. Clique em "Deploy"
2. Aguarde o build e deploy
3. Verifique os logs para confirmar sucesso

## Arquivos Modificados

### Novos Arquivos
- `back/supabase_config.py` - Configuração do Supabase
- `back/app_supabase.py` - Aplicação principal com Supabase
- `migrate_to_supabase.py` - Script de migração
- `.env.supabase.example` - Exemplo de variáveis

### Arquivos Modificados
- `docker-compose.coolify.yml` - Removido PostgreSQL, adicionado variáveis Supabase
- `back/Dockerfile` - Atualizado para usar app_supabase.py

## Benefícios da Migração

### Antes (PostgreSQL Local)
- ❌ Dependência de container PostgreSQL
- ❌ Problemas de inicialização (wait_for_database)
- ❌ Backup manual necessário
- ❌ Recursos limitados do container

### Depois (Supabase)
- ✅ Banco gerenciado na nuvem
- ✅ Inicialização rápida
- ✅ Backup automático
- ✅ Escalabilidade automática
- ✅ Interface web para administração

## Troubleshooting

### Erro de Conexão
```
Connection refused
```
**Solução**: Verifique se:
- SUPABASE_DATABASE_URL está correta
- Senha do banco está correta
- Projeto Supabase está ativo

### Variáveis Não Definidas
```
Variáveis de ambiente obrigatórias não definidas
```
**Solução**: 
- Execute `python migrate_to_supabase.py` para verificar
- Confirme que todas as 4 variáveis estão no .env ou Coolify

### Tabelas Não Existem
```
relation "trading_signals" does not exist
```
**Solução**:
- Execute `python migrate_to_supabase.py` para criar tabelas
- Ou crie manualmente no Supabase Dashboard

## Próximos Passos

1. ✅ Migração concluída
2. 🔄 Monitorar logs de produção
3. 📊 Configurar dashboards no Supabase
4. 🔒 Configurar Row Level Security (RLS) se necessário
5. 📈 Otimizar queries conforme uso

---

**🎉 Parabéns! Seu Krypton Trading Bot agora usa Supabase!**

Para suporte, consulte:
- [Documentação Supabase](https://supabase.com/docs)
- [Supabase Python Client](https://supabase.com/docs/reference/python/introduction)