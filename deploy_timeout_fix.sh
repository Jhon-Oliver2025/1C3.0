#!/bin/bash

# Script para Deploy das Correções de Gateway Timeout
# Este script aplica todas as otimizações necessárias para resolver timeouts em produção

set -e  # Parar em caso de erro

echo "🚀 Iniciando deploy das correções de Gateway Timeout..."
echo "📅 $(date)"
echo "==========================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log colorido
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar se está rodando como root
if [[ $EUID -eq 0 ]]; then
   log_warning "Este script está rodando como root. Certifique-se de que isso é necessário."
fi

# Função para backup de arquivos
backup_file() {
    local file=$1
    if [ -f "$file" ]; then
        cp "$file" "${file}.backup.$(date +%Y%m%d_%H%M%S)"
        log_success "Backup criado para $file"
    fi
}

# Função para verificar se um serviço está rodando
check_service() {
    local service=$1
    if systemctl is-active --quiet $service; then
        log_success "$service está rodando"
        return 0
    else
        log_error "$service não está rodando"
        return 1
    fi
}

# Função para testar configuração do Nginx
test_nginx_config() {
    log_info "Testando configuração do Nginx..."
    if nginx -t; then
        log_success "Configuração do Nginx está válida"
        return 0
    else
        log_error "Configuração do Nginx tem erros"
        return 1
    fi
}

# Função para aplicar configurações do Nginx
apply_nginx_config() {
    log_info "Aplicando configurações otimizadas do Nginx..."
    
    # Backup da configuração atual
    backup_file "/etc/nginx/nginx.conf"
    backup_file "/etc/nginx/sites-available/default"
    
    # Copiar nova configuração
    if [ -f "nginx/nginx.prod.conf" ]; then
        cp "nginx/nginx.prod.conf" "/etc/nginx/sites-available/default"
        log_success "Configuração do Nginx atualizada"
    else
        log_error "Arquivo nginx/nginx.prod.conf não encontrado"
        return 1
    fi
    
    # Testar configuração
    if test_nginx_config; then
        # Recarregar Nginx
        systemctl reload nginx
        log_success "Nginx recarregado com sucesso"
    else
        # Restaurar backup em caso de erro
        log_error "Erro na configuração. Restaurando backup..."
        cp "/etc/nginx/sites-available/default.backup."* "/etc/nginx/sites-available/default"
        systemctl reload nginx
        return 1
    fi
}

# Função para otimizar configurações do sistema
optimize_system() {
    log_info "Aplicando otimizações do sistema..."
    
    # Aumentar limites de arquivo
    echo "* soft nofile 65536" >> /etc/security/limits.conf
    echo "* hard nofile 65536" >> /etc/security/limits.conf
    
    # Otimizações de rede
    cat >> /etc/sysctl.conf << EOF
# Otimizações para resolver Gateway Timeout
net.core.somaxconn = 65536
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_max_syn_backlog = 65536
net.ipv4.tcp_keepalive_time = 600
net.ipv4.tcp_keepalive_intvl = 60
net.ipv4.tcp_keepalive_probes = 3
EOF
    
    # Aplicar configurações
    sysctl -p
    
    log_success "Otimizações do sistema aplicadas"
}

# Função para configurar logs
setup_logging() {
    log_info "Configurando sistema de logs..."
    
    # Criar diretórios de log
    mkdir -p /var/log/app
    mkdir -p /var/log/nginx
    
    # Configurar logrotate
    cat > /etc/logrotate.d/app << EOF
/var/log/app/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload nginx > /dev/null 2>&1 || true
    endscript
}
EOF
    
    log_success "Sistema de logs configurado"
}

# Função para instalar dependências
install_dependencies() {
    log_info "Verificando e instalando dependências..."
    
    # Atualizar pacotes
    apt-get update
    
    # Instalar dependências necessárias
    apt-get install -y \
        nginx \
        python3-pip \
        python3-venv \
        redis-server \
        htop \
        curl \
        wget \
        unzip
    
    # Instalar Gunicorn se não estiver instalado
    if ! command -v gunicorn &> /dev/null; then
        pip3 install gunicorn[gevent]
        log_success "Gunicorn instalado"
    fi
    
    log_success "Dependências verificadas/instaladas"
}

# Função para configurar o backend Python
setup_backend() {
    log_info "Configurando backend Python..."
    
    # Instalar dependências Python
    if [ -f "back/requirements.txt" ]; then
        pip3 install -r back/requirements.txt
        log_success "Dependências Python instaladas"
    fi
    
    # Copiar configuração de produção
    if [ -f "back/production_config.py" ]; then
        log_success "Configuração de produção encontrada"
    else
        log_warning "Arquivo production_config.py não encontrado"
    fi
}

