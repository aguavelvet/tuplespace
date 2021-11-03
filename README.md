# HashMap based Tuple Space



Tuple space (David Gelernter, Nicholas Carriero, Yale) was introduced some 35-40 years ago as a central concept in the distributed computing as the associative memory model.  Tuplespace was initially implemented in Linda and gained traction over time was implemented in Java as JavaSpace. 

However, JavaSpace was built on top of JINI infrastructure and the failure of JINI in the industry has also meant a slow decline of JavaSpace in the industry.  Nevertheless, Tuple Space remains to be an exceptionally simple idea that has many benefits.



## TupleSpace

If one thinks of TupleSpace implmentation as nothing more than HashMap of Items availiable across a network, we are 90% there.  Additionally, there are listeners (often refered to as workers) who are interested in knowing about the task inside the TupleSpace 

The operations are:

### Operations

| Operations       | Description                                                  |
| ---------------- | ------------------------------------------------------------ |
| Put              | Put an Item into the TupleSpace.                             |
| Take             | Take an item.  Take does not remove the Item from the space, although it is no longer available to be "read" by other processes. |
| Remove           | Remove the item from the tuple space.                        |
| Register Listner | Register a listener to the TupleSpace                        |
| Notify Listener  | When an item is inserted into TupleSpace, the associated listener is notified. |

 

[Diagram 1]

![Tuple Space](./tuplespace.png/Users/kikim/Desktop/Screen Sho)



##### Diagram 1 depicts how a tuple space could potentially be used. 

### Input

Input can come from multiple sources.  Typically, we can imagine inputs coming from one or more of Messaging Queue, Http Client or any other applications. 

### Workers

Workers are processes that typically that computes some specific tasks.  If you consider it a micro-service, it would not be wrong.  That is to say, it performs a very specific "simple" tasks.

In this example, states are assgined to the Tasks and each workers are registered for a specific state notification.  For example, we could imagine the work flow to be a set of state transisitions say of [NEW, VALIDATE, EMBELLISH, COMPUTE, PERSIST].  

### Items

We are not bound to define only one state transitions:  There may be multiple Task Items implementations.  Suppose we have the following types of Task Items:

```
Task
    Person       --> [State-A, State-B, State-C, State-D]
    Organization --> [State-A, State-E, State-F, State-G, State-H]
    Hierarchy    --> [State-B, State-D, State-I, ...]
```

We see that we can provide state transitions easily enough perhaps even sharing some common states.  The states are tightely coupled to the type of task we have.  





## Benefits

Why would be consider using TupleSpace?  Ultimately, the author believes Tuple Space offers the following benefits.

### Simplicity

The system consists of an aggregations of simple isolated tasks.  Hence, each tasks are easy to understand, code, debug, and maintain.  Moreover, since these tasks are isolated, perturbation of any one area of code does not impact another area.  Or to put it in another way, you really have to work hard to make another part of the application fail.

### Flexibility

Aside from the core TupleSpace, addition/update/delete of states is easy to accomplish.  Suppose we have the following work flow [NEW, VALIDATE, EMBELLISH, COMPUTE, PERSIST].    We can imagine the following modifications:

#### State Addition

The new state is [NEW, VALIDATE, EMBELLISH,**MERGE**, COMPUTE, PERSIST]. 

The steps to adding the additional states are:

* **author** the new step and register with the tuple space.
* dynamically **inject** the new state into  tuplespace.  Any task that has not Finished the EMBELLISH state will automatically pick up the MERGE worker.

By extension, we see that we also have a very easy way to Peek into the data structure at any point in the work flow.  That is, inject a PEEK state into the work flow to see what the data looks like.

#### Dynamic Application Update

Could we update a running PRODUCTION system?  under simple cases we can.   Suppose one of the workers were found to have a bug.  We can dynamically update the worker.

1. Inject the fixed worker into the TupleSpace registry.
2. One by one, kill off the Buggy Workers.



#### TupleSpace chaining

As seen in the diagram, there is no reason why we can not define a worker that allows for Tuple Spaces to be chained. Two scenarios are:

* High Availability
* Fault Tolerance
* Off loading non critical tasks to slower/cheaper hardware

#### Replay

