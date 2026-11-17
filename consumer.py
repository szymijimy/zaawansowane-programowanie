import argparse
import os
import sys
import time
from common import FileQueue, TaskStatus


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Task consumer worker")
    parser.add_argument(
        "--worker-id",
        type=str,
        default=None,
        help="Worker identifier (default: operator-<PID>)",
    )
    parser.add_argument(
        "--file",
        type=str,
        default="queue.csv",
        help="Queue file path (default: queue.csv)",
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
    queue = FileQueue(file_path=args.file)

    print(f"[{worker_id}] Worker started. Target file: '{args.file}', task duration: {args.duration}s, poll interval: {args.poll_interval}s")

    try:
        while True:
            task = queue.claim_next_pending(worker_id)
            if task is not None:
                print(f"[{worker_id}] Claimed task ID {task.id}: '{task.payload}' -> status '{TaskStatus.IN_PROGRESS.value}'")
                time.sleep(args.duration)
                queue.mark_done(task.id)
                print(f"[{worker_id}] Finished task ID {task.id} -> status '{TaskStatus.DONE.value}'")
            else:
                print(f"[{worker_id}] No pending tasks. Waiting {args.poll_interval}s...")
                time.sleep(args.poll_interval)
    except KeyboardInterrupt:
        print(f"\n[{worker_id}] Shutting down gracefully...")


if __name__ == "__main__":
    main()
