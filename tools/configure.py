import os
import subprocess

from env import Env


def docker_build_base() -> None:
    """ベースとなるdocker imageをビルドする"""
    cmd = f"docker build -t {Env.image_base_name} -f {Env.docker_file_base} ."
    subprocess.check_call(cmd, shell=True)


def docker_build() -> None:
    """必要な修正を加えたdocker imageをビルドする"""
    cmd1 = f"docker build -t {Env.image_name} -f {Env.docker_file} ."
    cmd2 = f"docker tag {Env.image_name} '{Env.gcr_path}'"
    subprocess.check_call(cmd1, shell=True)
    subprocess.check_call(cmd2, shell=True)


def docker_push() -> None:
    """GCRにdocker imageをpushする"""
    cmd = f"docker push '{Env.gcr_path}'"
    subprocess.check_call(cmd, shell=True)


def deploy_server() -> None:
    """Cloud Runにコンテナをデプロイする

    httpリクエストを受けてランを実行できるようにする
    argsの仕様は難解なので、server.shで起動させるようにした
    """
    max_instances = 3  # 小さめにしてみる
    concurrency = 1

    cmd = f"""gcloud run deploy {Env.service_name} --image {Env.gcr_path} --platform managed \\
    --region {Env.region} --no-allow-unauthenticated \\
    --set-env-vars USE_GCS=1 \\
    --max-instances {max_instances} --cpu 1 --memory 512Mi --timeout 900 --concurrency {concurrency}\\
    --command /bin/bash --args server.sh
    """
    print("---------------")
    print(cmd)
    print("---------------")
    subprocess.check_call(cmd, shell=True)


def docker_run_server(cwd: str) -> None:
    """ローカルでコンテナを起動する

    httpリクエストを受けてランを実行できるようにする
    """
    HOME = os.path.expanduser("~")
    PORT = 8080
    cmd = f"""
    docker run \\
      -v {HOME}/.config/gcloud:/root/.config/gcloud \\
      -v {cwd}/result:/app/result \\
      -v {cwd}/code:/app/code \\
      -e USE_GCS=1 \\
      -p {PORT}:{PORT} \\
      --rm -it {Env.image_name} gunicorn --bind :{PORT} --workers 1 --threads 1 server:app 
    """
    subprocess.call(cmd, shell=True)
