## core/

- Enthält die **Regeln**
- Bestimmt den **kompletten Ablauf**

### Entscheidet
- welcher Prozess läuft
- wie lange er läuft
- wie sich `vruntime` verändert

---

## scenarios/

- Enthält **Testfälle / Experimente**
- Beschreibt *Was passiert*, nicht *Wie entschieden wird*

### Legt fest
- welche Prozesse existieren
- ihre `nice`-Werte
- ihre gesamte Laufzeit / Workload
- ihre Startzeitpunkte

---

## metric/

- Wertet **Ergebnisse** aus
- Arbeitet **nachdem** ein Scenario gelaufen ist

### Bekommt
- Zustände / Snapshots
- Laufdaten aus `core`

### Rechnet
- Fairness
- Wartezeiten
- CPU-Anteile

### Macht Aussagen wie
- „Prozess A bekam doppelt so viel CPU wie B“
- „Nice −5 hatte langfristig X % Vorteil“
- „Kein Prozess verhungerte“

---

## ui/

- grafische Darstellung
- Startet den Scheduler
- Legt Prozesse an (wie ein Scenario)
- Ruft immer wieder:

    -   scheduler.step()
    -   scheduler.run()

- Holt sich danach einen Snapshot des Zustands
