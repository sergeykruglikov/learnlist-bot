import os
import random
import numpy as np

from classes.logging import Logging
from classes.globals import Globals


class CustomDictionary:
    @staticmethod
    def clear_dictionary(username):
        dictionary_file = f'./{username}_dictionary.ll'
        if not os.path.exists(dictionary_file):
            return 'Dictionary is empty!\nTo update your dictionary send /update'
        os.remove(dictionary_file)
        return 'Dictionary has been cleared.\nTo update your dictionary send /update'

    @staticmethod
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
            err = Logging.log_error(debug_msg)
            return pretty_msg if err is None else f'{pretty_msg}, {err}'
        if file_content != '':
            try:
                working_dictionary = eval(file_content)
            except Exception as ex:
                Logging.log_error(f'Failed to eval(file_content) in read_from_dictionary: {ex}')
                return 'Hmm... Something`s wrong with the dictionary:\n', str(ex)
        return working_dictionary

    @staticmethod
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
        working_dictionary = CustomDictionary.read_from_dictionary(username)
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
            err = Logging.log_error(debug_msg)
            return pretty_msg if err is None else f'{pretty_msg}, {err}'

    @staticmethod
    def delete_item(username, item):
        try:
            working_dictionary = CustomDictionary.read_from_dictionary(username)
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
            err = Logging.log_error(debug_msg)
            return pretty_msg if err is None else f'{pretty_msg}, {err}'

    @staticmethod
    def show_list(username, position, step):
        output = ''
        try:
            working_dictionary = CustomDictionary.read_from_dictionary(username)
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

    @staticmethod
    def start_training(username, answer=''):
        working_dictionary = CustomDictionary.read_from_dictionary(username)
        if working_dictionary is None or working_dictionary == {}:
            return 'Dictionary is empty!\nTo update your dictionary send /update'
        try:
            dict_keys = np.asarray(list(working_dictionary.keys()))
            dict_values = np.asarray(list(working_dictionary.values()))
        except Exception as ex:
            debug_msg = f'Failed to convert keys or values in start_training: {ex}'
            pretty_msg = f'An error occurred :(\n{str(ex)}'
            err = Logging.log_error(debug_msg)
            return pretty_msg if err is None else f'{pretty_msg}, {err}'

        previous_q = Globals.previous_question
        previous_a = Globals.previous_answer
        k = random.randint(0, len(dict_keys) - 1)

        # True for key, False for value
        key_selected = random.choice([False, True])
        current_question_list = dict_keys if key_selected else dict_values
        current_answer_list = dict_values if key_selected else dict_keys

        Globals.previous_question = current_question_list[k]
        Globals.previous_answer = current_answer_list[k]

        try:
            if answer == '':
                return f'Training started!\n{current_question_list[k]}:'
            if answer.lower().strip() == previous_a.lower().strip():
                return f'Yes!✅\n{current_question_list[k]}:'
            else:
                return f'No!❌\n{previous_q}: {previous_a}\n{current_question_list[k]}:'
        except Exception as ex:
            # debug_msg = f'Failed to evaluate answer in start_training, input = {answer.lower().strip()}: {ex}'
            # pretty_msg = f'Something went wrong, please press /start. If the issue persists, please report the issue.'
            # error = Logging.log_error(debug_msg)
            return 'To start training send /training'  # if error is None else f'{pretty_msg}, {error}'