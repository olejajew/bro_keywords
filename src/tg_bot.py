import asyncio
import os

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext, \
    Application
from src.tg_client import init_client_by_phone, init_client_with_code, sign_out, CODE_REQUESTED, ALREADY_AUTHORIZED, \
    AUTHORIZED, ERROR
from src.utils import extract_digits
from dotenv import load_dotenv
from src.rest.requests_provider import check_exist_trader

load_dotenv()

BOT_TOKEN = os.getenv('TG_CLIENT_BOT_TOKEN')

ASK_TRADER_ID, ASK_PHONE, ASK_CODE = range(3)


async def start(update: Update, context: CallbackContext):
    await update.message.reply_text('Привет! Я бот, который поможет вам авторизоваться в нашем сервисе. '
                                    'Для начала работы введите /add_me')


async def log_out(update: Update, context: CallbackContext):
    phone = context.user_data['phone']
    if phone is None:
        await update.message.reply_text('Вы не авторизованы!')
        return ConversationHandler.END
    await sign_out(phone)
    await update.message.reply_text('Вы вышли из аккаунта!')


async def add_me(update: Update, context: CallbackContext):
    await update.message.reply_text('Пожалуйста, пришлите id трейдера')
    return ASK_TRADER_ID


async def handle_trader_id(update: Update, context: CallbackContext):
    trader_id = update.message.text
    if await check_exist_trader(trader_id):
        context.user_data['trader_id'] = trader_id
        await update.message.reply_text('Пожалуйста, пришлите свой номер телефона')
        return ASK_PHONE
    else :
        await update.message.reply_text('Трейдер с таким id не существует')
        return ConversationHandler.END


async def handle_phone(update: Update, context: CallbackContext):
    phone = update.message.text
    context.user_data['phone'] = phone
    trader_id = context.user_data['trader_id']
    user_id = update.message.from_user.id
    result = await init_client_by_phone(user_id, trader_id, phone)
    if result == CODE_REQUESTED:
        await update.message.reply_text(
            'Пожалуйста, пришлите код. ВНИМАНИЕ! Код не должен быть отправлен в открытом виде! Пожалуйста, добавьте в него несколько символов - например, "12-34-5"')
        return ASK_CODE
    elif result == ALREADY_AUTHORIZED:
        await update.message.reply_text('Вы уже авторизованы!')
        return ConversationHandler.END


async def handle_code(update: Update, context: CallbackContext):
    code = update.message.text
    clear_code = extract_digits(code)
    phone = context.user_data['phone']
    result = await init_client_with_code(phone, clear_code)
    if result == AUTHORIZED:
        await update.message.reply_text(f'Вы авторизованы!')
    elif result == ERROR:
        await update.message.reply_text(f'Ошибка авторизации!')
    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text('Отменено')
    return ConversationHandler.END


async def async_init_bot():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('add_me', add_me)],
        states={
            ASK_TRADER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_trader_id)],
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone)],
            ASK_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('log_out', log_out))

    print('Bot started!')
    await application.initialize()
    await application.start()
    await application.updater.start_polling()


async def init_bot():
    print('Start bot!')
    await async_init_bot()
