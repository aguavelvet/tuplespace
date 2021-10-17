import json
import http.client
import time
from tuplespace.taskitem import TaskItem

if __name__ == "__main__":
    with open("../../test/tuplespace/c360.person.json") as f:
        muppets = json.load(f)

        headers = {'Content-type': 'application/json'}

        conn = http.client.HTTPConnection("localhost:5050", timeout=300)
        for m in muppets:

            taskitem = TaskItem(m);
            conn.request("POST", "/tuplespace/api/v1/new", taskitem.toJSON(), headers)

            resp = conn.getresponse()

            print (f" Status = {resp.status} on POST")

            time.sleep (2)





