import json
import uuid
import os
import ssl

from flask import Flask
from flask import request
from flask import make_response
from datetime import datetime, timedelta

from tuplespace.tuplespace import TupleSpace
from tuplespace.tuplespace import TaskItem

path = os.path.dirname(__file__)
app  = Flask(__name__)

tuplespace = TupleSpace (["NEW", "VALIDATE", "EMBELLISH", "COMPUTE", "PERSIST"])


@app.route('/tuplespace/api/v1/register', methods=['POST'])
def register_worker():
    rqst = request
    status = 400
    resp = {"status": status, "response": "sunny day..."}

    id = rqst.form['id']
    state = rqst.form['state']
    host = rqst.form['host']
    port = rqst.form['port']
    endpt = rqst.form['endpoint']

    if id is None or state is None or host is None or port is None or endpt is None:
        resp["response"] = "Invalid request. Missing one of id, state and/or url"
    else:
        try:
            tuplespace.register(id, state, host,port,endpt)

            status  = 200
            resp["status"] = status
            resp["message"] = ""


        except Exception as ex:
            resp["message"] = str(ex)

    response = make_response(json.dumps(resp), status)
    response.headers['Content-Type'] = "application/json; charset=utf-8"

    return response


@app.route('/tuplespace/api/v1/reregister-state', methods=['POST'])
def register_worker_state():
    rqst = request
    status = 400
    resp = {"status": status, "response": ""}

    current_state  = rqst.form['current_state']
    new_req_state  = rqst.form['new_req_state']
    new_post_state = rqst.form['new_post_state']

    try:
        tuplespace.reregister(current_state, new_req_state, new_post_state)

        status  = 200
        resp["status"] = status
        resp["message"] = f"reregistered {current_state} to ({new_req_state},{new_post_state})"


    except Exception as ex:
        resp["message"] = str(ex)

    response = make_response(json.dumps(resp), status)
    response.headers['Content-Type'] = "application/json; charset=utf-8"

    return response


@app.route('/tuplespace/api/v1/new', methods=['POST'])
def new_task():
    rqst = request
    status = 400
    resp = {"status": status, "response": "oh oh..."}

    body = rqst.get_json()
    if body is None:
        resp["response"] = "Invalid request. Missing body"
    else:
        try:

            task = tuplespace.write (TaskItem(body,'NEW'))

            status = 200
            resp["status"] = status
            resp["message"] = ""
            resp["id"] = task.get_id()

        except Exception as ex:
            resp["message"] = str(ex)

    response = make_response(json.dumps(resp), status)
    response.headers['Content-Type'] = "application/json; charset=utf-8"

    return response


@app.route('/tuplespace/api/v1/read', methods=['POST'])
def read():
    rqst = request
    status = 400
    resp = {"status": status, "response": "oh oh..."}

    body = rqst.get_json()
    if body is None:
        resp["response"] = "Invalid request. Missing body"
    else:
        try:
            id = tuplespace.read (body)

            status = 200
            resp["status"] = status
            resp["message"] = ""
            resp["id"] = id

        except Exception as ex:
            resp["message"] = str(ex)

    response = make_response(json.dumps(resp), status)
    response.headers['Content-Type'] = "application/json; charset=utf-8"

    return response

@app.route('/tuplespace/api/v1/checkout', methods=['GET'])
def checkout():
    rqst = request
    status = 400
    resp = {"status": status, "response": "oh oh..."}

    if 'state' not in rqst.args:
        resp["response"] = "Invalid request. Missing state"
    else:
        try:
            state = rqst.args['state']

            task = tuplespace.check_out (TaskItem({'state' : state}))

            status = 200
            resp["status"] = status
            resp["state"] = state
            resp["message"] = ""
            if task:
                resp["task"] = task.toJSON()

        except Exception as ex:
            resp["message"] = str(ex)

    response = make_response(json.dumps(resp), status)
    response.headers['Content-Type'] = "application/json; charset=utf-8"

    return response

@app.route('/tuplespace/api/v1/checkin', methods=['POST'])
def checkin():
    rqst = request
    status = 400
    resp = {"status": status, "response": "oh oh..."}

    try:
        payload = rqst.get_json()
        if payload:
            task  = tuplespace.check_in(TaskItem.load(payload))

            status = 200
            resp["status"] = status
            resp["state"] = task.get_state()
            resp["message"] = "checked in"


    except Exception as ex:
        resp["message"] = str(ex)

    response = make_response(json.dumps(resp), status)
    response.headers['Content-Type'] = "application/json; charset=utf-8"

    return response


if __name__ == "__main__":

    port = 5050
    if os.getenv("FLASK_RUN_PORT") is not None:
        port = int(os.getenv("FLASK_RUN_PORT"))

    app.run(port=port,debug=True)

