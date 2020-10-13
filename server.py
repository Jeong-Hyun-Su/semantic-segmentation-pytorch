import os
import sys
sys.path.append("/workspace/semantic")

from flask import Flask, render_template, request, Response, send_file, jsonify
from PIL import Image
from io import BytesIO
from queue import Queue, Empty
import threading
import time
import seg

if not os.path.exists("./imgs"):
    os.makedirs("./imgs")
if not os.path.exists("./result"):
    os.makedirs("./result")

# Server & Handling Setting
app = Flask(__name__)

requests_queue = Queue()
BATCH_SIZE = 1
CHECK_INTERVAL = 0.1


# Queue 핸들링
def handle_requests_by_batch():
    while True:
        requests_batch = []
        while not (len(requests_batch) >= BATCH_SIZE):
            try:
                requests_batch.append(requests_queue.get(timeout=CHECK_INTERVAL))
            except Empty:
                continue

            for requests in requests_batch:
                requests['output'] = run(requests['input'][0])


# 쓰레드
threading.Thread(target=handle_requests_by_batch).start()


@app.route("/")
def main():
    return render_template("index.html")


# Sketch Start
def run(img):
    # 전달받은 이미지 저장 및 변환
    img_dir = "./imgs/input.png"
    result_dir = "./result/output.png"

    img.save(img_dir)

    # 변환
    seg.segmentation()

    output = Image.open(result_dir)

    # 사진 체크 후 삭제
    if os.path.isfile(img_dir):
        os.remove(img_dir)
    if os.path.isfile(result_dir):
        os.remove(result_dir)

    byte_io = BytesIO()
    output.save(byte_io, "PNG")
    byte_io.seek(0)

    return byte_io


@app.route("/segmentation", methods=['POST'])
def segmentations():
    # 큐에 쌓여있을 경우,
    if requests_queue.qsize() > BATCH_SIZE:
        return jsonify({'error': 'TooManyReqeusts'}), 429

    try:
        img = request.files['image']

    except Exception:
        print("error : not contain image")
        return Response("fail", status=400)

    # Queue - put data
    req = {
        'input': [img]
    }
    requests_queue.put(req)

    # Queue - wait & check
    while 'output' not in req:
        time.sleep(CHECK_INTERVAL)

    # Get Result & Send Image
    byte_io = req['output']

    return send_file(byte_io, mimetype="image/png")


# Health Check
@app.route("/healthz", methods=["GET"])
def healthCheck():
    return "", 200


if __name__ == "__main__":
    from waitress import serve
    serve(app, host='0.0.0.0', port=80)
