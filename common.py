import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Generator, Optional


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"


@dataclass
class Task:
    id: int
    payload: str
    status: TaskStatus
    created_at: str
    updated_at: str
    worker_id: str = ""


class SqliteQueue:
    def __init__(
        self, db_path: str = "queue.db", timeout: float = 30.0
    ) -> None:
        self.db_path = db_path
        self.timeout = timeout
        self._initialize_schema()

    @contextmanager
    def _connection(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(self.db_path, timeout=self.timeout)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute(f"PRAGMA busy_timeout = {int(self.timeout * 1000)};")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _initialize_schema(self) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    payload TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(
                        status IN ('pending', 'in_progress', 'done')
                    ),
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    worker_id TEXT DEFAULT ''
                );
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_queue_status "
                "ON queue(status);"
            )

    def enqueue(self, payload: str) -> Task:
        now = datetime.now().isoformat(timespec="seconds")
        with self._connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO queue (
                    payload, status, created_at, updated_at, worker_id
                )
                VALUES (?, ?, ?, ?, '');
                """,
                (payload, TaskStatus.PENDING.value, now, now),
            )
            task_id = cursor.lastrowid
            return Task(
                id=task_id,
                payload=payload,
                status=TaskStatus.PENDING,
                created_at=now,
                updated_at=now,
            )

    def enqueue_batch(self, payloads: list[str]) -> list[Task]:
        if not payloads:
            return []
        now = datetime.now().isoformat(timespec="seconds")
        with self._connection() as conn:
            cursor = conn.cursor()
            inserted: list[Task] = []
            for p in payloads:
                cur = cursor.execute(
                    """
                    INSERT INTO queue (
                        payload, status, created_at, updated_at, worker_id
                    )
                    VALUES (?, ?, ?, ?, '');
                    """,
                    (p, TaskStatus.PENDING.value, now, now),
                )
                inserted.append(
                    Task(
                        id=cur.lastrowid,
                        payload=p,
                        status=TaskStatus.PENDING,
                        created_at=now,
                        updated_at=now,
                    )
                )
            return inserted

    def claim_next_pending(self, worker_id: str) -> Optional[Task]:
        conn = sqlite3.connect(self.db_path, timeout=self.timeout)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute(f"PRAGMA busy_timeout = {int(self.timeout * 1000)};")
        try:
            conn.execute("BEGIN IMMEDIATE;")
            row = conn.execute(
                """
                SELECT id, payload, status, created_at, updated_at, worker_id
                FROM queue
                WHERE status = ?
                ORDER BY id ASC
                LIMIT 1;
                """,
                (TaskStatus.PENDING.value,),
            ).fetchone()

            if row is None:
                conn.commit()
                return None

            now = datetime.now().isoformat(timespec="seconds")
            task_id = row["id"]
            conn.execute(
                """
                UPDATE queue
                SET status = ?, worker_id = ?, updated_at = ?
                WHERE id = ?;
                """,
                (TaskStatus.IN_PROGRESS.value, worker_id, now, task_id),
            )
            conn.commit()
            return Task(
                id=task_id,
                payload=row["payload"],
                status=TaskStatus.IN_PROGRESS,
                created_at=row["created_at"],
                updated_at=now,
                worker_id=worker_id,
            )
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def mark_done(self, task_id: int) -> bool:
        now = datetime.now().isoformat(timespec="seconds")
        with self._connection() as conn:
            cursor = conn.execute(
                """
                UPDATE queue
                SET status = ?, updated_at = ?
                WHERE id = ?;
                """,
                (TaskStatus.DONE.value, now, task_id),
            )
            return cursor.rowcount > 0

    def get_stats(self) -> dict[str, int]:
        with self._connection() as conn:
            cursor = conn.execute(
                "SELECT status, COUNT(*) as count FROM queue GROUP BY status;"
            )
            counts = {row["status"]: row["count"] for row in cursor.fetchall()}
            pending = counts.get(TaskStatus.PENDING.value, 0)
            in_progress = counts.get(TaskStatus.IN_PROGRESS.value, 0)
            done = counts.get(TaskStatus.DONE.value, 0)
            return {
                TaskStatus.PENDING.value: pending,
                TaskStatus.IN_PROGRESS.value: in_progress,
                TaskStatus.DONE.value: done,
                "total": pending + in_progress + done,
            }
