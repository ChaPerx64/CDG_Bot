import datetime
import logging
import os

from dotenv import load_dotenv
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    filters,
    MessageHandler,
    CallbackContext,
)

from TMPers import rf_text, wf_text

ADMIN_LIST_PATH = 'admin_ids.json'
REMINDER_TIME = datetime.time(hour=5, minute=0)
INIT_MSG = 'CDG is up and running!'
MSG_PATH = '/custom_messages/youth_prayer_reminder.txt'

# Class for storing the authentication information
class Authenticator:
    # Loads data from .env file during initialization
    def __init__(self):
        load_dotenv()
        self.token = os.environ.get('CDG_TOKEN')
        self.owner_id = int(os.environ.get('OWNER_ID'))
        self.mark = 455437881
        self.youth = os.environ.get('Y_CHAT_ID')

    def get_admins(self):
        return self.owner_id, self.mark


# Creating authenticator instance
curr_auth = Authenticator()


# Basic greeting function
async def start(update, context):
    user = update.message.from_user
    if user.id in curr_auth.get_admins():  # Owner's telegram profile id
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Здравствуй, смертный!")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Прости, " + str(user.first_name) + ", я разговариваю только с Чаяном. :'(")
    print(str(datetime.datetime.now()) + ' -- ' + str(user) + ' from chat id' + str(update.effective_chat.id))


async def set_msg_start(update, context):
    user = update.message.from_user
    print(str(datetime.datetime.now()) + ' -- ' + str(user) + ' from chat id' + str(update.effective_chat.id))
    if user.id in curr_auth.get_admins():  # Owner's telegram profile id
        await update.message.reply_text('Текущий текст напоминалки:')
        await update.message.reply_text(
            rf_text(MSG_PATH),
            disable_web_page_preview=True
        )
        await update.message.reply_text(
            'Что будем делать?',
            reply_markup=ReplyKeyboardMarkup([["Изменить", "Отмена"]])
        )
        return 'MESSAGE_SHOWN'
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Прости, " + str(user.first_name) + ", я разговариваю только с Чаяном. :'(")
        return ConversationHandler.END


async def msg_shown(update: Update, context: CallbackContext):
    input_1 = update.message.text
    input_1 = input_1.lower()
    match input_1:
        case "изменить":
            await update.message.reply_text(
                "Введи новый шаблон сообщения",
                reply_markup=ReplyKeyboardRemove()
            )
            return 'ENTER_MSG'
        case 'отмена':
            await update.message.reply_text(
                'Отменено',
                reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END


async def new_msg_txt_check(update: Update, context: CallbackContext) -> str:
    new_message = update.message.text
    await update.message.reply_text(
        'Давай проверим, что мы друг друга правильно поняли 💁‍♂️\nВот что я от тебя получил:')
    await update.message.reply_text(new_message, disable_web_page_preview=True)
    context.user_data.update({"NEW_TEXT": new_message})
    await update.message.reply_text(
        text='Выбери, что с этим делать:',
        reply_markup=ReplyKeyboardMarkup([['Повторить', 'Сохранить', 'Отмена']])
    )
    return "CHOOSE_ACTION"


async def choose_action(update: Update, context: CallbackContext):
    input_1 = update.message.text
    input_1 = input_1.lower()
    await update.message.reply_text(text='Понял-принял', reply_markup=ReplyKeyboardRemove())
    match input_1:
        case "сохранить":
            await update.message.reply_text('Cохранено!')
            wf_text(MSG_PATH, context.user_data.get("NEW_TEXT"))
            return ConversationHandler.END
        case "повторить":
            await update.message.reply_text(text='Хорошо, введи сообщение заново')
            return "ENTER_MSG"
        case "отмена":
            pass
            await update.message.reply_text(text='Отменено')
            return ConversationHandler.END
    return None


# A function for testing purposes executed when /test command is recieved
# Now immediately sends a message
async def send_test_message(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Oh! Hi, Mark!")


async def send_reminder(context: CallbackContext):
    await context.bot.send_message(
        chat_id=curr_auth.youth,
        text=rf_text(MSG_PATH)
    )


async def send_init_message(context: CallbackContext):
    await context.bot.send_message(
        chat_id=curr_auth.owner_id,
        text=INIT_MSG
    )


def main():
    # Launching logger
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    # Dispatcher initialization
    app = ApplicationBuilder().token(curr_auth.token).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('echo', send_test_message))
    app.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler('setmsg', set_msg_start)],
            states={
                'ENTER_MSG': [MessageHandler(filters.TEXT, new_msg_txt_check)],
                'CHOOSE_ACTION': [MessageHandler(filters.TEXT, choose_action)],
                'MESSAGE_SHOWN': [MessageHandler(filters.TEXT, msg_shown)]
            },
            fallbacks=[],
            conversation_timeout=180,
            allow_reentry=True,
        )
    )
    app.job_queue.run_daily(send_reminder, REMINDER_TIME)
    app.job_queue.run_once(send_init_message, 0)
    app.run_polling()


if __name__ == "__main__":
    print("Chaian's Digital Ghost (CDG) greets you!")
    main()
