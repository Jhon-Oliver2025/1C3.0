# Build stage
FROM node:18-alpine as build

# Instalar dependências do sistema necessárias
RUN apk add --no-cache \
    python3 \
    make \
    g++ \
    git \
    curl

# Verificar se node e npm estão disponíveis
RUN node --version && npm --version

WORKDIR /app

# Copiar package files
COPY package*.json ./

# Limpar cache npm e instalar dependências
RUN npm cache clean --force
RUN npm install --verbose

# Copiar código fonte
COPY . .

# Verificar estrutura antes do build
RUN ls -la
RUN ls -la src/

# Build da aplicação
RUN npm run build

# Verificar se dist foi criado
RUN ls -la dist/

# Production stage
FROM nginx:alpine

# Copiar build para nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Copiar configuração do nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]