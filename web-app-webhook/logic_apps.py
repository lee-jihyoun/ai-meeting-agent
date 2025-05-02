import requests

# TODO: .env 에서 받아오는 방식으로 수정 필요
LOGIC_APPS_URL = "https://prod-31.koreacentral.logic.azure.com:443/workflows/564e525201dc46d4b16939bf8a4aa104"

def send_email_via_logic_apps(email, subject, message):
    """Azure Logic Apps를 호출하여 이메일을 발송하는 함수"""
    payload = {
        "email": email,
        "subject": subject,
        "message": message
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(LOGIC_APPS_URL, json=payload, headers=headers)
    
    return response.status_code, response.text
