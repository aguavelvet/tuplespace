import threading

import http.client
from tuplespace.taskitem import TaskItem

class NotificationWorker(threading.Thread):

    def __init__(self, ts, threadId, name, debug=False):
        threading.Thread.__init__(self)
        self.thread_id = threadId
        self.thread_name = name
        self.tuple_space = ts
        self.debug = debug

    def run(self):

        print (f"-------------------------> running notification thread {self.thread_name}")
        while True:
            w = None
            try:
                task = self.tuple_space.notification_queue.get()

                notifiers = self.tuple_space.registry[task.get_state()]
                if notifiers:
                    for n in notifiers:
                        w = n
                        if self.debug:
                            print(f'notifying {n["id"]} {n["state"]} --> {n["host"]} {n["port"]} {n["endpoint"]} ')
                        else:
                            conn = http.client.HTTPConnection(n['host'],n['port'],timeout=300)
                            conn.request("GET", n['endpoint'])
                            resp = conn.getresponse()

                            print(f'notifying {n["id"]} {n["state"]} --> {n["host"]} {n["port"]} {n["endpoint"]} returned {resp.status}')

            except Exception as ex:
                print (f'Caught {ex} notifying {w["id"]} {w["state"]} --> {w["host"]} {w["port"]} {w["endpoint"]} ')
