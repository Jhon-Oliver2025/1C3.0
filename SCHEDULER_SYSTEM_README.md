# 🕐 Sistema de Limpeza de Sinais - Scheduler Robusto

## 📋 Visão Geral

Sistema automatizado para limpeza de sinais de trading em horários específicos (10:00 e 21:00 horário de São Paulo), com endpoints para monitoramento, diagnóstico e controle manual.

## 🚀 Funcionalidades Implementadas

### ⚙️ **Scheduler Automático**
- ✅ Limpeza matinal às **10:00** (preparação mercado americano)
- ✅ Limpeza noturna às **21:00** (preparação mercado asiático)
- ✅ Timezone correto: `America/Sao_Paulo`
- ✅ Logging detalhado de todas as operações
- ✅ Tratamento robusto de erros
- ✅ Prevenção de execuções simultâneas

### 🌐 **Endpoints de Gerenciamento**

#### 📊 **Monitoramento**
```
GET /api/scheduler/status
- Status detalhado do scheduler
- Próximas execuções
- Informações de timezone

GET /api/scheduler/health-check
- Diagnóstico completo do sistema
- Verificações de saúde
- Recomendações automáticas

GET /api/scheduler/logs
- Histórico de execuções
- Logs de erro detalhados
- Últimas 50 entradas
```

#### 🔧 **Controle Manual**
```
POST /api/scheduler/manual-cleanup
Body: {"type": "morning|evening|both"}
- Execução manual de limpezas
- Útil para resolver problemas imediatos

POST /api/scheduler/restart
- Reinicia o scheduler
- Resolve problemas de parada
```

## 🛠️ Arquivos Modificados/Criados

### 📁 **Novos Arquivos**
```
back/api_routes/scheduler_management.py  # Endpoints de gerenciamento
back/test_scheduler_system.py           # Testes automatizados
SCHEDULER_SYSTEM_README.md              # Esta documentação
```

### 📝 **Arquivos Melhorados**
```
back/market_scheduler.py                 # Scheduler principal (melhorado)
back/api.py                             # Registro do novo blueprint
```

## 🔍 Como Usar em Produção

### 1️⃣ **Verificar Status do Sistema**
```bash
# Via curl
curl https://1crypten.space/api/scheduler/health-check

# Resposta esperada:
{
  "success": true,
  "overall_status": "HEALTHY",
  "health_checks": {
    "scheduler_running": true,
    "log_file_exists": true,
    "current_hour": 14,
    "timezone_correct": true
  },
  "recommendations": []
}
```

### 2️⃣ **Executar Limpeza Manual (Emergência)**
```bash
# Limpeza matinal
curl -X POST https://1crypten.space/api/scheduler/manual-cleanup \
  -H "Content-Type: application/json" \
  -d '{"type": "morning"}'

# Limpeza noturna
curl -X POST https://1crypten.space/api/scheduler/manual-cleanup \
  -H "Content-Type: application/json" \
  -d '{"type": "evening"}'

# Ambas as limpezas
curl -X POST https://1crypten.space/api/scheduler/manual-cleanup \
  -H "Content-Type: application/json" \
  -d '{"type": "both"}'
```

### 3️⃣ **Reiniciar Scheduler (Se Necessário)**
```bash
curl -X POST https://1crypten.space/api/scheduler/restart
```

### 4️⃣ **Verificar Logs**
```bash
curl https://1crypten.space/api/scheduler/logs
```

## 📊 Monitoramento Recomendado

### 🔔 **Alertas Automáticos**
Configure alertas para:
- Scheduler parado por mais de 1 hora
- Falhas consecutivas nas limpezas
- Ausência de logs por mais de 24h

### 📈 **Métricas Importantes**
- `scheduler_running`: Deve ser sempre `true`
- `last_execution`: Não deve ser mais antigo que 12h
- `overall_status`: Deve ser `HEALTHY`

## 🚨 Resolução de Problemas

