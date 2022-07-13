import datetime

from django.utils import timezone
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.ext import CallbackContext
from telegram.ext import (
    Updater, Dispatcher, Filters,
    CommandHandler, MessageHandler,
    CallbackQueryHandler,
)
from tgbot.handlers.onboarding import static_text
from tgbot.handlers.utils.info import extract_user_data_from_update
from tgbot.models import User
from tgbot.handlers.onboarding.keyboards import make_keyboard_for_start_command

def start(update: Update, context: CallbackContext) -> None:
    """Sends a message with three inline buttons attached."""
    keyboard = [
        [
            InlineKeyboardButton("Add expense", callback_data='1'),
            InlineKeyboardButton("Add income", callback_data='2'),
        ],
        [
            InlineKeyboardButton("Balance", callback_data='3'),
            InlineKeyboardButton("History", callback_data='4'),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Welcome to expense tracking bot! \n Please choose from the commands below :', reply_markup=reply_markup)


def calculate_spendings(queryResult):
    total_dict = {}

    for row in queryResult:
        s = row.split(',')    #date,cat,money
        cat = s[1]  #cat
        if cat in total_dict:
            total_dict[cat] = round(total_dict[cat] + float(s[2]),2)    #round up to 2 decimal
        else:
            total_dict[cat] = float(s[2])
    total_text = ""
    for key, value in total_dict.items():
        total_text += str(key) + " $" + str(value) + "\n"
    return total_text
    


def new(update: Update, context: CallbackContext) -> None:
    user_input = update.message.text
    
    update.message.reply_text(calculate_spendings(user_input))
def secret_level(update: Update, context: CallbackContext) -> None:
    # callback_data: SECRET_LEVEL_BUTTON variable from manage_data.py
    """ Pressed 'secret_level_button_text' after /start command"""
    user_id = extract_user_data_from_update(update)['user_id']
    text = static_text.unlock_secret_room.format(
        user_count=User.objects.count(),
        active_24=User.objects.filter(updated_at__gte=timezone.now() - datetime.timedelta(hours=24)).count()
    )

    context.bot.edit_message_text(
        text=text,
        chat_id=user_id,
        message_id=update.callback_query.message.message_id,
        parse_mode=ParseMode.HTML
    )