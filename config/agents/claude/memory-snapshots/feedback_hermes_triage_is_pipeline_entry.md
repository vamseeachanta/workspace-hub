---
name: hermes-triage-is-pipeline-entry
description: "Hermes --triage flag is the ENTRY of the auto-promotion/decomposition pipeline, not a safe parking spot"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 000d04a3-532a-4959-becb-59b1f1349fb3
---

`hermes kanban create --triage` does NOT park tasks for human review. It puts them in the input queue of the gateway's auxiliary `triage_specifier` and `kanban_decomposer` LLMs, which automatically promote triage → todo within minutes AND fan out into child tasks with auto-generated acceptance criteria.

**Why:** Discovered 2026-05-22 during bulk-loading 1536 cards: 134 cards loaded with `--triage` produced 532 auto-decomposed child tasks + 260 active worker subprocesses within ~10 minutes, burning OpenRouter/Gemini API tokens. The CLI help text "Park in triage — a specifier will flesh out the spec and promote to todo" was read as "park" but means "be processed by the specifier". The verb "park" misleads — triage is processed, not parked.

**How to apply:**
- NEVER use `--triage` for bulk imports unless you actively want the specifier+decomposer to run on every card.
- For "import 1000s of tasks safely" workflows: keep cards as YAML-only outside Hermes runtime; promote individually via `hermes kanban specify <one-card>` when truly ready.
- If you must enter Hermes runtime in a non-dispatchable state: see [[hermes-blocked-status-auto-unblocked]] for the `blocked` alternative (which has its OWN auto-unblock hazard).
- Monitor with `hermes kanban --board <slug> stats` immediately after any bulk import; if you see non-zero `todo`/`ready`/`running`, the auto-pipeline has fired.
- Related defect class: [[hermes-blocked-status-auto-unblocked]]. The deeper lesson: Hermes runtime WANTS to dispatch; static parking requires terminal `archive` state.
