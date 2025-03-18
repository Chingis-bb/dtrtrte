import uuid
import requests

SHOP_ID = 'YOUR_SHOP_ID'
SECRET_KEY = 'YOUR_SECRET_KEY'
PAYMENT_URL = 'https://api.yookassa.ru/v3/payments'

def create_payment(user_id: int) -> str:
    headers = {
        'Content-Type': 'application/json',
        'Idempotence-Key': str(uuid.uuid4()),
    }
    data = {
        'amount': {
            'value': '10.00',
            'currency': 'RUB'
        },
        'confirmation': {
            'type': 'redirect',
            'return_url': 'https://your-website.com/success'
        },
        'capture': True,
        'description': f'Subscription for user {user_id}'
    }
    response = requests.post(PAYMENT_URL, json=data, auth=(SHOP_ID, SECRET_KEY), headers=headers)
    response_data = response.json()
    return response_data['confirmation']['confirmation_url']
