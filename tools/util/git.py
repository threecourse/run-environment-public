import subprocess


def commit_id_head() -> str:
    """コミットIDを取得する"""
    completed_process = subprocess.run("git rev-parse --short HEAD",
                                       shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return completed_process.stdout.decode().strip()


def is_git_clean() -> bool:
    """最新のコミットから変更された状態がないか確認する"""
    completed_process = subprocess.run("git status --short",
                                       shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout = completed_process.stdout.decode()
    return len(stdout) == 0
