@echo off
chcp 65001 >nul
echo Iniciando sistema localmente para testes...
echo Ambiente: Local (localhost)

REM Verificar se Docker esta rodando
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo Erro: Docker nao esta rodando!
    echo Inicie o Docker Desktop primeiro
    pause
    exit /b 1
)

REM Verificar se arquivo .env existe
if not exist ".env" (
    echo Erro: Arquivo .env nao encontrado!
    echo Copie .env.example para .env e configure as variaveis
    pause
    exit /b 1
)

REM Parar servicos existentes
echo Parando servicos existentes...
docker-compose down

REM Limpar containers orfaos
echo Limpando containers orfaos...
docker-compose down --remove-orphans

REM Criar diretorios necessarios
echo Criando diretorios necessarios...
if not exist "back\data" mkdir "back\data"
if not exist "nginx\ssl" mkdir "nginx\ssl"

REM Iniciar banco de dados e Redis primeiro
echo Iniciando banco de dados e Redis...
docker-compose up -d postgres redis

REM Aguardar banco de dados
echo Aguardando banco de dados...
timeout /t 15 /nobreak >nul

REM Iniciar backend
echo Iniciando backend...
docker-compose up -d backend

REM Aguardar backend
echo Aguardando backend...
timeout /t 20 /nobreak >nul

REM Iniciar frontend
echo Iniciando frontend...
docker-compose up -d frontend

REM Aguardar frontend
echo Aguardando frontend...
timeout /t 15 /nobreak >nul

REM Iniciar Nginx
echo Iniciando Nginx...
docker-compose up -d nginx

REM Status final
echo.
echo Status dos servicos:
docker-compose ps

echo.
echo Sistema iniciado com sucesso!
echo Frontend: http://localhost
echo Backend API: http://localhost:5000
echo Para monitorar: .\monitor-local.bat
echo Para parar: docker-compose down
echo.
pause