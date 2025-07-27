# Build stage
FROM node:18-alpine as build

WORKDIR /app

# Instalar dependências do sistema necessárias
RUN apk add --no-cache python3 make g++

# Copiar package files
COPY package*.json ./

# Limpar cache do npm e instalar dependências
RUN npm cache clean --force
RUN npm install

# Copiar código fonte
COPY . .

# Fazer build com mais memória disponível
RUN NODE_OPTIONS="--max-old-space-size=4096" npm run build

# Production stage
FROM nginx:alpine

# Copiar build para nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Copiar configuração customizada do nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]