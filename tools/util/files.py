import os
import tarfile


def compress(target_dir: str, out_path: str):
    """対象フォルダ内を圧縮してtar.gzに保存する"""

    # 一部フォルダ、拡張子の除外
    def filter(tar_info):
        if tar_info.name.endswith(".pyc"):
            return None
        elif tar_info.name.endswith("__pycache__"):
            return None
        else:
            return tar_info

    # フォルダの作成
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    # ファイルの追加
    archive = tarfile.open(out_path, mode='w:gz')
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            path = os.path.join(root, file)
            arcname = os.path.relpath(os.path.join(root, file), target_dir)
            archive.add(path, arcname=arcname, filter=filter)

    archive.close()


def extract(target_path: str, out_dir: str):
    """tar.gzを解凍する"""
    tar = tarfile.open(target_path)
    tar.extractall(path=out_dir)
    tar.close()
