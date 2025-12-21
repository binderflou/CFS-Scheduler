# 01_src/scenarios/interactive_vs_cpu.py

from __future__ import annotations

from ..core.scheduler import CFSScheduler
from ..core.process import Process
from ._helpers import run_simulation, print_timeline, print_summary


def main() -> None:
    s = CFSScheduler(tick=5.0)

    # CPU-bound: lange Arbeit
    cpu = Process(pid=1, nice=0, total_work=300, work_remaining=300)

    # "Interaktiv": kurze Jobs (wir simulieren das als mehrere kurze Prozesse)
    i1 = Process(pid=2, nice=0, total_work=40, work_remaining=40)
    i2 = Process(pid=3, nice=0, total_work=40, work_remaining=40)
    i3 = Process(pid=4, nice=0, total_work=40, work_remaining=40)

    procs = [cpu, i1, i2, i3]
    for p in procs:
        s.add_process(p)

    result = run_simulation(s, print_every=2)
    print_timeline(result["timeline"])
    print_summary(procs)


if __name__ == "__main__":
    main()
