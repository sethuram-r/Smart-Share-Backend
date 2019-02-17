import threading
from queue import Queue

from flask import Flask, request, jsonify

app = Flask(__name__)

requests = []
responses = {}


@app.route('/worker', methods=['GET'])
def get():
    """ worker gets task to be done from here"""

    if len(requests) == 0:
        request_to_process = 'Done'

    else:
        request_to_process = requests.pop(0)
        print("request_to_process------->", request_to_process)

    response = jsonify(request_to_process)
    response.status_code = 200
    return response


@app.route('/worker', methods=['POST'])
def post():
    """ worker puts back the result here"""

    if request:
        data = request.json
        print("data", data)
        responses[data["id"]] = data
        return "success"
    else:
        raise NotImplementedError


@app.route('/<path:path>')
def catch_all(path):
    print('You want path: %s' % path)

    que = Queue()
    try:
        thread = threading.Thread(target=request_preparation, args=(request, path, request.args.get('username'), que))

        thread.start()
        result = que.get()
        return jsonify(result)
    except:
        print("Error: unable to spawn")


def request_preparation(request, path, args, queue):
    with app.test_request_context():
        current_size_of_requests = len(requests)
        temp = {}
        id = current_size_of_requests + 1
        temp["id"] = id
        print(request.args.get('username'))
        if request.method == 'GET':
            temp["param"] = args
            temp["task"] = path
        else:
            temp["data"] = request.data
            temp["task"] = path
        requests.append(temp)
        while True:
            if id in responses:
                # print(responses)
                queue.put(responses[id]["response"])
                break
            else:
                print("waiting for the results from worker.......")
                pass
        del responses[id]
        print("responses after thread completion ----------->", responses)