If any of the workers generates a FAIL status, the task is taken out of the TupleSpace (This is more a policy based decision) and put into the failed queue(DB/File etc)

These failed tasks can be replayed from the previous state from failure.

#### TestCase Generation

All failed test cases can be easily converted into test cases.   Simply take the failed task and add to the test suite (DB/FlatFile etc)

### Scalability

Scalability is a key concept that is baked into this design pattern.  This pattern allows us to hook into HPA in Kubernetes as well as amazon auto scaling:

Since all the components (TupleSpace and workers) are built as docker containers, we can use both Kubernetes HPA and Amazon Auto scaling to add/remove additional components.



## Short Commings

### Large Data 

TupleSpace does not do well, if the payload is large for obvious reasons. There are ways to mitigate the large memory requirement, but in general,  TS is not suitable for large payload work flow.

### Data Dependencies

If there are lots of data depencies, tuple space may not be a good solution. For example, if each task needs to make multiple database calls, it may not be the right solution to use.

### Generates lots of IPC

TupleSpace performs lots of Interprocess communications.  The amount of IPC depends on the size of the payload as well as the number of steps.

### Flexibility VS Tricky Code

TupleSpace offers many benefits that are attractive for many solution space.  The cost comes in the form of tricky control flow.  For the novices, it may take a bit of familiarization to understand the control flow.

### Failure Step haults the entire work flow

This issue seems a lot more critical than it is, when compared to say a monolithic application.  If there is a work flow step that fails, all processing will stop at the point of failure.  We can replay from the failure point, once the fix has been made.







# Implementation

This TupleSpace implementation is very basic in that:

* Based on python Dictionary.
* Some efforts were made to find an implementation including a JavaSpace solution.  Very little work has been done with tuple space in the past 10 years.
  * GigaSpace. Commercial.  So did not pursue further.
  * Apache-Camel. 
* Based on HTTP.  

Supporting AWS SQS would be a good task to pursue next 



## Development Environment

See: https://github.com/aguavelvet/tuplespace

### Steps:

```
git clone https://github.com/aguavelvet/tuplespace.git
cd tuplespace
python3 -m venv venv
pip install -r requirements.txt
```



### Run:

tuplespace flask app:

```
cd tuplespace/src
python3 http_ts.py
```

Workers app:

```py
cd tuplespace/src
python3 worker.py
```

Note: pymongo install requires sudo



## Adding additional Tasks

There are three steps in creating an additional Task:

1.  code. For this task, please subclass AbstractTaskProcessor and implement the process method.
2. Determine what step you need to inject the task in and ensure that the work flow step is correct.
3. Create a worker flask instance that instantiates and registers the task to tuplespace.

### Step by Step

Suppose we wish to add the task step called Peek.  This task will be inserted into the work flow so we can peek at the state of the task.

#### Code

```python
class Peek(AbstractTaskProcessor):

    def __init__ (self, request_state, post_state):
        super().__init__(request_state, post_state)

    def process(self, task: TaskItem) -> TaskItem:
        ''' just dump to standard out'''
        print (task);
        return task

```

### Where?

We want to insert this task just before PERSIST.

#### Worker Flask

Please take a look at the worker.py file.  This is the template worker class.  In this class, we want to instantiate  the new class and register it to the tuplespace.

To perform this task, all we need to do is update the ``` initialize_task_map``` method:

```
def initialize_task_map (tasks):
    # demo to show that you can insert a step into the tuple space.
    # 1.  This worker only deals with Peek.
    # 2.  Register this worker with the tuple-space.
    #     TupleSpace already has Persist registered against COMPUTE
    #     Tell  TupleSpace that After Compute, we need to Peek.
    #     Tuple space then will notify the current existing PersistTask to listen to
    #     PEEK instead of COMPUTE.
    # 3.  At this point, no one is listening to COMPUTE.  
    #     Start the Peek listening thread
    reregister_state ("COMPUTE", "PEEK", "PERSIST")
    task_map["COMPUTE"] = Peek("COMPUTE", "PEEK")

		#  start the thread
    for k,v in task_map.items():
        v.start()

```

And we are done!





## Next Steps

* Add SQS
* Add additional tasks
* Code clean up and Load Test
* Hook in Buddha's hand for more nifty functional programming.