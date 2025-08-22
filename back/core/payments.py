from typing import Dict, Any, Optional, List
import os
import requests
import json
from datetime import datetime, timedelta
from .database import Database
import uuid

class PaymentManager:
    """Gerenciador de pagamentos integrado com Mercado Pago"""
    
    def __init__(self, db_instance: Database):
        self.db = db_instance
        self.access_token = os.getenv('MERCADO_PAGO_ACCESS_TOKEN')
        self.public_key = os.getenv('MERCADO_PAGO_PUBLIC_KEY')
        self.webhook_secret = os.getenv('MERCADO_PAGO_WEBHOOK_SECRET')
        self.base_url = 'https://api.mercadopago.com'
        
        # Definir cursos disponíveis
        self.available_courses = {
            'despertar_crypto': {
                'name': 'Despertar Crypto - 10 Aulas',
                'price': 197.00,
                'description': 'Curso completo de introdução às criptomoedas',
                'lessons': ['despertar-crypto-01', 'despertar-crypto-02', 'despertar-crypto-03', 
                           'despertar-crypto-04', 'despertar-crypto-05', 'despertar-crypto-06',
                           'despertar-crypto-07', 'despertar-crypto-08', 'despertar-crypto-09', 
                           'despertar-crypto-10']
            },
            'masterclass': {
                'name': 'Masterclass - Trading Avançado',
                'price': 497.00,
                'description': 'Curso avançado de trading e análise técnica',
                'lessons': ['masterclass-01', 'masterclass-02', 'masterclass-03', 'masterclass-04']
            },
            'app_mentoria': {
                'name': 'App 1Crypten e Mentoria',
                'price': 997.00,
                'description': 'Acesso ao app exclusivo e mentoria personalizada',
                'lessons': ['app-01', 'app-02', 'app-03', 'app-04']
            }
        }
        
        # Garantir que as tabelas de pagamento existam
        self._ensure_payment_tables()
    
    def _ensure_payment_tables(self):
        """Garante que as tabelas de pagamento existam no banco de dados"""
        try:
            # Tabela de clientes para capturar dados do checkout
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS customers (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    first_name VARCHAR(100),
                    last_name VARCHAR(100),
                    full_name VARCHAR(200),
                    phone VARCHAR(20),
                    identification_type VARCHAR(10),
                    identification_number VARCHAR(20),
                    address TEXT,
                    course_id VARCHAR(50),
                    course_name VARCHAR(200),
                    course_price DECIMAL(10,2),
                    payment_method VARCHAR(50),
                    status VARCHAR(20) DEFAULT 'lead',
                    source VARCHAR(50) DEFAULT 'checkout_form',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabela de eventos dos clientes
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS customer_events (
                    id SERIAL PRIMARY KEY,
                    customer_id INTEGER REFERENCES customers(id),
                    event_type VARCHAR(50) NOT NULL,
                    event_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabela de compras
            purchases_file = os.path.join(os.path.dirname(__file__), '..', 'purchases.csv')
            if not os.path.exists(purchases_file):
                import pandas as pd
                df = pd.DataFrame(columns=[
                    'id', 'user_id', 'course_id', 'payment_id', 'status', 
                    'amount', 'currency', 'created_at', 'updated_at'
                ])
                df.to_csv(purchases_file, index=False)
            
            # Tabela de acessos aos cursos
            course_access_file = os.path.join(os.path.dirname(__file__), '..', 'course_access.csv')
            if not os.path.exists(course_access_file):
                import pandas as pd
                df = pd.DataFrame(columns=[
                    'id', 'user_id', 'course_id', 'purchase_id', 'granted_at', 
                    'expires_at', 'status'
                ])
                df.to_csv(course_access_file, index=False)
                
        except Exception as e:
            print(f"Erro ao criar tabelas de pagamento: {e}")
    
    def create_payment_preference(self, user_id: str = None, course_id: str = None, 
                                success_url: str = None, failure_url: str = None,
                                course_name: str = None, course_price: float = None,
                                course_description: str = None) -> Optional[Dict[str, Any]]:
        """Cria uma preferência de pagamento no Mercado Pago"""
        try:
            print(f"🔄 [PREFERENCE] Criando preferência de pagamento...")
            print(f"📋 [PREFERENCE] Parâmetros: user_id={user_id}, course_id={course_id}")
            print(f"💰 [PREFERENCE] Dados do curso: name={course_name}, price={course_price}")
            print(f"🔑 [PREFERENCE] Access Token configurado: {'Sim' if self.access_token else 'Não'}")
            print(f"🔑 [PREFERENCE] Public Key configurado: {'Sim' if self.public_key else 'Não'}")
            
            # Verificar se o access_token está configurado
            if not self.access_token:
                error_msg = "MERCADO_PAGO_ACCESS_TOKEN não configurado"
                print(f"❌ [PREFERENCE] {error_msg}")
                raise ValueError(error_msg)
            
            if not self.public_key:
                error_msg = "MERCADO_PAGO_PUBLIC_KEY não configurado"
                print(f"❌ [PREFERENCE] {error_msg}")
                raise ValueError(error_msg)
            
            # Verificar se temos dados do curso (para checkout público)
            if course_name and course_price and course_description:
                course = {
                    'name': course_name,
                    'price': course_price,
                    'description': course_description
                }
                print(f"✅ Usando dados do curso fornecidos: {course['name']}")
            elif course_id and course_id in self.available_courses:
                course = self.available_courses[course_id]
                print(f"✅ Usando curso do catálogo: {course['name']}")
            else:
                error_msg = f"Dados do curso não fornecidos ou curso {course_id} não encontrado"
                print(f"❌ Erro: {error_msg}")
                raise ValueError(error_msg)
            
            # Dados da preferência
            preference_data = {
                "items": [{
                    "title": course['name'],
                    "description": course['description'],
                    "quantity": 1,
                    "currency_id": "BRL",
                    "unit_price": course['price']
                }],
                "payer": {
                    "email": self._get_user_email(user_id) if user_id else "guest@1crypten.com"
                },
                "back_urls": {
                    "success": success_url or f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/payment/success",
                    "failure": failure_url or f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/payment/failure",
                    "pending": f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/payment/pending"
                },

                "external_reference": f"{user_id}_{course_id}_{datetime.now().timestamp()}",
                "notification_url": f"{os.getenv('BACKEND_URL', 'http://localhost:5000')}/api/payments/webhook",
                "statement_descriptor": "1CRYPTEN CURSO",
                "installments": 12,
                "payment_methods": {
                    "excluded_payment_types": [],
                    "installments": 12
                }
            }
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            print(f"🌐 Enviando requisição para: {self.base_url}/checkout/preferences")
            print(f"📦 Dados da preferência: {preference_data}")
            
            response = requests.post(
                f'{self.base_url}/checkout/preferences',
                headers=headers,
                json=preference_data
            )
            
            print(f"📡 Resposta do Mercado Pago: {response.status_code}")
            print(f"📄 Conteúdo da resposta: {response.text}")
            
            if response.status_code == 201:
                preference = response.json()
                
                # Salvar a compra como pendente (apenas se tiver user_id)
                if user_id and course_id:
                    self._create_purchase_record(
                        user_id=user_id,
                        course_id=course_id,
                        payment_id=preference['id'],
                        amount=course['price'],
                        status='pending'
                    )
                
                return {
                    'preference_id': preference['id'],
                    'init_point': preference['init_point'],
                    'sandbox_init_point': preference.get('sandbox_init_point'),
                    'public_key': self.public_key
                }
            else:
                print(f"Erro ao criar preferência: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Erro ao criar preferência de pagamento: {e}")
            return None
    
    def process_webhook(self, webhook_data: Dict[str, Any]) -> bool:
        """Processa webhook do Mercado Pago"""
        try:
            # Verificar se é uma notificação de pagamento
            if webhook_data.get('type') == 'payment':
                payment_id = webhook_data.get('data', {}).get('id')
                
                if payment_id:
                    # Buscar detalhes do pagamento
                    payment_info = self._get_payment_info(payment_id)
                    
                    if payment_info:
                        # Processar o pagamento
                        return self._process_payment_status(payment_info)
            
            return True
            
        except Exception as e:
            print(f"Erro ao processar webhook: {e}")
            return False
    
    def _get_payment_info(self, payment_id: str) -> Optional[Dict[str, Any]]:
        """Busca informações do pagamento no Mercado Pago"""
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            
            response = requests.get(
                f'{self.base_url}/v1/payments/{payment_id}',
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Erro ao buscar pagamento: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Erro ao buscar informações do pagamento: {e}")
            return None
    
    def _process_payment_status(self, payment_info: Dict[str, Any]) -> bool:
        """Processa o status do pagamento e libera acesso se aprovado"""
        try:
            external_reference = payment_info.get('external_reference', '')
            status = payment_info.get('status')
            payment_id = payment_info.get('id')
            
            # Extrair user_id e course_id da referência externa
            if '_' in external_reference:
                parts = external_reference.split('_')
                if len(parts) >= 2:
                    user_id = parts[0]
                    course_id = parts[1]
                    
                    # Atualizar status da compra
                    self._update_purchase_status(payment_id, status)
                    
                    # Se pagamento aprovado, liberar acesso
                    if status == 'approved':
                        return self._grant_course_access(user_id, course_id, payment_id)
            
            return True
            
        except Exception as e:
            print(f"Erro ao processar status do pagamento: {e}")
            return False
    
    def _create_purchase_record(self, user_id: str, course_id: str, payment_id: str, 
                               amount: float, status: str) -> bool:
        """Cria registro de compra no banco de dados"""
        try:
            import pandas as pd
            
            purchases_file = os.path.join(os.path.dirname(__file__), '..', 'purchases.csv')
            
            # Ler arquivo existente
            if os.path.exists(purchases_file):
                df = pd.read_csv(purchases_file)
            else:
                df = pd.DataFrame()
            
            # Criar novo registro
            new_purchase = {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'course_id': course_id,
                'payment_id': payment_id,
                'status': status,
                'amount': amount,
                'currency': 'BRL',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Adicionar ao DataFrame
            df = pd.concat([df, pd.DataFrame([new_purchase])], ignore_index=True)
            
            # Salvar arquivo
            df.to_csv(purchases_file, index=False)
            
            return True
            
        except Exception as e:
            print(f"Erro ao criar registro de compra: {e}")
            return False
    
    def _update_purchase_status(self, payment_id: str, status: str) -> bool:
        """Atualiza status da compra"""
        try:
            import pandas as pd
            
            purchases_file = os.path.join(os.path.dirname(__file__), '..', 'purchases.csv')
            
            if os.path.exists(purchases_file):
                df = pd.read_csv(purchases_file)
                
                # Atualizar status
                mask = df['payment_id'] == payment_id
                df.loc[mask, 'status'] = status
                df.loc[mask, 'updated_at'] = datetime.now().isoformat()
                
                # Salvar arquivo
                df.to_csv(purchases_file, index=False)
                
                return True
            
            return False
            
        except Exception as e:
            print(f"Erro ao atualizar status da compra: {e}")
            return False
    
    def _grant_course_access(self, user_id: str, course_id: str, payment_id: str) -> bool:
        """Libera acesso ao curso para o usuário"""
        try:
            import pandas as pd
            
            course_access_file = os.path.join(os.path.dirname(__file__), '..', 'course_access.csv')
            
            # Ler arquivo existente
            if os.path.exists(course_access_file):
                df = pd.read_csv(course_access_file)
            else:
                df = pd.DataFrame()
            
            # Verificar se já existe acesso
            existing_access = df[
                (df['user_id'] == user_id) & 
                (df['course_id'] == course_id) & 
                (df['status'] == 'active')
            ]
            
            if len(existing_access) == 0:
                # Criar novo acesso
                new_access = {
                    'id': str(uuid.uuid4()),
                    'user_id': user_id,
                    'course_id': course_id,
                    'purchase_id': payment_id,
                    'granted_at': datetime.now().isoformat(),
                    'expires_at': None,  # Acesso vitalício
                    'status': 'active'
                }
                
                # Adicionar ao DataFrame
                df = pd.concat([df, pd.DataFrame([new_access])], ignore_index=True)
                
                # Salvar arquivo
                df.to_csv(course_access_file, index=False)
            
            return True
            
        except Exception as e:
            print(f"Erro ao liberar acesso ao curso: {e}")
            return False
    
    def check_course_access(self, user_id: str, course_id: str) -> bool:
        """Verifica se o usuário tem acesso ao curso"""
        try:
            import pandas as pd
            
            course_access_file = os.path.join(os.path.dirname(__file__), '..', 'course_access.csv')
            
            if os.path.exists(course_access_file):
                df = pd.read_csv(course_access_file)
                
                # Verificar acesso ativo
                access = df[
                    (df['user_id'] == user_id) & 
                    (df['course_id'] == course_id) & 
                    (df['status'] == 'active')
                ]
                
                return len(access) > 0
            
            return False
            
        except Exception as e:
            print(f"Erro ao verificar acesso ao curso: {e}")
            return False
    
    def check_lesson_access(self, user_id: str, lesson_id: str) -> bool:
        """Verifica se o usuário tem acesso a uma aula específica"""
        try:
            # Determinar qual curso a aula pertence
            course_id = self._get_course_by_lesson(lesson_id)
            
            if course_id:
                return self.check_course_access(user_id, course_id)
            
            return False
            
        except Exception as e:
            print(f"Erro ao verificar acesso à aula: {e}")
            return False
    
    def _get_course_by_lesson(self, lesson_id: str) -> Optional[str]:
        """Determina qual curso uma aula pertence"""
        for course_id, course_data in self.available_courses.items():
            if lesson_id in course_data['lessons']:
                return course_id
        return None
    
    def _get_user_email(self, user_id: str) -> str:
        """Busca email do usuário"""
        try:
            user = self.db.get_user_by_id(user_id)
            if user:
                return user.get('email', 'user@example.com')
            return 'user@example.com'
        except:
            return 'user@example.com'
    
    def get_user_courses(self, user_id: str) -> List[Dict[str, Any]]:
        """Retorna lista de cursos que o usuário tem acesso"""
        try:
            import pandas as pd
            
            course_access_file = os.path.join(os.path.dirname(__file__), '..', 'course_access.csv')
            
            if os.path.exists(course_access_file):
                df = pd.read_csv(course_access_file)
                
                # Buscar acessos ativos do usuário
                user_access = df[
                    (df['user_id'] == user_id) & 
                    (df['status'] == 'active')
                ]
                
                courses = []
                for _, access in user_access.iterrows():
                    course_id = access['course_id']
                    if course_id in self.available_courses:
                        course_data = self.available_courses[course_id].copy()
                        course_data['course_id'] = course_id
                        course_data['granted_at'] = access['granted_at']
                        courses.append(course_data)
                
                return courses
            
            return []
            
        except Exception as e:
            print(f"Erro ao buscar cursos do usuário: {e}")
            return []
    
    def get_available_courses(self) -> Dict[str, Any]:
        """Retorna lista de cursos disponíveis para compra"""
        return self.available_courses
    
    def process_card_payment(self, payment_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Processa pagamento com cartão de crédito via API do Mercado Pago"""
        try:
            print(f"🔄 [CARD_PAYMENT] Iniciando processamento...")
            print(f"📋 [CARD_PAYMENT] Dados: {payment_data}")
            
            # Verificar se o access_token está configurado
            if not self.access_token:
                error_msg = "MERCADO_PAGO_ACCESS_TOKEN não configurado"
                print(f"❌ [CARD_PAYMENT] {error_msg}")
                return {'success': False, 'error': error_msg}
            
            # Preparar dados do pagamento
            payment_payload = {
                "token": payment_data.get('token'),
                "payment_method_id": payment_data.get('payment_method_id'),
                "transaction_amount": float(payment_data.get('transaction_amount')),
                "installments": int(payment_data.get('installments', 1)),
                "description": payment_data.get('description', 'Pagamento de curso'),
                "payer": {
                    "email": payment_data.get('payer', {}).get('email', 'guest@1crypten.com'),
                    "identification": {
                        "type": payment_data.get('payer', {}).get('identification', {}).get('type', 'CPF'),
                        "number": payment_data.get('payer', {}).get('identification', {}).get('number', '12345678901')
                    }
                },
                "external_reference": f"course_{payment_data.get('course_id', 'unknown')}_{datetime.now().timestamp()}",
                "notification_url": f"{os.getenv('BACKEND_URL', 'http://localhost:5000')}/api/payments/webhook",
                "statement_descriptor": "1CRYPTEN CURSO"
            }
            
            # Adicionar issuer_id se fornecido
            if payment_data.get('issuer_id'):
                payment_payload['issuer_id'] = payment_data.get('issuer_id')
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json',
                'X-Idempotency-Key': str(uuid.uuid4())
            }
            
            print(f"🌐 [CARD_PAYMENT] Enviando para: {self.base_url}/v1/payments")
            print(f"📦 [CARD_PAYMENT] Payload: {payment_payload}")
            
            response = requests.post(
                f'{self.base_url}/v1/payments',
                headers=headers,
                json=payment_payload
            )
            
            print(f"📡 [CARD_PAYMENT] Status: {response.status_code}")
            print(f"📄 [CARD_PAYMENT] Resposta: {response.text}")
            
            if response.status_code in [200, 201]:
                payment_result = response.json()
                
                # Salvar registro do pagamento
                if payment_data.get('course_id'):
                    self._create_purchase_record(
                        user_id=payment_data.get('user_id', 'guest'),
                        course_id=payment_data.get('course_id'),
                        payment_id=payment_result.get('id'),
                        amount=payment_result.get('transaction_amount'),
                        status=payment_result.get('status', 'pending')
                    )
                
                return {
                    'success': True,
                    'payment_id': payment_result.get('id'),
                    'status': payment_result.get('status'),
                    'status_detail': payment_result.get('status_detail'),
                    'transaction_amount': payment_result.get('transaction_amount'),
                    'currency_id': payment_result.get('currency_id'),
                    'date_created': payment_result.get('date_created'),
                    'external_reference': payment_result.get('external_reference')
                }
            else:
                error_response = response.json() if response.content else {}
                error_msg = error_response.get('message', f'Erro HTTP {response.status_code}')
                print(f"❌ [CARD_PAYMENT] Erro na API: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'details': error_response
                }
                
        except Exception as e:
            print(f"❌ [CARD_PAYMENT] Erro no processamento: {e}")
            import traceback
            print(f"📋 [CARD_PAYMENT] Traceback: {traceback.format_exc()}")
            return {
                'success': False,
                'error': str(e)
            }