import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError

load_dotenv()


class MemoryCollection:
    def __init__(self) -> None:
        self.rows: List[Dict[str, Any]] = []

    def create_index(self, *_args: Any, **_kwargs: Any) -> None:
        return None

    def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        for row in self.rows:
            if all(row.get(key) == value for key, value in query.items()):
                return row
        return None

    def insert_one(self, document: Dict[str, Any]):
        document = dict(document)
        document.setdefault("_id", str(len(self.rows) + 1))
        document.setdefault("created_at", datetime.utcnow())
        self.rows.append(document)

        class Result:
            inserted_id = document["_id"]

        return Result()

    def find(self, query: Dict[str, Any]):
        matched = [
            row for row in self.rows
            if all(row.get(key) == value for key, value in query.items())
        ]
        return MemoryCursor(matched)


class MemoryCursor:
    def __init__(self, rows: List[Dict[str, Any]]) -> None:
        self.rows = rows

    def sort(self, key: str, direction: int):
        reverse = direction < 0
        self.rows.sort(key=lambda row: row.get(key, datetime.min), reverse=reverse)
        return self

    def __iter__(self):
        return iter(self.rows)


class Database:
    def __init__(self) -> None:
        self.using_memory = False
        self.users: Any = MemoryCollection()
        self.analyses: Any = MemoryCollection()
        self._connect()

    def _connect(self) -> None:
        uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        db_name = os.getenv("DATABASE_NAME", "ai_resume_analyzer")
        try:
            client = MongoClient(uri, serverSelectionTimeoutMS=1200)
            client.admin.command("ping")
            db = client[db_name]
            self.users = db["users"]
            self.analyses = db["analyses"]
            self.users.create_index("email", unique=True)
            self.analyses.create_index("user_email")
        except (PyMongoError, ServerSelectionTimeoutError):
            self.using_memory = True


database = Database()

