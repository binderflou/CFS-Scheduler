# 01_src/core/ – Scheduler-Kern (Clean & Denkbar)

---

## 🎯 Ziel von `01_src/core/`

- Enthält **nur** den Scheduler-Kern  
  - ❌ keine GUI  
  - ❌ kein Plotting  
  - ❌ keine Szenarien
- Jede Datei ist so gestaltet, dass sie im Kopf wie **Kernel-Bausteine** zusammengesetzt werden kann
- Fokus auf **Lesbarkeit + mentale Simulation**

---

## 💡 Aha-Moment (Leitprinzip)

- **CFS = Wähle immer den Prozess mit der kleinsten `vruntime`**
- Priorität / `nice`:
  - wirkt **nicht magisch**
  - beeinflusst nur das **Gewicht**
- Unterschiedliche Gewichte ⇒
  - `vruntime` wächst unterschiedlich schnell
  - Scheduler bleibt simpel und fair

---

## 📦 `core/process.py` – Prozessmodell

### Zweck
- Reines Daten- + Minimal-Logik-Objekt
- Kein Scheduling-Wissen

### Struktur
- `Process` als Dataclass / Objekt

### Pflichtfelder
- `pid`  
  - eindeutig
- `nice`  
  - z. B. `-20 … +19`
- `weight`  
  - aus `nice` abgeleitet
- `vruntime`  
  - Start meist `0.0`
- `runtime` / `exec_done`  
  - tatsächlich erhaltene CPU-Zeit
- `burst_total` / `work_remaining`  
  - gesamte vs. verbleibende Arbeit
- `state`  
  - `RUNNABLE | RUNNING | FINISHED`

### Methoden (minimal)
- `is_finished()`
- optional `run_for(delta_exec)`  
  - reduziert `work_remaining`
  - erhöht `runtime`

---

## ⚖️ `core/weights.py` oder `core/constants.py` – Nice → Weight

### Inhalt
- Funktion oder Tabelle:
  - `nice_to_weight(nice)`
- Konstante:
  - `NICE_0_WEIGHT`
- optional:
  - inverse Gewichte
  - Helper für `vruntime`-Berechnung

### Aha
- Nice-Logik **sichtbar & explizit**
- Nicht im Scheduler „versteckt“

---

## 🧺 `core/runqueue.py` – Runqueue

### Zweck
- Verwaltung aller **RUNNABLE** Prozesse
- Zentrale Datenstruktur des Schedulers

### Kernoperationen
- `add(proc)`
- `remove(proc)`
- `pick_next()`  
  - liefert Prozess mit **kleinster `vruntime`**
- optional `update(proc)`  
  - bei geänderter `vruntime`

### Implementationsvarianten
- simpel:
  - `list + min(...)`
- eleganter:
  - sortierte Liste (`bisect`)
  - `heapq`

### Aha
- Runqueue = **„Sortiert nach vruntime“**
- Kein Hexenwerk

---

## 🎼 `core/scheduler.py` – CFS-Logik

### Klasse
- `CFSScheduler`

### Verantwortlichkeiten
- Prozesse registrieren:
  - `add_process(proc)`
- Zeitschritt simulieren:
  - `step()`
- Ablauf pro Step:
  - nächsten Prozess aus Runqueue wählen
  - reale Laufzeit bestimmen (`delta_exec`)
  - `vruntime` aktualisieren (gewichtsbasiert)
  - Prozess beenden, wenn Arbeit fertig

### Timeslice / Granularity
- Parameter:
  - `target_latency`
  - `min_granularity`
- Idee:
  - `slice ≈ target_latency * weight / sum_weights`
  - aber **nie kleiner als** `min_granularity`

### Exports (für GUI / Szenarien)
- `snapshot()`:
  - Liste aller Prozesse
  - aktuelle Werte
  - aktuell laufende `pid`

---

## ⏱️ `core/vruntime.py` (optional, aber sauber)

### Zweck
- Zentrale Formel
- Keine Magie im Scheduler

### Funktion
- `calc_vruntime_delta(delta_exec, weight, NICE_0_WEIGHT)`

### Klassische Formel
- `vruntime += delta_exec * (NICE_0_WEIGHT / weight)`

### Aha
- großes `weight` ⇒
  - kleiner `vruntime`-Anstieg
  - Prozess bleibt länger „vorn“

---

## 🧾 `core/types.py` oder `core/enums.py` (optional)

### Inhalt
- `ProcessState` Enum:
  - `RUNNABLE`
  - `RUNNING`
  - `FINISHED`
- optional:
  - `SchedulerConfig` als Dataclass

---

## 🚫 Was **nicht** in `core/` gehört

- ❌ GUI → `ui/`
- ❌ Plots / Metriken → `metric/`
- ❌ Demo-Workloads → `scenarios/`
- ❌ Dateizugriff / Exporte  
  - maximal: minimaler Logger

---
