# 🗄️ PLANO DE MIGRAÇÃO PARA SUPABASE
## Centralização e Padronização do Sistema de Sinais

### 🚨 PROBLEMA IDENTIFICADO

#### **Múltiplas Fontes de Dados:**
- ❌ SQLite local: `Cryptem1.1/back/signals.db` (38 sinais)
- ❌ CSV histórico: `back/signals_history.csv` (3 sinais)
- ❌ APIs inconsistentes retornando 0 sinais
- ❌ Dashboard mostrando 66 sinais (fonte desconhecida)
- ❌ Sistema de monitoramento vazio

#### **Consequências:**
- 🔄 Dados inconsistentes entre sistemas
- 📊 Dashboard e monitoramento desconectados
- 🚫 Simulação de $1.000 não funciona
- ⚠️ Conflitos de sincronização

---

## 🎯 SOLUÇÃO: CENTRALIZAÇÃO NO SUPABASE

### **📋 ESTRUTURA ÚNICA DE DADOS**

#### **1️⃣ Tabela Principal: `trading_signals`**
```sql
CREATE TABLE trading_signals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  symbol VARCHAR(20) NOT NULL,
  signal_type VARCHAR(10) NOT NULL CHECK (signal_type IN ('COMPRA', 'VENDA')),
  entry_price DECIMAL(20, 8) NOT NULL,
  target_price DECIMAL(20, 8),
  entry_time TIMESTAMP WITH TIME ZONE NOT NULL,
  confirmed_at TIMESTAMP WITH TIME ZONE,
  status VARCHAR(20) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'CONFIRMED', 'REJECTED', 'EXPIRED')),
  quality_score DECIMAL(5, 2),
  signal_class VARCHAR(20) DEFAULT 'PREMIUM',
  confirmation_reasons TEXT[],
  btc_correlation DECIMAL(5, 2),
  btc_trend VARCHAR(20),
  projection_percentage DECIMAL(5, 2),
  
  -- Campos de monitoramento
  is_monitored BOOLEAN DEFAULT FALSE,
  monitoring_started_at TIMESTAMP WITH TIME ZONE,
  monitoring_status VARCHAR(20) DEFAULT 'INACTIVE' CHECK (monitoring_status IN ('INACTIVE', 'MONITORING', 'COMPLETED', 'EXPIRED')),
  days_monitored INTEGER DEFAULT 0,
  
  -- Campos de simulação financeira
  simulation_investment DECIMAL(10, 2) DEFAULT 1000.00,
  simulation_current_value DECIMAL(10, 2) DEFAULT 1000.00,
  simulation_pnl_usd DECIMAL(10, 2) DEFAULT 0.00,
  simulation_pnl_percentage DECIMAL(5, 2) DEFAULT 0.00,
  simulation_max_value_reached DECIMAL(10, 2) DEFAULT 1000.00,
  simulation_target_value DECIMAL(10, 2) DEFAULT 4000.00,
  simulation_position_size DECIMAL(20, 8) DEFAULT 0.00,
  
  -- Campos de alavancagem
  max_leverage INTEGER,
  required_percentage DECIMAL(5, 2),
  current_profit DECIMAL(5, 2) DEFAULT 0.00,
  max_profit_reached DECIMAL(5, 2) DEFAULT 0.00,
  
  -- Metadados
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  -- Índices
  UNIQUE(symbol, signal_type, entry_time)
);

-- Índices para performance
CREATE INDEX idx_trading_signals_status ON trading_signals(status);
CREATE INDEX idx_trading_signals_monitoring ON trading_signals(is_monitored, monitoring_status);
CREATE INDEX idx_trading_signals_symbol ON trading_signals(symbol);
CREATE INDEX idx_trading_signals_created_at ON trading_signals(created_at DESC);
```

#### **2️⃣ Tabela de Histórico de Preços: `signal_price_history`**
```sql
CREATE TABLE signal_price_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  signal_id UUID REFERENCES trading_signals(id) ON DELETE CASCADE,
  price DECIMAL(20, 8) NOT NULL,
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  -- Índices
  INDEX(signal_id, timestamp)
);
```

#### **3️⃣ Tabela de Configurações: `system_config`**
```sql
CREATE TABLE system_config (
  key VARCHAR(100) PRIMARY KEY,
  value JSONB NOT NULL,
  description TEXT,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Configurações padrão
INSERT INTO system_config (key, value, description) VALUES
('monitoring_days', '15', 'Dias de monitoramento por sinal'),
('simulation_investment', '1000.00', 'Valor de investimento simulado em USD'),
('target_profit_percentage', '300', 'Meta de lucro em percentual'),
('auto_monitoring', 'true', 'Ativar monitoramento automático de sinais confirmados');
```

