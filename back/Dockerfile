# Usar Python 3.11 slim como base
FROM python:3.11-slim

# Definir variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV FLASK_DEBUG=0

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro (para cache do Docker)
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar usuário não-root para segurança
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expor porta
EXPOSE 5000

# Health check
HEALTHCHECK --interval=90s --timeout=60s --start-period=300s --retries=3 \
    CMD python healthcheck.py || exit 1

# Comando para iniciar a aplicação (versão minimal para debug)
CMD ["python", "app_supabase.py"]