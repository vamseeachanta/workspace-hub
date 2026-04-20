# Session summary — #43 WRK-1107 provider assessment (closed/rescoped)

**Session date:** 2026-04-19 → 2026-04-20
**Outcome:** #43 closed after 3 adversarial review waves converged to MAJOR. Rescoped to #2376 + #2377.
**Total artifacts preserved:** 2 plan files + 7 review artifacts + 1 session summary (this file).

---

## Timeline

| Step | Output | Commit |
|---|---|---|
| Resource intel | Verified 11 files reference WRK-NNNN; `.claude/state/` vs `state/` dual session-signals stores; `scripts/analysis/session-analysis.sh` line 101 filter; `behavior-contract.yaml` already has `provider_assignment.task_type_matrix`; `logs/*` is gitignored | n/a |
| Draft v1 → v2 | Resolved 7 design Qs with user-approved recommendations; absorbed Claude MINOR (10 findings) | `d06413a4f` |
| Codex + Gemini v2 review | Codex MAJOR (7 findings), Gemini MAJOR (2 genuine + 2 stale-state false positives) | n/a |
| Draft v3 (sibling file) | Absorbed 8 distinct blockers; scope reduced 6→3 derivable dimensions | `5068a48de` |
| Claude + Codex + Gemini v3 review | All three returned MAJOR (5+4+4 findings) | n/a |
| Rescope decision | Close #43; open #2376 (corpus-honest subset) and #2377 (upstream emitters) | `989e5b1aa` |
| Session follow-ups | Filed #2385 (dual-store consolidation), #2386 (fixture-path policy), #2387 (predecessor cleanup) | (this commit) |

---

## Why #43 could not converge

Across 3 review waves, the reviewers independently triangulated on a single root cause: **the plan's scope exceeded what the verified event corpus can express.**

- **Fabricated schema fields** — scorer pseudocode invoked `next_gap_seconds`, `gate_bypass`, `e.type`, and a `provider` field on `session_tool_summary` — none of which exist. All three v3 reviewers flagged this.
- **No Gemini data** exists in `.claude/state/session-signals/` or `state/session-signals/` for any reviewed window. The 6-dim × 3-provider Deliverable was unsupportable from day 1.
- **Fictional routing-rules precedence** — `config/agents/behavior-contract.yaml` explicitly says it is "a planning-stage decision, not runtime routing." Claiming it took precedence in a runtime routing chain contradicted the file itself.
- **Silent scope drop** — issue body Output 2 items (L1 hook trigger count from WRK-1044; WRK-1035/1044 regression analysis) were silently absent in both v2 and v3.

A fourth revision would likely have fabricated more schema to cover the fabrication findings — symptom of scope mismatch, not sloppy drafting.

---

## Key artifacts (preserved on main)

| Artifact | Path |
|---|---|
| v2 plan | `docs/plans/2026-04-19-issue-43-wrk-1107-provider-assessment.md` |
| v3 plan (sibling, superseded v2 before close) | `docs/plans/2026-04-20-issue-43-v3.md` |
| Claude v2 review (MINOR) | `scripts/review/results/2026-04-19-plan-43-claude.md` |
| Codex v2 review (MAJOR) | `scripts/review/results/2026-04-19-plan-43-codex.md` |
| Gemini v2 review (MAJOR) | `scripts/review/results/2026-04-19-plan-43-gemini.md` |
| Claude v3 review (MAJOR) | `scripts/review/results/2026-04-20-plan-43-v3-claude.md` |
| Codex v3 review (MAJOR) | `scripts/review/results/2026-04-20-plan-43-v3-codex.md` |
| Gemini v3 review (MAJOR) | `scripts/review/results/2026-04-20-plan-43-v3-gemini.md` |

---

## Issue graph after this session

```
#43 (closed)
  ├── #2376  corpus-honest 2-dim × 2-provider assessment
  ├── #2377  upstream event emitters (unblocks deferred 4 dimensions)
  ├── #2385  dual session-signals store consolidation
  ├── #2386  logs/ fixture-path policy (out of gitignore)
  └── #2387  predecessor governance cross-ref cleanup (#798, #871, #826, #950)

Superseded closed predecessors (governance drift, handled by #2387):
  #798, #871  (WRK-1005 duplicates)
  #826, #950  (WRK-1045 duplicates)
```

---

## Process observations — worth promoting to memory or skills

1. **Cross-provider review payoff was real this session.** Claude found surface defects; Codex found structural ones (pipeline-merge, routing-precedence); Gemini found concurrency/race defects. Memory entry `feedback_cross_provider_review_payoff` now has two confirmations (this session + prior #2342 experience).

2. **Sibling-file delivery beat in-place edits for v3.** A pattern worth noting: when a plan requires a large absorption pass, writing a new file (`YYYY-MM-DD-issue-N-v3.md`) is more robust than chained `Edit` ops against the committed v2 path.

3. **Pushed-artifact anchoring for Codex works.** Codex's GitHub connector successfully fetched commits `d06413a4f` and `5068a48de`, verified adjacent repo files (`behavior-contract.yaml`, `session-analysis.sh`, `.gitignore`), and surfaced defects that depended on cross-file verification.

4. **"`insufficient_corpus`" placeholders are an honest way to express scope reduction in a scorer.** The pattern — compute derivable dimensions, emit machine-readable placeholders with named missing events for the rest — gives downstream issues a clean prerequisite list (which is exactly what #2377 became).

5. **Adversarial framing shifts review quality materially.** Every review prompt this session used the 6-clause stance contract from the `issue-planning-mode` skill. Outcome: 17 total findings across 6 reviews, 0 rubber-stamp APPROVEs, triangulated convergence on root cause in wave 3.

---

## Closed. No further action on #43.
