import os
import random
import numpy as np

from classes.gcp import Gcp
from classes.globals import Globals
from classes.logging_ import Logging


class CustomDictionary:
    @staticmethod
    def sync_dictionaries(user_name):
        if Globals.first_start:
            active_dictionary = Gcp.read_file_from_bucket(Globals.get_active_dictionary_blob_name_cache(user_name))
            if active_dictionary is not None:
                Globals.active_dictionary = active_dictionary
            Gcp.download_dictionary_from_bucket(user_name)
            Globals.first_start = False

    @staticmethod
    def clear_dictionary(user_name):
        dictionary_file = f'./{Globals.get_dictionary_file(user_name)}'
        if not os.path.exists(dictionary_file):
            return 'Dictionary is empty!\nTo update your dictionary send /update'
        os.remove(dictionary_file)
        Gcp.delete_dictionary_from_gcp_bucket(user_name)
        return 'Dictionary has been cleared.\nTo update your dictionary send /update'

    @staticmethod
    def read_from_dictionary(user_name):
        dictionary_file = f'./{Globals.get_dictionary_file(user_name)}'

        if not os.path.exists(dictionary_file):
            Gcp.download_dictionary_from_bucket(user_name)

        try:
            with open(dictionary_file, 'r', encoding='utf-8') as f:
                file_content = f.read()
        except Exception as ex:
            debug_msg = f'Failed to read dictionary in read_from_dictionary (file={dictionary_file}): {ex}'
            pretty_msg = f'Failed to read dictionary :(\n{ex}'
            err = Logging.log_error(debug_msg)
            return pretty_msg if err is None else f'{pretty_msg}, {err}'
        working_dictionary = {}

        if file_content != '':
            try:
                working_dictionary = eval(file_content)
            except Exception as ex:
                Logging.log_error(f'Failed to eval(file_content) in read_from_dictionary: {ex}')
                return f'Hmm... Something`s wrong with the dictionary:\n{ex}'
        return working_dictionary

    @staticmethod
    def change_dictionary(user_name, dictionary_name):
        Globals.active_dictionary = dictionary_name
        file_name = Globals.get_active_dictionary_file_name_cache(user_name)
        with open(f'./{file_name}', 'w', encoding='utf-8') as f:
            f.write(Globals.active_dictionary)
        Gcp.upload_file_to_bucket(user_name, file_name)

    @staticmethod
    def show_list(user_name, position, step=None):
        output = ''
        try:
            working_dictionary = CustomDictionary.read_from_dictionary(user_name)
        except Exception as ex:
            return 'Dictionary is empty!\nTo update your dictionary send /update'
        for item, value in working_dictionary.items():
            output += item + ' - ' + value + '\n'
        output += f'\nTotal: {len(working_dictionary.items())}'
        if len(output) >= 4096 and step:
            # output range: from current counter position plus step value
            return output[position:position + step]
        else:
            return output

    @staticmethod
    def list_dictionaries(user_name):
        is_local_dictionary_returned_from_gcp = False
        dictionary_gcp_paths = Gcp.list_user_dictionaries(user_name)
        all_dictionaries = 'Your dictionaries:\n'
        for dictionary_path in dictionary_gcp_paths:
            dictionary_pretty_name = dictionary_path.replace(f'{user_name}_', '').replace(user_name, '').replace('/', '').replace('.ll', '')
            if dictionary_pretty_name == Globals.active_dictionary:
                is_local_dictionary_returned_from_gcp = True
            all_dictionaries += f'{dictionary_pretty_name} [ACTIVE]\n' if dictionary_pretty_name == Globals.active_dictionary else f'{dictionary_pretty_name}\n'
        if not is_local_dictionary_returned_from_gcp:
            all_dictionaries += f'{Globals.active_dictionary} [ACTIVE]\n'
        return all_dictionaries

    @staticmethod
    def update_dictionary(user_name, words_in_string_1, words_in_string_2):
        dictionary_file = f'./{Globals.get_dictionary_file(user_name)}'
        temp_dictionary = {}
        try:
            list_1 = words_in_string_1.split('\n')
            list_2 = words_in_string_2.split('\n')
            temp_dictionary = zip(list_1, list_2)
            temp_dictionary = dict(temp_dictionary)
        except Exception as ex:
            str(ex)
        # To update dictionary we first need to update local dictionary, e.g. not downloading from GCP
        try:
            working_dictionary = CustomDictionary.read_from_dictionary(user_name)
        except Exception as ex:
            debug_msg = f'Failed to read dictionary file in update_dictionary, dictionary_file={dictionary_file}: {ex}'
            pretty_msg = f'Dictionary update failed :(\n{ex}'
            err = Logging.log_error(debug_msg)
            return pretty_msg if err is None else f'{pretty_msg}, {err}'

        if not working_dictionary:
            working_dictionary = temp_dictionary
        else:
            working_dictionary.update(temp_dictionary)
        try:
            with open(dictionary_file, 'w', encoding='utf-8') as f:
                f.write(str(working_dictionary))
            Gcp.upload_dictionary_to_bucket(user_name)
            return 'Dictionary updated!'
        except Exception as ex:
            debug_msg = f'Failed to write to dictionary file in update_dictionary, dictionary_file={dictionary_file}, working_dictionary={working_dictionary}: {ex}'
            pretty_msg = f'Dictionary update failed :(\n{ex}'
            err = Logging.log_error(debug_msg)
            return pretty_msg if err is None else f'{pretty_msg}, {err}'

    @staticmethod
    def delete_item(user_name, item):
        try:
            working_dictionary = CustomDictionary.read_from_dictionary(user_name)
            del working_dictionary[item]
        except Exception as ex:
            return 'Item not found!'
        dictionary_file = f'./{Globals.get_dictionary_file(user_name)}'
        try:
            with open(dictionary_file, 'w', encoding='utf-8') as f:
                f.write(str(working_dictionary))
            Gcp.upload_dictionary_to_bucket(user_name)
            return f'Item "{item}" deleted.'
        except Exception as ex:
            debug_msg = f'Failed to write to dictionary file, dictionary_file={dictionary_file}, working_dictionary={working_dictionary}: {ex}'
            pretty_msg = f'Item deletion failed :(\n{str(ex)}'
            err = Logging.log_error(debug_msg)
            return pretty_msg if err is None else f'{pretty_msg}, {err}'

    @staticmethod
    def start_training(user_name, answer=''):
        working_dictionary = CustomDictionary.read_from_dictionary(user_name)
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
            return 'To start training send /training'
