# noinspection
import logging
import os
import ssl

import uvicorn
from cryptography import x509
from cryptography.hazmat.backends import default_backend

import requests

from app import app, logger
from config import (DEBUG, UVICORN_HOST, UVICORN_PORT, UVICORN_SSL_CERTFILE,
                    UVICORN_SSL_KEYFILE, UVICORN_UDS)

MARZBAN_API_URL = 'https://your-marzban-instance/api'
MARZBAN_API_KEY = 'YOUR_API_KEY'

def create_marzban_profile(user_id: int):
    headers = {
        'Authorization': f'Bearer {MARZBAN_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        'user_id': user_id,
        'profile': {
            'name': f'User {user_id}',
            'email': f'user{user_id}@example.com'
        }
    }
    response = requests.post(f'{MARZBAN_API_URL}/profiles', json=data, headers=headers)
    response.raise_for_status()

def get_keys(user_id: int) -> str:
    headers = {
        'Authorization': f'Bearer {MARZBAN_API_KEY}',
        'Content-Type': 'application/json'
    }
    response = requests.get(f'{MARZBAN_API_URL}/profiles/{user_id}/keys', headers=headers)
    response.raise_for_status()
    keys = response.json()
    return keys

if __name__ == "__main__":
    try:
        uvicorn.run(
            "main:app",
            host=('0.0.0.0' if DEBUG else UVICORN_HOST),
            port=UVICORN_PORT,
            uds=(None if DEBUG else UVICORN_UDS),
            ssl_certfile=UVICORN_SSL_CERTFILE,
            ssl_keyfile=UVICORN_SSL_KEYFILE,
            workers=1,
            reload=DEBUG,
            log_level=logging.DEBUG if DEBUG else logging.INFO
        )
    except FileNotFoundError:  # to prevent error on removing unix sock
        pass
