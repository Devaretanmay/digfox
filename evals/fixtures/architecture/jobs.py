class JobQueue:
    def __init__(self):
        self._pending = []

    def enqueue(self, job):
        self._pending.append(job)

    def drain(self):
        while self._pending:
            self._pending.pop(0)()
