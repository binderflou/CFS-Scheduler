# cfs/core/weights.py

from __future__ import annotations

NICE_MIN = -20
NICE_MAX = 19
NICE_0_WEIGHT = 1024

# Linux-inspirierte Gewichtstabelle (CFS). Index 0 entspricht nice=-20, Index 20 entspricht nice=0.

# Tabelle für die Umrechnung von nice-Wert in weight-Wert
# keine Umrechnung über Prozentwerte weil
# Linux nutzt intern auch eine Tabelle
NICE_TO_WEIGHT = [
    88761, 71755, 56483, 46273, 36291,
    29154, 23254, 18705, 14949, 11916,
    9548, 7620, 6100, 4904, 3906,
    3121, 2501, 1991, 1586, 1277,
    1024, 820, 655, 526, 423,
    335, 272, 215, 172, 137,
    110, 87, 70, 56, 45,
    36, 29, 23, 18, 15,
]

# nice-Eingabewert überprüfungen und wenn notwendig auf min oder max setzen (-20,+19)
def clamp_nice(nice: int) -> int:
    """Clamp nice into the supported range."""
    return max(NICE_MIN, min(NICE_MAX, nice))

# Umwandlung nice in weight
def nice_to_weight(nice: int) -> int:
    """
    Convert a nice value [-20..+19] to a CFS weight.
    Higher weight => slower vruntime growth => more CPU share over time.
    """
    n = clamp_nice(nice)
    return NICE_TO_WEIGHT[n - NICE_MIN]


# Mini-Test
if __name__ == "__main__":
    for n in [-21, -20, 0, 19, 20]:
        print(n, nice_to_weight(n))
