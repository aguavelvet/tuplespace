import json
from tuplespace.taskitem import TaskItem

class JsonTaskCompletionHandler:

    def __init__(self, filepath):
        self.file = open(filepath, 'w+')

    def handle(self, t: TaskItem):
        self.file.write(t.toJSON()+"\n")
        self.file.flush()
