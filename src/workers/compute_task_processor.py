import random
import queue
import os
from datetime import datetime
from tuplespace.taskitem import TaskItem

from workers.abstract_task_processor import AbstractTaskProcessor


class ComputeTaskProcessor(AbstractTaskProcessor):

    def __init__ (self, request_state, post_state):
        super().__init__(request_state, post_state)

    def process(self, task: TaskItem) -> TaskItem:

        print (f'---------------------------------------------------> Processing COMPUTE')

        x = random.randrange (0,1000000)
        n = random.randrange (0,20)
        compute = {"created-by": f"compute proces id {os.getpid()}",
                   "started-at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                   "compute": {"f(x) = (3x+1)": self.three_x_plus_1(x),
                               "f(x) = (fib(n))": self.fib(n)
                                  },
                   "ended-at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                   "status": 'SUCCESS'
                   }

        task.set_state(self.post_state)
        task.add_subtask(self.post_state,compute)

        return task

    def three_x_plus_1 (self, x):
        # all numbers up to 2**60 goes to 1
        c = 0
        m = 0
        xx = x
        while xx > 1:
            m = xx if xx > m else m

            xx = xx/2 if xx%2 == 0 else 3*xx+1
            c+= 1

        return {"x" : x, "max" : m, "iterations" : c}

    def fib(self, n):

        if n < 0:
            result = { "n" : n, "comment": "Invalid n"}
        elif n <= 1:
            result = {"n": n, "result": 1}
        else:
            c,n1,n2 = 0,0,1
            while c < n:
                nth = n1 + n2

                n1 = n2
                n2 = nth
                c += 1
            result = {"n": n, "result" : n2}
        return result

if __name__ == "__main__":
    proc = ComputeTaskProcessor ("a","b")

    print (f"fib(1) = {proc.fib(0)}")
    print (f"fib(1) = {proc.fib(1)}")
    print (f"fib(2) = {proc.fib(2)}")
    print (f"fib(3) = {proc.fib(3)}")
    print (f"fib(4) = {proc.fib(4)}")
    print (f"fib(5) = {proc.fib(5)}")

    print (f"f(10) = 3x+1 = {proc.three_x_plus_1(10)}")
    print (f"f(11) = 3x+1 = {proc.three_x_plus_1(11)}")
    print (f"f(12) = 3x+1 = {proc.three_x_plus_1(12)}")
    print (f"f(17) = 3x+1 = {proc.three_x_plus_1(17)}")