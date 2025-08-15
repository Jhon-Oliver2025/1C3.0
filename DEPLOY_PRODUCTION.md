# 🚀 Deploy em Produção - Sistema de Pagamentos

## 📋 Pré-requisitos

Para testar o Mercado Pago em produção, você precisa:

- ✅ **Servidor com SSL (HTTPS)** - Obrigatório para webhooks
- ✅ **Domínio próprio** - Para configurar certificado SSL
- ✅ **Credenciais de produção** do Mercado Pago
- ✅ **Banco de dados em produção** (Supabase recomendado)

## 🔧 Opções de Deploy

### 1. 🌐 Vercel (Recomendado para Frontend)

**Vantagens:**
- ✅ SSL automático
- ✅ Deploy fácil via GitHub
- ✅ Domínio gratuito com HTTPS
- ✅ Ideal para React/Next.js

**Passos:**
```bash
# 1. Instalar Vercel CLI
npm install -g vercel

# 2. No diretório front/
cd front
vercel

# 3. Seguir instruções do CLI
# Resultado: https://seu-app.vercel.app
```

### 2. 🐳 Railway (Recomendado para Backend)

**Vantagens:**
- ✅ SSL automático
- ✅ Deploy de Python/Flask
- ✅ Variáveis de ambiente seguras
- ✅ Logs em tempo real

**Passos:**
```bash
# 1. Criar conta no Railway.app
# 2. Conectar repositório GitHub
# 3. Configurar variáveis de ambiente
# 4. Deploy automático
```

### 3. 🌊 DigitalOcean App Platform

**Vantagens:**
- ✅ SSL automático
- ✅ Suporte a Docker
- ✅ Escalabilidade
- ✅ Preço acessível

### 4. ☁️ Heroku

**Vantagens:**
- ✅ SSL automático
- ✅ Add-ons integrados
- ✅ Fácil configuração

## 🔐 Configuração do Mercado Pago

### 1. Obter Credenciais de Produção

