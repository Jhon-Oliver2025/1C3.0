# Usar Node.js 20 Debian (resolve problemas do Rollup com musl)
FROM node:20-slim

# Instalar dependências básicas
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Configurar variáveis de ambiente para Node.js
ENV NODE_ENV=production
ENV NODE_OPTIONS="--max-old-space-size=4096"
ENV CI=true
ENV npm_config_legacy_peer_deps=true

# Copiar package files e configurações
COPY package*.json ./
COPY .npmrc ./
COPY build-docker.sh ./

# Tornar script executável
RUN chmod +x build-docker.sh

# Copiar arquivos de configuração
COPY tsconfig*.json ./
COPY vite.config.ts ./
COPY index.html ./

# Copiar código fonte
COPY src/ ./src/
COPY public/ ./public/

# Executar script de build robusto
RUN ./build-docker.sh

# Estágio 2: Servir com Nginx
FROM nginx:alpine

# Instalar curl para health check
RUN apk add --no-cache curl

# Copiar configuração do Nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Copiar arquivos buildados
COPY --from=0 /app/dist /usr/share/nginx/html

# Criar fallback se necessário
RUN test -f /usr/share/nginx/html/index.html || echo '<h1>Build Error</h1>' > /usr/share/nginx/html/index.html

# Expor porta
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# Comando padrão
CMD ["nginx", "-g", "daemon off;"]