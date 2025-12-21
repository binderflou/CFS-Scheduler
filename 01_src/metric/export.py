# 01_src/metric/export.py

from __future__ import annotations
import csv
from typing import List

from .metrics import compute_process_metrics
from ..core.process import Process


def export_metrics_csv(processes: List[Process], path: str) -> None:
    pms = compute_process_metrics(processes)

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "pid", "nice", "weight", "runtime",
            "cpu_share", "expected_share", "share_error"
        ])
        for x in pms:
            writer.writerow([
                x.pid, x.nice, x.weight, x.runtime,
                f"{x.cpu_share:.6f}",
                f"{x.expected_share:.6f}",
                f"{x.share_error:.6f}",
            ])
