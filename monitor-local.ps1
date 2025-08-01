# Script de monitoramento local em PowerShell

function Show-SystemStatus {
    Clear-Host
    Write-Host "Status do Sistema - Ambiente Local" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    
    # Status dos containers
    Write-Host "`nStatus dos Containers:" -ForegroundColor Cyan
    docker-compose ps
    
    # Uso de recursos
    Write-Host "`nUso de Recursos:" -ForegroundColor Cyan
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
    
    # Teste de conectividade
    Write-Host "`nTeste de Conectividade Local:" -ForegroundColor Cyan
    
    # Frontend
    Write-Host "Frontend (localhost): " -NoNewline
    try {
        $response = Invoke-WebRequest -Uri "http://localhost" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -in @(200, 301, 302)) {
            Write-Host "OK" -ForegroundColor Green
        } else {
            Write-Host "ERRO" -ForegroundColor Red
        }
    } catch {
        Write-Host "ERRO" -ForegroundColor Red
    }
    
    # Backend
    Write-Host "Backend API (localhost:5000): " -NoNewline
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "OK" -ForegroundColor Green
        } else {
            Write-Host "ERRO" -ForegroundColor Red
        }
    } catch {
        Write-Host "ERRO" -ForegroundColor Red
    }
    
    # Portas em uso
    Write-Host "`nPortas em Uso:" -ForegroundColor Cyan
    netstat -an | Select-String ":80|:443|:5000|:5432|:6379"
    
    # Logs recentes
    Write-Host "`nLogs Recentes:" -ForegroundColor Cyan
    Write-Host "--- Backend (ultimas 3 linhas) ---" -ForegroundColor Yellow
    docker-compose logs --tail=3 backend
    Write-Host "`n--- Frontend (ultimas 3 linhas) ---" -ForegroundColor Yellow
    docker-compose logs --tail=3 frontend
    
    Write-Host "`nPressione 'R' para atualizar, 'Q' para sair" -ForegroundColor Yellow
}

# Loop principal
do {
    Show-SystemStatus
    $key = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
} while ($key.Character -ne 'q' -and $key.Character -ne 'Q')

Write-Host "`nMonitoramento encerrado!" -ForegroundColor Green