# Função para criar serviço systemd
create_systemd_service() {
    log_info "Criando serviço systemd..."
    
    cat > /etc/systemd/system/kryptonbot.service << EOF
[Unit]
Description=KryptonBot Backend
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=$(pwd)/back
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/gunicorn --workers 4 --worker-class gevent --worker-connections 1000 --timeout 120 --keepalive 5 --max-requests 1000 --bind 0.0.0.0:5000 --access-logfile /var/log/app/gunicorn_access.log --error-logfile /var/log/app/gunicorn_error.log --log-level info --preload app:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
    
    # Recarregar systemd
    systemctl daemon-reload
    systemctl enable kryptonbot
    
    log_success "Serviço systemd criado e habilitado"
}

# Função para testar a aplicação
test_application() {
    log_info "Testando aplicação..."
    
    # Aguardar alguns segundos para a aplicação iniciar
    sleep 10
    
    # Testar endpoint de health
    if curl -f -s http://localhost:5000/api/status > /dev/null; then
        log_success "Backend está respondendo"
    else
        log_error "Backend não está respondendo"
        return 1
    fi
    
    # Testar através do Nginx (se configurado)
    if curl -f -s http://localhost/api/status > /dev/null; then
        log_success "Nginx está proxy passando corretamente"
    else
        log_warning "Nginx pode não estar configurado ou não está funcionando"
    fi
}

# Função para monitoramento pós-deploy
setup_monitoring() {
    log_info "Configurando monitoramento..."
    
    # Script de monitoramento simples
    cat > /usr/local/bin/monitor_timeout.sh << 'EOF'
#!/bin/bash

# Script de monitoramento para Gateway Timeout
LOG_FILE="/var/log/app/timeout_monitor.log"
ALERT_THRESHOLD=30  # segundos

while true; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Testar tempo de resposta
    RESPONSE_TIME=$(curl -o /dev/null -s -w "%{time_total}" http://localhost:5000/api/status 2>/dev/null || echo "999")
    
    if (( $(echo "$RESPONSE_TIME > $ALERT_THRESHOLD" | bc -l) )); then
        echo "$TIMESTAMP - WARNING: Slow response detected: ${RESPONSE_TIME}s" >> $LOG_FILE
        
        # Verificar se há muitas conexões
        CONNECTIONS=$(netstat -an | grep :5000 | wc -l)
        echo "$TIMESTAMP - Active connections: $CONNECTIONS" >> $LOG_FILE
        
        # Verificar uso de CPU e memória
        CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')
        MEM_USAGE=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
        echo "$TIMESTAMP - CPU: ${CPU_USAGE}%, Memory: ${MEM_USAGE}%" >> $LOG_FILE
    else
        echo "$TIMESTAMP - OK: Response time: ${RESPONSE_TIME}s" >> $LOG_FILE
    fi
    
    sleep 60
done
EOF
    
    chmod +x /usr/local/bin/monitor_timeout.sh
    
    # Criar serviço de monitoramento
    cat > /etc/systemd/system/timeout-monitor.service << EOF
[Unit]
Description=Timeout Monitor
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/monitor_timeout.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable timeout-monitor
    systemctl start timeout-monitor
    
    log_success "Monitoramento configurado e iniciado"
}

# Função principal
main() {
    log_info "Iniciando deploy das correções de Gateway Timeout"
    
    # Verificar se estamos no diretório correto
    if [ ! -f "nginx/nginx.prod.conf" ]; then
        log_error "Arquivo nginx/nginx.prod.conf não encontrado. Execute este script no diretório raiz do projeto."
        exit 1
    fi
    
    # Executar etapas do deploy
    install_dependencies
    setup_logging
    optimize_system
    setup_backend
    apply_nginx_config
    create_systemd_service
    
    # Reiniciar serviços
    log_info "Reiniciando serviços..."
    systemctl restart kryptonbot
    systemctl restart nginx
    
    # Aguardar e testar
    log_info "Aguardando serviços iniciarem..."
    sleep 15
    
    if test_application; then
        setup_monitoring
        
        log_success "Deploy concluído com sucesso!"
        log_info "Configurações aplicadas:"
        echo "  ✅ Timeouts aumentados para 120s"
        echo "  ✅ Buffers otimizados"
        echo "  ✅ Keep-alive configurado"
        echo "  ✅ Sistema de monitoramento ativo"
        echo "  ✅ Logs configurados em /var/log/app/"
        
        log_info "Próximos passos:"
        echo "  1. Monitorar logs: tail -f /var/log/app/timeout_monitor.log"
        echo "  2. Verificar status: systemctl status kryptonbot nginx"
        echo "  3. Testar aplicação: curl -I https://seu-dominio.com/api/status"
        
    else
        log_error "Deploy falhou. Verifique os logs para mais detalhes."
        exit 1
    fi
}

# Função de limpeza em caso de interrupção
cleanup() {
    log_warning "Deploy interrompido. Executando limpeza..."
    # Adicionar comandos de limpeza se necessário
    exit 1
}

# Capturar sinais de interrupção
trap cleanup SIGINT SIGTERM

# Executar função principal
main "$@"

log_success "🎉 Deploy das correções de Gateway Timeout concluído!"
echo "==========================================="
echo "📅 $(date)"