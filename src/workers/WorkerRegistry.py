import uuid

class WorkerRegistry:

    workers = {}

    @staticmethod
    def register (worker: dict) -> str:
        if "id" in worker:
            id = worker["id"];
        else:
            id = uuid.uuid4();

        if id in WorkerRegistry.workers:
            raise RuntimeError ("Can not reigster worker {} exists ", id)

        WorkerRegistry.workers[id] = worker

        return id











