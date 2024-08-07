import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv('API_URL')

async def check_exist_trader(trader_id):
    response = requests.get(API_URL + f'/check_trader?id={trader_id}')
    return response.status_code == 200


async def get_keywords():
    response = requests.get(API_URL + '/keywords')
    print(response)
    if response.text:
        return response.text.split(', ')
    else:
        return []


def send_message_to_core(trader_id, message):
    data = {
        "traderId": str(trader_id),
        "message": str(message),
        "unixTimeInMills": message.date.timestamp()
    }
    print("Sending message to core: ", data)
    response = requests.post(API_URL + '/tdl_message', json=data)
    print(response)