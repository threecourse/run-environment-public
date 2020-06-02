import argparse
import os
import subprocess
import tarfile

from google.cloud import storage

from env import Env


def download_blob(bucket_name: str, source_blob_name: str, destination_file_name: str, project_id: str):
    # フォルダの作成
    os.makedirs(os.path.dirname(destination_file_name), exist_ok=True)

    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)


def extract(target_path: str, out_dir: str):
    """tar.gzを解凍する"""
    tar = tarfile.open(target_path)
    tar.extractall(path=out_dir)
    tar.close()
    os.remove(target_path)


def run(work_dir):
    os.chdir(work_dir)
    subprocess.check_call(["python", "main.py"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", type=str, required=True)
    args, unknown_args = parser.parse_known_args()

    run_name = args.name

    # local path
    local_tar_path = f"../work/code-{run_name}.tar.gz"
    local_extract_path = f"../code-{run_name}"
    local_run_info_path = os.path.join(local_extract_path, "run_info.json")

    download_blob(Env.bucket_name, Env.blob_name(run_name), local_tar_path, Env.project_id)
    extract(local_tar_path, local_extract_path)
    download_blob(Env.bucket_name, Env.blob_name_run_info(run_name), local_run_info_path, Env.project_id)
    run(local_extract_path)
