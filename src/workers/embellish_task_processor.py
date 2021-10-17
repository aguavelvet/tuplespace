import os
from datetime import datetime
from tuplespace.taskitem import TaskItem

from workers.abstract_task_processor import AbstractTaskProcessor


class EmbellishTaskProcessor(AbstractTaskProcessor):

    def __init__ (self, request_state, post_state):
        super().__init__(request_state, post_state)

    def process(self, task: TaskItem) -> TaskItem:
        print (f'---------------------------------------------------> Processing EMBELLISH')

        emblish = {"created-by": f"embellish proces id {os.getpid()}",
                   "started-at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                   "validation": {"embellished-1": "You wouldn't believe what I've seen",
                        "embellished-2": "with your eyes ....",
                        "embellished-3": "I've stood on the back deck of a blinker bound for the Plutition Camps",
                        "embellished-4": " with sweat in my eyes watching stars fight on the shoulder of Orion.."
                   },
                   "ended-at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                   "status": 'SUCCESS'
         }

        task.set_state(self.post_state)
        task.add_subtask(self.post_state, emblish)

        return task