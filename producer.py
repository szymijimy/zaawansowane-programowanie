import argparse
import sys
from common import RabbitQueue, TaskStatus


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="RabbitMQ task producer")
    parser.add_argument(
        "count",
        nargs="?",
        type=int,
        default=1,
        help="Number of tasks to produce (default: 1)",
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
        "--payload",
        type=str,
        default="Rozmowa telefoniczna z klientem",
        help="Task description payload",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    queue = RabbitQueue(
        host=args.host, port=args.port, queue_name=args.queue
    )

    if args.count <= 0:
        print(
            "[PRODUCER] Error: count must be a positive integer",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.count == 1:
        task = queue.enqueue(args.payload)
        print(
            f"[PRODUCER] Enqueued task ID {task.id}: "
            f"'{task.payload}' (status: {task.status.value})"
        )
    else:
        payloads = [
            f"{args.payload} (ID {i})" for i in range(1, args.count + 1)
        ]
        created = queue.enqueue_batch(payloads)
        print(
            f"[PRODUCER] Enqueued {len(created)} tasks "
            f"(IDs {created[0].id}..{created[-1].id}) "
            f"with status '{TaskStatus.PENDING.value}'"
        )


if __name__ == "__main__":
    main()
