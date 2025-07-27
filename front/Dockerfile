# Build stage
FROM node:16-alpine as build

# Instalar dependências do sistema
RUN apk add --no-cache python3 make g++ git

WORKDIR /app

# Definir variáveis de ambiente para o build
ENV NODE_ENV=production
ENV GENERATE_SOURCEMAP=false

# Copiar package files
COPY package*.json ./

# Limpar cache e instalar dependências
RUN npm cache clean --force
RUN npm install --legacy-peer-deps

# Copiar código fonte
COPY . .

# Debug: mostrar estrutura
RUN echo "=== Estrutura de arquivos ===" && ls -la
RUN echo "=== Conteúdo src ===" && ls -la src/ || echo "src não encontrado"
RUN echo "=== Verificando vite.config.ts ===" && cat vite.config.ts || echo "vite.config.ts não encontrado"

# Tentar build com mais detalhes
RUN echo "=== Iniciando build ===" && npm run build --verbose

# Verificar se dist foi criado
RUN echo "=== Verificando dist ===" && ls -la dist/ || echo "dist não foi criado"

# Production stage
FROM nginx:alpine

# Copiar build para nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Copiar configuração customizada do nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]