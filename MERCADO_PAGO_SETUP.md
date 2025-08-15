# 🛒 Sistema de Pagamentos - Mercado Pago

## 📋 Visão Geral

Este sistema implementa uma integração completa com o Mercado Pago para venda de cursos online, incluindo:

- ✅ **Criação de preferências de pagamento**
- ✅ **Processamento de webhooks**
- ✅ **Controle de acesso aos cursos**
- ✅ **Verificação de permissões por aula**
- ✅ **Interface de checkout responsiva**
- ✅ **Páginas de sucesso e falha**

## 🔧 Configuração

### 1. Variáveis de Ambiente

Adicione as seguintes variáveis no arquivo `.env` do backend:

```bash
# Configurações do Mercado Pago
MERCADO_PAGO_ACCESS_TOKEN=your_mercado_pago_access_token
MERCADO_PAGO_PUBLIC_KEY=your_mercado_pago_public_key
MERCADO_PAGO_WEBHOOK_SECRET=your_webhook_secret

# URLs do Frontend e Backend
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:5000
```

### 2. Obter Credenciais do Mercado Pago

1. **Acesse o [Mercado Pago Developers](https://www.mercadopago.com.br/developers)**
2. **Crie uma aplicação**
3. **Copie as credenciais:**
   - `Access Token` (para o backend)
   - `Public Key` (para o frontend)

### 3. Configurar Webhook

1. **No painel do Mercado Pago, configure o webhook:**
   - URL: `https://seu-dominio.com/api/payments/webhook`
   - Eventos: `payment`

2. **Para desenvolvimento local, use ngrok:**
   ```bash
   ngrok http 5000
   # Use a URL gerada: https://abc123.ngrok.io/api/payments/webhook
   ```

## 🏗️ Estrutura do Sistema

### Backend

```
back/
├── core/
│   └── payments.py          # Gerenciador de pagamentos
├── api_routes/
│   └── payments.py          # Rotas da API de pagamentos
├── purchases.csv            # Registro de compras
└── course_access.csv        # Controle de acesso aos cursos
```

### Frontend

```
front/src/
├── components/
│   ├── MercadoPagoCheckout/     # Componente de checkout
│   └── ProtectedLesson/         # Proteção de aulas
├── hooks/
│   └── useCourseAccess.ts       # Hook para gerenciar acesso
└── pages/
    └── Payment/                 # Páginas de sucesso/falha
```

## 🎯 Como Usar

### 1. Adicionar Checkout a uma Página

```tsx
import MercadoPagoCheckout from '../components/MercadoPagoCheckout/MercadoPagoCheckout';

const CoursePage = () => {
  return (
    <div>
      <h1>Curso Despertar Crypto</h1>
      
      <MercadoPagoCheckout
        courseId="despertar_crypto"
        course={{
          name: "Despertar Crypto - 10 Aulas",
          description: "Curso completo de introdução às criptomoedas",
          price: 197.00
        }}
        onSuccess={(paymentData) => {
          console.log('Pagamento realizado:', paymentData);
        }}
        onError={(error) => {
          console.error('Erro no pagamento:', error);
        }}
      />
    </div>
  );
};
```

### 2. Proteger uma Aula

```tsx
import ProtectedLesson from '../components/ProtectedLesson/ProtectedLesson';

const LessonPage = () => {
  return (
    <ProtectedLesson lessonId="despertar-crypto-01">
      {/* Conteúdo da aula - só será exibido se o usuário tiver acesso */}
      <video src="aula01.mp4" controls />
      <h2>Aula 1 - Introdução</h2>
      <p>Conteúdo da aula...</p>
    </ProtectedLesson>
  );
};
```

### 3. Verificar Acesso Programaticamente

```tsx
import { useCourseAccess } from '../hooks/useCourseAccess';

const MyComponent = () => {
  const { 
    userCourses, 
    hasAccessToCourse, 
    checkLessonAccess 
  } = useCourseAccess();

  const handleCheckAccess = async () => {
    const hasAccess = await checkLessonAccess('despertar-crypto-01');
    console.log('Tem acesso:', hasAccess);
  };

  return (
    <div>
      <p>Cursos do usuário: {userCourses.length}</p>
      <button onClick={handleCheckAccess}>Verificar Acesso</button>
    </div>
  );
};
```

## 📊 Cursos Disponíveis

O sistema vem pré-configurado com 3 cursos:

### 1. Despertar Crypto (R$ 197,00)
- **ID:** `despertar_crypto`
- **Aulas:** `despertar-crypto-01` até `despertar-crypto-10`
- **Descrição:** Curso completo de introdução às criptomoedas

### 2. Masterclass (R$ 497,00)
- **ID:** `masterclass`
- **Aulas:** `masterclass-01` até `masterclass-04`
- **Descrição:** Curso avançado de trading e análise técnica

### 3. App 1Crypten e Mentoria (R$ 997,00)
- **ID:** `app_mentoria`
- **Aulas:** `app-01` até `app-04`
- **Descrição:** Acesso ao app exclusivo e mentoria personalizada

## 🔄 Fluxo de Pagamento

1. **Usuário clica em "Comprar"**
2. **Sistema cria preferência no Mercado Pago**
3. **Usuário é redirecionado para o checkout**
4. **Mercado Pago processa o pagamento**
5. **Webhook notifica o sistema**
6. **Sistema libera acesso ao curso**
7. **Usuário é redirecionado para página de sucesso**

## 🛡️ Segurança

- ✅ **Tokens JWT** para autenticação
- ✅ **Verificação de webhook** do Mercado Pago
- ✅ **Validação de acesso** em cada aula
- ✅ **Proteção contra acesso não autorizado**
- ✅ **Logs de transações**

## 🧪 Testes

### Cartões de Teste (Sandbox)

```
# Cartão Aprovado
Número: 4509 9535 6623 3704
CVC: 123
Vencimento: 11/25

# Cartão Rejeitado
Número: 4013 5406 8274 6260
CVC: 123
Vencimento: 11/25
```

### Testar Webhook Localmente

```bash
# 1. Instalar ngrok
npm install -g ngrok

# 2. Expor porta local
ngrok http 5000

# 3. Configurar webhook no Mercado Pago
# URL: https://abc123.ngrok.io/api/payments/webhook
```

## 📝 API Endpoints

### Pagamentos
- `GET /api/payments/courses` - Lista cursos disponíveis
- `GET /api/payments/user-courses` - Cursos do usuário
- `POST /api/payments/create-preference` - Criar preferência
- `POST /api/payments/webhook` - Webhook do Mercado Pago
- `GET /api/payments/check-access/:courseId` - Verificar acesso ao curso
- `GET /api/payments/check-lesson-access/:lessonId` - Verificar acesso à aula

### Exemplo de Uso da API

```javascript
// Criar preferência de pagamento
const response = await fetch('/api/payments/create-preference', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    course_id: 'despertar_crypto'
  })
});

const data = await response.json();
if (data.success) {
  // Redirecionar para checkout
  window.location.href = data.preference.init_point;
}
```

## 🚀 Deploy em Produção

### 1. Configurar Variáveis de Ambiente

```bash
# Produção
MERCADO_PAGO_ACCESS_TOKEN=PROD_ACCESS_TOKEN
MERCADO_PAGO_PUBLIC_KEY=PROD_PUBLIC_KEY
FRONTEND_URL=https://seu-dominio.com
BACKEND_URL=https://api.seu-dominio.com
```

### 2. Configurar Webhook

- URL: `https://api.seu-dominio.com/api/payments/webhook`
- Certificado SSL válido obrigatório

### 3. Monitoramento

- Logs de pagamento em `logs/payments.log`
- Dashboard do Mercado Pago para acompanhar transações
- Alertas para falhas de webhook

## 🆘 Troubleshooting

### Problemas Comuns

**1. Webhook não está sendo chamado**
- Verificar URL do webhook
- Certificar que a URL está acessível publicamente
- Verificar logs do servidor

**2. Pagamento aprovado mas acesso não liberado**
- Verificar processamento do webhook
- Verificar logs de erro
- Verificar se o external_reference está correto

**3. Erro de autenticação**
- Verificar se o token JWT está válido
- Verificar se o usuário está logado

### Logs Importantes

```bash
# Backend logs
tail -f logs/app.log | grep payment

# Webhook logs
tail -f logs/webhook.log
```

## 📞 Suporte

Para dúvidas sobre a integração:

1. **Documentação oficial:** [Mercado Pago Developers](https://www.mercadopago.com.br/developers)
2. **Logs do sistema:** Verificar arquivos de log
3. **Testes:** Usar ambiente sandbox para testes

---

**🎉 Sistema pronto para uso! Agora você pode vender seus cursos com segurança e facilidade.**