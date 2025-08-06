# 📱 DESENHO TÉCNICO - DESIGN MOBILE DEFINITIVO

## 🎯 ESTRUTURA HIERÁRQUICA

```
┌─────────────────────────────────────────┐
│ 📱 MOBILE LAYOUT (375px width)         │
├─────────────────────────────────────────┤
│ 🔝 TOP MENU BAR (height: 72px)         │
│ ┌─────┬─────────────────────┬─────────┐ │
│ │ ☰   │ 🔴 LOGO PISCANTE    │         │ │
│ │MENU │ (Backend Status)    │         │ │
│ └─────┴─────────────────────┴─────────┘ │
├─────────────────────────────────────────┤
│ 💭 MOTIVATIONAL CONTAINER               │
│ position: fixed                         │
│ top: 72px                              │
│ height: 90px                           │
│ ┌─────────────────────────────────────┐ │
│ │ "Frase motivacional aqui..."        │ │
│ └─────────────────────────────────────┘ │
├─────────────────────────────────────────┤
│ 📊 MAIN CONTENT CONTAINER               │
│ margin-top: 162px (72px + 90px)        │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ 📈 CABEÇALHO DOS SINAIS             │ │
│ │                                     │ │
│ │ LINHA 1: HORÁRIOS DOS MERCADOS      │ │
│ │ ┌─────────┬─────────┬─────────────┐ │ │
│ │ │ 🇺🇸 EUA  │ 🌏 ÁSIA │ ⏰ TIMER    │ │ │
│ │ │ 09:30   │ 21:00   │ 05:30:15   │ │ │
│ │ │ ABERTO  │ FECHADO │ P/ ABERTURA │ │ │
│ │ └─────────┴─────────┴─────────────┘ │ │
│ │                                     │ │
│ │ LINHA 2: ESTATÍSTICAS               │ │
│ │ ┌─────────┬─────────┬─────────────┐ │ │
│ │ │ Total:  │ Compra: │ Venda:      │ │ │
│ │ │   15    │   08    │    07       │ │ │
│ │ └─────────┴─────────┴─────────────┘ │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ 🃏 CARDS DOS SINAIS                     │
│ ┌─────────────────────────────────────┐ │
│ │ CARD MODELO (baseado na imagem)     │ │
│ │ ┌─────────────────────────────────┐ │ │
│ │ │ UNIUSDT            [VENDA] 🔴   │ │ │
│ │ │ Entrada: 8.977                  │ │ │
│ │ │ Alvo: 7.478                     │ │ │
│ │ │ 01/08/2025, 15:20              │ │ │
│ │ │ Projeção: (16.70%) 📈          │ │ │
│ │ └─────────────────────────────────┘ │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

## 📐 DIMENSÕES E ESPAÇAMENTOS

### 🔝 Top Menu Bar
- **Height:** 72px
- **Position:** fixed, top: 0
- **Background:** #1a1a2e
- **Z-index:** 1000

#### Menu Button (☰)
- **Position:** left: 16px
- **Size:** 24px x 24px
- **Color:** #ffffff
- **Padding:** 12px

#### Logo Piscante
- **Position:** center-left (após menu)
- **Animation:** blink 2s infinite
- **Colors:** 
  - 🔴 Vermelho: Backend OFF
  - 🟢 Verde: Backend ON

### 💭 Motivational Container
- **Position:** fixed
- **Top:** 72px
- **Height:** 90px
- **Width:** 100%
- **Background:** linear-gradient(135deg, #667eea 0%, #764ba2 100%)
- **Padding:** 16px
- **Text-align:** center
- **Font-size:** 14px
- **Color:** #ffffff

### 📊 Main Content Container
- **Margin-top:** 162px (72px + 90px)
- **Padding:** 16px
- **Background:** #f5f5f5

### 📈 Cabeçalho dos Sinais
- **Background:** #ffffff
- **Border-radius:** 12px
- **Padding:** 16px
- **Margin-bottom:** 16px
- **Box-shadow:** 0 2px 8px rgba(0,0,0,0.1)

#### Linha 1: Horários dos Mercados
- **Display:** flex
- **Justify-content:** space-between
- **Margin-bottom:** 12px

**Cada mercado:**
- **Width:** 30%
- **Text-align:** center
- **Font-size:** 12px
- **Font-weight:** 600

**Status Colors:**
- 🟢 ABERTO: #22c55e
- 🔴 FECHADO: #ef4444
- 🟡 TIMER: #f59e0b

#### Linha 2: Estatísticas
- **Display:** flex
- **Justify-content:** space-between
- **Font-size:** 14px
- **Font-weight:** 500

### 🃏 Cards dos Sinais

#### Card Container
- **Background:** #ffffff
- **Border-radius:** 12px
- **Padding:** 16px
- **Margin-bottom:** 12px
- **Box-shadow:** 0 2px 8px rgba(0,0,0,0.1)
- **Border-left:** 4px solid (cor do tipo)

#### Card Header
- **Display:** flex
- **Justify-content:** space-between
- **Align-items:** center
- **Margin-bottom:** 12px

**Símbolo (UNIUSDT):**
- **Font-size:** 18px
- **Font-weight:** 700
- **Color:** #1a1a2e

**Botão Tipo:**
- **COMPRA:** 
  - Background: #22c55e
  - Color: #ffffff
  - Border-left: 4px solid #16a34a
- **VENDA:**
  - Background: #ef4444
  - Color: #ffffff
  - Border-left: 4px solid #dc2626
- **Padding:** 6px 12px
- **Border-radius:** 6px
- **Font-size:** 12px
- **Font-weight:** 600

#### Card Content
**Preços:**
- **Font-size:** 16px
- **Font-weight:** 600
- **Margin-bottom:** 8px

**Labels (Entrada/Alvo):**
- **Font-size:** 12px
- **Color:** #6b7280
- **Font-weight:** 500

**Values:**
- **Color:** #1a1a2e

#### Card Footer
- **Display:** flex
- **Justify-content:** space-between
- **Align-items:** center
- **Margin-top:** 12px
- **Font-size:** 12px

**Data:**
- **Color:** #6b7280

**Projeção:**
- **Font-weight:** 600
- **Color:** 
  - 🟢 Positiva: #22c55e
  - 🔴 Negativa: #ef4444

## 🎨 PALETA DE CORES

```css
:root {
  /* Cores Principais */
  --primary-bg: #1a1a2e;
  --secondary-bg: #16213e;
  --accent-color: #0f3460;
  
  /* Cores dos Sinais */
  --buy-color: #22c55e;
  --buy-hover: #16a34a;
  --sell-color: #ef4444;
  --sell-hover: #dc2626;
  
  /* Cores de Status */
  --market-open: #22c55e;
  --market-closed: #ef4444;
  --market-timer: #f59e0b;
  
  /* Cores de Texto */
  --text-primary: #1a1a2e;
  --text-secondary: #6b7280;
  --text-white: #ffffff;
  
  /* Cores de Fundo */
  --bg-white: #ffffff;
  --bg-light: #f5f5f5;
  --bg-card: #ffffff;
  
  /* Sombras */
  --shadow-sm: 0 2px 8px rgba(0,0,0,0.1);
  --shadow-md: 0 4px 12px rgba(0,0,0,0.15);
}
```

## 📱 RESPONSIVIDADE

### Mobile First (375px - 768px)
- Layout principal otimizado
- Cards em coluna única
- Texto legível
- Touch targets ≥ 44px

### Tablet (768px+)
- Cards em 2 colunas
- Espaçamentos maiores
- Fonte ligeiramente maior

## 🔄 ANIMAÇÕES E TRANSIÇÕES

```css
/* Logo Piscante */
@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0.3; }
}

