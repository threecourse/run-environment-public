import json
import os
import tarfile
import tempfile
import shutil
import subprocess
from google.cloud import tasks_v2
from env import Env
from util import files, gcp


def docker_run(cwd: str) -> None:
    """ローカルのdocker上で起動する"""
    HOME = os.path.expanduser("~")
    PORT = 8080
    cmd = f"""
    docker run \\
      -v {HOME}/.config/gcloud:/root/.config/gcloud \\
      -v {cwd}/result:/app/result \\
      -v {cwd}/code:/app/code \\
      -p {PORT}:{PORT} \\
      -e USE_GCS=0 \\
      -w /app/code \\
      --rm -it {Env.image_name} /bin/bash
    """
    subprocess.call(cmd, shell=True)


def upload_code(run_name: str) -> None:
    """対象フォルダ内を圧縮してGCSにアップロードする"""
    tmpdir = tempfile.mkdtemp()
    local_tar_path = os.path.join(tmpdir, "codes.tar.gz")
    files.compress(Env.local_target_dir, local_tar_path)
    gcp.upload_blob(Env.bucket_name, local_tar_path, Env.blob_name(run_name))
    shutil.rmtree(tmpdir)


def upload_run_info(run_name: str, commit_id: str, params: dict, self_delete: int) -> None:
    """ラン情報をGCSにアップロードする"""
    image_digest = gcp.get_image_digest(Env.gcr_path)
    data = {"run_name": run_name,
            "image": Env.gcr_path,
            "commit_id": commit_id,
            "image_digest": image_digest,
            "self_delete": self_delete}
    for k, v in params.items():
        data[k] = v
    source_str = json.dumps(data)
    gcp.upload_json(Env.bucket_name, source_str, Env.blob_name_run_info(run_name))


def create_instance(run_name: str) -> None:
    """コンテナを用いてインスタンスを起動する"""

    cmd = f""" gcloud compute instances create-with-container {run_name} \\
          --machine-type=n1-standard-1 \\
          --metadata=google-logging-enabled=true \\
          --scopes=cloud-platform \\
          --boot-disk-size=50GB \\
          --container-restart-policy never \\
          --container-image="{Env.gcr_path}" \\
          --container-env USE_GCS=1 \\
          --container-env RUN_NAME={run_name} \\
          --container-command=/bin/bash \\
          --container-arg startup.sh \\
          --zone {Env.zone}
    """
    print("----------------------")
    print(cmd)
    print("----------------------")
    subprocess.check_call(cmd, shell=True)


def local_submit(run_name: str) -> None:
    """ローカルのdocker上のサーバにhttpリクエストを投げる（デバッグ用）"""
    payload = f'{{"run_name": "{run_name}"}}'
    subprocess.check_call(f"curl -X POST -d '{payload}' localhost:8080/run", shell=True)


def submit(run_name: str) -> None:
    """Cloud TasksにタスクをSubmitする"""

    client = tasks_v2.CloudTasksClient()
    parent = client.queue_path(Env.project_id, Env.region, Env.cloud_task_queue)
    task = {
        'http_request': {
            'http_method': 'POST',
            'url': Env.cloud_run_url,
            'oidc_token': {
                'service_account_email': Env.cloud_run_invoker_email
            }
        }
    }

    payload = f'{{"run_name": "{run_name}"}}'
    if payload is not None:
        converted_payload = payload.encode()
        task['http_request']['body'] = converted_payload

    response = client.create_task(parent, task)
    # print('Created task {}'.format(response.name))
    # print(response)
