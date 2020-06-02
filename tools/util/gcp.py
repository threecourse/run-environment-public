import os
import subprocess

from google.cloud import storage


def upload_blob(bucket_name: str, source_file_name: str, destination_blob_name: str) -> None:
    """ファイルをGCSにアップロードする"""

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)


def upload_json(bucket_name: str, source_str: str, destination_blob_name: str) -> None:
    """文字列をGCSにアップロードする"""

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(source_str)


def download_blob(bucket_name: str, source_blob_name: str, destination_file_name: str) -> None:
    """ファイルをGCSからダウンロードする"""

    # フォルダの作成
    os.makedirs(os.path.dirname(destination_file_name), exist_ok=True)

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)


def get_image_digest(gcr_path) -> str:
    """コンテナのimage digestを取得する"""
    # TODO: 適切な取得方法の検討
    completed_process = subprocess.run(
        f"gcloud container images describe {gcr_path} --format 'value(image_summary.digest)'",
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = completed_process.stdout.decode().strip()
    return result[7:19]
