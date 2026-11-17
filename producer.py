import argparse
import sys
from common import SqliteQueue, TaskStatus


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SQLite task producer")
    parser.add_argument(
        "count",
        nargs="?",
        type=int,
        default=1,
        help="Number of tasks to produce (default: 1)",
    )
    parser.add_argument(
        "--db",
        type=str,
        default="queue.db",
        help="SQLite database path (default: queue.db)",
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
    queue = SqliteQueue(db_path=args.db)

    if args.count <= 0:
        print("[PRODUCER] Error: count must be a positive integer", file=sys.stderr)
        sys.exit(1)

    if args.count == 1:
        task = queue.enqueue(args.payload)
        print(f"[PRODUCER] Enqueued task ID {task.id}: '{task.payload}' (status: {task.status.value})")
    else:
        payloads = [f"{args.payload} (ID {i})" for i in range(1, args.count + 1)]
        created = queue.enqueue_batch(payloads)
        print(f"[PRODUCER] Enqueued {len(created)} tasks (IDs {created[0].id}..{created[-1].id}) with status '{TaskStatus.PENDING.value}'")


if __name__ == "__main__":
    main()
