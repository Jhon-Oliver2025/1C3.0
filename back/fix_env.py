import os

# Função para recriar o arquivo .env com as informações reais
def recreate_env_file():
    """Recria o arquivo .env com todas as configurações de produção"""
    env_content = '''DATABASE_URL=sqlite:///app.db
FLASK_ENV=production
SECRET_KEY=gZ4!vN$pWq8#sB2@kF6^a10prasempre
JWT_SECRET_KEY=X9&eR3@cM7!zL10prasempre1*kP5^f
JWT_SECRET=X9&eR3@cM7!zL10prasempre1*kP5^f
BINANCE_API_KEY=CBeEjFuDgfCCdAuyC9ITwP9cRd5mc4AIGaK8eWgDisEdzjdt32S2JflZwMLwIjFp
BINANCE_SECRET_KEY=RS5p0K6l6802saRfE23erEZMtwoZu65GrAfBWP6r5BCAyrUasN4fQCGjS9UzB7Xk
TELEGRAM_BOT_TOKEN=7690455274:AAHB64l8csWoE5UpV1Pnn9c8chJzd5sZTXQ
TELEGRAM_CHAT_ID=1249100206
REDIS_URL=redis://localhost:6379/0
USE_BINANCE_API=true
SENDPULSE_CLIENT_ID=7b28b045d31c3d6d51591d7f56a26c99
SENDPULSE_CLIENT_SECRET=26393054ce0cd24fc16a73382a3d5eef
SENDPULSE_SENDER_EMAIL=crypten@portaldigital10.com
SENDPULSE_API_URL=https://api.sendpulse.com
CORS_ORIGINS=https://1crypten.space
POSTGRES_PASSWORD=sD6*qY1@jV3^cK8#m10prasempreF5&g
DOCKER_PASSWORD=sD311101jV3^c05#m10prasempreF5&g'''
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ Arquivo .env atualizado com configurações de produção!")
        print("🔑 Chaves da Binance configuradas")
        print("📱 Token do Telegram configurado")
        print("📧 SendPulse configurado")
        print("🌐 CORS configurado para https://1crypten.space")
        print("🚀 USE_BINANCE_API habilitado")
    except Exception as e:
        print(f"❌ Erro ao atualizar .env: {e}")

if __name__ == "__main__":
    recreate_env_file()