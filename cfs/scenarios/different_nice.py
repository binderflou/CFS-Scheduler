# 01_src/scenarios/different_nice.py

from __future__ import annotations

from ..core.scheduler import CFSScheduler
from ..core.process import Process
from ._helpers import run_simulation, print_timeline, print_summary


from ..metric.metrics import print_report
from ..metric.plotter import plot_cpu_share_vs_expected
from ..metric.export import export_metrics_csv

def main() -> None:
    s = CFSScheduler(tick=10.0)

    procs = [
        Process(pid=1, nice=0,  total_work=200, work_remaining=200),
        Process(pid=2, nice=5,  total_work=200, work_remaining=200),
        Process(pid=3, nice=10, total_work=200, work_remaining=200),
    ]
    for p in procs:
        s.add_process(p)

    result = run_simulation(s, print_every=1)
    print_timeline(result["timeline"])
    print_summary(procs)
    print_report(procs)
    plot_cpu_share_vs_expected(procs, title="different_nice: Expected vs Actual CPU Share")
    export_metrics_csv(procs, "different_nice_metrics.csv")

if __name__ == "__main__":
    main()
