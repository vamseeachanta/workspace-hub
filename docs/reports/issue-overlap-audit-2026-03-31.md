# Issue Overlap Audit

> Issue: #1536 | Date: 2026-03-31

## Duplicate Issue Sets

Three identical sets of the hygiene program were filed. The canonical set is **#1530-#1536** (most recent).

| Role | Set 1 (close) | Set 2 (close) | Set 3 (KEEP) |
|------|:---:|:---:|:---:|
| Feature parent | #1516 | #1523 | **#1530** |
| Inventory docs | #1517 | #1524 | **#1531** |
| Control-plane contract | #1518 | #1525 | **#1532** |
| File-structure taxonomy | #1519 | #1526 | **#1533** |
| Root artifacts | #1520 | #1527 | **#1534** |
| Cross-platform policy | #1521 | #1528 | **#1535** |
| Issue consolidation | #1522 | #1529 | **#1536** |

**Action:** Close sets 1 and 2 as duplicates of set 3.

## Overlap with #1514 and #1515

| Issue | Scope | Overlap with #1530 program | Disposition |
|-------|-------|---------------------------|-------------|
| **#1514** | Provider-neutral AI harness architecture | Partial — #1514 deliverable 9 is "repo-hygiene workstream" and its body mentions redundant folders, stale plugin dirs, interchange artifacts | **KEEP SEPARATE** — #1514 is broader (orchestrator/reviewer/adapter architecture), hygiene is one output. Reference #1532 contract from #1514 when the harness architecture stabilizes. |
| **#1515** | Operationalize review/routing policy from #1514 | Partial — scope item 3 marks `.hive-mind`, `.swarm`, `.SLASH_COMMAND_ECOSYSTEM` as legacy | **KEEP SEPARATE** — #1515 is about review routing policy, not filesystem cleanup. The legacy marking in #1515 aligns with #1533 taxonomy but doesn't duplicate it. |

## Overlap with #53

| Issue | Scope | Disposition |
|-------|-------|-------------|
| **#53** | Audit empty submodule dirs (CAD-DEVELOPMENTS et al) | **CLOSE or DEFER** — CAD-DEVELOPMENTS is now a full git repo. The original concern about empty submodule dirs should be re-evaluated. |

## Summary of Actions

| Action | Issues |
|--------|--------|
| **Close as duplicate** | #1516, #1517, #1518, #1519, #1520, #1521, #1522, #1523, #1524, #1525, #1526, #1527, #1528, #1529 |
| **Keep as canonical** | #1530, #1531, #1532, #1533, #1534, #1535, #1536 |
| **Keep separate** | #1514, #1515 |
| **Evaluate** | #53 |
