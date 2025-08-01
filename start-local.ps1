# Script de inicializacao local em PowerShell
# Execucao: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

Write-Host "Iniciando sistema localmente para testes..." -ForegroundColor Green
Write-Host "Ambiente: Local (localhost)" -ForegroundColor Cyan

# Funcao para verificar servico
function Test-Service {
    param([string]$ServiceName, [int]$MaxAttempts = 30)
    
    Write-Host "Aguardando $ServiceName..." -ForegroundColor Yellow
    
    for ($i = 1; $i -le $MaxAttempts; $i++) {
        $status = docker-compose ps $ServiceName | Select-String "Up"
        if ($status) {
            Write-Host "$ServiceName esta rodando!" -ForegroundColor Green
            return $true
        }
        Write-Host "Tentativa $i/$MaxAttempts - Aguardando $ServiceName..." -ForegroundColor Yellow
        Start-Sleep -Seconds 2
    }
    
    Write-Host "Erro: $ServiceName nao iniciou corretamente" -ForegroundColor Red
    return $false
}

# Verificar Docker
try {
    docker version | Out-Null
    Write-Host "Docker esta rodando" -ForegroundColor Green
} catch {
    Write-Host "Erro: Docker nao esta rodando!" -ForegroundColor Red
    Write-Host "Inicie o Docker Desktop primeiro" -ForegroundColor Yellow
    Read-Host "Pressione Enter para sair"
    exit 1
}

# Verificar arquivo .env
if (-not (Test-Path ".env")) {
    Write-Host "Erro: Arquivo .env nao encontrado!" -ForegroundColor Red
    Write-Host "Copie .env.example para .env e configure as variaveis" -ForegroundColor Yellow
    Read-Host "Pressione Enter para sair"
    exit 1
}

# Parar servicos existentes
Write-Host "Parando servicos existentes..." -ForegroundColor Yellow
docker-compose down

# Limpar containers orfaos
Write-Host "Limpando containers orfaos..." -ForegroundColor Yellow
docker-compose down --remove-orphans

# Criar diretorios
Write-Host "Criando diretorios necessarios..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "back\data" | Out-Null
New-Item -ItemType Directory -Force -Path "nginx\ssl" | Out-Null

# Iniciar servicos sequencialmente
Write-Host "Iniciando banco de dados e Redis..." -ForegroundColor Cyan
docker-compose up -d postgres redis

if (-not (Test-Service "postgres")) { exit 1 }
if (-not (Test-Service "redis")) { exit 1 }

Write-Host "Iniciando backend..." -ForegroundColor Cyan
docker-compose up -d backend

if (-not (Test-Service "backend")) { exit 1 }

# Testar backend
Write-Host "Testando backend..." -ForegroundColor Yellow
for ($i = 1; $i -le 10; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "Backend respondendo corretamente!" -ForegroundColor Green
            break
        }
    } catch {
        Write-Host "Tentativa $i/10 - Aguardando backend..." -ForegroundColor Yellow
        Start-Sleep -Seconds 3
    }
}

Write-Host "Iniciando frontend..." -ForegroundColor Cyan
docker-compose up -d frontend

if (-not (Test-Service "frontend")) { exit 1 }

Write-Host "Iniciando Nginx..." -ForegroundColor Cyan
docker-compose up -d nginx

if (-not (Test-Service "nginx")) { exit 1 }

# Status final
Write-Host "`nStatus dos servicos:" -ForegroundColor Cyan
docker-compose ps

Write-Host "`nSistema iniciado com sucesso!" -ForegroundColor Green
Write-Host "Frontend: http://localhost" -ForegroundColor Cyan
Write-Host "Backend API: http://localhost:5000" -ForegroundColor Cyan
Write-Host "`nComandos uteis:" -ForegroundColor Yellow
Write-Host "   docker-compose logs -f" -ForegroundColor White
Write-Host "   docker-compose down" -ForegroundColor White
Write-Host "   .\monitor-local.ps1" -ForegroundColor White

Read-Host "`nPressione Enter para continuar"