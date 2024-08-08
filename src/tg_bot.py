import asyncio
import os

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext, \
    Application
from src.tg_client import init_client_by_phone, init_client_with_code, sign_out, CODE_REQUESTED, ALREADY_AUTHORIZED, \
    AUTHORIZED, ERROR
from src.utils import extract_digits
from dotenv import load_dotenv
from src.db.config_dao import get_user_words, save_keywords
from src.db.authorized_users_dao import update_chat_id

load_dotenv()

BOT_TOKEN = os.getenv('TG_CLIENT_BOT_TOKEN')

ASK_PHONE, ASK_CODE, ASK_WORDS = range(3)

application = None


async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        'Йоу, бро. Я кароч бот, который поможет тебе авторизоваться и считывать слова.\n'
        'Для начала работы вводи /add_me, бро\n'
        'Если хочешь добавить слова, вводи /set_words, бро\n'
        'Если хочешь, чтоб присылал в чат, вводи /this_chat, бро. Но учти - лучше, чтоб это был отдельный чат, а не наша с тобой переписка, бро\n'
        'Если хочешь выйти, вводи /log_out, бро\n'
        'Надеюсь найдешь то, что ищешь, бро'
    )


async def log_out(update: Update, context: CallbackContext):
    phone = context.user_data['phone']
    if phone is None:
        await update.message.reply_text('И вообще хз, кто ты был, бро')
        return ConversationHandler.END
    await sign_out(phone)
    await update.message.reply_text('И вообще хз, кто ты был, бро')
    return ConversationHandler.END


async def set_this_chat(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    update_chat_id(user_id, chat_id)
    await update.message.reply_text('Окей, теперь буду слать сюда, бро')


async def handle_words(update: Update, context: CallbackContext):
    words = update.message.text.split(',')
    user_id = update.message.from_user.id
    save_keywords(user_id, words)
    await update.message.reply_text('Слова добавлены, бро')
    return ConversationHandler.END


async def add_me(update: Update, context: CallbackContext):
    await update.message.reply_text('Присылай номер телефона, бро')
    return ASK_PHONE


async def request_words(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_words = get_user_words(user_id)
    message = None
    if len(user_words) == 0:
        message = ""
    else:
        message = "Твои слова: " + ', '.join(user_words)

    await update.message.reply_text('Присылай слова через запятую, бро \nУчитывай, что я ищу слова целиком, но в любом регистре\n\n' + message)
    return ASK_WORDS


async def handle_phone(update: Update, context: CallbackContext):
    phone = update.message.text
    context.user_data['phone'] = phone
    user_id = update.message.from_user.id
    result = await init_client_by_phone(user_id, phone)
    if result == CODE_REQUESTED:
        await update.message.reply_text(
            'Присылай код, бро. Только не надо в чистом виде - не сработает. Присылай типо если код 12345, то присылай 12-34-5, бро. ')
        return ASK_CODE
    elif result == ALREADY_AUTHORIZED:
        await update.message.reply_text('Уже авторизован, бро')
        return ConversationHandler.END


async def handle_code(update: Update, context: CallbackContext):
    code = update.message.text
    clear_code = extract_digits(code)
    phone = context.user_data['phone']
    result = await init_client_with_code(phone, clear_code)
    if result == AUTHORIZED:
        await update.message.reply_text(f'Авторизован, бро')
        return ConversationHandler.END
    elif result == ERROR:
        await update.message.reply_text(f'Чет не поперло, бро')
        return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text('Ага, забыли, бро')
    return ConversationHandler.END


async def async_init_bot():
    global application
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler('add_me', add_me)],
        states={
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone)],
            ASK_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    ))
    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler('set_words', request_words)],
        states={
            ASK_WORDS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_words)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    ))
    application.add_handler(CommandHandler('this_chat', set_this_chat))
    application.add_handler(CommandHandler('cancel', cancel))
    application.add_handler(CommandHandler('log_out', log_out))

    print('Bot started!')
    await application.initialize()
    await application.start()
    await application.updater.start_polling()


async def init_bot():
    print('Start bot!')
    await async_init_bot()
