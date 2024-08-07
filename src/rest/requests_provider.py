import requests

url = 'https://api.dev.rrpay.online/v2/telegramtdl'

# TODO запрашиваем keywords
# TODO записываем в базу
# TODO отлавливаем сообщения
# TODO записываем в базу в сервисе
# TODO отправляем в core


async def check_exist_trader(trader_id):
    response = requests.get(url + f'/check_trader?id={trader_id}')
    return response.status_code == 200


async def get_keywords():
    response = requests.get(url + '/keywords')
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
    response = requests.post(url + '/tdl_message', json=data)
    print(response)