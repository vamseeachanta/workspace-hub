# Next-session prompts — 2026-05-15 hand-off

> **Source session:** d4fe73ec (2026-05-14 22:00 CT → 2026-05-15 21:00 CT, ace-linux-1)
> **What this is:** copy-paste-ready prompts for a fresh Claude session. Each is self-contained — assumes the next session has no memory of this one.
> **Why this exists:** prompts that name files and issue numbers explicitly let the next session start working in minutes instead of re-discovering state.

## Session summary (what landed)

| Outcome | Issues |
|---|---|
| **Closed** | [#2528](https://github.com/vamseeachanta/workspace-hub/issues/2528) (skill retirements + .agents/skills mirror), [#2685](https://github.com/vamseeachanta/workspace-hub/issues/2685) (DNV-OS-E301 citation pilot LIVE) |
| **Filed** | [#2712](https://github.com/vamseeachanta/workspace-hub/issues/2712) (ace-linux-2 PATH gap), [#2718](https://github.com/vamseeachanta/workspace-hub/issues/2718) (kanban-worker dispatch hazards) |
| **Updated** | [#2715](https://github.com/vamseeachanta/workspace-hub/issues/2715) (kanban-worker evidence), [#2695](https://github.com/vamseeachanta/workspace-hub/issues/2695) (D7 reconciliation) |
| **Partial + blocked** | [#2702](https://github.com/vamseeachanta/workspace-hub/issues/2702) (routing audit, `status:blocked` on #2715) |
| **Halted on gate inconsistency** | [#2626](https://github.com/vamseeachanta/workspace-hub/issues/2626), [#2550](https://github.com/vamseeachanta/workspace-hub/issues/2550) |
| **Deferred** | [#2694](https://github.com/vamseeachanta/workspace-hub/issues/2694) (cathodic edition-merge, T2) |

Commits: `f997dab14`, `07d659507`, `8e3063530`, `9ac1fd1e8` (workspace-hub); `49071159` (digitalmodel).

Memory entries created:
- `project_ace_linux_2_dispatch_capability.md`
- `feedback_hermes_provider_openai_codex_routes_via_codex_exec.md`
- `feedback_label_vs_planbody_gate_inconsistency.md`

---

## Memory pointers — load these before any prompt below

```
Read these memory files first:
- /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_hermes_provider_openai_codex_routes_via_codex_exec.md
- /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_label_vs_planbody_gate_inconsistency.md
- /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/project_ace_linux_2_dispatch_capability.md
- /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_dispatch_local_marker_rationalization.md
- /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_never_offer_to_self_label_plan_approved.md
```

---

## Prompt 1 — Quick unlock: ace-linux-2 PATH fix (~10 min) [#2712]

```
Fix #2712 (ace-linux-2 PATH gap blocking cross-machine kanban dispatch).

Context: Last night's session verified ace-linux-2 is dispatch-ready end-to-end (SSH ✓, workspace ✓, Hermes gateway running ✓, kanban accepts task creation ✓) EXCEPT worker spawn fails with `hermes` executable not found on PATH. Symlink at ~/.local/bin/hermes already exists pointing to the venv binary, but ~/.local/bin isn't on the gateway-subprocess PATH.

Recommended fix (option A from the issue body): `ssh ace-linux-2 'sudo ln -s ~/.hermes/hermes-agent/venv/bin/hermes /usr/local/bin/hermes'`. Verify with `ssh ace-linux-2 'which hermes'` returning the system-wide path.

Then verify by re-dispatching #2628 Phase 1 (digitalmodel CI domain-divided architecture) onto ace-linux-2 — the task body was already drafted last night at /tmp/hermes-dispatch-20260514/body-2628-ace-linux-2.txt (may be gone if /tmp purged; if so reconstruct from the plan at docs/plans/2026-05-03-issue-2628-digitalmodel-domain-divided-ci.md).

Acceptance: hermes worker on ace-linux-2 spawns and survives past the 2-min danger window. Don't run the full Phase 1 to completion — just confirm spawn works, then archive the task.

Memory to consult: project_ace_linux_2_dispatch_capability.md (venv path is `venv/` not `.venv/`).
```

---

## Prompt 2 — Gate reconciliation: #2626, #2550, #2510 (~30 min, no code)

```
Reconcile the label-vs-plan-body gate inconsistency on three issues: #2626, #2550, #2510. All three carry status:plan-approved but plan bodies say plan-review / MAJOR-blocked / sustained-MAJOR-loop. Memory entry: feedback_label_vs_planbody_gate_inconsistency.md.

For each issue:
1. Read the latest comment thread (the 2026-05-15 halt comments are there) — confirm conditions still apply.
2. Read the plan body's "Status:" line and the most-recent cross-review verdicts in scripts/review/results/.
3. Decide one of: (a) rerun reviews to clear MAJOR (likely needs codex CLI fixed via #2715 first), (b) explicit override with truthful local marker .planning/plan-approved/<n>.md, (c) remove status:plan-approved label to honestly reflect plan-review state.

For #2550 specifically: the 2026-05-11 commit 106e8d476 set the precedent. Don't re-discover its findings — it's already on file at docs/reports/2026-05-11-issue-2550-approval-blocker.md.

Acceptance: each of the 3 issues has a clear gate state by end of session (consistent label + body + marker, or explicit override documented). No new implementation; this is a governance pass.
```

---

## Prompt 3 — Implement [#2694] cathodic edition-merge (~1-2 hr, T2 scope)

```
Implement #2694 cathodic protection edition-merge sub-piece. The bigger #2694 epic covers 6 duplicate-implementation cleanups (catenary, PipeCapacity, cathodic protection, natural-period, hydro-matrix, on-bottom stability) — this session ONLY does the cathodic sub-piece per the plan at docs/plans/2026-05-13-issue-2694-cathodic-protection-edition-merge-plan.md.

Preflight before implementation:
1. Verify the plan body "Status:" says plan-approved (not plan-review) — per feedback_label_vs_planbody_gate_inconsistency.md, halt if body disagrees with the label.
2. Check digitalmodel/src/digitalmodel/cathodic_protection/ for the file structure (already 10+ modules per last night's sweep).
3. Read the 2 investigation docs: commits 0594be8b5 (DNV edition decision investigation) and 0eb88735e (PipeCapacity 5-way canonicalization investigation).

Implementation pattern: similar to #2685 manual implementation (3 commits across digitalmodel + workspace-hub). digitalmodel is SEPARATE git repo per CLAUDE.md — cd in before commit. Watch for the same .gitignore surprises (knowledge/wikis/ rules) and ansys/__init__.py abandoned stash-pop conflict (may still be there if no one cleaned up).

Memory to consult:
- feedback_silent_verdict_flip_defect_class.md (cathodic protection example: two impls citing same standard but different sections → opposite verdicts at design margin)
- feedback_hermes_provider_openai_codex_routes_via_codex_exec.md (don't dispatch this via Hermes default profile while #2715 is open)

Acceptance: cathodic edition-merge plan ACs all PASS, tests green, commits land on digitalmodel + workspace-hub mains, close-out comment on #2694 noting THIS sub-piece is done with the other 5 still pending.
```

---

## Prompt 4 — Complete [#2702] audit (gated on #2715 closure)

```
Complete the #2702 routing-layer audit. The codex-hand finding is already documented at docs/sessions/2026-05-15-hermes-delegate-codex-trace.md (commit 8e3063530). Remaining ACs are blocked on #2715 (codex-cli stdin-hang) — only run this prompt AFTER #2715 closes / is fixed.

When #2715 is fixed:
1. Verify the fix: `timeout 30 bash -c 'echo "Say hello" | codex exec -'` should now exit 0.
2. Run live `hermes chat -z` delegate_task tests per plan pseudocode in docs/plans/2026-05-13-issue-2702-routing-layer-audit-plan.md sections "test_codex_hand" and "test_claude_code_hand". Capture traces at docs/sessions/2026-05-15-hermes-delegate-{codex,claude}-trace.md (codex one already exists from last session — append or replace per fix).
3. Bracket the Claude-Code-hand call with Anthropic console.anthropic.com pre/post snapshots. Use mcp__claude-in-chrome__* tools for the dashboard browsing. Save as docs/sessions/2026-05-15-anthropic-usage-{pre,post}.png.
4. Compute Δ_base and Δ_overage from the snapshots.
5. Update findings comment on #2702 with the Δ table + D7 decision (confirm / refute / ambiguous).
6. Post D7 reconciliation comment on #2695 (confirmation or child issue revising D7).
7. Remove status:blocked from #2702.

Acceptance: all 5 plan ACs PASS, #2702 closed, D7 either confirmed or revised via child issue.
```

---

## Prompt 5 — Investigate [#2715] upstream codex-cli hang (~30-60 min)

```
Triage #2715 codex-cli 0.130.0 stdin-hang regression. This is blocking #2702 audit completion AND blocking re-dispatch of #2685-style work via Hermes default profile (per #2718). Three possible paths:

1. Downgrade workaround: install codex-cli 0.123.0 via npm (per the prior #2479 workaround). Verify with `codex exec "say hello"` returns within 30s.
2. Upstream fix tracking: search openai/codex-cli GitHub issues for the stdin-hang regression. If filed, link in #2715. If not, file it with a minimal reproduction script.
3. Hermes config workaround: investigate whether Hermes can route via a non-codex-exec path for tool-using prompts (e.g., direct OpenAI API call instead of codex subprocess). May need `hermes config` review.

Memory: feedback_codex_cli_0_124_upstream_regression.md (prior recurrence — downgrade worked then), feedback_hermes_provider_openai_codex_routes_via_codex_exec.md (the Hermes routing chain).

Acceptance: one of the 3 paths chosen and documented in #2715. If downgrade: codex-cli 0.123.0 installed + verified. If upstream: link to upstream issue + reproduction. If config workaround: Hermes config change committed + dispatch smoke test.
```

---

## Prompt 6 — Morning catch-all triage (~10 min, every day)

```
Morning catch-all. Run this prompt at the start of any session to surface what's changed overnight without diving into a specific issue.

1. `gh issue list --repo vamseeachanta/workspace-hub --label "status:plan-approved" --state open --limit 30 --json number,title,labels --jq '[.[] | {n: .number, t: .title, l: ([.labels[].name] | map(select(test("priority:|agent:|status:"))) | join(","))}] | sort_by(.n) | reverse | .[] | "#\(.n) [\(.l)] \(.t)"'` — see plan-approved slate.
2. `git log --oneline --since="12 hours ago" main | head -30` (workspace-hub) and same in digitalmodel — see overnight commits.
3. `hermes kanban stats; hermes kanban list` — any dispatched tasks running, blocked, or done overnight.
4. `pgrep -af 'hermes|claude.*--print|codex exec'` — active parallel sessions.
5. Check if #2715 closed (`gh issue view 2715 --json state`) — if so, unblocks #2702 audit completion and re-enables dispatch.
6. Check open blockers: #2712 (ace-linux-2 PATH), #2718 (kanban-worker hazards), #2715 (codex-cli hang).

Surface a one-paragraph summary: what's new, what unblocked, what's still blocking. Then ask user where to focus.
```

---

## Suggested order

If you're doing one prompt: **Prompt 1** (fastest win, unlocks parallelism).
If you're doing all in one day: **Prompt 6** (catch-all) → **Prompt 1** (quick win) → **Prompt 5** (#2715 unblocks everything else) → **Prompt 4** (#2702 audit completion, now unblocked) → **Prompt 2** (gate reconcile) → **Prompt 3** (#2694 implementation).

If you're doing one *implementation* prompt: **Prompt 3** (#2694) is the highest-content piece remaining.
