import threading
import re
import json
import http.client
from tuplespace.taskitem import TaskItem

class ReregistrationWorker(threading.Thread):

    def __init__(self, notification_workers,  new_req_state, new_post_state):
        threading.Thread.__init__(self)
        self.debug = False
        self.notification_workers = notification_workers
        self.new_req_state = new_req_state
        self.new_post_state = new_post_state
        self.status = 200

    def get_status (self):
        return self.status

    def run(self):

        print (f"-------------------------> running re-registration thread:  {self.new_req_state}")
        w = None
        try:
            # suppose we have the following states:
            #  new --> validate --> embellish --> compute --> persist   and we go to
            #  new --> validate --> embellish --> compute --> threshold --> persist
            # Then, we need to tell compute is going to thresold and we need to tell persist that we're accepting
            # perist as the state
            for worker in self.notification_workers:
                w = worker
                if self.debug:
                    print(f'notifying {worker["id"]} {worker["state"]} --> {worker["host"]} {worker["port"]} {worker["endpoint"]} ')
                else:
                    conn = http.client.HTTPConnection(worker['host'],worker['port'],timeout=300)

                    endpt = f"{worker['endpoint']}&new_req_state={self.new_req_state}&new_post_state={self.new_post_state}"
                    conn.request("GET", endpt)
                    resp = conn.getresponse()

                    if resp.status == 200:
                        x = re.sub("state=.*$", f"state={self.new_req_state}", worker['endpoint'])
                        worker['state'] = self.new_req_state
                        worker['post_state'] = self.new_post_state
                        worker['endpoint'] = x

                        print (f" ----------. reregistration: {json.dumps(worker,indent=4)}")

                    else:
                        self.status = resp.status
                        break

        except Exception as ex:
            print (f"Caught {ex} on {json.dumps(w, indent=4)}")

        w = None
