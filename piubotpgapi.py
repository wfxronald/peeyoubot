# Main file to be run in order to keep the bot up and running
# This uses the python-telegram-bot wrapper in creating the bot
# It is migrated from the previous version that does not use the wrapper
import json, requests, urllib, time, pumpout, os
from fuzzywuzzy import process, fuzz
from pgdeploy import add_user, update_user, get_user_level, add_item, delete_item, get_items 
from re import sub

import logging
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters


# Obtain token securely
TOKEN = os.environ["TOKEN"]
URL = f"https://api.telegram.org/bot{TOKEN}/"


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Constant for ConversationHandler
ADD, DELETE = range(2)


# Helper functions
def prettify_group_string(arr):
    arr_of_str = []
    counter = 1
    string = ""
    for index in range(len(arr)):
        # trim message every 50 items
        if counter > 50:
            arr_of_str.append(string)
            counter = 1
            string = ""

        ele = arr[index]
        if index == len(arr) - 1:
            string = string + str(index+1) + r'\. ' + ele
        else:
            string = string + str(index+1) + r'\. ' + ele + "\n"
        counter += 1
    if string:
        arr_of_str.append(string)
    return arr_of_str

def extract_hundred(fuzzy_list_of_tuples):
    res = []
    for tup in fuzzy_list_of_tuples:
        if tup[1] == 100:
            res.append(tup[0])
    return res

def tie_break_by_partial_ratio(query, arr):
    res = []
    for song in arr:
        clean_song_string = sub('[*_]', '', song).lower()
        if fuzz.partial_ratio(query.lower(), clean_song_string) == 100:
            res.append(song)
    return res

def is_int(val):
    try:
        num = int(val)
    except ValueError:
        return False
    return True


# Telegram bot functions
def start(update, context):
    update.message.reply_text('Welcome to PIU Bot, a bot for all your PIU needs!')

# LISTING COMMAND
def list_level(update, context):
    args_arr = context.args
    if len(args_arr) != 1 or not is_int(args_arr[0]):
        return update.message.reply_text('Usage: /list <int> to show all songs of level <int>')

    level = int(args_arr[0])
    if not 20 <= level <= 28:
        update.message.reply_text('Currently, you can only list songs with level between 20 to 28, inclusive')
    else:
        arr = pumpout.get_array_for_level(level)
        arr = pumpout.escape_array(arr)
        arr_of_str = prettify_group_string(arr)

        update.message.reply_text("Total level " + str(level) + " in the database: *" + str(len(arr)) + "*", parse_mode=ParseMode.MARKDOWN_V2)
        for message in arr_of_str:
            update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN_V2)

def cleared(update, context):
    chat_id = update.message.from_user.id
    lvl_in_db = get_user_level(chat_id)

    if lvl_in_db is None:
        update.message.reply_text("You need to declare your level first before checking cleared songs")
    else:
        lst = get_items(chat_id)
        lst = pumpout.escape_array(lst)
        arr_of_str = prettify_group_string(lst)

        update.message.reply_text("Total level " + str(lvl_in_db) + " cleared: *" + str(len(lst)) + "*", parse_mode=ParseMode.MARKDOWN_V2)
        for message in arr_of_str:
            update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN_V2)

# DATABASE COMMAND
def exit(update, context):
    update.message.reply_text("Adding or deleting songs ended, you can now execute other commands as per normal")
    return ConversationHandler.END
    
def add(update, context):
    chat_id = update.message.from_user.id
    lvl_in_db = get_user_level(chat_id)

    if lvl_in_db is None:
        update.message.reply_text("You need to declare your level first before adding songs")
        return ConversationHandler.END
    else:
        update.message.reply_text("Write down songs you have cleared, each in separate message. Once done, send /exit command")
        return ADD

def middle_add(update, context):
    update.message.reply_text("Any command written while adding songs are ignored, execute /exit command before typing another command")
    return ADD

