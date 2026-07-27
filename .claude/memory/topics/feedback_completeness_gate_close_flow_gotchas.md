> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-27
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_completeness_gate_close_flow_gotchas.md

---
name: feedback_completeness_gate_close_flow_gotchas
description: "Operational gotchas for closing gate:completeness issues (#2798) — env-var false alarm, evidence class for harness, same-actor close OK"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 23aefe56-3d99-4ddd-bd1e-43aba4d12059
---

Closing a `gate:completeness` issue (the #2798 gate, auto-applied by `autoapply-completeness-label.yml`) requires a stamped ```completeness {json}``` record on the body + an owner `status:completeness-verified` label, or the Level-3 GH Action (`.github/workflows/completeness-gate.yml`) reopens it. Non-obvious operational details I had to reverse-engineer (2026-05-29, closing #2851/#2814/#2801):

**Why:** the gate machinery (`scripts/workflow/completeness_{score,gate_check,gate_runner}.py`, `scripts/enforcement/check-completeness-before-close.sh`) lives ONLY on `origin/main` — a stale local branch won't have it; use a worktree off `origin/main` to run it.

**How to apply:**
- **Local check reads `$COMPLETENESS_OWNERS` from the SHELL ENV, not the GitHub repo variable.** Unset → false "CONFIG ERROR — COMPLETENESS_OWNERS unset". The real value is a repo variable (`vamseeachanta`, set 2026-05-26); the server-side Action reads that. Always run the local check as `COMPLETENESS_OWNERS=vamseeachanta bash scripts/enforcement/check-completeness-before-close.sh <N>`.
- **Class is honesty-driven, not gate-enforced.** `evaluate_close` trusts the body record's `cls`+`completeness_pct` (thresholds code=90, evidence=80). Harness scripts (`scripts/readiness/*`, `scripts/memory/*`) do NOT map to a #1629 module-status package, so `score_code` can't apply → use **evidence class** (precedent: #2846). The agent computes+stamps; only the owner applies the verified label (can't self-verify).
- **Same-actor verify+close IS allowed** — `COMPLETENESS_REQUIRE_SEPARATE_CLOSER` is OFF, so the owner may both verify and close (verified live: #2851/#2814/#2801 all closed by vamseeachanta after vamseeachanta verified). An OLD 2026-05-26 reopen comment says "not the closing actor" — that's stale; ignore it.
- **Anti-forgery ordering:** the verified label must post-date the LAST body edit. So stamp the record FIRST, never edit the body after the owner labels. Editing #2801's already-stamped record would have reset its freshness clock — left it untouched.
- **`stateReason=REOPENED` with `closedAt=null` = old history, not a fresh reopen.** Check `closedAt` + newest `github-actions` comment date before assuming the gate just rejected a close.
- To run `completeness_score.py` standalone, register it in `sys.modules` before `exec_module` (its `@dataclass` needs it), and use `UV_LINK_MODE=copy UV_CACHE_DIR=/tmp/uv-cache`.

Related: [[feedback_completeness_gate_reopen_is_freshness_not_separate_closer]], [[feedback_completeness_score_before_closure]].