1. **Acesse:** [Mercado Pago Developers](https://www.mercadopago.com.br/developers)
2. **Vá em:** Suas integrações → Sua aplicação
3. **Copie as credenciais de PRODUÇÃO:**
   - `Access Token`
   - `Public Key`

### 2. Configurar Variáveis de Ambiente

**Backend (.env):**
```bash
# Mercado Pago - PRODUÇÃO
MERCADO_PAGO_ACCESS_TOKEN=APP_USR-1234567890abcdef...
MERCADO_PAGO_PUBLIC_KEY=APP_USR-abcdef1234567890...
MERCADO_PAGO_WEBHOOK_SECRET=sua_chave_secreta_webhook

# URLs de Produção
FRONTEND_URL=https://seu-app.vercel.app
BACKEND_URL=https://seu-backend.railway.app

# Banco de Dados
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua_chave_supabase

# JWT
JWT_SECRET=sua_chave_jwt_super_secreta
```

**Frontend (.env):**
```bash
VITE_API_URL=https://seu-backend.railway.app
VITE_MERCADO_PAGO_PUBLIC_KEY=APP_USR-abcdef1234567890...
```

### 3. Configurar Webhook

1. **No painel do Mercado Pago:**
   - URL: `https://seu-backend.railway.app/api/payments/webhook`
   - Eventos: `payment`

2. **Testar webhook:**
   ```bash
   curl -X POST https://seu-backend.railway.app/api/payments/webhook \
     -H "Content-Type: application/json" \
     -d '{"type":"payment","data":{"id":"123456789"}}'
   ```

## 📦 Deploy Passo a Passo

### Opção A: Vercel + Railway

#### 1. Deploy do Frontend (Vercel)

```bash
# 1. Preparar build
cd front
npm run build

# 2. Deploy
vercel --prod

# 3. Configurar domínio personalizado (opcional)
vercel domains add seu-dominio.com
```

#### 2. Deploy do Backend (Railway)

```bash
# 1. Criar railway.json na raiz do projeto
echo '{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "cd back && python app_supabase.py"
  }
}' > railway.json

# 2. Fazer push para GitHub
git add .
git commit -m "Deploy para produção"
git push

# 3. Conectar no Railway.app
# - Importar repositório
# - Configurar variáveis de ambiente
# - Deploy automático
```

### Opção B: DigitalOcean App Platform

#### 1. Criar App Spec

```yaml
# .do/app.yaml
name: crypten-app
services:
- name: backend
  source_dir: /back
  github:
    repo: seu-usuario/seu-repo
    branch: main
  run_command: python app_supabase.py
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: MERCADO_PAGO_ACCESS_TOKEN
    value: ${MERCADO_PAGO_ACCESS_TOKEN}
  - key: MERCADO_PAGO_PUBLIC_KEY
    value: ${MERCADO_PAGO_PUBLIC_KEY}
  - key: SUPABASE_URL
    value: ${SUPABASE_URL}
  - key: SUPABASE_KEY
    value: ${SUPABASE_KEY}

- name: frontend
  source_dir: /front
  github:
    repo: seu-usuario/seu-repo
    branch: main
  build_command: npm run build
  run_command: npm run preview
  environment_slug: node-js
  instance_count: 1
  instance_size_slug: basic-xxs
```

## 🧪 Testes em Produção

### 1. Cartões de Teste (Sandbox)

```
# Aprovado
Número: 4509 9535 6623 3704
CVC: 123
Vencimento: 11/25
Nome: APRO

# Rejeitado
Número: 4013 5406 8274 6260
CVC: 123
Vencimento: 11/25
Nome: OTHE
```

### 2. Fluxo de Teste

1. **Acesse:** `https://seu-app.vercel.app/checkout-demo`
2. **Escolha um curso** e clique em "Comprar"
3. **Use cartão de teste** no checkout
4. **Verifique webhook** nos logs do backend
5. **Confirme liberação** de acesso

### 3. Monitoramento

```bash
# Logs do Railway
railway logs

# Logs do Vercel
vercel logs

# Status do webhook
curl https://seu-backend.railway.app/api/health
```

## 🔍 Troubleshooting

### Problemas Comuns

**1. Webhook não funciona**
```bash
# Verificar se URL está acessível
curl https://seu-backend.railway.app/api/payments/webhook

# Verificar logs
railway logs --tail
```

**2. CORS Error**
```python
# No backend, verificar CORS
CORS(server, resources={
    r"/api/*": {
        "origins": ["https://seu-app.vercel.app"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

**3. Variáveis de ambiente**
```bash
# Verificar se estão configuradas
echo $MERCADO_PAGO_ACCESS_TOKEN

# No Railway/Vercel, verificar no dashboard
```

## 📊 Monitoramento de Produção

### 1. Logs Importantes

- ✅ **Pagamentos processados**
- ✅ **Webhooks recebidos**
- ✅ **Erros de autenticação**
- ✅ **Falhas de conexão**

### 2. Métricas

- 📈 **Taxa de conversão**
- 💰 **Valor total processado**
- ⚡ **Tempo de resposta**
- 🔄 **Uptime do sistema**

### 3. Alertas

```bash
# Configurar alertas para:
# - Webhook failures
# - Payment errors
# - System downtime
# - High response times
```

## 🎯 Checklist de Deploy

### Antes do Deploy
- [ ] Credenciais de produção configuradas
- [ ] Banco de dados em produção
- [ ] Domínio com SSL configurado
- [ ] Variáveis de ambiente definidas
- [ ] Testes locais passando

### Durante o Deploy
- [ ] Frontend deployado com sucesso
- [ ] Backend deployado com sucesso
- [ ] Webhook configurado no Mercado Pago
- [ ] DNS apontando corretamente
- [ ] SSL funcionando

### Após o Deploy
- [ ] Teste de pagamento com cartão de teste
- [ ] Webhook recebendo notificações
- [ ] Logs sem erros críticos
- [ ] Acesso aos cursos funcionando
- [ ] Performance adequada

## 🚀 URLs de Exemplo

**Frontend:** https://crypten-app.vercel.app
**Backend:** https://crypten-api.railway.app
**Demo:** https://crypten-app.vercel.app/checkout-demo
**Webhook:** https://crypten-api.railway.app/api/payments/webhook

---

**🎉 Com essas configurações, seu sistema estará pronto para processar pagamentos reais com o Mercado Pago!**

## 📞 Suporte

- **Mercado Pago:** [Documentação](https://www.mercadopago.com.br/developers)
- **Vercel:** [Docs](https://vercel.com/docs)
- **Railway:** [Docs](https://docs.railway.app)
- **Supabase:** [Docs](https://supabase.com/docs)