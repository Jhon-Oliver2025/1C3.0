# Estágio 1: Build da aplicação React
FROM node:18-alpine as build

WORKDIR /app

# Copiar apenas arquivos de dependências primeiro (para cache do Docker)
COPY package*.json ./

# Instalar todas as dependências
RUN npm ci --silent

# Copiar código fonte
COPY . .

# Build da aplicação para produção
RUN npm run build

# Estágio 2: Servir com Nginx
FROM nginx:alpine

# Instalar curl para health check
RUN apk add --no-cache curl

# Remover configuração padrão do Nginx
RUN rm /etc/nginx/conf.d/default.conf

# Copiar configuração customizada do Nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Copiar arquivos buildados do estágio anterior
COPY --from=build /app/dist /usr/share/nginx/html

# Criar usuário não-root para segurança
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

# Definir permissões corretas
RUN chown -R nextjs:nodejs /usr/share/nginx/html
RUN chown -R nextjs:nodejs /var/cache/nginx
RUN chown -R nextjs:nodejs /var/log/nginx
RUN chown -R nextjs:nodejs /etc/nginx/conf.d

# Criar diretórios necessários
RUN touch /var/run/nginx.pid
RUN chown -R nextjs:nodejs /var/run/nginx.pid

# Mudar para usuário não-root
USER nextjs

# Expor porta 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# Comando padrão do Nginx
CMD ["nginx", "-g", "daemon off;"]