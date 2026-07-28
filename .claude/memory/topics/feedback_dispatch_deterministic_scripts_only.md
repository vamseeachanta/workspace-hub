> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-28
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_dispatch_deterministic_scripts_only.md

---
name: feedback_dispatch_deterministic_scripts_only
description: Licensed-host dispatch runs ONLY deterministic scripts — no LLM calls anywhere in the dispatch/execution path (owner directive 2026-07-12)
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 8034de14-b6b8-4ad0-bcc4-728969a4191e
---

Work dispatched to the licensed Windows hosts (ace-win-1/ace-win-2 via the deckhand licensed-run lane) must be **clearly executed via scripts — as deterministic as possible. No LLM calling, no agentic steps, "no silly business"** anywhere in the dispatch chain: manifest/sweep generation, queue requests, the host agent, the solver workflows, postprocess rollups, and the watchdog are all plain deterministic code.

**Why:** troubleshooting. A failed run must be reproducible from its pinned input (same input.yml sha → same behavior); an LLM step anywhere makes failures non-reproducible and burns licensed-seat time on debugging.

**How to apply:**
- The lane's existing "fixed command only" rule (`uv run python -m <pkg> <input.yml>`) already embodies this — never weaken it toward prompt-driven execution.
- Sweep catalogs (dm#1557) are YAML + a deterministic generator script; the continuous scheduler (deckhand#551) must be cron/systemd running scripts, NOT an LLM agent deciding what to enqueue.
- LLMs (Claude/Codex) stay on the Linux side for authoring code, plans, and reviews — their OUTPUT is committed, reviewed script code; they are never in the runtime dispatch path.
- **LLM work is ad-hoc, user-initiated, and ONE-TIME**: when something new is needed (a new sweep family, a workflow fix, an onboarding), the user invokes an LLM session once, the result lands as committed deterministic code, and the pipeline resumes flowing autonomously. Steady state has zero LLM involvement.
- When designing any new lane feature, ask: "can this step's behavior be reproduced exactly from committed files?" If not, redesign.

Related: [[project_ace_win1_batch_operability_program]], [[feedback_externalize_all_config_to_yaml]].
