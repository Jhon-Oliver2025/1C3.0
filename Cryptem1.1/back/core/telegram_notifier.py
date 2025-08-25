import requests
import json
from typing import Optional
from datetime import datetime
from .database import Database

class TelegramNotifier:
    def __init__(self, token: Optional[str] = None, chat_id: Optional[str] = None):
        self.db = Database()
        self.token = token or self.db.get_config('telegram_token')
        self.chat_id = chat_id or self.db.get_config('telegram_chat_id')
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        
    def setup_credentials(self, token: str, chat_id: str) -> bool:
        """Configura as credenciais do Telegram no banco de dados"""
        try:
            self.db.set_config('telegram_token', token)
            self.db.set_config('telegram_chat_id', chat_id)
            
            # Atualiza as credenciais na instância atual
            self.token = token
            self.chat_id = chat_id
            self.base_url = f"https://api.telegram.org/bot{self.token}"
            
            return True
        except Exception as e:
            print(f"❌ Erro ao configurar credenciais: {e}")
            return False
    
    def send_message(self, message: str) -> bool:
        """Envia mensagem para o Telegram"""
        try:
            if not self.token or not self.chat_id:
                print("❌ Token ou Chat ID não configurados")
                return False
                
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            print(f"📤 Tentando enviar mensagem para {self.chat_id}")
            response = requests.post(url, json=data)
            
            if response.status_code == 200:
                print("✅ Mensagem enviada com sucesso")
                return True
            else:
                print(f"❌ Erro ao enviar mensagem. Status code: {response.status_code}")
                print(f"Resposta: {response.text}")
                return False
            
        except Exception as e:
            print(f"❌ Erro ao enviar mensagem: {e}")
            return False

    def send_signal(self, symbol, signal_type, price, quality_score, timeframe='4h', tp_price=None):
        try:
            # --- Início da Edição ---
            # Garantir que quality_score seja numérico
            try:
                quality_score = float(quality_score)
            except (ValueError, TypeError):
                print(f"❌ Erro: quality_score inválido recebido para {symbol}: {quality_score}")
                return False # Não envia sinal com score inválido

            # Define a classificação baseada no quality_score
            # Agora, apenas verifica se é Premium (>= 90)
            if quality_score >= 90:
                signal_class_text = "💎 Sinais Premium" # Texto para o Telegram
            else:
                # Se o score for menor que 90, não envia o sinal
                print(f"❌ Sinal para {symbol} com score {quality_score} abaixo do mínimo para Telegram (90)")
                return False
            # --- Fim da Edição ---

            # Formatação para o Telegram
            direction = '🟢 COMPRA' if signal_type == "LONG" else '🔴 VENDA'

            # Calculando o preço alvo
            if tp_price is None:
                target_percentage = 9.2 if signal_type == "LONG" else -9.2
                tp_price = price * (1 + target_percentage/100)
            
            # Calcula a porcentagem real entre entrada e alvo
            profit_target = abs(((tp_price - price) / price) * 100)
            
            # Formatando a data atual
            current_time = datetime.now().strftime("%d/%m/%Y %H:%M")

            message = (
                f"<b>{symbol}</b>\n"
                f"{direction}\n"
                # --- Início da Edição ---
                f"{signal_class_text}\n" # Usar o texto definido acima
                # --- Fim da Edição ---
                f"💰 Entrada: ${price:.8f}\n"
                f"🎯 Alvo: ${tp_price:.8f} (+{profit_target:.1f}%)\n"
                f"📊 Score: {quality_score}\n"
                f"🕒{current_time}"
            )

            return self.send_message(message)

        except Exception as e:
            print(f"❌ Erro ao enviar sinal: {e}")
            return False

    def diagnose(self) -> None:
        """Diagnóstico do sistema de notificações"""
        print("\n🔍 Iniciando diagnóstico do Telegram...")
        
        # Verificar configurações
        print(f"\nConfigurações atuais:")
        print(f"Token: {self.token if self.token else 'Não configurado'}")
        print(f"Chat ID: {self.chat_id if self.chat_id else 'Não configurado'}")
        
        # Tentar carregar configurações do banco
        db_token = self.db.get_config('telegram_token')
        db_chat_id = self.db.get_config('telegram_chat_id')
        print(f"\nConfigurações no banco de dados:")
        print(f"Token no banco: {db_token if db_token else 'Não encontrado'}")
        print(f"Chat ID no banco: {db_chat_id if db_chat_id else 'Não encontrado'}")
        
        # Tentar enviar mensagem de teste
        print("\nTentando enviar mensagem de teste...")
        result = self.send_message("🤖 Teste de diagnóstico do sistema")
        if result:
            print("✅ Sistema funcionando corretamente!")
        else:
            print("❌ Falha no envio da mensagem")

    def test_connection(self) -> bool:
        """Testa a conexão com o Telegram"""
        try:
            if not self.token or not self.chat_id:
                print("❌ Token ou Chat ID não configurados")
                return False
                
            test_message = "🤖 Teste de conexão do bot"
            return self.send_message(test_message)
            
        except Exception as e:
            print(f"❌ Erro ao testar conexão: {e}")
            return False