import config
import os
import google.cloud.logging

from google.cloud import storage
from classes.globals import Globals


class Gcp:
    _storage_client = None
    _logging_client = None

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
    def _blob_exists(bucket_name, blob_name):
        Gcp._ensure_storage_client()
        bucket = Gcp._storage_client.bucket(bucket_name)
        blob_exists = storage.Blob(bucket=bucket, name=blob_name).exists(Gcp._storage_client)
        if blob_exists:
            return True
        return False

    @staticmethod
    def _write_to_storage(bucket_name, user_name, file_name):
        Gcp._ensure_storage_client()
        bucket = Gcp._storage_client.bucket(bucket_name)
        blob = bucket.blob(f'{user_name}/{file_name}')
        blob.upload_from_filename(file_name)

    @staticmethod
    def _ensure_dictionary_bucket():
        Gcp._ensure_storage_client()
        bucket = Gcp._storage_client.bucket(config.DICT_BUCKET_NAME)
        if not Gcp._bucket_exists(config.DICT_BUCKET_NAME):
            bucket.create()

    @staticmethod
    def _delete_file_in_bucket(bucket_name, blob_name):
        Gcp._ensure_storage_client()
        bucket = Gcp._storage_client.get_bucket(bucket_name)
        blobs = bucket.list_blobs(prefix=blob_name)
        for blob in blobs:
            blob.delete()

    @staticmethod
    def get_token():
        return Gcp._read_from_storage(config.TOKEN_BUCKET_NAME, config.TOKEN_BLOB_NAME)

    @staticmethod
    def upload_dictionary_to_bucket(user_name):
        Gcp._ensure_dictionary_bucket()
        Gcp._write_to_storage(config.DICT_BUCKET_NAME, user_name, Globals.get_dictionary_file(user_name))

    @staticmethod
    def upload_file_to_bucket(user_name, file_name):
        Gcp._ensure_dictionary_bucket()
        Gcp._write_to_storage(config.DICT_BUCKET_NAME, user_name, file_name)

    @staticmethod
    def read_file_from_bucket(blob_name):
        Gcp._ensure_dictionary_bucket()
        if Gcp._blob_exists(config.DICT_BUCKET_NAME, blob_name):
            return Gcp._read_from_storage(config.DICT_BUCKET_NAME, blob_name)
        return None

    @staticmethod
    def download_dictionary_from_bucket(user_name):
        blob_name = Globals.get_active_dictionary_blob_name(user_name)
        dictionary_file = Globals.get_dictionary_file(user_name)
        Gcp._ensure_dictionary_bucket()
        content = ''
        if Gcp._blob_exists(config.DICT_BUCKET_NAME, blob_name):
            content = Gcp._read_from_storage(config.DICT_BUCKET_NAME, blob_name)
        if os.path.exists(dictionary_file):
            os.remove(dictionary_file)
        open(dictionary_file, 'a').close()
        with open(dictionary_file, 'w', encoding='utf-8') as f:
            f.write(content)

    @staticmethod
    def _list_files_from_folder(bucket_name, blob_path):
        Gcp._ensure_storage_client()
        files = []
        for blob in Gcp._storage_client.list_blobs(bucket_name, prefix=blob_path):
            files.append(str(blob.name))
        return files

    @staticmethod
    def list_user_dictionaries(user_name):
        Gcp._ensure_dictionary_bucket()
        bucket_name = config.DICT_BUCKET_NAME
        all_files = Gcp._list_files_from_folder(bucket_name, user_name)
        dictionaries = []
        for file in all_files:
            if file != Globals.get_active_dictionary_blob_name_cache(user_name):
                dictionaries.append(file)
        return dictionaries

    @staticmethod
    def delete_dictionary_from_gcp_bucket(user_name):
        blob_name = Globals.get_active_dictionary_blob_name(user_name)
        Gcp._ensure_dictionary_bucket()
        if Gcp._blob_exists(config.DICT_BUCKET_NAME, blob_name):
            Gcp._delete_file_in_bucket(config.DICT_BUCKET_NAME, blob_name)
