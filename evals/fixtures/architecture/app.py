from jobs import JobQueue
from storage import ReportStore


def submit_report(payload, database_path="reports.db"):
    store = ReportStore(database_path)
    queue = JobQueue()
    queue.enqueue(lambda: store.save(payload))
    queue.drain()
    return payload["id"]
