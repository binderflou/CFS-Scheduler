# 01_src/scenarios/simple_equal.py

from __future__ import annotations

from ..core.scheduler import CFSScheduler
from ..core.process import Process
from ._helpers import run_simulation, print_timeline, print_summary

from ..metric.metrics import print_report

def main() -> None:
    s = CFSScheduler(tick=10.0)

    procs = [
        Process(pid=1, nice=0, total_work=100, work_remaining=100),
        Process(pid=2, nice=0, total_work=100, work_remaining=100),
        Process(pid=3, nice=0, total_work=100, work_remaining=100),
    ]
    for p in procs:
        s.add_process(p)

    result = run_simulation(s, print_every=1)
    print_timeline(result["timeline"])
    print_summary(procs)
    print_report(procs)


if __name__ == "__main__":
    main()
