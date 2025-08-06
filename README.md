# 1Crypten - Sistema de Sinais de Criptomoedas

Sistema completo de análise técnica e sinais de trading para criptomoedas, desenvolvido com React (frontend) e Flask (backend).

## 🐳 Desenvolvimento via Docker (ÚNICO MODELO SUPORTADO)

Este projeto foi otimizado para funcionar **EXCLUSIVAMENTE via Docker**. Todos os arquivos de desenvolvimento local foram removidos para manter o foco no modelo Docker.

### Pré-requisitos
- Docker Desktop instalado e rodando
- Arquivo `.env` configurado (copie de `.env.example`)

### Como Executar

```bash
# 1. Clone o repositório
git clone <repo-url>
cd 1C3.0

# 2. Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas configurações

# 3. Inicie o sistema completo
docker-compose -f docker-compose.prod.yml up -d

# 4. Verifique o status
docker ps
```

### Acessos
- **Frontend**: http://localhost/dashboard
- **API**: http://localhost/api/status
- **Nginx**: http://localhost

### Comandos Úteis

```bash
# Parar o sistema
docker-compose -f docker-compose.prod.yml down

# Rebuild completo
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build

# Ver logs
docker logs crypto-frontend
docker logs crypto-backend
docker logs crypto-nginx

# Reiniciar um serviço específico
docker-compose -f docker-compose.prod.yml restart frontend
```

## 🏗️ Arquitetura

- **Backend**: Python Flask + PostgreSQL + Redis
- **Frontend**: React + TypeScript + Vite
- **Deploy**: Docker + Coolify
- **Automação**: n8n workflows

## 🚀 Deploy Rápido

```bash
# Clone o repositório
git clone <repo-url>
cd crypto-signals

# Configure variáveis de ambiente
cp .env.example .env

# Execute com Docker
docker-compose up -d
```

## 📊 Funcionalidades

- ✅ Análise técnica automatizada
- ✅ Sinais em tempo real
- ✅ Dashboard executivo
- ✅ Integração Binance
- ✅ Notificações Telegram
- ✅ Sistema de usuários

## 🔧 Desenvolvimento

### Backend
```bash
cd back
pip install -r requirements.txt
python app.py
```

### Frontend
```bash
cd front
npm install
npm run dev
```

## 📈 Roadmap

- [ ] Integração com mais exchanges
- [ ] IA para análise preditiva
- [ ] Mobile app
- [ ] API pública