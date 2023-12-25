import os
import google.cloud.logging

from google.cloud import storage
from classes.logging_ import Logging


class Gcp:
    _storage_client = None
    _logging_client = None
    _DICT_BUCKET_NAME = 'learnlist-dictionaries'
    _TOKEN_BUCKET_NAME = 'learnlist-api-keys'
    _TOKEN_BLOB_NAME = 'bot-api-key.txt'

    @staticmethod
    def _ensure_storage_client():
        if Gcp._storage_client is None:
            Gcp._storage_client = storage.Client()

    @staticmethod
    def ensure_logging_client():
        if Gcp._logging_client is None:
            Gcp._logging_client = google.cloud.logging.Client()
            Gcp._logging_client.setup_logging()

    @staticmethod
    def _read_from_storage(bucket_name, blob_name):

        Gcp._ensure_storage_client()
        bucket = Gcp._storage_client.bucket(bucket_name)
        if not Gcp._bucket_exists(bucket_name):
            raise Exception(f'Bucket {bucket_name} does not exist')
        blob = bucket.blob(blob_name)
        with blob.open('r', encoding='utf8') as f:
            content = f.read()
        return content

    @staticmethod
    def _bucket_exists(bucket_name):
        Gcp._ensure_storage_client()
        for b in Gcp._storage_client.list_buckets():
            if b.name == bucket_name:
                return True
        return False

    @staticmethod
    def _write_to_storage(bucket_name, user_name, temp_file_name):
        Gcp._ensure_storage_client()
        bucket = Gcp._storage_client.bucket(bucket_name)
        if not Gcp._bucket_exists(bucket_name):
            bucket.create()
        blob = bucket.blob(f'{user_name}/{user_name}_dictionary.ll')
        blob.upload_from_filename(temp_file_name)

    @staticmethod
    def _delete_file_in_bucket(bucket_name, blob_name):
        Gcp._ensure_storage_client()
        bucket = Gcp._storage_client.get_bucket(bucket_name)
        blobs = bucket.list_blobs(prefix=blob_name)
        for blob in blobs:
            blob.delete()

    @staticmethod
    def get_token():
        return Gcp._read_from_storage(Gcp._TOKEN_BUCKET_NAME, Gcp._TOKEN_BLOB_NAME)

    @staticmethod
    def upload_dictionary_to_bucket(user_name, dictionary_file):
        Gcp._write_to_storage(Gcp._DICT_BUCKET_NAME, user_name, dictionary_file)

    @staticmethod
    def download_dictionary_from_bucket(user_name):
        blob_name = f'{user_name}/{user_name}_dictionary.ll'
        dictionary_file = f'./{user_name}_dictionary.ll'
        content = Gcp._read_from_storage(Gcp._DICT_BUCKET_NAME, blob_name)
        if os.path.exists(dictionary_file):
            os.remove(dictionary_file)
        open(dictionary_file, 'a').close()
        with open(dictionary_file, 'w', encoding='utf-8') as f:
            f.write(content)

    @staticmethod
    def delete_dictionary_from_gcp_bucket(user_name):
        blob_name = f'{user_name}/{user_name}_dictionary.ll'
        Gcp._delete_file_in_bucket(Gcp._DICT_BUCKET_NAME, blob_name)

