import json
import os
from google.cloud import storage


def upload_directory(bucket_name: str, blob_dir: str, target_dir: str):
    """対象フォルダ内のファイルを、GCSに保存する"""

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    for root, dirs, files in os.walk(target_dir):
        for file in files:
            path = os.path.join(root, file)
            arcname = os.path.relpath(os.path.join(root, file), target_dir)
            blob = bucket.blob(f"{blob_dir}/{arcname}")
            blob.upload_from_filename(path)


def download_json(bucket_name: str, source_blob_name: str):
    """文字列をGCSにアップロードする"""

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    json_str = blob.download_as_string()
    data = json.loads(json_str)
    return data


