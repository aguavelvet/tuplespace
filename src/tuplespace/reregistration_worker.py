import threading

import http.client
from tuplespace.taskitem import TaskItem

class ReregistrationWorker(threading.Thread):

    def __init__(self, notification_workers, new_req_state, new_post_state):
        threading.Thread.__init__(self)
        self.debug = False
        self.notification_workers = notification_workers
        self.new_req_state = new_req_state
        self.new_post_state = new_post_state

    def run(self):

        print (f"-------------------------> running re-registration thread {self.thread_name}")
        try:

            for n in self.notification_workers:
                if self.debug:
                    print(f'notifying {n["id"]} {n["state"]} --> {n["host"]} {n["port"]} {n["endpoint"]} ')
                else:
                    conn = http.client.HTTPConnection(n['host'],n['port'],timeout=5)
                    conn.request("GET", f"{n['endpoint']}&new_req_state={self.new_req_state}&new_post_state={self.new_post_state}")
                    resp = conn.getresponse()

                    print(f'notifying {n["id"]} {n["state"]} --> {n["host"]} {n["port"]} {n["endpoint"]} returned {resp.status}')
        except Exception as ex:
            print (f"Caught {ex}")
