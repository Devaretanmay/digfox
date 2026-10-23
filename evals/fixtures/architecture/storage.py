import json
import sqlite3


class ReportStore:
    def __init__(self, database_path):
        self.connection = sqlite3.connect(database_path)
        self.connection.execute("CREATE TABLE IF NOT EXISTS reports (id TEXT PRIMARY KEY, body TEXT)")

    def save(self, report):
        self.connection.execute(
            "INSERT INTO reports (id, body) VALUES (?, ?)",
            (report["id"], json.dumps(report)),
        )
        self.connection.commit()
