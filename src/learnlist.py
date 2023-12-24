#!/usr/bin/python3

import datetime
import numpy as np
import os
import random
import sys
import telebot

from google.cloud import storage

bucket_name = 'learnlist-api-keys'
blob_name = 'bot-api-key.txt'

storage_client = storage.Client()
bucket = storage_client.bucket(bucket_name)
blob = bucket.blob(blob_name)

with blob.open('r') as f:
    token = f.read()

bot = telebot.TeleBot(token)

# Default mode
mode = 'training'

previous_question = None
previous_answer = None

temp_user_input_1 = ''
temp_user_input_2 = ''


def log_error(error):
    log_file_path = '/var/log/learnlist.err.log'
    date = datetime.datetime.now()
    try:
        with open(log_file_path, 'a+', encoding='utf-8') as f:
            f.write(f'{date}    {error}\n')
    except Exception as ex:
        return f'Unable to write error log: {ex}'


def clear_dictionary(username):
    dictionary_file = f'./{username}_dictionary.ll'
    if not os.path.exists(dictionary_file):
        return 'Dictionary is empty!\nTo update your dictionary send /update'
    os.remove(dictionary_file)
    return 'Dictionary has been cleared.\nTo update your dictionary send /update'


def read_from_dictionary(username):
    dictionary_file = f'./{username}_dictionary.ll'
    if not os.path.exists(dictionary_file):
        open(dictionary_file, 'a').close()
        return None
    working_dictionary = {}
    try:
        with open(dictionary_file, 'r', encoding='utf-8') as f:
            file_content = f.read()
    except Exception as ex:
        debug_msg = f'Failed to read dictionary in read_from_dictionary (file={dictionary_file}): {ex}'
        pretty_msg = f'Failed to read dictionary :(\n{ex}'
        err = log_error(debug_msg)
        return pretty_msg if err is None else f'{pretty_msg}, {err}'
    if file_content != '':
        try:
            working_dictionary = eval(file_content)
        except Exception as ex:
            log_error(f'Failed to eval(file_content) in read_from_dictionary: {ex}')
            return 'Hmm... Something`s wrong with the dictionary:\n', str(ex)
    return working_dictionary


def update_dictionary(username, words_in_string_1, words_in_string_2):
    dictionary_file = f'./{username}_dictionary.ll'
    temp_dictionary = {}
    try:
        list_1 = words_in_string_1.split('\n')
        list_2 = words_in_string_2.split('\n')
        temp_dictionary = zip(list_1, list_2)
        temp_dictionary = dict(temp_dictionary)
    except Exception as ex:
        str(ex)
    working_dictionary = read_from_dictionary(username)
    if not working_dictionary:
        working_dictionary = temp_dictionary
    else:
        working_dictionary.update(temp_dictionary)
    try:
        with open(dictionary_file, 'w', encoding='utf-8') as f:
            f.write(str(working_dictionary))
        return 'Dictionary updated!'
    except Exception as ex:
        debug_msg = f'Failed to write to dictionary file in update_dictionary, dictionary_file={dictionary_file}, working_dictionary={working_dictionary}: {ex}'
        pretty_msg = f'Dictionary update failed :(\n{ex}'
        err = log_error(debug_msg)
        return pretty_msg if err is None else f'{pretty_msg}, {err}'


def delete_item(username, item):
    try:
        working_dictionary = read_from_dictionary(username)
        del working_dictionary[item]
    except Exception as ex:
        return 'Item not found!'
    dictionary_file = f'./{username}_dictionary.ll'
    try:
        with open(dictionary_file, 'w', encoding='utf-8') as f:
            f.write(str(working_dictionary))
        return f'Item "{item}" deleted.'
    except Exception as ex:
        debug_msg = f'Failed to write to dictionary file, dictionary_file={dictionary_file}, working_dictionary={working_dictionary}: {ex}'
        pretty_msg = f'Item deletion failed :(\n{str(ex)}'
        err = log_error(debug_msg)
        return pretty_msg if err is None else f'{pretty_msg}, {err}'


def show_list(username, position, step):
    output = ''
    try:
        working_dictionary = read_from_dictionary(username)
    except Exception as ex:
        return 'Dictionary is empty!\nTo update your dictionary send /update'
    for item, value in working_dictionary.items():
        output += item + ' - ' + value + '\n'
    output += f'\nTotal: {len(working_dictionary.items())}'
    if len(output) >= 4096:
        # output range: from current counter position plus step value
        return output[position:position + step]
    else:
        return output


