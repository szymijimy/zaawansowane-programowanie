import csv
import os
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


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

    def to_row(self) -> list[str]:
        return [
            str(self.id),
            self.payload,
            self.status.value,
            self.created_at,
            self.updated_at,
            self.worker_id,
        ]

    @classmethod
    def from_row(cls, row: list[str]) -> "Task":
        return cls(
            id=int(row[0]),
            payload=row[1],
            status=TaskStatus(row[2]),
            created_at=row[3],
            updated_at=row[4],
            worker_id=row[5] if len(row) > 5 else "",
        )


CSV_HEADER = [
    "id", "payload", "status", "created_at", "updated_at", "worker_id"
]


@contextmanager
def file_lock(lock_path: str):
    if sys.platform == "win32":
        import msvcrt

        lock_fd = os.open(lock_path, os.O_CREAT | os.O_RDWR)
        try:
            while True:
                try:
                    msvcrt.locking(lock_fd, msvcrt.LK_NBLCK, 1)
                    break
                except OSError:
                    time.sleep(0.05)
            yield
        finally:
            try:
                msvcrt.locking(lock_fd, msvcrt.LK_UNLCK, 1)
            finally:
                os.close(lock_fd)
    else:
        import fcntl

        with open(lock_path, "a") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)


class FileQueue:
    def __init__(self, file_path: str = "queue.csv") -> None:
        self.file_path = file_path
        self.lock_path = f"{file_path}.lock"
        self._initialize_storage()

    def _initialize_storage(self) -> None:
        with file_lock(self.lock_path):
            is_empty = (
                not os.path.exists(self.file_path)
                or os.path.getsize(self.file_path) == 0
            )
            if is_empty:
                with open(
                    self.file_path, mode="w", newline="", encoding="utf-8"
                ) as f:
                    writer = csv.writer(f)
                    writer.writerow(CSV_HEADER)

    def _read_tasks_unlocked(self) -> list[Task]:
        if not os.path.exists(self.file_path):
            return []
        tasks: list[Task] = []
        with open(self.file_path, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if not header:
                return []
            for row in reader:
                if row:
                    tasks.append(Task.from_row(row))
        return tasks

    def _write_tasks_unlocked(self, tasks: list[Task]) -> None:
        temp_file = f"{self.file_path}.tmp"
        with open(temp_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADER)
            for task in tasks:
                writer.writerow(task.to_row())
        os.replace(temp_file, self.file_path)

    def enqueue(self, payload: str) -> Task:
        with file_lock(self.lock_path):
            tasks = self._read_tasks_unlocked()
            next_id = max((t.id for t in tasks), default=0) + 1
            now = datetime.now().isoformat(timespec="seconds")
            task = Task(
                id=next_id,
                payload=payload,
                status=TaskStatus.PENDING,
                created_at=now,
                updated_at=now,
            )
            tasks.append(task)
            self._write_tasks_unlocked(tasks)
            return task

    def enqueue_batch(self, payloads: list[str]) -> list[Task]:
        with file_lock(self.lock_path):
            tasks = self._read_tasks_unlocked()
            current_id = max((t.id for t in tasks), default=0)
            now = datetime.now().isoformat(timespec="seconds")
            created_tasks: list[Task] = []
            for payload in payloads:
                current_id += 1
                task = Task(
                    id=current_id,
                    payload=payload,
                    status=TaskStatus.PENDING,
                    created_at=now,
                    updated_at=now,
                )
                tasks.append(task)
                created_tasks.append(task)
            self._write_tasks_unlocked(tasks)
            return created_tasks

    def claim_next_pending(self, worker_id: str) -> Optional[Task]:
        with file_lock(self.lock_path):
            tasks = self._read_tasks_unlocked()
            for task in tasks:
                if task.status == TaskStatus.PENDING:
                    task.status = TaskStatus.IN_PROGRESS
                    task.worker_id = worker_id
                    now = datetime.now().isoformat(timespec="seconds")
                    task.updated_at = now
                    self._write_tasks_unlocked(tasks)
                    return task
            return None

    def mark_done(self, task_id: int) -> bool:
        with file_lock(self.lock_path):
            tasks = self._read_tasks_unlocked()
            for task in tasks:
                if task.id == task_id:
                    task.status = TaskStatus.DONE
                    now = datetime.now().isoformat(timespec="seconds")
                    task.updated_at = now
                    self._write_tasks_unlocked(tasks)
                    return True
            return False

    def get_stats(self) -> dict[str, int]:
        with file_lock(self.lock_path):
            tasks = self._read_tasks_unlocked()
            pending_count = sum(
                1 for t in tasks if t.status == TaskStatus.PENDING
            )
            in_progress_count = sum(
                1 for t in tasks if t.status == TaskStatus.IN_PROGRESS
            )
            done_count = sum(
                1 for t in tasks if t.status == TaskStatus.DONE
            )
            return {
                TaskStatus.PENDING.value: pending_count,
                TaskStatus.IN_PROGRESS.value: in_progress_count,
                TaskStatus.DONE.value: done_count,
                "total": len(tasks),
            }
