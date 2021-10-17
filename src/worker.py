import json
import sys
import os
import ssl
import getopt
import requests
from flask import Flask
from flask import request
from flask import make_response
from datetime import datetime, timedelta

from workers import WorkerRegistry
from tuplespace import tuplespace
from workers.compute_task_processor import ComputeTaskProcessor
from workers.embellish_task_processor import EmbellishTaskProcessor
from workers.persist_task_processor import PersistTaskProcessor
from workers.compute_threshold_task_processor import ComputeThresholdTaskProcessor
from workers.validate_task_processor import ValidateTaskProcessor


path = os.path.dirname(__file__)
app  = Flask(__name__)

task_map = {}


@app.route('/worker/processor/notify', methods=['GET'])
def notification():
    '''

    :return:
    '''
    rqst = request

    state = request.args.get("state")
    new_state = request.args.get("new_req_state")
    post_state = request.args.get("new_post_state")

    if new_state is None or post_state is None:
        # notify the worker thread that work is available.
        t = task_map[state].task_queue.put (state)
    else:
        # states have changed.  This means, someone has added/removed the current work flow.
        # So, we are now listening to a new request state and updating the new post work state.
        t = task_map[state]
        del task_map[state]
        t.reregister_state (new_state, post_state)
        task_map[new_state] = t

    status = 200
    resp = {"status": status, "response": f"received notification for {state}"}

    response = make_response(json.dumps(resp), status)
    response.headers['Content-Type'] = "application/json; charset=utf-8"
    return response


def register_to_tuplespace (port):

    for k,v in task_map.items():
        data = { "id" : f"processor-{os.getpid()}",
                 "state" : k,
                 "host" : "localhost",
                 "port" : port,
                 "endpoint" : f"/worker/processor/notify?state={k}",
                 "url" : f"http://localhost:{port}/worker/processor/notify?state={k}"
                 }
        resp = requests.post (url="http://localhost:5050/tuplespace/api/v1/register", data=data)
        print (f"Registered {k} and got {resp.status_code}")


def reregister_state (current_state, new_req_state, new_post_state):
    #  reregister ("COMPUTE", "COMPUTE-THRESHOLD", "PERSIST")
    data = {
        "current_state": current_state,
        "new_req_state": new_req_state,
        "new_post_state": new_post_state
    }
    resp = request.post(url="http://localhost:5050/tuplespace/api/v1/reregister-state", data=data)

    print(f"Re-registered {current_state} to ({new_req_state}, {new_post_state}) and got {resp.status_code}")


def usage (msg=None,code=0):
    if msg:
        print (msg)

    print ("python3 worker.py [task={NEW|VALIDATE|EMBELLISH|COMPUTE|PERSIST}] [port=N]")
    print ("  run the worker application.  This flask application is an app that receives TupleSpace ")
    print ("  notification after the worker has registered to the space. In principle, each flask app")
    print ("  should house either one or a small number of task workers.  ")
    print ("  When the notification is received, the flask driver looks for the worker task and dispatches the work ")
    print ("to the worker thread")

    sys.exit(code)


def initialize_task_map (tasks):
    if task == "*":
        task_map["NEW"] = ValidateTaskProcessor("NEW", "VALIDATE")
        task_map["VALIDATE"] = EmbellishTaskProcessor("VALIDATE", "EMBELLISH")
        task_map["EMBELLISH"] = ComputeTaskProcessor("EMBELLISH", "COMPUTE")
        task_map["COMPUTE"] = PersistTaskProcessor("COMPUTE", "PERSIST")
    else:
        # demo to show that you can insert a step into the tuple space.
        if task == "COMPUTE_THRESHOLD":
            task_map["NEW"] = ComputeThresholdTaskProcessor("COMPUTE", "COMPUTE-THRESHOLD")

        reregister_state ("COMPUTE", "COMPUTE-THRESHOLD", "PERSIST")

    for k,v in task_map.items():
        v.start()



if __name__ == "__main__":

    try:
        opts, args = getopt.getopt(sys.argv[1:], "ht:p:", ["help", "task=", "port="])

        task = "*"
        port = 5090

        verbose = False
        for o, a in opts:
            if o == "-v":
                verbose = True
            elif o in ("-h", "--help"):
                usage()
                sys.exit()
            elif o in ("-t", "--task"):
                task = a
            elif o in ("-p", "--port"):
                port = int (a)
            else:
                usage (f'unhandled option {o}', 2)

        initialize_task_map(task)

        register_to_tuplespace(port)

        app.run(port=port, debug=True)

    except getopt.GetoptError as err:
        print (str(err))  # will print something like "option -a not recognized"
        usage(2)



