# Usar Node.js 18 Alpine
FROM node:18-alpine

# Instalar dependências do sistema necessárias
RUN apk add --no-cache \
    git \
    python3 \
    make \
    g++

WORKDIR /app

# Copiar arquivos de configuração
COPY package.json ./
COPY package-lock.json ./
COPY tsconfig.json ./
COPY vite.config.ts ./
COPY eslint.config.js ./

# Instalar dependências
RUN npm cache clean --force
RUN npm install --legacy-peer-deps --no-audit --no-fund

# Copiar código fonte
COPY src/ ./src/
COPY public/ ./public/
COPY index.html ./

# Definir variáveis de ambiente para build
ENV NODE_ENV=production
ENV GENERATE_SOURCEMAP=false
ENV CI=false
ENV NODE_OPTIONS="--max-old-space-size=4096"
ENV NPM_CONFIG_LOGLEVEL=warn
ENV NPM_CONFIG_PROGRESS=false
# Configurações adicionais para estabilidade do build
ENV VITE_BUILD_TIMEOUT=600000
ENV VITE_BUILD_ROLLUP_TIMEOUT=600000

# Build da aplicação
RUN npm run build

# Verificar se o build foi criado
RUN ls -la dist/

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