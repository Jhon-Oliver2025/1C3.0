@echo off
chcp 65001 >nul
:loop
cls
echo Status do Sistema - Ambiente Local
echo ====================================

REM Status dos containers
echo.
echo Status dos Containers:
docker-compose ps

REM Uso de recursos
echo.
echo Uso de Recursos:
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

REM Verificar conectividade local
echo.
echo Teste de Conectividade Local:
echo Frontend (localhost): 
curl -s -o nul -w "%%{http_code}" http://localhost | findstr "200 301 302" >nul
if %errorlevel% equ 0 (
    echo OK
) else (
    echo ERRO
)

echo Backend API (localhost:5000): 
curl -s -o nul -w "%%{http_code}" http://localhost:5000/health | findstr "200" >nul
if %errorlevel% equ 0 (
    echo OK
) else (
    echo ERRO
)

REM Logs recentes
echo.
echo Logs Recentes (ultimas 3 linhas):
echo --- Backend ---
docker-compose logs --tail=3 backend
echo.
echo --- Frontend ---
docker-compose logs --tail=3 frontend

echo.
echo Pressione qualquer tecla para atualizar ou Ctrl+C para sair
pause >nul
goto loop
cls
goto :eof