def add_database_call(update, context):
    song = update.message.text
    chat_id = update.message.from_user.id
    level = get_user_level(chat_id)

    current_clear_list = get_items(chat_id)
    songlist = pumpout.get_array_for_level(level)
    highest_match = process.extract(song, songlist, scorer=fuzz.token_set_ratio)
    possible_songs = extract_hundred(highest_match)

    if len(possible_songs) > 1:
        second_possible_songs = tie_break_by_partial_ratio(song, possible_songs)

    if len(possible_songs) == 1:
        correct_song_name = possible_songs[0]

        if correct_song_name not in current_clear_list:
            add_item(correct_song_name, chat_id)
            update.message.reply_text(pumpout.escape_telegram(correct_song_name) + " successfully added", parse_mode=ParseMode.MARKDOWN_V2)
        else:
            update.message.reply_text(pumpout.escape_telegram(correct_song_name) + " is already in the cleared list", parse_mode=ParseMode.MARKDOWN_V2)

    elif len(possible_songs) > 1 and len(second_possible_songs) == 1: 
        correct_song_name = second_possible_songs[0]

        if correct_song_name not in current_clear_list:
            add_item(correct_song_name, chat_id)
            update.message.reply_text(pumpout.escape_telegram(correct_song_name) + " successfully added", parse_mode=ParseMode.MARKDOWN_V2)
        else:
            update.message.reply_text(pumpout.escape_telegram(correct_song_name) + " is already in the cleared list", parse_mode=ParseMode.MARKDOWN_V2)

    elif possible_songs:
        prettified_string = ""
        for i in range(len(possible_songs)):
            string = possible_songs[i]
            if i == len(possible_songs) - 1:
                prettified_string += string
            else:
                prettified_string = prettified_string + string + ", "
        update.message.reply_text(song + " matches with: " + pumpout.escape_telegram(prettified_string) + "\. Please specify the song you want to add", parse_mode=ParseMode.MARKDOWN_V2)
                
    else:
        update.message.reply_text(song + " not found in the database. Please check your spelling!")

    return ADD

def delete(update, context):
    chat_id = update.message.from_user.id
    lvl_in_db = get_user_level(chat_id)

    if lvl_in_db is None:
        update.message.reply_text("You need to declare your level first before deleting cleared songs from the list")
        return ConversationHandler.END
    elif not get_items(chat_id):
        update.message.reply_text("You have no cleared songs in this level")
        return ConversationHandler.END
    else:
        listen_to_messages_because_delete = True
        update.message.reply_text("Write down songs you wish to remove, each in separate message. Once done, send /exit command")
        return DELETE

def middle_delete(update, context):
    update.message.reply_text("Any command written while deleting songs are ignored, execute /exit command before typing another command")
    return DELETE

def delete_database_call(update, context):
    song = update.message.text
    chat_id = update.message.from_user.id
    level = get_user_level(chat_id)

    songlist = get_items(chat_id)
    highest_match = process.extract(song, songlist, scorer=fuzz.token_set_ratio)
    possible_songs = extract_hundred(highest_match)

    if len(possible_songs) > 1:
        second_possible_songs = tie_break_by_partial_ratio(song, possible_songs)

    if len(possible_songs) == 1:
        correct_song_name = possible_songs[0]
        delete_item(correct_song_name, chat_id)
        update.message.reply_text(pumpout.escape_telegram(correct_song_name) + " successfully deleted", parse_mode=ParseMode.MARKDOWN_V2)

    elif len(possible_songs) > 1 and len(second_possible_songs) == 1: 
        correct_song_name = second_possible_songs[0]
        delete_item(correct_song_name, chat_id)
        update.message.reply_text(pumpout.escape_telegram(correct_song_name) + " successfully deleted", parse_mode=ParseMode.MARKDOWN_V2)

    elif possible_songs:
        prettified_string = ""
        for i in range(len(possible_songs)):
            string = possible_songs[i]
            if i == len(possible_songs) - 1:
                prettified_string += string
            else:
                prettified_string = prettified_string + string + ", "
        update.message.reply_text(song + " matches with: " + pumpout.escape_telegram(prettified_string) + "\. Please specify the song you want to delete", parse_mode=ParseMode.MARKDOWN_V2)
            
    else:
        update.message.reply_text("No such song in the current clear list. Check that your clear list is not empty, or check your spelling!")

    return DELETE

# PERSONAL COMMAND
def level(update, context):
    chat_id = update.message.from_user.id
    lvl_in_db = get_user_level(chat_id)

    if lvl_in_db is None:
        update.message.reply_text("You have not declared your level yet!")
    else:
        update.message.reply_text("Your currently declared level is: *" + str(lvl_in_db) + "*", parse_mode=ParseMode.MARKDOWN_V2)

def declare(update, context):
    chat_id = update.message.from_user.id
    lvl_in_db = get_user_level(chat_id)

    args_arr = context.args
    if len(args_arr) != 1 or not is_int(args_arr[0]):
        return update.message.reply_text('Usage: /declare <int> to declare your current level to be level <int>')

    level = int(args_arr[0])
    if not 20 <= level <= 28:
        update.message.reply_text("Currently, user can only choose a level between 20 to 28, inclusive")
    else:
        if lvl_in_db is None:
            add_user(chat_id, level)
            update.message.reply_text("Congratulations, you can now add songs of level *" + str(level) + "*", parse_mode=ParseMode.MARKDOWN_V2)
        elif lvl_in_db == level:
            update.message.reply_text("Your current level is as declared, no change to be made")
        else:
            update_user(chat_id, level)
            update.message.reply_text("Congratulations, your level has been updated to *" + str(level) + "*", parse_mode=ParseMode.MARKDOWN_V2)

