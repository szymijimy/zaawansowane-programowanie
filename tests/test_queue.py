import os
import tempfile
from concurrent.futures import ThreadPoolExecutor
from common import FileQueue, TaskStatus


def test_file_queue_lifecycle() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        q_path = os.path.join(tmpdir, "test_queue.csv")
        queue = FileQueue(file_path=q_path)

        task1 = queue.enqueue("Test task 1")
        assert task1.id == 1
        assert task1.status == TaskStatus.PENDING

        task2 = queue.enqueue("Test task 2")
        assert task2.id == 2
        assert task2.status == TaskStatus.PENDING

        claimed1 = queue.claim_next_pending("worker-1")
        assert claimed1 is not None
        assert claimed1.id == 1
        assert claimed1.status == TaskStatus.IN_PROGRESS
        assert claimed1.worker_id == "worker-1"

        claimed2 = queue.claim_next_pending("worker-2")
        assert claimed2 is not None
        assert claimed2.id == 2
        assert claimed2.status == TaskStatus.IN_PROGRESS
        assert claimed2.worker_id == "worker-2"

        claimed_none = queue.claim_next_pending("worker-3")
        assert claimed_none is None

        assert queue.mark_done(1) is True
        assert queue.mark_done(2) is True

        stats = queue.get_stats()
        assert stats["pending"] == 0
        assert stats["in_progress"] == 0
        assert stats["done"] == 2
        assert stats["total"] == 2


def test_file_queue_batch_enqueue() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        q_path = os.path.join(tmpdir, "test_batch.csv")
        queue = FileQueue(file_path=q_path)

        payloads = [f"Job {i}" for i in range(1, 11)]
        created = queue.enqueue_batch(payloads)
        assert len(created) == 10

        stats = queue.get_stats()
        assert stats["pending"] == 10
        assert stats["total"] == 10


def test_concurrent_claims() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        q_path = os.path.join(tmpdir, "test_concurrent.csv")
        queue = FileQueue(file_path=q_path)
        queue.enqueue_batch([f"Job {i}" for i in range(1, 21)])

        def claim_worker(worker_id: str):
            claimed = []
            while True:
                task = queue.claim_next_pending(worker_id)
                if task is None:
                    break
                queue.mark_done(task.id)
                claimed.append(task.id)
            return claimed

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(claim_worker, f"worker-{i}") for i in range(4)]
            results = [f.result() for f in futures]

        all_claimed_ids = [task_id for worker_tasks in results for task_id in worker_tasks]
        assert len(all_claimed_ids) == 20
        assert len(set(all_claimed_ids)) == 20
        assert set(all_claimed_ids) == set(range(1, 21))

        stats = queue.get_stats()
        assert stats["pending"] == 0
        assert stats["in_progress"] == 0
        assert stats["done"] == 20
