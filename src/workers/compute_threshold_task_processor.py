import os
from datetime import datetime
from tuplespace.taskitem import TaskItem

from workers.abstract_task_processor import AbstractTaskProcessor


class ComputeThresholdTaskProcessor(AbstractTaskProcessor):

    def __init__ (self, request_state, post_state):
        super().__init__(request_state, post_state)

    def process(self, task: TaskItem) -> TaskItem:
        '''
        This task filters the result of the previously computed step by determining if max value obtained in
        the processing has breached 5,000,000.  If it has, it fails this task.
        :param task:
        :return:
        '''
        print (f'---------------------------------------------------> Processing COMPUTE THRESHOLD')

        max = self.get_max_value (task)

        threshold = {"created-by": f"compute filter pid-{os.getpid()}",
                     "started-at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                     "computeFilter": { "max value" : max,
                                        "max breach" : "true" if max > 5000000 else "false",
                      },
                     "ended-at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                     "status": "FAIL" if max > 5000000 else "SUCCESS"
         }

        task.set_state(self.post_state)
        task.add_subtask(self.post_state, threshold)

        return task

    def get_max_value (self, task: TaskItem):
        for s in task.subtasks:
            if s['workspace.subtask.state'] == "COMPUTE":
                max = s['compute']['f(x) = (3x+1)']['max']
                break

        return int(max)


if __name__ == "__main__":
    proc = ComputeThresholdTaskProcessor ("a","b")

    subtasks = [
        {
        "created-by": "validator pid87054",
        "started-at": "2021-10-16 19:28:55",
        "validation": {
            "validation-1": "Sunny day",
            "validation-2": "Sweeping the clouds away ...."
        },
        "status": "SUCCESS",
        "workspace.subtask.state": "VALIDATE",
        "workspace.subtask.createdAt": "2021-10-16 19:28:55"
        },
        {
        "created-by": "embellish proces id 87054",
        "started-at": "2021-10-16 19:28:55",
        "validation": { "embellished-1": "You wouldn't believe what I've seen",
                        "embellished-2": "with your eyes ....",
                        "embellished-3": "I've stood on the back deck of a blinker bound for the Plutition Camps",
                        "embellished-4": " with sweat in my eyes watching stars fight on the shoulder of Orion.."
                        },
        "status": "SUCCESS",
        "workspace.subtask.state": "EMBELLISH",
        "workspace.subtask.createdAt": "2021-10-16 19:28:55"
        },
        {
        "created-by": "compute proces id 87054",
        "started-at": "2021-10-16 19:28:55",
        "compute": { "f(x) = (3x+1)": {
            "x": 1.0,
            "max": 4928932.0,
            "iterations": 102
        },
        "f(x) = (fib(n))": {
            "n": 0,
            "result": 1
        }
        },
        "status": "SUCCESS",
        "workspace.subtask.state": "COMPUTE",
        "workspace.subtask.createdAt": "2021-10-16 19:28:55"
        },
        {
        "created-by": "persist proces id 87054",
        "started-at": "2021-10-16 19:28:55",
        "collection": "tuplespace.tasks",
        "persisted": {
        "_id": "616b60370f3af477f08528fb"
        },

        "status": "SUCCESS",
        "workspace.subtask.state": "PERSIST",
        "workspace.subtask.createdAt": "2021-10-16 19:28:55"
        }
    ]

    payload = {
            "workspace": "PROTO-1",
            "type": "import",
            "business-entity": "c360.person",
            "firstName": "kermit",
            "lastName": "frog",
            "fullName": "Kermit the Frog",
            "title": "Mr",
            "gender": {
                "Code": "M",
                "Name": "Male"
            },
            "maritalStatus": {
                "Code": "Single",
                "Name": "Single"
            },
            "workspace.task.id": "aacab7de-1604-419e-a711-49c8abfd5ed1",
            "workspace.task.createdAt": "2021-10-16 19:28:55",
            "workspace.task.checked.out": "false"
        }


    task = TaskItem (payload)
    task.subtasks = subtasks

    proc.process(task)

    assert task.get_status () == 'SUCCESS'

    task.subtasks[2]['compute']['f(x) = (3x+1)']['max'] = 5000001
    proc.process(task)
    assert task.get_status () == 'FAIL'

