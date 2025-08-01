@echo off
echo Iniciando ambiente de desenvolvimento...
echo.

echo 1. Iniciando Backend (Python Flask):
start "Backend" cmd /k "cd back && python app.py"

echo 2. Aguardando 3 segundos...
timeout /t 3 /nobreak >nul

echo 3. Iniciando Frontend (React):
start "Frontend" cmd /k "cd front && npm start"

echo.
echo ✅ Serviços iniciados!
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo Pressione qualquer tecla para sair...
pause >nul