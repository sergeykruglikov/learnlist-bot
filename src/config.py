class Mode:
    CREATE = 'create'
    UPDATE_ITEM = 'item key'
    UPDATE_VALUE = 'item value'
    DELETE = 'delete'
    CLEAR = 'clear'
    TRAINING = 'training'
    CHANGE_DICTIONARY = 'change dictionary'


DICT_BUCKET_NAME = 'learnlist-dictionaries'
TOKEN_BUCKET_NAME = 'learnlist-api-keys'
TOKEN_BLOB_NAME = 'bot-api-key.txt'
DEFAULT_DICTIONARY = 'dictionary'
