# 📐 DESENHO TÉCNICO MOBILE - ESPECIFICAÇÃO COMPLETA

## 🎯 ESTRUTURA GERAL

### Dimensões Base
- **Largura da tela:** 375px (iPhone padrão)
- **Altura total:** 100vh (viewport height)
- **Orientação:** Portrait (vertical)

---

## 🔝 HEADER FIXO (Container 0)

### Especificações
- **Altura:** 72px
- **Posição:** `position: fixed; top: 0; left: 0; right: 0;`
- **Z-index:** 1000
- **Background:** Gradiente escuro `linear-gradient(135deg, #0A192F 0%, #1a365d 100%)`
- **Border-bottom:** 1px solid #64FFDA

### Elementos Internos
1. **Botão Menu (Esquerda)**
   - Posição: 16px da esquerda
   - Ícone: ☰ (hamburger)
   - Cor: #ffffff
   - Tamanho: 24px

2. **Logo Central (Piscante)**
   - Posição: Centro horizontal
   - Tamanho: 40px x 40px
   - Efeito: Piscar quando backend offline
   - Cores: Verde (#4CAF50) online / Vermelho (#E53E3E) offline

3. **Espaço Direita**
   - Reservado para futuras funcionalidades

---

## 📦 CONTAINER 1 - MOTIVAÇÃO + CABEÇALHO (Fixo)

### Posicionamento
- **Posição:** `position: fixed`
- **Top:** 72px (após header)
- **Left/Right:** 0
- **Z-index:** 100
- **Background:** Transparente

### 💭 SEÇÃO MOTIVACIONAL
- **Altura:** 90px
- **Background:** `linear-gradient(135deg, #2d5a87, #1e3a5f)`
- **Border-bottom:** 1px solid #64FFDA
- **Padding:** 0 16px
- **Text-align:** center
- **Font-size:** 14px
- **Color:** #ffffff
- **Text-shadow:** 2px 2px 4px rgba(0, 0, 0, 0.8)
- **Transition:** opacity 0.8s ease-in-out (para troca de frases)

### 🔄 ESPAÇAMENTO DE SEGURANÇA
- **Altura:** 4px
- **Background:** Transparente
- **Função:** Separação visual entre motivação e cabeçalho

### 📊 CABEÇALHO DOS SINAIS
- **Altura:** 70px
- **Background:** `var(--card-bg)` (#0f2a44)
- **Border-radius:** 8px
- **Border:** 1px solid rgba(100, 255, 218, 0.3)
- **Margin:** 0 16px
- **Box-shadow:** 0 2px 8px rgba(0, 0, 0, 0.1)

#### Linha 1 - Horários dos Mercados (35px)
- **Display:** Grid 3 colunas
- **Grid-template-columns:** 1fr 1fr 1fr
- **Gap:** 8px
- **Padding:** 5px 10px
- **Background:** #1a365d

**Itens do mercado:**
- EUA: Horário + Status (ABERTO/FECHADO)
- ÁSIA: Horário + Status (ABERTO/FECHADO)
- RELÓGIO: Hora atual + "24/7"

**Cores dos status:**
- ABERTO: #4CAF50
- FECHADO: #E53E3E
- 24/7: #FFD700

#### Linha 2 - Estatísticas (35px)
- **Display:** Grid 3 colunas
- **Grid-template-columns:** 1fr 1fr 1fr
- **Gap:** 8px
- **Padding:** 5px 10px
- **Background:** #1a365d

**Estatísticas:**
- Total: Número total de sinais
- Compra: Sinais de compra
- Venda: Sinais de venda

---

## 📱 CONTAINER 2 - CARDS DOS SINAIS (Scrollável)

### Posicionamento
- **Margin-top:** 232px (72px header + 90px motivação + 70px cabeçalho)
- **Padding:** 16px
- **Height:** `calc(100vh - 232px)`
- **Overflow-y:** auto
- **Overflow-x:** hidden
- **Background:** Transparente

### 🎴 LAYOUT DOS CARDS
- **Display:** Grid
- **Grid-template-columns:** repeat(2, 1fr)
- **Gap:** 16px
- **Margin:** 0
- **Padding:** 0

### 🎨 DESIGN DOS CARDS
- **Background:** Fundo azul escuro com efeitos glassmorfismo
- **Border-radius:** 12px
- **Border:** 1px solid rgba(100, 255, 218, 0.2)
- **Box-shadow:** 
  - `0 8px 32px rgba(0, 0, 0, 0.3)`
  - `inset 0 1px 0 rgba(255, 255, 255, 0.1)`
- **Backdrop-filter:** blur(10px)
- **Min-height:** 120px
- **Padding:** 12px

### 📜 BARRA DE ROLAGEM CUSTOMIZADA
- **Width:** 6px
- **Background:** rgba(100, 255, 218, 0.1)
- **Border-radius:** 3px
- **Thumb-color:** rgba(100, 255, 218, 0.5)
- **Thumb-hover:** rgba(100, 255, 218, 0.8)
- **Position:** Lado direito

---

## 📐 RESPONSIVIDADE

### Mobile (até 480px)
- **Container 2 padding:** 12px
- **Cards gap:** 12px
- **Cabeçalho margin:** 0 12px

### Tablet (481px - 768px)
- **Container 2 padding:** 24px
- **Cards gap:** 16px
- **Max-width:** 768px (centralizado)
- **Cabeçalho margin:** 0 24px

---

## 🎨 PALETA DE CORES

### Cores Principais
- **Primary:** #64FFDA (Cyan/Turquesa)
- **Background Dark:** #0A192F
- **Card Background:** #0f2a44
- **Secondary Dark:** #1a365d
- **Text Primary:** #ffffff
- **Text Secondary:** #A0AEC0

### Cores de Status
- **Success/Open:** #4CAF50
- **Error/Closed:** #E53E3E
- **Warning/24-7:** #FFD700
- **Info:** #64FFDA

### Efeitos Glassmorfismo
- **Backdrop-filter:** blur(10px)
- **Background:** rgba(15, 42, 68, 0.8)
- **Border:** 1px solid rgba(100, 255, 218, 0.2)
- **Box-shadow:** 0 8px 32px rgba(0, 0, 0, 0.3)

---

## ⚡ ANIMAÇÕES E TRANSIÇÕES

### Frases Motivacionais
- **Duração:** 8 segundos por frase
- **Transição:** opacity 0.8s ease-in-out
- **Efeito:** Fade in/out suave

### Cards
- **Hover:** transform: translateY(-2px)
- **Transition:** all 0.3s ease
- **Shadow-hover:** 0 12px 40px rgba(0, 0, 0, 0.4)

### Scroll
- **Smooth-scrolling:** enabled
- **Scroll-behavior:** smooth

---

## 🔧 IMPLEMENTAÇÃO TÉCNICA

### CSS Classes Principais
```css
.mobile-container
.mobile-top-header
.mobile-motivation-header-container
.mobile-motivational
.mobile-signals-header
.mobile-cards-container
.mobile-signals-list
```

### Z-Index Hierarchy
1. **Header:** 1000
2. **Container 1:** 100
3. **Container 2:** 1

### Performance
- **Will-change:** transform (para animações)
- **Contain:** layout style paint
- **Transform3d:** translateZ(0) para aceleração GPU

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

- [ ] Header fixo com logo piscante
- [ ] Container 1 fixo (motivação + cabeçalho)
- [ ] Espaçamento de 4px entre motivação e cabeçalho
- [ ] Container 2 scrollável com cards
- [ ] Grid 2x2 para cards
- [ ] Barra de rolagem customizada
- [ ] Efeitos glassmorfismo nos cards
- [ ] Responsividade mobile/tablet
- [ ] Animações suaves
- [ ] Cores e gradientes corretos

---

**Data de criação:** $(date)
**Versão:** 1.0
**Status:** Especificação completa para implementação