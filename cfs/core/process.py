# 01_src/core/process.py

from __future__ import annotations
from dataclasses import dataclass

from .weights import nice_to_weight


@dataclass
class Process:
    pid: int
    nice: int
    total_work: float          # z.B. in ms (wie viel Arbeit insgesamt)
    work_remaining: float      # wie viel Arbeit noch übrig ist

    weight: int = 0            # wird aus nice berechnet
    vruntime: float = 0.0      # CFS-Fairness-Zähler
    runtime: float = 0.0       # echte CPU-Zeit, die der Prozess bekam

    def __post_init__(self) -> None:
        # Wird automatisch nach dem Erstellen des Objekts aufgerufen
        self.weight = nice_to_weight(self.nice)

    def is_finished(self) -> bool:
        return self.work_remaining <= 0

    def run_for(self, delta_exec: float) -> None:
        """Simuliere, dass der Prozess delta_exec echte Zeit läuft."""
        if delta_exec < 0:
            raise ValueError("delta_exec must be >= 0")

        actual = min(delta_exec, self.work_remaining)
        self.runtime += actual
        self.work_remaining -= actual


if __name__ == "__main__":
    p = Process(pid=1, nice=0, total_work=50, work_remaining=50)
    print("pid:", p.pid)
    print("nice:", p.nice)
    print("weight:", p.weight)
    p.run_for(10)
    print("runtime:", p.runtime)
    print("remaining:", p.work_remaining)
