---
name: crossprovider hermes solver-execution-is-windows-only-linux-hosts-are
description: Solver execution is Windows-only; Linux hosts are orchestration-only
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [architecture, solver-execution, multi-machine-constraint]
---

ace-linux-2 and Linux orchestration nodes lack OrcaWave, OrcaFlex, AQWA, ANSYS, MATLAB, and Python OrcFxAPI. Only licensed-win-1 and licensed-win-2 (Windows, ssh:null, GUI-only) execute solvers. Cannot deploy solver runs to Linux; Linux hosts queue/validate/monitor only.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
