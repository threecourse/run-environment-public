import argparse
import google.cloud.logging
import logging
import os
import sys
import configure
import warnings
import run
from env import Env
from util import git

if __name__ == "__main__":

    # このフォルダのコードはローカルで実行するので、ユーザーアカウント権限で構わない
    warnings.filterwarnings("ignore", "Your application has authenticated using end user credentials")

    # Cloud Loggingのセットアップ
    client = google.cloud.logging.Client()
    client.setup_logging()

    # 引数の扱い
    parser = argparse.ArgumentParser()

    # configure
    parser.add_argument("--build_base", action="store_true")
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--push", action="store_true")
    parser.add_argument("--deploy_server", action="store_true")
    parser.add_argument("--local_server", action="store_true")

    # run
    parser.add_argument("--local_run", action="store_true")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--local_submit", action="store_true")
    parser.add_argument("--submit", action="store_true")

    # others
    parser.add_argument("--commit_id_tmp", type=str, default=None)
    # parser.add_argument("--temp", action="store_true")

    args, unknown_args = parser.parse_known_args()

    # (--key, value)の組として入力された未定義引数は計算用のパラメータとして扱う
    if len(unknown_args) % 2 == 1:
        print(f"引数が不適切です : {unknown_args}")
        sys.exit(11)
    params = {}
    for i in range(len(unknown_args) // 2):
        key = unknown_args[i * 2]
        value = unknown_args[i * 2 + 1]
        if not key.startswith("--"):
            print(f"引数が不適切です : {unknown_args}")
            sys.exit(11)
        params[key[2:]] = value

    args_print = [(k, v) for k, v in vars(args).items() if not ((v == False) or v is None or v == 0)]
    print(f"args: {args_print}")
    print(f"params: {params}")

    # parameter ------------------------------
    cwd = os.getcwd()

    # configure ------------------------------
    if args.build_base:
        # ベースとなるdocker imageのビルド
        configure.docker_build_base()
    if args.build:
        # docker imageのビルド
        configure.docker_build()
    if args.push:
        # docker imageのGCRへのpush
        configure.docker_push()
    if args.deploy_server:
        # Cloud Runへのデプロイ
        configure.deploy_server()
    if args.local_server:
        # （デバッグ用）ローカルでCloud Runと同じようにサーバを立ち上げる
        configure.docker_run_server(cwd)

    # run ------------------------------
    run_name = Env.generate_run_name()

    if args.local_run:
        # （デバッグ用）ローカルでのデバッグ実行
        logging.info(f"[{run_name}] LOCAL RUN")
        run.docker_run(cwd)

    # ランを行う場合は、commit_id_tmpを指定するか、gitに変更がない状態とする
    is_run = args.run or args.local_submit or args.submit
    commit_id = "commit_id_not_set"
    if is_run:
        if git.is_git_clean():
            commit_id = git.commit_id_head()
        else:
            if args.commit_id_tmp is not None:
                commit_id = args.commit_id_tmp
            else:
                print("ランを行う場合はcommit_id_tmpを指定するか、gitに変更がない状態にしてください")
                sys.exit(10)

    if args.run:
        # GCEインスタンスを立ち上げてランを行う
        logging.info(f"[{run_name}] RUN")
        run.upload_code(run_name)
        run.upload_run_info(run_name, commit_id, params, self_delete=1)
        run.create_instance(run_name)
    if args.local_submit:
        # （デバッグ用）ローカルのサーバにランをsubmitする
        # 計算はlocalのdockerに行わせるが、GCSは使用する
        logging.info(f"[{run_name}] LOCAL SUBMIT")
        run.upload_code(run_name)
        run.upload_run_info(run_name, commit_id, params, self_delete=0)
        run.local_submit(run_name)
    if args.submit:
        # Cloud Runにランをsubmitする
        logging.info(f"[{run_name}] SUBMIT")
        run.upload_code(run_name)
        run.upload_run_info(run_name, commit_id, params, self_delete=0)
        run.submit(run_name)
