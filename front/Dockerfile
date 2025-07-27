# Build stage
FROM node:18-alpine as build

# Instalar dependências do sistema
RUN apk add --no-cache python3 make g++ git

WORKDIR /app

# Definir variáveis de ambiente para o build
ENV NODE_ENV=production
ENV GENERATE_SOURCEMAP=false

# Copiar package files primeiro (para cache do Docker)
COPY package*.json ./

# Instalar dependências
RUN npm ci --only=production

# Copiar código fonte
COPY . .

# Build da aplicação
RUN npm run build

# Production stage
FROM nginx:alpine

# Copiar build para nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Copiar configuração customizada do nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]