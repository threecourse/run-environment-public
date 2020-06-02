## Run Environment

### モチベーション

ランを気軽にサーバに投げて結果やログを取れる環境を構築したい。

* コマンドを実行すると、ランがGCP上のサーバで行われ、結果やログが保存されるようにしたい。
* ローカルで容易にデバッグができる環境としたい
* ローカルおよびGCPでのランにはdockerを用いたい
* 行ったランとそのコードを紐付けたい

調査した内容を情報共有するために記述したものです。セキュリティや課金額を確認したわけではないので、使用する場合は十分ご注意下さい。

 
### ディレクトリ構成

* tools - ローカルで動かすための各種ユーティリティ。コンテナのビルド、GCRへのpush、GCPプロジェクトの構成、ランの実行など
* docker - dockerfileおよびコンテナに含めるファイル  
* code - 計算コード。行いたい任意の計算、結果のGCSへのアップロードなどの機能を持つ   

### requirements

* docker  
  see https://docs.docker.com/engine/install/
* Google Cloud SDK  
  see https://cloud.google.com/sdk/install?hl=ja  
  権限設定が必要（以下のコマンドなどが必要かもしれない）
  ```
  gcloud auth application-default login 
  ```
* Google Cloudクライアント ライブラリ
  ```
  pip install google-cloud-storage==1.28.1   
  pip install google-cloud-tasks==1.5.0
  pip install google-cloud-logging==1.15.0
  ```

### GCPプロジェクトの構成

(途中で必要なAPIの許可などを行う必要があるため、1行ごとに実行するほうが良いかも。)

1. tools/env.py, code/env.py, docker/env.py に適切な名前を入力しておく

2. 以下のコマンドを実行する
```
PROJECT_ID=<project-id> # 適宜セットして下さい
TASK_NAME=judge-queue
SERVICE_NAME=judge-service

# プロジェクトの作成
gcloud projects create ${PROJECT_ID} 
gcloud config set project ${PROJECT_ID} 

# 権限設定が必要？
gcloud auth application-default login 

# プロジェクトの作成
gcloud tasks queues create ${TASK_NAME} --max-concurrent-dispatches=3
gsutil mb gs://${PROJECT_ID}/

# dockerイメージのビルド
python tools/main.py --build_base --build

# dockerイメージのプッシュ
python tools/main.py --push 

# Cloud Runへのデプロイ
python tools/main.py --deploy_server

# Cloud Tasksのサービスアカウントの作成
gcloud iam service-accounts create invoker-service-account --display-name "Invoker Service Account"
gcloud run services add-iam-policy-binding ${SERVICE_NAME} \
       --member=serviceAccount:invoker-service-account@${PROJECT_ID}.iam.gserviceaccount.com \
       --role=roles/run.invoker --platform=managed --region us-central1
```

* Cloud Runによるランを行わない場合、Cloud RunやCloud Tasksに関する部分の構成は不要

### ランの実行

#### 1. GCEインスタンスを作成してランの実行
```
python tools/main.py --run --commit_id_tmp tmp_run
```

#### 2. Cloud Runによるランの実行
```
python tools/main.py --submit --commit_id_tmp tmp_run
```

#### （デバッグ用）localでdockerを起動する
```
python tools/main.py --local_run
```

#### （デバッグ用）localでサーバを立て、そのサーバに対してsubmitする
```
python tools/main.py --local_server
python tools/main.py --local_submit --commit_id_tmp temp1
```