def start_training(username, answer=''):
    working_dictionary = read_from_dictionary(username)
    if working_dictionary is None or working_dictionary == {}:
        return 'Dictionary is empty!\nTo update your dictionary send /update'
    try:
        dict_keys = np.asarray(list(working_dictionary.keys()))
        dict_values = np.asarray(list(working_dictionary.values()))
    except Exception as ex:
        debug_msg = f'Failed to convert keys or values in start_training: {ex}'
        pretty_msg = f'An error occurred :(\n{str(ex)}'
        err = log_error(debug_msg)
        return pretty_msg if err is None else f'{pretty_msg}, {err}'

    global previous_question, previous_answer
    previous_q = previous_question
    previous_a = previous_answer
    k = random.randint(0, len(dict_keys) - 1)

    # True for key, False for value
    key_selected = random.choice([False, True])
    current_question_list = dict_keys if key_selected else dict_values
    current_answer_list = dict_values if key_selected else dict_keys

    previous_question = current_question_list[k]
    previous_answer = current_answer_list[k]

    try:
        if answer == '':
            return f'Training started!\n{current_question_list[k]}:'
        if answer.lower().strip() == previous_a.lower().strip():
            return f'Yes!✅\n{current_question_list[k]}:'
        else:
            return f'No!❌\n{previous_q}: {previous_a}\n{current_question_list[k]}:'
    except Exception as ex:
        #debug_msg = f'Failed to evaluate answer in start_training, input = {answer.lower().strip()}: {ex}'
        #pretty_msg = f'Something went wrong, please press /start. If the issue persists, please report the issue.'
        #error = log_error(debug_msg)
        return 'To start training send /training' #if error is None else f'{pretty_msg}, {error}'


@bot.message_handler(commands=['start'])
def start_message(msg):
    bot.send_message(msg.chat.id,
                     f'Dear {msg.from_user.first_name}, \nto add items, please send /update\nfor training send /training.')


@bot.message_handler(commands=['update'])
def update_message(msg):
    global mode
    mode = 'update1'
    bot.send_message(msg.chat.id, f'Enter a list before translation:')


@bot.message_handler(commands=['delete'])
def delete_message(msg):
    global mode
    mode = 'delete'
    bot.send_message(msg.chat.id, f'Enter a value you would like to delete:')


@bot.message_handler(commands=['clear'])
def training_message(msg):
    global mode
    mode = 'clear'
    bot.send_message(msg.chat.id, 'Do you want to clear your dictionary? (yes/no)')


@bot.message_handler(commands=['show'])
def training_message(msg):
    # Telegram doesn't support messages > 4096, we need to split output in case if dictionary has exceeded 4096
    # To split dictionary by 2+ messages we use position and step
    username = msg.from_user.username
    position = 0
    step = 4090
    while 'Total' not in show_list(username, position, step):
        bot.send_message(msg.chat.id, show_list(username, position, step))
        # change position:
        position += step
    bot.send_message(msg.chat.id, show_list(username, position, step))


@bot.message_handler(commands=['training'])
def training_message(msg):
    global mode
    mode = 'training'
    bot.send_message(msg.chat.id, start_training(msg.from_user.username))


@bot.message_handler(content_types=['text'])
def send_text(msg):
    global mode, temp_user_input_1, temp_user_input_2
    username = msg.from_user.username
    user_text = msg.text.lower()
    if mode == 'training':
        bot.send_message(msg.chat.id, start_training(username, user_text))
    elif mode == 'update1':
        temp_user_input_1 = user_text
        bot.send_message(msg.chat.id, 'Enter a list after translation:')
        mode = 'update2'
    elif mode == 'update2':
        temp_user_input_2 = user_text
        bot.send_message(msg.chat.id, update_dictionary(username, temp_user_input_1, temp_user_input_2))
        mode = 'training'
    elif mode == 'clear':
        if user_text == 'yes':
            bot.send_message(msg.chat.id, clear_dictionary(username))
            mode = 'training'
        elif user_text == 'no':
            mode = 'training'
        else:
            bot.send_message(msg.chat.id, 'Do you want to clear your dictionary? (yes/no)')
    elif mode == 'delete':
        bot.send_message(msg.chat.id, delete_item(username, user_text))
        mode = 'training'


bot.polling()

