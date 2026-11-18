import argparse
import os
import sys
import time
from common import RabbitQueue, Task, TaskStatus


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="RabbitMQ task consumer worker"
    )
    parser.add_argument(
        "--worker-id",
        type=str,
        default=None,
        help="Worker identifier (default: operator-<PID>)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="RabbitMQ host (default: localhost)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="RabbitMQ port (default: 8081 or RABBITMQ_PORT)",
    )
    parser.add_argument(
        "--queue",
        type=str,
        default="calls_queue",
        help="Target queue name (default: calls_queue)",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=30.0,
        help="Job processing duration in seconds (default: 30.0)",
    )
    parser.add_argument(
        "--poll-interval",
        type=float,
        default=5.0,
        help="Polling interval when idle in seconds (default: 5.0)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    worker_id = args.worker_id or f"operator-{os.getpid()}"
    queue = RabbitQueue(
        host=args.host, port=args.port, queue_name=args.queue
    )

    conn = queue.get_connection()
    channel = conn.channel()
    queue.declare_queue(channel)
    channel.basic_qos(prefetch_count=1)

    print(
        f"[{worker_id}] Worker started. Target queue: '{args.queue}', "
        f"task duration: {args.duration}s, "
        f"poll interval: {args.poll_interval}s"
    )

    try:
        while True:
            method, properties, body = channel.basic_get(
                queue=args.queue, auto_ack=False
            )
            if method is not None:
                task = Task.from_json(body.decode("utf-8"))
                print(
                    f"[{worker_id}] Claimed task ID {task.id}: "
                    f"'{task.payload}' -> status "
                    f"'{TaskStatus.IN_PROGRESS.value}'"
                )
                time.sleep(args.duration)
                channel.basic_ack(delivery_tag=method.delivery_tag)
                print(
                    f"[{worker_id}] Finished task ID {task.id} -> "
                    f"status '{TaskStatus.DONE.value}'"
                )
            else:
                print(
                    f"[{worker_id}] No pending tasks. "
                    f"Waiting {args.poll_interval}s..."
                )
                time.sleep(args.poll_interval)
    except KeyboardInterrupt:
        print(f"\n[{worker_id}] Shutting down gracefully...")
    finally:
        if conn.is_open:
            conn.close()


if __name__ == "__main__":
    main()
