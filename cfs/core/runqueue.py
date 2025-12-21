# 01_src/core/runqueue.py

from __future__ import annotations
from typing import List

from .process import Process


class RunQueue:
    def __init__(self) -> None:
        self._queue: List[Process] = []

    def add(self, proc: Process) -> None:
        self._queue.append(proc)

    def remove(self, proc: Process) -> None:
        self._queue.remove(proc)

    def pick_next(self) -> Process | None:
        if not self._queue:
            return None
        return min(self._queue, key=lambda p: p.vruntime)

if __name__ == "__main__":
    from .process import Process

    rq = RunQueue()
    rq.add(Process(pid=1, nice=0, total_work=50, work_remaining=50))
    rq.add(Process(pid=2, nice=5, total_work=50, work_remaining=50))

    rq._queue[0].vruntime = 10
    rq._queue[1].vruntime = 30

    next_proc = rq.pick_next()
    print("picked pid:", next_proc.pid)
