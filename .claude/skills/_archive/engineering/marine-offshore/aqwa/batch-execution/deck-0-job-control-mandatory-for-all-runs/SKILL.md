---
name: aqwa-batch-execution-deck-0-job-control-mandatory-for-all-runs
description: "Sub-skill of aqwa-batch-execution: Deck 0 \u2014 Job Control (mandatory\
  \ for all runs) (+3)."
version: 1.1.0
category: engineering
type: reference
scripts_exempt: true
---

# Deck 0 — Job Control (mandatory for all runs) (+3)

## Deck 0 — Job Control (mandatory for all runs)


```
SYSTEM DATA AREA 50000        ! Scratch memory allocation (bytes)
JOB      analysis LINE        ! <jobname> <program_code>
TITLE    FPSO Diffraction Analysis 2026
NUM_CORES 8                   ! OpenMP threads (base licence: max 4 free)
OPTIONS  REST AHD1 END        ! REST=restart capable; AHD1=write ASCII .AH1
RESTART  1 1                  ! Start stage, stop stage (1=LINE, 2=LIBR, 3=NAUT)
```

Common `OPTIONS` flags:

| Flag | Effect |
|------|--------|
| `REST` | Enable restart capability (writes `.RES`) |
| `AHD1` | Write ASCII hydrodynamic database (`.AH1`) for OrcaFlex import |
| `GOON` | Continue past non-fatal errors |
| `NOFIG` | Suppress figure output |
| `NOLIST` | Suppress listing output |


## Deck Structure (Categories 1–6 for AQWA-LINE)


| Category | Keyword | Purpose |
|----------|---------|---------|
| 0 | (top of file) | Job control (JOB, TITLE, NUM_CORES, OPTIONS, RESTART) |
| 1 | `COOR` | Node coordinates: `ID  X  Y  Z` |
| 2 | `QPPL` / `TPPL` | Element topology: quad/tri panel connectivity |
| 3 | `PMAS` | Mass properties |
| 4 | `GEOM` | Geometric properties / CoG / inertia |
| 5 | `GLOB` | Global environment (DPTH, DENS, ACCG) |
| 6 | `FREQ` / `DIRN` | Wave frequencies and directions |
| — | `STOP` | Terminates entire input file |


## Minimal AQWA-LINE DAT Template


```
SYSTEM DATA AREA 50000
JOB      fpso LINE
TITLE    FPSO Hydrodynamic Diffraction
NUM_CORES 8
OPTIONS  REST AHD1 END
RESTART  1 1
COOR
   1001   0.0    0.0    0.0
   1002  50.0    0.0    0.0
   1003  50.0   15.0    0.0
   1004   0.0   15.0    0.0
END
QPPL
   QPPL DIFF
   1001  1001  1002  1003  1004
END
PMAS
   ...
END
GEOM
   ...
END
GLOB
DPTH     200.0
DENS     1025.0
ACCG     9.81
END
FREQ
   0.2  0.3  0.4  0.5  0.6  0.8  1.0  1.2  1.5  2.0
END
DIRN
   0.0  45.0  90.0  135.0  180.0
END
STOP
```


## Critical DAT Conventions


| Convention | Detail |
|-----------|--------|
| `QPPL DIFF` | Omitting `DIFF` makes panels non-diffracting — no error, wrong results |
| `ILID AUTO 21` | Irregular frequency removal; add after ZLWL waterline card |
| `SEAG nx ny` | 2 params in standalone mode; 6-param form is Workbench-only |
| `OPTIONS GOON` | Overrides non-fatal errors; does NOT bypass FATAL mesh errors |
| 80-col limit | Strictly enforced — AQWA truncates silently at column 80 |
| `STOP` vs `END` | `STOP` terminates the whole file; `END` terminates each category |
