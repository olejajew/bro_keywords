import traceback

from src.rest.requests_provider import get_keywords
from src.db.config_dao import save_keywords, get_keywords_from_config
from src.db.authorized_users_dao import get_trader_id_by_phone
from src.rest.requests_provider import send_message_to_core

keywords = []


async def init_keywords():
    global keywords  # Declare keywords as global
    try:
        keywords = await get_keywords()
        if len(keywords) > 0:
            save_keywords(keywords)
            print('Keywords have been updated')
    except Exception as e:
        print("Error in init_keywords: ", str(e))
        print(traceback.format_exc())


async def init():
    print('init function called')
    global keywords
    try:
        await init_keywords()
        keywords = get_keywords_from_config()
        print('Initialization completed. Keywords: ', keywords)
    except Exception as e:
        print("Error in init: ", str(e))
        print(traceback.format_exc())


def proceed_message(phone, message):
    print(f"Proceeding message: {message.text}. Keywords: {keywords}")
    for keyword in keywords:
        if keyword.lower() in message.message.lower():
            trader_id = get_trader_id_by_phone(phone)
            if trader_id:
                send_message_to_core(trader_id, message)

