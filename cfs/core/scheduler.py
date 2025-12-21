# 01_src/core/scheduler.py

from __future__ import annotations
from typing import List, Optional

from .process import Process
from .runqueue import RunQueue
from .weights import NICE_0_WEIGHT

class CFSScheduler:
    def __init__(self, tick: float = 1.0) -> None:
        self.tick = tick                  # reale Zeit pro Tick (z.B. ms)
        self.runqueue = RunQueue()
        self.current: Optional[Process] = None
        self.time: float = 0.0            # globale Simulationszeit

    def add_process(self, proc: Process) -> None:
        self.runqueue.add(proc) 
        
    def step(self) -> Process | None:
        proc = self.runqueue.pick_next()
        if proc is None:
            return None
        delta_exec = min(self.tick, proc.work_remaining)
        proc.run_for(delta_exec)

        vruntime_delta = delta_exec * (NICE_0_WEIGHT / proc.weight)
        proc.vruntime += vruntime_delta

        self.time += delta_exec

        if proc.is_finished():
            self.runqueue.remove(proc)

        self.current = proc
        return proc

    def snapshot(self) -> List[Process]:
        return list(self.runqueue._queue)

if __name__ == "__main__":
    s = CFSScheduler(tick=10)

    s.add_process(Process(pid=1, nice=0, total_work=50, work_remaining=50))
    s.add_process(Process(pid=2, nice=5, total_work=50, work_remaining=50))

    for i in range(6):
        p = s.step()
        if p:
            print(f"t={s.time:>3} ran pid={p.pid} vruntime={p.vruntime:.1f}")
