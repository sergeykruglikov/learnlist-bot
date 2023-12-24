from google.cloud import storage


class Gcp:
    @staticmethod
    def get_token():
        bucket_name = 'learnlist-api-keys'
        blob_name = 'bot-api-key.txt'
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        with blob.open('r') as f:
            token = f.read()
        return token