### ❌ **Scheduler Parado**
```bash
# 1. Verificar status
curl https://1crypten.space/api/scheduler/health-check

# 2. Reiniciar
curl -X POST https://1crypten.space/api/scheduler/restart

# 3. Verificar se voltou
curl https://1crypten.space/api/scheduler/status
```

### ❌ **Sinais Antigos Acumulados**
```bash
# Executar limpeza manual imediata
curl -X POST https://1crypten.space/api/scheduler/manual-cleanup \
  -H "Content-Type: application/json" \
  -d '{"type": "both"}'
```

### ❌ **Logs de Erro**
```bash
# Verificar logs detalhados
curl https://1crypten.space/api/scheduler/logs

# Procurar por:
# - SCHEDULER_SETUP_ERROR
# - MORNING_CLEANUP_ERROR
# - EVENING_CLEANUP_ERROR
```

## 🔧 Configurações Técnicas

### ⚙️ **Scheduler (APScheduler)**
```python
# Configurações aplicadas:
max_instances=1      # Evita execuções simultâneas
coalesce=True        # Combina execuções perdidas
timezone='America/Sao_Paulo'  # Timezone correto
```

### 📝 **Sistema de Logs**
```
Arquivo: scheduler_log.txt
Formato: TIPO_EVENTO: YYYY-MM-DD HH:MM:SS - Detalhes

Eventos registrados:
- SCHEDULER_SETUP_STARTED/SUCCESS/ERROR
- MORNING_CLEANUP_STARTED/SUCCESS/ERROR
- EVENING_CLEANUP_STARTED/SUCCESS/ERROR
- MANUAL_CLEANUP_EXECUTED
- SCHEDULER_RESTARTED
```

## 🎯 Benefícios da Nova Implementação

### ✅ **Robustez**
- Tratamento completo de erros
- Logs detalhados para debugging
- Prevenção de execuções simultâneas
- Recovery automático

### ✅ **Monitoramento**
- Endpoints para verificação de saúde
- Diagnóstico automático
- Histórico de execuções
- Recomendações inteligentes

### ✅ **Controle Manual**
- Limpeza sob demanda
- Restart do scheduler
- Flexibilidade operacional
- Resolução rápida de problemas

### ✅ **Produção-Ready**
- Compatível com Coolify/Docker
- Logs estruturados
- APIs RESTful
- Documentação completa

## 📅 Cronograma de Execução

```
🌅 10:00 (São Paulo) - Limpeza Matinal
├── Remove sinais OPEN anteriores às 10:00
├── Remove sinais com datas futuras
├── Prepara sistema para mercado americano
└── Log: MORNING_CLEANUP_SUCCESS

🌙 21:00 (São Paulo) - Limpeza Noturna
├── Remove sinais OPEN anteriores às 21:00
├── Remove sinais com datas futuras
├── Prepara sistema para mercado asiático
└── Log: EVENING_CLEANUP_SUCCESS
```

## 🚀 Deploy em Produção

### 1️⃣ **Commit e Push**
```bash
git add .
git commit -m "feat: Sistema robusto de limpeza de sinais com monitoramento"
git push origin main
```

### 2️⃣ **Deploy via Coolify**
- O Coolify detectará as mudanças automaticamente
- O novo sistema será ativado no próximo deploy
- Endpoints estarão disponíveis imediatamente

### 3️⃣ **Verificação Pós-Deploy**
```bash
# Verificar se o sistema está funcionando
curl https://1crypten.space/api/scheduler/health-check

# Deve retornar overall_status: "HEALTHY"
```

---

**✅ Sistema pronto para produção!**

Este sistema resolve definitivamente o problema de limpeza de sinais, fornecendo:
- ⚡ Execução automática confiável
- 🔍 Monitoramento completo
- 🛠️ Controle manual para emergências
- 📊 Logs detalhados para debugging
- 🚀 Compatibilidade total com produção