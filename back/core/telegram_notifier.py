import requests
import json
import os
from typing import Optional
from datetime import datetime
from .database import Database

class TelegramNotifier:
    def __init__(self, token: Optional[str] = None, chat_id: Optional[str] = None):
        self.db = Database()
        
        # Tentar obter configurações do banco, usar variáveis de ambiente como fallback
        try:
            self.token = token or self.db.get_config_value('telegram_token') or os.getenv('TELEGRAM_TOKEN')
            self.chat_id = chat_id or self.db.get_config_value('telegram_chat_id') or os.getenv('TELEGRAM_CHAT_ID')
        except AttributeError:
            # Se get_config_value não existir, usar apenas variáveis de ambiente
            self.token = token or os.getenv('TELEGRAM_TOKEN')
            self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')
        
        if self.token:
            self.base_url = f"https://api.telegram.org/bot{self.token}"
        else:
            self.base_url = None
            print("⚠️ Token do Telegram não configurado. Notificações desabilitadas.")
        
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

    def send_signal(self, symbol, signal_type, price, quality_score, timeframe='4h', tp_price=None,
                trend_score=0.0, confirmation_score=0.0, rsi_score=0.0, pattern_score=0.0):
        """Envia sinal para o Telegram no formato simplificado solicitado"""
        try:
            # Garantir que quality_score seja numérico
            try:
                quality_score = float(quality_score)
            except (ValueError, TypeError):
                print(f"❌ Erro: quality_score inválido recebido para {symbol}: {quality_score}")
                return False # Não envia sinal com score inválido
    
            # Define a classificação baseada no quality_score
            if quality_score >= 110:
                signal_class_text = "💎 ELITE+ ⭐⭐⭐"
            elif quality_score >= 95:
                signal_class_text = "💎 ELITE ⭐⭐"
            elif quality_score >= 85:
                signal_class_text = "💎 PREMIUM+ ⭐⭐"
            elif quality_score >= 80:
                signal_class_text = "💎 PREMIUM ⭐"
            else:
                print(f"❌ Sinal para {symbol} com score {quality_score} abaixo do mínimo para Telegram (80)")
                return False
    
            # Formatação para o Telegram - Corrigido para usar o valor exato de signal_type
            # Agora aceita tanto "COMPRA"/"VENDA" quanto "LONG"/"SHORT"
            if signal_type == "LONG" or signal_type == "COMPRA":
                direction = '🟢 COMPRA'
            else:
                direction = '🔴 VENDA'
    
            # Calculando o preço alvo
            if tp_price is None:
                # Cálculo dinâmico do preço alvo com base na qualidade do sinal
                # Garantindo um mínimo de 6% de ganho
                min_percentage = 6.0
                
                # Adicionar percentual extra baseado na qualidade do sinal
                if quality_score >= 90:  # ELITE
                    extra_percentage = 3.0
                elif quality_score >= 80:  # PREMIUM Alto
                    extra_percentage = 2.0
                elif quality_score >= 70:  # PREMIUM Baixo
                    extra_percentage = 1.0
                else:
                    extra_percentage = 0.0
                
                # Calcular percentual final
                target_percentage = min_percentage + extra_percentage
                
                # Aplicar o percentual conforme o tipo de sinal
                if signal_type == "LONG" or signal_type == "COMPRA":
                    tp_price = price * (1 + target_percentage/100)
                else:
                    tp_price = price * (1 - target_percentage/100)
            
            # Calcula a porcentagem real entre entrada e alvo
            profit_target = abs(((tp_price - price) / price) * 100)
            
            # Formatando a data atual
            current_time = datetime.now().strftime("%d/%m/%Y %H:%M")
    
            # Mensagem simplificada conforme solicitado pelo usuário
            # Mantendo os emojis e o formato visual
            message = (
                f"<b>{symbol}</b>\n"
                f"{direction}\n"
                f"{signal_class_text}\n"
                f"💰 Entrada: ${price:.8f}\n"
                f"🎯 Alvo: ${tp_price:.8f} (+{profit_target:.1f}%)\n"
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
        db_token = self.db.get_config_value('telegram_token')
        db_chat_id = self.db.get_config_value('telegram_chat_id')
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