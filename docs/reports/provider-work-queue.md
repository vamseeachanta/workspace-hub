# Provider work queue

Generated: 2026-06-27T17:20:47.323906Z
Current week: 2026-W26
Recommended provider order: codex, gemini, claude

Execution-ready means the issue already carries `status:plan-approved`. agent:* labels are routing hints only and do not grant execution approval.

## claude

- Routing priority: high
- Execution-ready candidates: 39
- Total routed candidates: 175

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2686 Catenary solver canonicalization: 8 implementations, 4 numerically diverge, 5 shadows to delete | yes | strategy/workflow/architecture language | bug, priority:high, cat:engineering, cat:bugfix, machine:dev-primary, status:plan-approved |
| #2694 Epic: Cross-domain duplicate-implementation cleanup (catenary, PipeCapacity, cathodic protection, natural-period, hydro-matrix, on-bottom stability) | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:engineering, cat:bugfix, domain:refactor, machine:dev-primary |
| #2738 feat(hermes): harden ace-linux-1 Telegram gateway as dispatch coordinator | yes | existing claude agent label | enhancement, priority:high, cat:ai-orchestration, cat:operations, machine:ace-linux-1, agent:claude |
| #2739 feat(hermes): promote ace-linux-2 as first Telegram/Hermes dispatch worker | yes | existing claude agent label | enhancement, priority:high, cat:ai-orchestration, cat:operations, machine:ace-linux-2, agent:claude |
| #2751 Cross-platform harness setup: integrate AI-provider bootstrap, auth orchestration, macOS+PowerShell, per-machine status registry | yes | strategy/workflow/architecture language | priority:high, cat:harness, domain:machine-setup, machine:dev-primary, status:plan-approved, dispatch:ready |
| #2754 throughput(workstations): activate ace-linux-1 provider/machine lane | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:ai-orchestration, cat:operations, machine:ace-linux-1, status:plan-approved |
| #2755 throughput(workstations): activate ace-linux-2 provider/machine lane | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:ai-orchestration, cat:operations, status:working, machine:ace-linux-2 |
| #2760 revise(naval-arch): B1528 SIROCCO force calculation review updates | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:engineering-calculations, domain:naval-architecture, machine:dev-primary, status:plan-approved |

## codex

- Routing priority: highest
- Execution-ready candidates: 2
- Total routed candidates: 21

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #3030 Dispatch-time codex weekly-quota gate: suspend lane:codex routing when available <10% | yes | implementation/test/fix language | domain:ai-tools, status:plan-approved, gate:completeness, lane:claude |
| #3143 bug(automation): a preserve/prune process destroys /tmp git worktrees + feature branches mid-session | yes | implementation/test/fix language | bug, cat:harness/ops, status:plan-approved, gate:completeness |
| #2880 feat(codex): make yolo-equivalent permission defaults travel across machines | no | existing codex agent label | enhancement, priority:high, cat:harness, domain:ai-config, machine:multi, agent:codex |
| #3026 ace-linux-2: gnome-shell crash recovery (2026-06-10) + /dev/sda end-of-life replacement plan | no | implementation/test/fix language | priority:high, lane:claude |
| #2671 R3 — Hydrodynamics: Industry practice (conferences, journals, vendor docs) | no | implementation/test/fix language | priority:medium, cat:engineering, cat:research, domain:hydrodynamics, machine:dev-primary, dispatch:ready |
| #2718 audit(hermes): kanban-worker dispatch hazards — parallel-spawn race + silent-hang (#2715-affected) | no | implementation/test/fix language | priority:medium, cat:ai-orchestration, cat:harness, domain:ai-config, machine:dev-primary, dispatch:ready |
| #2750 Hermes: integrate pre-completion-cleanup-audit into sub-agent completion relay | no | implementation/test/fix language | priority:medium, cat:harness, machine:dev-primary, dispatch:ready, gate:completeness, domain:harness |
| #2763 plan(operations): migrate gsd-researcher scheduled AI work through Hermes Agent | no | implementation/test/fix language | enhancement, priority:medium, cat:ai-orchestration, cat:operations, cat:harness, domain:automation |

## gemini

- Routing priority: highest
- Execution-ready candidates: 1
- Total routed candidates: 4

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2733 epic: make Hermes agent memory canonical across all AI providers | yes | existing gemini agent label | priority:high, cat:ai-orchestration, machine:dev-primary, agent:gemini, agent:claude, agent:codex |
| #2679 R3 — Mooring: Industry practice (Vryhof, Bridon, MIRP, OMAE sessions) | no | research/triage/audit language | priority:medium, cat:engineering, cat:research, machine:dev-primary, dispatch:ready, gate:completeness |
| #2854 gap(memory): Hermes read-back leg missing — consolidated memory never flows back into ~/.hermes/memories (parallel to #2841 Codex) | no | research/triage/audit language | priority:medium, cat:ai-orchestration, domain:knowledge-management-platform, lane:claude |
| #3031 triage: backfill placeholder bodies on gh-next-id.sh / backfill-github-refs.sh created issues | no | research/triage/audit language | priority:medium, domain:work-queue |

