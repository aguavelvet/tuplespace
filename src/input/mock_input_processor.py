import http.client
import time
from  tuplespace.taskitem import TaskItem

def generate_task (i):

    template = { "workspace": "PROTO-1",
                 "type": "import",
                 "business-entity": "c360.person",
                 "firstName": f"first-{i}",
                 "lastName": f"last name - {i}",
                 "fullName": f"first-{i} last name - {i}",
                 "title": "Mr",
                 "gender": { "Code": "M" if i%2 == 1 else "F", "Name": "Male" if i%2 == 0 else "Female"},
                 "maritalStatus": {"Code": "Single", "Name": "Single"}
               }

    return TaskItem(template,'NEW')


if __name__ == "__main__":

    headers = {'Content-type': 'application/json'}
    conn = http.client.HTTPConnection("localhost:5050", timeout=300)

    for i in range(1,100):

        taskitem = generate_task (i)
        conn.request("POST", "/tuplespace/api/v1/new", taskitem.toJSON(), headers)

        resp = conn.getresponse()

        print (f" Status = {resp.status} on POST")

        time.sleep (1)

