import os

import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('TG_CLIENT_BOT_TOKEN')


async def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    response = requests.post(url, json=payload)
