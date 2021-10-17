
import json
import pytest
from datetime import datetime

from tuplespace.tuplespace import TupleSpace
from tuplespace.taskitem import TaskItem

class TestTupleSpaceRegistry:

    states = ["NEW", "VALIDATE", "EMBELLISH", "COMPUTE", "PERSIST"]
    space = TupleSpace(states)

    @pytest.mark.order(1)
    def test_register(self):

        self.space.register('NEW',        'NEW',       'http://localhost/new/processor:8090')
        self.space.register('VALIDATE-1', 'VALIDATE',  'http://localhost/validate/processor:8090')
        self.space.register('VALIDATE-2', 'VALIDATE',  'http://localhost/validate/processor:8090')
        self.space.register('EMBELLISH-1', 'EMBELLISH', 'http://localhost/embelish/processor:8090')
        self.space.register('EMBELLISH-2', 'EMBELLISH', 'http://localhost/embelish/processor:8090')
        self.space.register('COMPUTE-1',   'COMPUTE',   'http://localhost/compute/processor:8095')
        self.space.register('COMPUTE-2',   'COMPUTE',   'http://localhost/compute/processor:8095')
        self.space.register('PERSIST-1',   'PERSIST',   'http://localhost/persist/processor:8095')
        self.space.register('PERSIST-2',   'PERSIST',   'http://localhost/persist/processor:8095')
        self.space.register('PERSIST-3',   'PERSIST',   'http://localhost/persist/processor:8095')

        assert len(self.space.registry) == 5
        assert len(self.space.registry['PERSIST']) == 3


    @pytest.mark.order(2)
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

    @pytest.mark.order(3)
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

