# 01_src/metric/metrics.py

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict

from ..core.process import Process


@dataclass
class ProcessMetrics:
    pid: int
    nice: int
    weight: int
    runtime: float
    cpu_share: float          # Ist-Anteil: runtime / sum(runtime)
    expected_share: float     # Soll-Anteil: weight / sum(weight)
    share_error: float        # cpu_share - expected_share


def _safe_div(a: float, b: float) -> float:
    return a / b if b != 0 else 0.0


def compute_process_metrics(processes: List[Process]) -> List[ProcessMetrics]:
    total_runtime = sum(p.runtime for p in processes)
    total_weight = sum(p.weight for p in processes)

    out: List[ProcessMetrics] = []
    for p in processes:
        cpu_share = _safe_div(p.runtime, total_runtime)
        expected = _safe_div(p.weight, total_weight)
        out.append(
            ProcessMetrics(
                pid=p.pid,
                nice=p.nice,
                weight=p.weight,
                runtime=p.runtime,
                cpu_share=cpu_share,
                expected_share=expected,
                share_error=cpu_share - expected,
            )
        )
    return out


def mean_absolute_share_error(pms: List[ProcessMetrics]) -> float:
    # 0.0 = perfekt, größer = schlechter
    if not pms:
        return 0.0
    return sum(abs(x.share_error) for x in pms) / len(pms)


def max_absolute_share_error(pms: List[ProcessMetrics]) -> float:
    if not pms:
        return 0.0
    return max(abs(x.share_error) for x in pms)


def jains_fairness_index(values: List[float]) -> float:
    """
    Jain's Fairness Index:
    1.0 = perfekt gleich verteilt (bei gleichen Ansprüchen).
    Für uns: nutzbar als "wie gleich sind die runtimes?"
    """
    if not values:
        return 1.0
    s = sum(values)
    ss = sum(v * v for v in values)
    if ss == 0:
        return 1.0
    n = len(values)
    return (s * s) / (n * ss)


def make_report(processes: List[Process]) -> Dict[str, object]:
    pms = compute_process_metrics(processes)

    report = {
        "per_process": pms,
        "mean_abs_share_error": mean_absolute_share_error(pms),
        "max_abs_share_error": max_absolute_share_error(pms),
        "jain_runtime": jains_fairness_index([p.runtime for p in processes]),
    }
    return report


def print_report(processes: List[Process]) -> None:
    rep = make_report(processes)
    pms: List[ProcessMetrics] = rep["per_process"]  # type: ignore[assignment]

    print("\nMetrics Report:")
    print("pid | nice | weight | runtime | cpu_share | expected | error")
    print("------------------------------------------------------------")
    for x in sorted(pms, key=lambda z: z.pid):
        print(
            f"{x.pid:>3} | {x.nice:>4} | {x.weight:>6} | {x.runtime:>7.1f} | "
            f"{x.cpu_share:>8.3f} | {x.expected_share:>8.3f} | {x.share_error:>+6.3f}"
        )

    print("\nSummary Metrics:")
    print(f"Mean |cpu_share-expected| : {rep['mean_abs_share_error']:.4f}")
    print(f"Max  |cpu_share-expected| : {rep['max_abs_share_error']:.4f}")
    print(f"Jain(runtime)            : {rep['jain_runtime']:.4f}")
