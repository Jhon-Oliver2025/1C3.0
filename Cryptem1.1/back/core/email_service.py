import requests
import os
import json
from typing import Optional # Adicione esta importação

# --- Configurações do SendPulse ---
# É ALTAMENTE RECOMENDADO usar variáveis de ambiente para estas credenciais em produção.
# Por enquanto, você pode colocá-las diretamente aqui para testes, mas lembre-se de removê-las.
SENDPULSE_CLIENT_ID = os.getenv('SENDPULSE_CLIENT_ID', '7b28b045d31c3d6d51591d7f56a26c99') # Substitua pelo seu Client ID do SendPulse
SENDPULSE_CLIENT_SECRET = os.getenv('SENDPULSE_CLIENT_SECRET', '26393054ce0cd24fc16a73382a3d5eef') # Substitua pelo seu Client Secret do SendPulse
SENDPULSE_SENDER_EMAIL = os.getenv('SENDPULSE_SENDER_EMAIL', 'crypten@portaldigital10.com') # E-mail do remetente verificado no SendPulse

SENDPULSE_API_URL = "https://api.sendpulse.com"

def _get_sendpulse_token() -> Optional[str]:
    """Obtém um token de acesso da API do SendPulse."""
    try:
        auth_data = {
            "grant_type": "client_credentials",
            "client_id": SENDPULSE_CLIENT_ID,
            "client_secret": SENDPULSE_CLIENT_SECRET
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(f"{SENDPULSE_API_URL}/oauth/access_token", json=auth_data, headers=headers)
        response.raise_for_status() # Levanta um erro para códigos de status HTTP ruins (4xx ou 5xx)
        return response.json().get("access_token")
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao obter token do SendPulse: {e}")
        return None

def send_email(to_email: str, subject: str, text_content: str, html_content: Optional[str] = None) -> bool:
    """
    Envia um e-mail usando a API do SendPulse.

    Args:
        to_email (str): O endereço de e-mail do destinatário.
        subject (str): O assunto do e-mail.
        text_content (str): O conteúdo do e-mail em texto puro.
        html_content (str, optional): O conteúdo do e-mail em HTML. Se fornecido, será preferido.

    Returns:
        bool: True se o e-mail foi enviado com sucesso, False caso contrário.
    """
    if not SENDPULSE_CLIENT_ID or SENDPULSE_CLIENT_ID == 'SEU_CLIENT_ID_DO_SENDPULSE':
        print("❌ Erro: SENDPULSE_CLIENT_ID não configurado. Não é possível enviar e-mail.")
        return False
    if not SENDPULSE_CLIENT_SECRET or SENDPULSE_CLIENT_SECRET == 'SEU_CLIENT_SECRET_DO_SENDPULSE':
        print("❌ Erro: SENDPULSE_CLIENT_SECRET não configurado. Não é possível enviar e-mail.")
        return False
    if not SENDPULSE_SENDER_EMAIL or SENDPULSE_SENDER_EMAIL == 'seu_email_remetente@exemplo.com':
        print("❌ Erro: SENDPULSE_SENDER_EMAIL não configurado. Não é possível enviar e-mail.")
        return False

    token = _get_sendpulse_token()
    if not token:
        return False

    try:
        email_data = {
            "email": {
                "html": html_content if html_content else text_content,
                "text": text_content,
                "subject": subject,
                "from": {
                    "name": "Seu Nome/Empresa", # Opcional: Nome do remetente
                    "email": SENDPULSE_SENDER_EMAIL
                },
                "to": [
                    {
                        "email": to_email
                    }
                ]
            }
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        response = requests.post(f"{SENDPULSE_API_URL}/smtp/emails", json=email_data, headers=headers)
        response.raise_for_status() # Levanta um erro para códigos de status HTTP ruins (4xx ou 5xx)

        response_json = response.json()
        if response_json.get("result") == True:
            print(f"✅ E-mail enviado com sucesso para {to_email}")
            return True
        else:
            print(f"❌ Erro ao enviar e-mail para {to_email}: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Exceção ao enviar e-mail: {e}")
        return False

if __name__ == '__main__':
    # Exemplo de uso (apenas para teste direto deste arquivo)
    print("Tentando enviar e-mail de teste com SendPulse...")
    success = send_email(
        to_email="estruturablogs83@gmail.com", # Substitua pelo seu e-mail para testar
        subject="Teste de E-mail do Backend com SendPulse",
        text_content="Este é um e-mail de teste enviado do seu backend Python usando SendPulse.",
        html_content="<p>Este é um e-mail de teste enviado do seu backend Python usando <strong>SendPulse</strong>.</p>"
    )
    if success:
        print("E-mail de teste enviado com sucesso!")
    else:
        print("Falha ao enviar e-mail de teste.")