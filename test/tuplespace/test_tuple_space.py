
import json
import pytest
from datetime import datetime


from tuplespace.tuplespace import TupleSpace
from tuplespace.taskitem import TaskItem

class TestTupleSpace:

    states = ["NEW", "VALIDATE", "EMBELLISH", "COMPUTE", "PERSIST"]
    space = TupleSpace(states)

    @pytest.mark.order(1)
    def test_write(self):
        with open("./c360.person.json") as f:
            muppets = json.load(f)

        for muppet in muppets:
            task = TaskItem(muppet)
            self.space.write(task)
            print (f"Wrote:{task}")

        tasks = self.space.get_all('NEW')
        ids = { t.get_id(): '' for t in tasks }

        assert len(tasks) == 9
        assert len(tasks) == len(muppets)
        assert len(ids) == 9

    @pytest.mark.order(2)
    def test_read(self):
        task = TaskItem({'state': 'NEW'})
        item = self.space.read(task)

        print(item.to_string())

        assert item
        assert item.get_state() == 'NEW'


    @pytest.mark.order(3)
    def test_check_out(self):
        task = TaskItem({'status': 'NEW'})
        item = self.space.check_out(task)

        assert item.payload['workspace.task.checked.out.by'] == "NEW"

    @pytest.mark.order(4)
    def test_check_out_check_in_validate(self):

        validated = [
            {  "created-by": "validator processor 123",
               "started-at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
               "validation": { "validation-1": "Sunny day",
                               "validation-2": "Sweeping the clouds away ...."  },
               "status": "SUCCESS"
               },
            { "created-by": "vaiidator processor 456",
                "started-at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "validation": { "validation-1": "On my way",
                                "validation-2": "to where the air is sweet ...."  },
                "status": "SUCCESS"
              },
            { "created-by": "validator-processor 789",
                "started-at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "validation": { "validation-1": "can you tell me how to get",
                                "validation-2": "how to get to ...." },
                "status": "SUCCESS"
              }
        ]

        for v in validated:
            task = TaskItem({'state': 'NEW'})
            item = self.space.check_out(task)
            item.add_subtask('VALIDATE', v)
            item = self.space.check_in ('VALIDATE',item)

        new_tasks = self.space.get_all("NEW")
        validate_tasks = self.space.get_all("VALIDATE")

        assert len(new_tasks) == 6
        assert len(validate_tasks) == 3

        assert validate_tasks[0].get_state () == 'VALIDATE'
        assert len(validate_tasks[0].get_subtasks()) == 1
        assert len(validate_tasks[1].get_subtasks()) == 1
        assert len(validate_tasks[2].get_subtasks()) == 1

    @pytest.mark.order(5)
    def test_check_out_check_in_embellished(self):

        embellished = [
            {  "created-by": "embelish processor abc",
               "started-at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
               "validation": { "embellished-1": "aaaaaaaaaaaa",
                               "embellished-2": "bbbbbbbbbbbbbbbbbb ...."  },
               "status": 'SUCCESS'
               },
            { "created-by": "embellish processor def",
                "started-at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "validation": { "embellished-1": "You wouldn't believe what I've seen",
                                "embellished-2": "with your eyes ....",
                                "embellished-3": "I've stood on the back deck of a blinker bound for the Plutition Camps",
                                "embellished-4": " with sweat in my eyes watching stars fight on the shoulder of Orion.."
                                },
                "status": 'SUCCESS'
              }
        ]

        for e in embellished:
            item = self.space.check_out(TaskItem({'state': 'VALIDATE'}))
            item.add_subtask('EMBELLISH', e)
            item = self.space.check_in ('EMBELLISH',item)

        new_tasks = self.space.get_all("NEW")
        validate_tasks = self.space.get_all("VALIDATE")
        embellished = self.space.get_all("EMBELLISH")

        assert len(new_tasks) == 6
        assert len(validate_tasks) == 1
        assert len(embellished) == 2

        assert embellished[0].get_state () == 'EMBELLISH'
        assert len(embellished[0].get_subtasks()) == 2
        assert len(embellished[1].get_subtasks()) == 2


    @pytest.mark.order(6)
    def test_check_out_check_in_to_completion(self):

        compute = {  "created-by": "compute processor 123",
                     "started-at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                     "compute": { "compute": "3x+1","response": "1234 ...."  },
                     "status" : "SUCCESS"}
        persist =  { "created-by": "mongo write processor",
                     "started-at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                     "persisted": { "database": "mongodb",
                                    "url":"localhost:27017",
                                    "user":"admin",
                                    "password" : "******",
                                    "collection": "ent_master.customer",
                                    "key" : "xyz-123"},
                     "status": "SUCCESS" }

        item = self.space.check_out(TaskItem({'state': 'EMBELLISH'}))
        item.add_subtask('COMPUTE', compute)
        item = self.space.check_in ('COMPUTE',item)

        item = self.space.check_out(TaskItem({'state': 'COMPUTE'}))
        item.add_subtask('PERSIST', persist)
        item = self.space.check_in ('PERSIST',item)

        new_tasks = self.space.get_all("NEW")
        validate_tasks = self.space.get_all("VALIDATE")
        embellished = self.space.get_all("EMBELLISH")
        computed = self.space.get_all("COMPUTE")
        persisted = self.space.get_all("PERSIST")
        completed = self.space.get_all("COMPLETE")

        assert len(new_tasks) == 6
        assert len(validate_tasks) == 1
        assert len(embellished) == 1
        assert len(computed) == 0
        assert len(persisted) == 0
        assert len(completed) == 0

        assert embellished[0].get_state () == 'EMBELLISH'
        assert len(embellished[0].get_subtasks()) == 2



