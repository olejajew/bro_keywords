import os
import asyncio

from dotenv import load_dotenv
from telethon import TelegramClient, events
from src.db.authorized_users_dao import save_user, mark_as_authenticated, mark_as_not_authenticated, get_authenticated_phone_numbers
from src.service import proceed_message

load_dotenv()

clients = {}
phone_code_hashes = {}

api_id = os.getenv('TG_CLIENT_APP_ID')
api_hash = os.getenv('TG_CLIENT_API_HASH')

ALREADY_AUTHORIZED, CODE_REQUESTED, AUTHORIZED, ERROR = range(4)


async def start_listening_client(phone):
    client = clients[phone]
    print(f"User {phone} is listening!")

    @client.on(events.NewMessage)
    async def my_event_handler(event):
        await proceed_message(phone, event.message)

    await client.run_until_disconnected()


async def init_client_with_code(phone, code):
    print(f"User {phone} is trying to authorize! Code: {code}")
    client = clients[phone]
    phone_code_hash = phone_code_hashes[phone]
    await client.connect()
    result = await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
    if result:
        mark_as_authenticated(phone)
        await start_listening_client(phone)
        print(f"User {phone} successfully authorized!")
        return AUTHORIZED
    else:
        print(f"User {phone} authorization failed!")
        return ERROR


async def init_client_by_phone(user_id, phone):
    save_user(user_id, phone)
    client = TelegramClient(f'sessions/{phone}', api_id, api_hash)
    clients[phone] = client
    await client.connect()
    if not await client.is_user_authorized():
        print(f"User {phone} is not authorized!")
        mark_as_not_authenticated(phone)
        response = await client.send_code_request(phone)
        phone_code_hashes[phone] = response.phone_code_hash
        print(f"Code sent to {phone}")
        return CODE_REQUESTED
    else:
        print("try to mark as authenticated")
        mark_as_authenticated(phone)
        print(f"User {phone} is already authorized!")
        return ALREADY_AUTHORIZED


async def sign_out(phone):
    if phone in clients:
        await clients[phone].log_out()
        clients.pop(phone)
        print(f"User {phone} successfully logged out!")
        return True
    else:
        client = TelegramClient(f'sessions/{phone}', api_id, api_hash)
        await client.connect()
        await client.log_out()
        print(f"User {phone} successfully logged out!")


async def init_database_users():
    phone_numbers = get_authenticated_phone_numbers()
    print('Phone numbers: ' + str(phone_numbers))
    if phone_numbers is None:
        return None

    phone_numbers = [phone[0] for phone in phone_numbers]

    for phone in phone_numbers:
        try:
            client = TelegramClient(f'sessions/{phone}', api_id, api_hash)
            await client.connect()
            if not await client.is_user_authorized():
                print(f"User {phone} is not authorized!")
                mark_as_not_authenticated(phone)
            else:
                clients[phone] = client
                await client.start()
                asyncio.create_task(start_listening_client(phone))
        except Exception as e:
            print(f"Error in init_database_users: {str(e)}")
            continue