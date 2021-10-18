import os
import queue

from tuplespace.taskitem import TaskItem
from tuplespace.json_task_completion_handler import JsonTaskCompletionHandler
from tuplespace.notification_worker import NotificationWorker
from tuplespace.reregistration_worker import ReregistrationWorker

class TupleSpace:
    '''
    Hashmap based tuple space.
      -- new write() to tuple space.
      -- state tasks are checked in and out.
      -- when the last state is reached, the task is removed from the tuplespace and persisted to completion handler.
      -- On error, the task is removed to error handler.
      -- On check out the task is no longer available for consumption.
      -- On check in, the subsequent state workers are notified.

    Additional Concepts to be added:
      -- states are not hard coded.
         Hence, we should be able to update the available states dynamically.
         - When a task arrives to the tuplespace, the states list is assigned to the task.  Then, per task basis,
           we know what the next state is and it can move on.
         To change the work flow:
           - make sure that the taks worker is registered.
           -
    '''

    def __init__ (self, states: list):

        self.spacemap = {}
        self.registry = {}
        self.states = states
        self.complete_handler = JsonTaskCompletionHandler (os.path.join (os.getcwd(),"completed.tasks.json"))
        self.error_handler = JsonTaskCompletionHandler (os.path.join (os.getcwd(),"error.tasks.json"))
        self.LAST_STATE = states[-1]

        self.notification_queue = queue.Queue(10000)

        self.notification_worker = NotificationWorker (self, "tuplespace.notification.worker-1", "Thread Worker")
        self.notification_worker.start()

    def register (self, id:str, state:str,post_state:str,  host:str, port:str, endpoint:str):
        if state not in self.registry:
            self.registry[state] = []

        self.registry[state].append ({ "id" : id, "state" : state, "post_state": post_state,
                                       "host" : host, "port": int(port), "endpoint":endpoint })

    def reregister (self, current_state:str, new_req_state:str, new_post_state:str):

        workers = self.registry[current_state]

        register_worker = ReregistrationWorker (workers, new_req_state, new_post_state)
        register_worker.run()

        if register_worker.get_status() == 200:
            if current_state != new_req_state:
                del self.registry[current_state]
                self.registry[new_req_state] = workers

            for worker in workers:
                worker['state'] = new_req_state
                worker['post_state'] = new_post_state

    def write (self, task:TaskItem) -> TaskItem:
        self.spacemap[task.get_id()] = task
        self.notify(task)
        return task

    def read (self, task: TaskItem) -> TaskItem:
        found = None
        id = task.get_id()
        if id is not None:
            if id in self.spacemap:
                found = self.spacemap[id]

        if not found:
            state = task.get_state()
            if state:
                found = self.find(state)

        return found

    def check_out (self, task:TaskItem) -> TaskItem:

        item = self.read(task)

        # TODO need to ensure that the lease is set for a certain period of time
        if item:
            item.set_checked_out_by(task.get_state())

        return item

    def check_in (self, task:TaskItem) -> TaskItem:

        if task.get_status() != "SUCCESS":
            self.error_handler.handle(task)
        else:

            item = self.read(task)
            if item is None:
                raise RuntimeError(f"Could not find task {task.get_id()}")

            self.spacemap[task.get_id()] = task

            if self.LAST_STATE == task.get_state():
                self.complete_handler.handle (task)
                del self.spacemap[task.get_id()]
            else:
                self.notify (task)

            print (f"-----------------------------------------> checked in {task.get_state()}:{task.get_id()}")

        return task

    def take (self, task:TaskItem) -> TaskItem:

        item = None
        if task.get_id() in self.spacemap:
            item = self.spacemap[item.get_id()]

        return item

    def get_all (self, state:str) :
        return  list(filter(lambda t: t.get_state() == state, list(self.spacemap.values())))

    def get_all (self) :
        return  list(self.spacemap.values())

    def find (self, state:str) -> TaskItem:

        for task in self.spacemap.values():
            if task.get_state() == state:
                return task

        return None

    def notify (self, task:TaskItem):
        self.notification_queue.put(task)


