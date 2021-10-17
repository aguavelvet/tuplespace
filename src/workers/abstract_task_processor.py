import queue
import json
import threading
import http.client
from tuplespace.taskitem import TaskItem


class AbstractTaskProcessor(threading.Thread):

    task_queue = queue.Queue(1000)

    def __init__ (self, request_state, post_state):
        threading.Thread.__init__(self)
        self.request_state = request_state
        self.post_state = post_state
        self.headers = {'Content-type': 'application/json;charset=UTF-8'}

    def reregister_state (self, request_state, post_state) :
        self.request_state = request_state
        self.post_state = post_state


    def run (self):
        '''
        Abstract task processor is a daemon thread that runs infinitely.  The task blocks on the thread safe
        queue.  When a task is placed in the queue, it wakes up and performs a specific task:  Specifically:
          * wakes up.  Makes a GET call to the task provider to get a task.
          * If the task is available, it gets it and processes it.
          * Once the task is perfored, it returns the task and looks for a subsequent task.
        '''
        while True:
            # queue blocks. If a task is there, it means we have a task to consume.
            state = self.task_queue.get ()

            resp = self.get_task();
            data = str(resp.read().decode())

            if resp.status == 200:
                payload = json.loads(data)
                if "task" in payload:
                    task = self.process(TaskItem.loads(payload['task']))

                    self.put_task(task)
            else:
                print (f"Got {resp.status} while requesting {endpt}")


    def process(self, task: TaskItem) -> TaskItem:
        raise NotImplemented ("process not implemented")
        return None


    def get_task (self):
        host = "localhost"
        port = 5050
        endpt = f"/tuplespace/api/v1/checkout?state={self.request_state}"

        # watch for timeout
        conn = http.client.HTTPConnection(host, port, timeout=300)
        conn.request("GET", endpt)

        return conn.getresponse();

    def put_task (self, task):
        host = "localhost"
        port = 5050

        conn = http.client.HTTPConnection(host, port, timeout=300)
        conn.request("POST", "/tuplespace/api/v1/checkin", task.toJSON(), self.headers)
        resp = conn.getresponse()

        print(resp.read().decode())


