import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional
import pika


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

    def to_json(self) -> str:
        data = asdict(self)
        data["status"] = self.status.value
        return json.dumps(data)

    @classmethod
    def from_json(cls, raw: str) -> "Task":
        data: dict[str, Any] = json.loads(raw)
        return cls(
            id=int(data["id"]),
            payload=str(data["payload"]),
            status=TaskStatus(data["status"]),
            created_at=str(data["created_at"]),
            updated_at=str(data.get("updated_at", data["created_at"])),
            worker_id=str(data.get("worker_id", "")),
        )


def get_default_port() -> int:
    env_port = os.getenv("RABBITMQ_PORT")
    if env_port is not None:
        return int(env_port)
    return 8081


def create_connection(
    host: str = "localhost",
    port: Optional[int] = None,
    heartbeat: int = 600,
) -> pika.BlockingConnection:
    target_port = port if port is not None else get_default_port()
    params = pika.ConnectionParameters(
        host=host,
        port=target_port,
        heartbeat=heartbeat,
        blocked_connection_timeout=300,
    )
    try:
        return pika.BlockingConnection(params)
    except pika.exceptions.AMQPConnectionError:
        fallback_port = 5672 if target_port == 8081 else 8081
        fallback_params = pika.ConnectionParameters(
            host=host,
            port=fallback_port,
            heartbeat=heartbeat,
            blocked_connection_timeout=300,
        )
        return pika.BlockingConnection(fallback_params)


class RabbitQueue:
    def __init__(
        self,
        host: str = "localhost",
        port: Optional[int] = None,
        queue_name: str = "calls_queue",
    ) -> None:
        self.host = host
        self.port = port
        self.queue_name = queue_name

    def get_connection(self) -> pika.BlockingConnection:
        return create_connection(host=self.host, port=self.port)

    def declare_queue(self, channel: Any) -> Any:
        return channel.queue_declare(queue=self.queue_name, durable=True)

    def enqueue(self, payload: str, task_id: int = 1) -> Task:
        now = datetime.now().isoformat(timespec="seconds")
        task = Task(
            id=task_id,
            payload=payload,
            status=TaskStatus.PENDING,
            created_at=now,
            updated_at=now,
        )
        conn = self.get_connection()
        try:
            channel = conn.channel()
            self.declare_queue(channel)
            channel.basic_publish(
                exchange="",
                routing_key=self.queue_name,
                body=task.to_json().encode("utf-8"),
                properties=pika.BasicProperties(
                    delivery_mode=pika.DeliveryMode.Persistent
                ),
            )
            return task
        finally:
            conn.close()

    def enqueue_batch(self, payloads: list[str]) -> list[Task]:
        now = datetime.now().isoformat(timespec="seconds")
        created_tasks: list[Task] = []
        conn = self.get_connection()
        try:
            channel = conn.channel()
            self.declare_queue(channel)
            for idx, payload in enumerate(payloads, start=1):
                task = Task(
                    id=idx,
                    payload=payload,
                    status=TaskStatus.PENDING,
                    created_at=now,
                    updated_at=now,
                )
                channel.basic_publish(
                    exchange="",
                    routing_key=self.queue_name,
                    body=task.to_json().encode("utf-8"),
                    properties=pika.BasicProperties(
                        delivery_mode=pika.DeliveryMode.Persistent
                    ),
                )
                created_tasks.append(task)
            return created_tasks
        finally:
            conn.close()

    def purge(self) -> None:
        conn = self.get_connection()
        try:
            channel = conn.channel()
            self.declare_queue(channel)
            channel.queue_purge(queue=self.queue_name)
        finally:
            conn.close()
