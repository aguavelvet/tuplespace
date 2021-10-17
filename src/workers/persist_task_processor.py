import os
import uuid
import json
from datetime import datetime
from tuplespace.taskitem import TaskItem
from pymongo import MongoClient
from bson import ObjectId

from workers.abstract_task_processor import AbstractTaskProcessor


class PersistTaskProcessor(AbstractTaskProcessor):

    def __init__ (self, request_state, post_state):
        super().__init__(request_state, post_state)

        self.client = MongoClient('localhost', 27017)
        self.tuplespace = self.client['tuplespace']
        self.tasks = self.tuplespace['tasks']

    def process(self, task: TaskItem) -> TaskItem:

        print (f'---------------------------------------------------> Processing PERSIST')

        objId = ObjectId()

        persist = {"created-by": f"persist proces id {os.getpid()}",
                   "started-at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                   "collection" : "tuplespace.tasks",
                   "persisted": { "_id" : str(objId) },
                   "status": 'SUCCESS'
                   }
        task.set_state(self.post_state)
        task.add_subtask(self.post_state, persist)

        dbrec = json.loads(task.toJSON())
        dbrec['_id'] = objId

        rec = self.tasks.insert_one(dbrec)

        persist["ended-at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return task

