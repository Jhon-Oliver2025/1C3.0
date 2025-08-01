@echo off
echo 🚀 Iniciando build de produção...

echo 📦 Instalando dependências do frontend...
cd front
npm install

echo 🔨 Fazendo build do frontend...
npm run build

echo 📦 Instalando dependências do backend...
cd ..\back
pip install -r requirements.txt

echo ✅ Build de produção concluído!
echo 📁 Arquivos estão em: front/dist
echo 🐍 Backend pronto para deploy

pause