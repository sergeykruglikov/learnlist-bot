#!/usr/bin/python3

import telebot

from classes.custom_dictionary import CustomDictionary
from classes.gcp import Gcp
from classes.globals import Globals

print('Loading...')

print('Setting up Stack driver agent...')
Gcp.ensure_logging_client()

print('Getting token...')
token = Gcp.get_token()

print('Initializing TeleBot...')
bot = telebot.TeleBot(token)

print('Ready.')


@bot.message_handler(commands=['start'])
def start_message(msg):
    CustomDictionary.download_dictionary_on_first_start(msg.from_user.username)
    bot.send_message(msg.chat.id, f'Dear {msg.from_user.first_name}, \nto add items, please send /update\nfor training send /training.')


@bot.message_handler(commands=['update'])
def update_message(msg):
    CustomDictionary.download_dictionary_on_first_start(msg.from_user.username)
    Globals.mode = 'update1'
    bot.send_message(msg.chat.id, f'Enter a list before translation:')


@bot.message_handler(commands=['delete'])
def delete_message(msg):
    CustomDictionary.download_dictionary_on_first_start(msg.from_user.username)
    Globals.mode = 'delete'
    bot.send_message(msg.chat.id, f'Enter a value you would like to delete:')


@bot.message_handler(commands=['clear'])
def clear_message(msg):
    CustomDictionary.download_dictionary_on_first_start(msg.from_user.username)
    Globals.mode = 'clear'
    bot.send_message(msg.chat.id, 'Do you want to clear your dictionary? (yes/no)')


@bot.message_handler(commands=['show'])
def show_message(msg):
    CustomDictionary.download_dictionary_on_first_start(msg.from_user.username)
    # Telegram doesn't support messages > 4096, we need to split output in case if dictionary has exceeded 4096
    # To split dictionary by 2+ messages we use position and step
    username = msg.from_user.username
    position = 0
    step = 4090
    dictionary_list = CustomDictionary.show_list(username, position)
    if 'Dictionary is empty!' not in dictionary_list:
        while 'Total' not in CustomDictionary.show_list(username, position, step):
            bot.send_message(msg.chat.id, CustomDictionary.show_list(username, position, step))
            position += step
    bot.send_message(msg.chat.id, CustomDictionary.show_list(username, position, step))


@bot.message_handler(commands=['training'])
def training_message(msg):
    CustomDictionary.download_dictionary_on_first_start(msg.from_user.username)
    Globals.mode = 'training'
    bot.send_message(msg.chat.id, CustomDictionary.start_training(msg.from_user.username))


@bot.message_handler(content_types=['text'])
def send_text(msg):
    CustomDictionary.download_dictionary_on_first_start(msg.from_user.username)
    user_name = msg.from_user.username
    user_text = msg.text.lower()
    if Globals.mode == 'training':
        bot.send_message(msg.chat.id, CustomDictionary.start_training(user_name, user_text))
    elif Globals.mode == 'update1':
        Globals.temp_user_input_1 = user_text
        bot.send_message(msg.chat.id, 'Enter a list after translation:')
        Globals.mode = 'update2'
    elif Globals.mode == 'update2':
        Globals.temp_user_input_2 = user_text
        bot.send_message(msg.chat.id, CustomDictionary.update_dictionary(user_name, Globals.temp_user_input_1, Globals.temp_user_input_2))
        Globals.mode = 'training'
    elif Globals.mode == 'clear':
        if user_text == 'yes':
            bot.send_message(msg.chat.id, CustomDictionary.clear_dictionary(user_name))
            Globals.mode = 'training'
        elif user_text == 'no':
            Globals.mode = 'training'
        else:
            bot.send_message(msg.chat.id, 'Do you want to clear your dictionary? (yes/no)')
    elif Globals.mode == 'delete':
        bot.send_message(msg.chat.id, CustomDictionary.delete_item(user_name, user_text))
        Globals.mode = 'training'


bot.polling()
