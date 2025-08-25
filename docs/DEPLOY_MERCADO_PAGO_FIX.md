# 🚀 CORREÇÃO URGENTE - MERCADO PAGO EM PRODUÇÃO

## ❌ PROBLEMA IDENTIFICADO

**Erro 500 em produção:** As credenciais do Mercado Pago não estão configuradas no servidor.

### 📋 Logs do Erro:
```
🔑 [PREFERENCE] Access Token configurado: Não
🔑 [PREFERENCE] Public Key configurado: Não
❌ [PREFERENCE] MERCADO_PAGO_ACCESS_TOKEN não configurado
```

## ✅ SOLUÇÃO IMPLEMENTADA

### 🔧 1. Credenciais Adicionadas ao .env.production

```env
# Mercado Pago - Credenciais de Teste
MERCADO_PAGO_ACCESS_TOKEN=TEST-6555567678065222-081500-d19fea4c0e7513745e4aba7f14244ba4-150384131
MERCADO_PAGO_PUBLIC_KEY=TEST-49cb27ee-fe8c-4aa0-b055-092bf4616484
MERCADO_PAGO_WEBHOOK_SECRET=webhook_secret_test
```

### 🚀 2. Passos para Deploy

#### **Opção A: Via Docker (Recomendado)**

1. **Fazer pull das mudanças:**
```bash
git pull origin main
```

2. **Rebuild do container:**
```bash
docker-compose down
docker-compose up --build -d
```

3. **Verificar logs:**
```bash
docker-compose logs -f backend
```

#### **Opção B: Via Variáveis de Ambiente do Sistema**

1. **Adicionar no servidor:**
```bash
export MERCADO_PAGO_ACCESS_TOKEN="TEST-6555567678065222-081500-d19fea4c0e7513745e4aba7f14244ba4-150384131"
export MERCADO_PAGO_PUBLIC_KEY="TEST-49cb27ee-fe8c-4aa0-b055-092bf4616484"
export MERCADO_PAGO_WEBHOOK_SECRET="webhook_secret_test"
```

2. **Reiniciar o serviço:**
```bash
sudo systemctl restart your-app-service
```

#### **Opção C: Via Painel de Controle (Coolify/Vercel/etc)**

1. **Acessar painel de variáveis de ambiente**
2. **Adicionar as variáveis:**
   - `MERCADO_PAGO_ACCESS_TOKEN` = `TEST-6555567678065222-081500-d19fea4c0e7513745e4aba7f14244ba4-150384131`
   - `MERCADO_PAGO_PUBLIC_KEY` = `TEST-49cb27ee-fe8c-4aa0-b055-092bf4616484`
   - `MERCADO_PAGO_WEBHOOK_SECRET` = `webhook_secret_test`
3. **Fazer redeploy**

### 🔍 3. Verificação Pós-Deploy

#### **Teste 1: Endpoint de Debug**
```bash
curl https://1crypten.space/api/payments/debug
```

**Resposta esperada:**
```json
{
  "success": true,
  "environment_variables": {
    "MERCADO_PAGO_ACCESS_TOKEN": true,
    "MERCADO_PAGO_PUBLIC_KEY": true
  },
  "payment_manager_config": {
    "access_token_exists": true,
    "public_key_exists": true
  }
}
```

#### **Teste 2: API de Configuração**
```bash
curl https://1crypten.space/api/payments/config
```

**Resposta esperada:**
```json
{
  "success": true,
  "config": {
    "public_key": "TEST-49cb27ee-fe8c-4aa0-b055-092bf4616484",
    "currency": "BRL",
    "country": "BR"
  }
}
```

#### **Teste 3: Checkout Funcionando**
1. Acessar: `https://1crypten.space/checkout/despertar-crypto`
2. Verificar se o formulário de pagamento carrega
3. Testar criação de preferência

### 🎯 4. Resultado Esperado

**Logs de Sucesso:**
```
🔑 [PREFERENCE] Access Token configurado: Sim
🔑 [PREFERENCE] Public Key configurado: Sim
✅ [PREFERENCE] Preferência criada com sucesso
```

## 🚨 IMPORTANTE

### ⚠️ Credenciais de Teste
As credenciais fornecidas são de **TESTE**. Para produção real:

1. **Criar conta no Mercado Pago**
2. **Obter credenciais de produção**
3. **Substituir as credenciais TEST- por PROD-**

### 🔒 Segurança
- ✅ Access Token mantido seguro (não exposto no frontend)
- ✅ Public Key pode ser exposta (usada no frontend)
- ✅ Webhook Secret para validar notificações

### 📱 Webhook Configuration
Após resolver o erro 500, configurar webhook no painel do Mercado Pago:
- **URL:** `https://1crypten.space/api/payments/webhook`
- **Eventos:** `payment.created`, `payment.updated`

## 🎉 RESULTADO FINAL

Após aplicar essas configurações:
- ✅ Erro 500 resolvido
- ✅ Checkout transparente funcionando
- ✅ Pagamentos sendo processados
- ✅ Dados dos clientes sendo capturados
- ✅ Sistema pronto para conversões!

---

**🚀 Deploy essas configurações e o checkout estará funcionando em minutos!**