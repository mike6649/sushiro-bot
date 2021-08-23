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
import hashlib
import logging

from telegram import ReplyKeyboardRemove, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler
)
from typing import List, Tuple
from src.localization import localization
from src.dal import ContextDal as Dal
from src.utils import SushiroUtils

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

STORE, LANGUAGE, LOCATION, QUEUE = range(4)
POLL_INTERVAL = 10
ALERT_LIST = [5, 4, 3, 2, 1]  # when to trigger each queue alert


def start(update: Update, context: CallbackContext) -> int:
    """Starts the conversation and asks the user about their gender."""
    update.message.reply_text('\n'.join([msg.welcome for msg in localization.values()]))

    update.message.reply_text(
        '\n'.join([msg.choose_langauage for msg in localization.values()]),
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
    no_of_cols = 3
    store_list = [store_list[i:i+no_of_cols] for i in range(0, len(store_list), no_of_cols)]

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
        query.edit_message_text(localization[lan].store_closed.format(store['name']))
        return ConversationHandler.END
    else:
        query.edit_message_text(localization[lan].display_store_info(store['name'], ', '.join(queue_numbers)))

    query.message.reply_text(localization[lan].ask_queue_number)
    return QUEUE


def get_wait_progress(tables_left: int) -> int:
    for i, n in enumerate(ALERT_LIST):
        if tables_left > n:
            return i
    else:
        return len(ALERT_LIST)


def get_current_queue(store_id: int) -> Tuple[int, List]:
    queue_numbers = SushiroUtils.get_queue_info(store_id)
    queue_numbers_int = [int(q) for q in queue_numbers]
    return max(queue_numbers_int, default=-1), queue_numbers_int


def poll_queue(context: CallbackContext) -> None:
    job = context.job
    # noinspection PyTypeChecker
    user_data: dict = job.context
    lan = user_data['language']

    max_queue, queue_numbers = get_current_queue(user_data['store_id'])
    if max_queue == -1:
        return

    tables_left = user_data['queue_number'] - max_queue
    cur_wait_progress = get_wait_progress(tables_left)
    if cur_wait_progress <= user_data.get('wait_progress', 0):
        # no updates
        return
    queues_txt = ', '.join(queue_numbers)
    if cur_wait_progress == len(ALERT_LIST):
        context.bot.send_message(user_data['chat_id'],
                                 text=localization[lan].final_call_queue_now(queues_txt))
        context.job.schedule_removal()
        return

    context.bot.send_message(user_data['chat_id'],
                             text=localization[lan].almost_ready_queue_now(queues_txt, tables_left))

    user_data['wait_progress'] = cur_wait_progress


def handle_queue_input(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user.username
    queue_num = int(update.message.text)
    Dal.save_queue_number(user, queue_num, context)
    chat_id = update.message.chat_id
    Dal.save_chat_id(user, chat_id, context)
    lan = Dal.get_language(user, context)
    context.job_queue.run_repeating(poll_queue, interval=POLL_INTERVAL,
                                    context=context.user_data, name=str(chat_id))
    update.message.reply_text(text=localization[lan].entered_queue_pls_wait.format(queue_num))
    return ConversationHandler.END


def handle_bad_queue_input(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user.username
    lan = Dal.get_language(user, context)

    update.message.reply_text(text=localization[lan].bad_queue_input)
    return QUEUE


def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    update.message.reply_text(
        'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
    )
    jobs = context.job_queue.get_jobs_by_name(str(update.message.chat_id))
    for job in jobs:
        job.schedule_removal()
    return ConversationHandler.END


def show_queue_info(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    lan = Dal.get_language('', context)
    jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    if jobs and len(jobs):
        user_queue = jobs[0].context.get('queue_number', 0)
        store_id = jobs[0].context.get('store_id', None)
        if not store_id or not user_queue:
            return
        max_queue, queue_numbers = get_current_queue(store_id)
        if max_queue == -1:
            return
        localization[lan].almost_ready_queue_now(queue_numbers, max_queue - user_queue)


def command_help(update: Update, context: CallbackContext):
    username = update.message.from_user.username
    lan = Dal.get_language(username, context)
    if not lan:
        update.message.reply_text('\n'.join([lan.help_msg for lan in localization.values()]))
    else:
        update.message.reply_text(localization[lan].help_msg)


def handle_every_message(update: Update, context: CallbackContext):
    username = update.message.from_user.username
    show_queue_info(update, context)

    lan = Dal.get_language(username, context)
    if not lan:
        update.message.reply_text('\n'.join([lan.help_msg for lan in localization.values()]))
    else:
        update.message.reply_text(localization[lan].help_msg)


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
            QUEUE: [MessageHandler(Filters.regex("^[1-9][0-9]*$"), handle_queue_input),
                    MessageHandler(Filters.text, handle_bad_queue_input)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CommandHandler('help', command_help))
    dispatcher.add_handler(MessageHandler(~Filters.command, handle_every_message))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    f = open("token.txt", "r")
    main(str(f.read()))
