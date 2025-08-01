# Estágio 1: Build da aplicação React
FROM node:18-alpine as build

# Instalar dependências do sistema necessárias
RUN apk add --no-cache git python3 make g++

WORKDIR /app

# Copiar package.json e package-lock.json
COPY package*.json ./

# Limpar cache do npm e instalar TODAS as dependências (incluindo devDependencies)
RUN npm cache clean --force
RUN npm ci

# Copiar código fonte
COPY . .

# Definir variáveis de ambiente para build
ENV NODE_ENV=production
ENV GENERATE_SOURCEMAP=false
ENV CI=false

# Build da aplicação para produção
RUN npm run build

# Verificar se o build foi criado
RUN ls -la dist/

# Estágio 2: Servir com Nginx
FROM nginx:alpine

# Instalar curl para health check
RUN apk add --no-cache curl

# Copiar configuração customizada do Nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Copiar arquivos buildados do estágio anterior
COPY --from=build /app/dist /usr/share/nginx/html

# Criar arquivo index.html se não existir (fallback)
RUN test -f /usr/share/nginx/html/index.html || echo '<h1>Build Error</h1>' > /usr/share/nginx/html/index.html

# Expor porta 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# Comando padrão do Nginx
CMD ["nginx", "-g", "daemon off;"]