# Build stage
FROM node:18-alpine as build

WORKDIR /app

# Copiar package files
COPY package*.json ./

# Instalar TODAS as dependências (incluindo devDependencies) para o build
RUN npm install

# Copiar código e fazer build
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Copiar build para nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Copiar configuração customizada do nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]