/* Hover nos Cards */
.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  transition: all 0.3s ease;
}

/* Transições Suaves */
* {
  transition: all 0.3s ease;
}
```

## 🎯 IMPLEMENTAÇÃO PRIORITÁRIA

### Fase 1: Estrutura Base ⚡
1. ✅ Top Menu Bar (72px)
2. ✅ Motivational Container (fixed, 90px)
3. ✅ Main Content Container (margin-top: 162px)

### Fase 2: Cabeçalho dos Sinais 📊
1. ✅ Linha 1: Horários EUA/ÁSIA + Timer
2. ✅ Linha 2: Estatísticas (Total/Compra/Venda)

### Fase 3: Cards dos Sinais 🃏
1. ✅ Layout baseado na imagem anexa
2. ✅ Cores diferenciadas (COMPRA/VENDA)
3. ✅ Informações: Símbolo, Entrada, Alvo, Data, Projeção

### Fase 4: Interações e Animações ✨
1. ✅ Menu expansível
2. ✅ Logo piscante (status backend)
3. ✅ Hover effects nos cards
4. ✅ Transições suaves

## 📋 CHECKLIST DE IMPLEMENTAÇÃO

- [ ] Estrutura HTML mobile-first
- [ ] CSS com variáveis personalizadas
- [ ] Menu expansível funcional
- [ ] Logo com animação de status
- [ ] Container motivacional fixo
- [ ] Cabeçalho com horários dos mercados
- [ ] Cards no formato da imagem
- [ ] Cores diferenciadas por tipo
- [ ] Responsividade tablet
- [ ] Animações e transições
- [ ] Testes em dispositivos reais

---

**🎯 OBJETIVO:** Interface mobile otimizada, intuitiva e visualmente atrativa, seguindo exatamente o modelo da imagem anexa para os cards de sinais.