import uuid
import json
from datetime import datetime


class TaskItem :

    def __init__ (self, payload:{} = {}, state:str="NEW"):

        if 'state' in payload:
            self.state = payload['state']
        else:
            self.state = state

        self.status = 'SUCCESS'

        self.payload = self.get_payload (payload)
        self.payload['workspace.task.id'] = str(uuid.uuid4())
        self.payload['workspace.task.createdAt'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if 'workspace.task.checked.out' not in self.payload:
            self.payload['workspace.task.checked.out'] = False

        self.subtasks = []

    def loads (payload):
        task = TaskItem({'state' : 'NEW'})

        item = json.loads(payload)

        task.state = item['state']
        task.payload = item['payload']
        task.subtasks = item['subtasks']

        return task

    def load (payload):
        task = TaskItem({'state' : 'NEW'})

        task.state = payload['state']
        task.payload = payload['payload']
        task.subtasks = payload['subtasks']

        return task

    def add_subtask (self,state:str, subtask:{}):
        if subtask is not None:
            subtask["workspace.subtask.state"] = state
            subtask["workspace.subtask.createdAt"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            self.subtasks.append (subtask)
            self.set_status(subtask['status'])

    def get_id(self):
        id = None
        if 'workspace.task.id' in self.payload:
            id = self.payload['workspace.task.id']

        return id

    def get_state (self):
        return self.state

    def set_state (self, state):
        self.state = state

    def get_status (self):
        return self.status

    def set_status (self, status):
        self.status = status

    def checked_out (self):
        rc = False

        if 'workspace.task.checked.out' in self.payload:
            rc = self.payload['workspace.task.checked.out']

        return rc in ('1','True','true',1,True)

    def checked_out_by (self):
        rc = None

        if 'workspace.task.checked.out.by' in self.payload:
            rc = self.payload['workspace.task.checked.out.by']

        return rc

    def set_checked_out_by (self, status):
        self.payload['workspace.task.checked.out.by'] = status

    def to_string (self, prettyprint=False):
        buf = ""
        if self.payload is not None:
            buf = json.dumps(self.payload, indent=(4 if prettyprint else 0))

        return buf

    def get_payload (self, payload:{}):

        resp = payload
        keys = list(payload.keys())
        if len(keys) > 0:
            if isinstance(keys[0], (bytes, bytearray)):
                resp = { k.decode('ascii') : payload.get(k).decode('ascii') for k in payload.keys() }

        return resp

    def get_subtasks (self):
        return self.subtasks

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)