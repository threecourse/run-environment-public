import os
import subprocess

from flask import Flask, request, json, jsonify

app = Flask(__name__)


@app.route('/')
def hello_world():
    # テスト用
    target = os.environ.get('TARGET', 'World')
    return 'Hello {}!\n'.format(target)


@app.route('/run', methods=["POST"])
def run():
    # 常に成功のレスポンスを返すようにする
    try:
        # mime-application/json を入れなくても動くようにする
        data = request.get_data().decode('utf-8')
        data = json.loads(data)
        run_name = str(data['run_name'])
        subprocess.check_call(["python", f"startup.py", f"--name", f"{run_name}"])
        return jsonify({"message": f"task finished"})
    except Exception as ex:
        return jsonify({"message": f"task failed - Exception: {ex}"})


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
