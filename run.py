import os

from src.tg_client import init_database_users
from src.tg_bot import init_bot
from src.service import init
from src.db.database_manager import db_manager
import asyncio


async def init_environment():
    session_dir = 'sessions'
    os.makedirs(session_dir, exist_ok=True)
    db_manager.create_tables()
    await init()
    await init_database_users()


async def main():
    try:
        await init_environment()
        print("Database initialized!")
        await init_bot()  # Initialize and start the bot
        while True:  # Infinite loop to keep the bot running
            await asyncio.sleep(1)  # Prevents 100% CPU utilization
    except KeyboardInterrupt:
        print("Bot stopped!")

if __name__ == '__main__':
    asyncio.run(main())