---

## 🔄 PLANO DE MIGRAÇÃO

### **FASE 1: PREPARAÇÃO (30 min)**

#### **1.1 Criar Estrutura no Supabase**
- ✅ Criar tabelas no Supabase
- ✅ Configurar RLS (Row Level Security)
- ✅ Inserir configurações padrão

#### **1.2 Backup dos Dados Atuais**
- ✅ Exportar SQLite para JSON
- ✅ Exportar CSV para JSON
- ✅ Salvar backup completo

### **FASE 2: MIGRAÇÃO DE DADOS (45 min)**

#### **2.1 Script de Migração**
- ✅ Ler dados do SQLite (38 sinais)
- ✅ Ler dados do CSV (3 sinais)
- ✅ Normalizar formato dos dados
- ✅ Inserir no Supabase
- ✅ Validar integridade

#### **2.2 Ativação do Monitoramento**
- ✅ Marcar sinais como monitorados
- ✅ Inicializar simulação de $1.000
- ✅ Calcular alavancagem automática

### **FASE 3: ATUALIZAÇÃO DOS SISTEMAS (60 min)**

#### **3.1 Backend APIs**
- ✅ Atualizar `Database` class para usar Supabase
- ✅ Modificar `BTCSignalManager` para Supabase
- ✅ Atualizar `SignalMonitoringSystem` para Supabase
- ✅ Atualizar todas as rotas da API

#### **3.2 Frontend**
- ✅ Atualizar endpoints no Dashboard
- ✅ Atualizar página de Investimentos Simulados
- ✅ Testar todas as funcionalidades

### **FASE 4: LIMPEZA (15 min)**

#### **4.1 Remover Fontes Antigas**
- ❌ Deletar `signals.db`
- ❌ Deletar `signals_history.csv`
- ❌ Remover código SQLite obsoleto

#### **4.2 Validação Final**
- ✅ Testar dashboard (deve mostrar sinais corretos)
- ✅ Testar monitoramento (deve funcionar)
- ✅ Testar simulação (deve calcular P&L)

---

## 🎯 BENEFÍCIOS DA MIGRAÇÃO

### **✅ Vantagens Imediatas:**
- 🗄️ **Fonte única de verdade:** Todos os dados no Supabase
- 🔄 **Sincronização automática:** Tempo real entre sistemas
- 📊 **Dados consistentes:** Dashboard e monitoramento alinhados
- 💰 **Simulação funcionando:** $1.000 por sinal
- 🚀 **Performance melhorada:** Queries otimizadas
- 🔒 **Backup automático:** Dados seguros na nuvem

### **✅ Vantagens a Longo Prazo:**
- 📈 **Escalabilidade:** Suporte a milhares de sinais
- 🔧 **Manutenibilidade:** Código mais limpo
- 🌐 **Acessibilidade:** Dados acessíveis de qualquer lugar
- 📊 **Analytics:** Queries complexas possíveis
- 🔄 **Integrações:** Fácil conexão com outros sistemas

---

## 🚀 CRONOGRAMA DE EXECUÇÃO

### **⏰ Tempo Total Estimado: 2h 30min**

```
09:00 - 09:30 | FASE 1: Preparação
09:30 - 10:15 | FASE 2: Migração de Dados  
10:15 - 11:15 | FASE 3: Atualização dos Sistemas
11:15 - 11:30 | FASE 4: Limpeza e Validação
```

### **🎯 Resultado Final:**
- ✅ **66 sinais** migrados e funcionando
- ✅ **Sistema de monitoramento** ativo
- ✅ **Simulação de $1.000** operacional
- ✅ **Dashboard** mostrando dados corretos
- ✅ **APIs** todas funcionando
- ✅ **Código** limpo e organizado

---

## 💡 PRÓXIMOS PASSOS

1. **Aprovação do Plano** ✋
2. **Execução da Migração** 🚀
3. **Testes Completos** 🧪
4. **Deploy em Produção** 🌐

---

**🎉 RESULTADO: SISTEMA UNIFICADO E EFICIENTE!**

Após a migração, teremos um sistema robusto, escalável e totalmente funcional com todos os 66 sinais sendo monitorados com simulação de $1.000 USD em tempo real!