import os
from datetime import datetime
from tuplespace.taskitem import TaskItem

from workers.abstract_task_processor import AbstractTaskProcessor


class ValidateTaskProcessor(AbstractTaskProcessor):

    def __init__ (self, request_state, post_state):
        super().__init__(request_state, post_state)

    def process(self, task: TaskItem) -> TaskItem:

        print (f'---------------------------------------------------> Processing VALIDATE')

        validated = {"created-by": f"validator pid{os.getpid()}",
                     "started-at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                     "validation": {"validation-1": "Sunny day",
                                    "validation-2": "Sweeping the clouds away ...."
                      },
                     "ended-at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                     "status": "SUCCESS"
         }

        task.set_state(self.post_state)
        task.add_subtask(self.post_state, validated)

        return task
