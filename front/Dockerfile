# Build stage
FROM node:16-alpine as build

WORKDIR /app

# Instalar dependências do sistema
RUN apk add --no-cache git

# Copiar package files
COPY package*.json ./

# Instalar dependências
RUN npm ci --only=production=false

# Copiar código fonte
COPY . .

# Fazer build
RUN npm run build

# Production stage
FROM nginx:alpine

# Copiar build para nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Copiar configuração customizada do nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]