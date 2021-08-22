#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler
)
from src.localization import localization
from src.dal import ContextDal as Dal
from src.utils import SushiroUtils

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

STORE, LANGUAGE, LOCATION, QUEUE = range(4)


def start(update: Update, context: CallbackContext) -> int:
    """Starts the conversation and asks the user about their gender."""
    update.message.reply_text('Hello! I am sushiro bot. Send /cancel to stop this conversation.')

    update.message.reply_text(
        'Please choose a language',
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(v.language_text, callback_data=f"language:{k}")
                                            for k, v in localization.items()]])
    )

    return LANGUAGE


def handle_language(update: Update, context: CallbackContext) -> int:
    """Stores the selected gender and asks for a photo."""
    query = update.callback_query
    query.answer()
    user = query.from_user.username
    lan = query.data.split(':')[1]
    Dal.save_language(user, lan, context)

    store_dict = SushiroUtils.get_all_stores_info()
    store_list = [InlineKeyboardButton(v['name'], callback_data=f"store:{k}") for k, v in store_dict.items()]
    n = 3
    store_list = [store_list[i:i+n] for i in range(0, len(store_list), n)]

    query.edit_message_text(localization[lan].choose_store, reply_markup=InlineKeyboardMarkup(store_list))

    return STORE


def handle_store(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    user = query.from_user.username
    lan = Dal.get_language(user, context)
    store_id = query.data.split(':')[1]

    store_dict = SushiroUtils.get_all_stores_info()
    store = store_dict[store_id]
    Dal.save_store_id(user, store_id, context)

    queue_numbers = SushiroUtils.get_queue_info(store_id=store_id)
    if not queue_numbers:
        query.edit_message_text(localization[lan].store_closed)
    else:
        query.edit_message_text(localization[lan].display_store_info(store['name'], ', '.join(queue_numbers)))

    query.message.reply_text(localization[lan].ask_queue_number)
    return QUEUE


def poll_queue(context: CallbackContext) -> None:
    job = context.job
    user_data = job.context
    queue_numbers = SushiroUtils.get_queue_info(user_data['store_id'])
    queue_numbers_int = [int(q) for q in queue_numbers]
    lan = user_data['language']

    max_queue = max(queue_numbers_int, default=-1)
    if max_queue == -1:
        return

    if user_data['queue_number'] - max_queue < 5:
        context.bot.send_message(job.context['chat_id'],
                                 text=localization[lan].almost_read_queue_now(', '.join(queue_numbers)))
        context.job.schedule_removal()


def handle_queue_input(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user.username
    queue_num = int(update.message.text)
    Dal.save_queue_number(user, queue_num, context)
    chat_id = update.message.chat_id
    Dal.save_chat_id(user, chat_id, context)
    lan = Dal.get_language(user, context)
    context.job_queue.run_repeating(poll_queue, interval=10, context=context.user_data, name=str(chat_id))
    update.message.reply_text(text=localization[lan].entered_queue_pls_wait.format(queue_num))
    return 1


def photo(update: Update, context: CallbackContext) -> int:
    """Stores the photo and asks for a location."""
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('user_photo.jpg')
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    update.message.reply_text(
        'Gorgeous! Now, send me your location please, or send /skip if you don\'t want to.'
    )

    return LOCATION


def skip_photo(update: Update, context: CallbackContext) -> int:
    """Skips the photo and asks for a location."""
    user = update.message.from_user
    logger.info("User %s did not send a photo.", user.first_name)
    update.message.reply_text(
        'I bet you look great! Now, send me your location please, or send /skip.'
    )

    return LOCATION


def bio(update: Update, context: CallbackContext) -> int:
    """Stores the info about the user and ends the conversation."""
    user = update.message.from_user
    logger.info("Bio of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('Thank you! I hope we can talk again some day.')

    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main(token: str) -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            LANGUAGE: [CallbackQueryHandler(handle_language, pattern="^language:.+")],
            STORE: [CallbackQueryHandler(handle_store, pattern="^store:.+")],
            QUEUE: [MessageHandler(Filters.regex("^[1-9][0-9]*$"), handle_queue_input)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    f = open("token.txt", "r")
    main(str(f.read()))
