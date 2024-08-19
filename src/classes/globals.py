from config import Mode


class Globals:
    previous_question = previous_answer = None
    current_mode = Mode.TRAINING
    temp_user_input_1 = temp_user_input_2 = ''
    first_start = True
