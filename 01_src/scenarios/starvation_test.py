# 01_src/scenarios/starvation_test.py

from __future__ import annotations

from ..core.scheduler import CFSScheduler
from ..core.process import Process
from ._helpers import run_simulation, print_timeline, print_summary


def main() -> None:
    s = CFSScheduler(tick=2.0)

    # Ein sehr "wichtiger" Prozess (negative nice) + viele unwichtige
    vip = Process(pid=1, nice=-5, total_work=200, work_remaining=200)
    procs = [vip]

    # viele Background-Prozesse
    for i in range(2, 12):
        procs.append(Process(pid=i, nice=10, total_work=60, work_remaining=60))

    for p in procs:
        s.add_process(p)

    result = run_simulation(s, print_every=5)
    print_timeline(result["timeline"])
    print_summary(procs)


if __name__ == "__main__":
    main()
