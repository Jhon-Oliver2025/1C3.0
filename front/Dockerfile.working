# Dockerfile simplificado e funcional
FROM node:18-alpine

# Instalar dependências do sistema
RUN apk add --no-cache git

WORKDIR /app

# Copiar arquivos de configuração
COPY package*.json ./
COPY tsconfig.json ./
COPY vite.config.ts ./

# Instalar TODAS as dependências
RUN npm install

# Copiar código fonte
COPY src/ ./src/
COPY public/ ./public/
COPY index.html ./

# Configurar ambiente
ENV NODE_ENV=production
ENV CI=false

# Build da aplicação
RUN npm run build

# Servir com servidor simples
RUN npm install -g serve

EXPOSE 3000

CMD ["serve", "-s", "dist", "-l", "3000"]