# STATIC RANDOMISER COMMAND
def randomst(update, context):
    args_arr = context.args
    if len(args_arr) != 1 or not is_int(args_arr[0]):
        return update.message.reply_text('Usage: /randomst <int> to randomise a single train (4 songs) of level <int>')

    level = int(args_arr[0])
    if not 20 <= level <= 24:
        update.message.reply_text("Currently, you can only random single train with level between 20 to 24, inclusive")
    else:
        to_send = pumpout.randomise_single_train(level)
        update.message.reply_text(to_send, parse_mode=ParseMode.MARKDOWN_V2)

def randomdt(update, context):
    args_arr = context.args
    if len(args_arr) != 1 or not is_int(args_arr[0]):
        return update.message.reply_text('Usage: /randomdt <int> to randomise a double train (4 songs) of level <int>')

    level = int(args_arr[0])
    if not 20 <= level <= 26:
        update.message.reply_text("Currently, you can only random double train with level between 20 to 26, inclusive")
    else:
        to_send = pumpout.randomise_double_train(level)
        update.message.reply_text(to_send, parse_mode=ParseMode.MARKDOWN_V2)

def randomsa(update, context):
    args_arr = context.args
    if len(args_arr) != 1 or not is_int(args_arr[0]):
        return update.message.reply_text('Usage: /randomsa <int> to randomise a single arcade song of level <int>')

    level = int(args_arr[0])
    if not 20 <= level <= 25:
        update.message.reply_text("Currently, you can only random single arcades with level between 20 to 25, inclusive")
    else:
        to_send = pumpout.randomise_single_arcade(level)
        update.message.reply_text(to_send, parse_mode=ParseMode.MARKDOWN_V2)

def randomda(update, context):
    args_arr = context.args
    if len(args_arr) != 1 or not is_int(args_arr[0]):
        return update.message.reply_text('Usage: /randomda <int> to randomise a double arcade song of level <int>')

    level = int(args_arr[0])
    if not 20 <= level <= 28:
        update.message.reply_text("Currently, you can only random double arcades with level between 20 to 28, inclusive")
    else:
        to_send = pumpout.randomise_double_arcade(level)
        update.message.reply_text(to_send, parse_mode=ParseMode.MARKDOWN_V2)

def random(update, context):
    args_arr = context.args
    if len(args_arr) != 1 or not is_int(args_arr[0]):
        return update.message.reply_text('Usage: /random <int> to randomise any song of level <int>')

    level = int(args_arr[0])
    if not 20 <= level <= 28:
        update.message.reply_text("Currently, you can only random songs of level between 20 to 28, inclusive")
    else:
        to_send = pumpout.randomise_songs(level)
        update.message.reply_text(to_send, parse_mode=ParseMode.MARKDOWN_V2)

# HANDLE MESSAGE OR UNKNOWN COMMAND
def handle_message(update, context):
    update.message.reply_text('Only commands will be recognised, text will be ignored')

def handle_unknown_command(update, context):
    update.message.reply_text('Unknown command, please refer to the list of commands')

def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


# The main function that runs the telegram bot
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))

    # DATABASE COMMAND
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('add', add), 
                      CommandHandler('delete', delete)],

        states={
            ADD: [CommandHandler('exit', exit),
                  MessageHandler(Filters.command, middle_add),
                  MessageHandler(Filters.text, add_database_call)],
            DELETE: [CommandHandler('exit', exit),
                     MessageHandler(Filters.command, middle_delete),
                     MessageHandler(Filters.text, delete_database_call)],
        },

        fallbacks=[CommandHandler('exit', exit)],
    )

    dp.add_handler(conv_handler)

    # LISTING COMMAND
    dp.add_handler(CommandHandler("list", list_level))
    dp.add_handler(CommandHandler("cleared", cleared))

    # PERSONAL COMMAND
    dp.add_handler(CommandHandler("level", level))
    dp.add_handler(CommandHandler("declare", declare))

    # STATIC RANDOMISER COMMAND
    dp.add_handler(CommandHandler("randomst", randomst))
    dp.add_handler(CommandHandler("randomdt", randomdt))
    dp.add_handler(CommandHandler("randomsa", randomsa))
    dp.add_handler(CommandHandler("randomda", randomda))
    dp.add_handler(CommandHandler("random", random))

    # HANDLE MESSAGE OR UNKNOWN COMMAND
    dp.add_handler(MessageHandler(Filters.command, handle_unknown_command))
    dp.add_handler(MessageHandler(Filters.text, handle_message))

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
