import traceback

from src.db.authorized_users_dao import get_user_id_by_phone, get_chat_id
from src.db.config_dao import get_user_words
from src.rest.tg_rest_client import send_message


async def proceed_message(phone, message):
    sender = message.sender_id
    user_id = get_user_id_by_phone(phone)
    if user_id == sender:
        return

    chat_id = get_chat_id(user_id)
    if chat_id == message.chat_id:
        return

    keywords = get_user_words(user_id)
    for keyword in keywords:
        if keyword.lower().strip() in message.text.lower():
            print(f"Keyword {keyword} found in message {message.text}. User id: {user_id}")
            if chat_id:
                print(f"Chat id: {chat_id}")
                await message.forward_to(chat_id)
                await send_message(chat_id, "Новое сообщеение, бро")
            else:
                print(f"Chat id: me")
                await message.forward_to('me')
                await send_message(user_id, "Новое сообщение, бро")
