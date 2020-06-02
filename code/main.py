import datetime
import json
import logging
import os

import google.cloud.logging

from env import Env
from model import Model
from util import gce, gcs


def run(data: dict):
    # パラメータ
    n = int(data.get("n", 100))  # 100で10秒程度

    # 計算の実行
    start_time = datetime.datetime.now()
    model = Model()
    ans = model.calc(n)
    end_time = datetime.datetime.now()

    # 情報の取得
    elapsed = (int)((end_time - start_time).total_seconds() * 1000)
    result = {"run_name": run_name, "commit_id": commit_id, "image_digest": image_digest,
              "result": ans, "elapsed_time": elapsed,
              "n": n}
    logging.info(f"[{run_name}] calculation time: {elapsed} ms")

    # 結果の保存
    result_dir = f"../result/{run_name}"
    os.makedirs(result_dir, exist_ok=True)
    result_path = os.path.join(result_dir, "result.json")
    with open(result_path, "w") as f:
        json.dump(result, f)

    # GCSに送付
    if use_gcs:
        blob_dir = f"result/{run_name}"
        gcs.upload_directory(Env.bucket_name, blob_dir, result_dir)


if __name__ == "__main__":
    # Cloud Loggingのセットアップ
    client = google.cloud.logging.Client()
    client.setup_logging()

    # 環境変数・入力の取得
    use_gcs = bool(int(os.environ["USE_GCS"]))

    if use_gcs:
        json_path = "run_info.json"
    else:
        json_path = "run_info_default.json"

    with open(json_path) as f:
        data = json.load(f)
    run_name = data["run_name"]
    commit_id = data["commit_id"]
    image_digest = data["image_digest"]
    self_delete = int(data.get('self_delete', 0))

    # ランの実行
    try:
        logging.info(f"[{run_name}] started run")
        run(data)
        logging.info(f"[{run_name}] finished run")
    except Exception as ex:
        logging.info(f"[{run_name}] failed run - {ex}")
    finally:
        # 自分のインスタンスを削除する
        if self_delete:
            gce.self_delete()
            logging.info(f"[{run_name}] deleted instance")
