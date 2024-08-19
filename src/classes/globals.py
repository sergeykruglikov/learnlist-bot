from config import Mode, DEFAULT_DICTIONARY


class Globals:
    previous_question = previous_answer = None
    current_mode = Mode.TRAINING
    temp_user_input_1 = temp_user_input_2 = ''
    first_start = True
    active_dictionary = DEFAULT_DICTIONARY

    @staticmethod
    def get_active_dictionary_blob_name(user_name):
        return f'{user_name}/{user_name}_{Globals.active_dictionary}.ll'

    @staticmethod
    def get_dictionary_file(user_name):
        return f'{user_name}_{Globals.active_dictionary}.ll'

    @staticmethod
    def get_active_dictionary_blob_name_cache(user_name):
        return f'{user_name}/{user_name}_active_dictionary.al'

    @staticmethod
    def get_active_dictionary_file_name_cache(user_name):
        return f'{user_name}_active_dictionary.al'
