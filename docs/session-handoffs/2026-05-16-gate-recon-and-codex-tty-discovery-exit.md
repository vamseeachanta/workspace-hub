# Exit handoff — gate-reconciliation batch + codex-cli TTY-detection discovery

Date: 2026-05-16
Repository: `vamseeachanta/workspace-hub`
Predecessor entry handoff: [`2026-05-15-issue-81-perforating-authoring-exit.md`](2026-05-15-issue-81-perforating-authoring-exit.md) (which included the 5-prompt slate executed here)
Session model: Claude Opus 4.7 (1M context)

## What this session did

Executed 4 of 5 items from the predecessor slate (item 4 was already CLOSED before this session started). Resolved cross-machine dispatch capability question, reconciled gate state on 4 mis-labeled issues, materialized 2 user-authorized plan-approval markers, and significantly refined the codex-cli 0.130.0 hang diagnosis from "auth-layer / non-deterministic" to "TTY-detection layer" with a reliable `script -qc` workaround.

## Landing commits

| Commit | Scope |
|---|---|
| `a4ac3093c` | chore(planning): materialize plan-approval markers for #2694 + #2510. 3 files, 74+/1-. Pre-commit `[plan-gate] PASS`. |

## GH state changes

| Issue | Action | Reason |
|---|---|---|
| [#2712](https://github.com/vamseeachanta/workspace-hub/issues/2712) | Closed as `NOT_PLANNED` with [diagnostic comment](https://github.com/vamseeachanta/workspace-hub/issues/2712#issuecomment-4464990520) | Live-state verification: gateway systemd-user-unit env already has hermes in PATH; original RCA conflated SSH-session PATH with worker-subprocess PATH. Recommended sudo symlink was unnecessary. |
| [#2721](https://github.com/vamseeachanta/workspace-hub/issues/2721) | Filed (NEW) with `priority:high, cat:ai-orchestration, cat:harness, domain:agent-cost-tracking` | `submit-to-codex.sh:197-220` silently degrades in non-TTY contexts. 2026-04-20 wrapper comment claims `</dev/null` is sufficient — true for 0.121.0, false for 0.130.0. Retrofit needed with `script -qc`. |
| [#2550](https://github.com/vamseeachanta/workspace-hub/issues/2550) | Removed `status:plan-approved` label + posted [governance comment](https://github.com/vamseeachanta/workspace-hub/issues/2550#issuecomment-4466553204) | Plan-body says plan-review, 2/3 substantive verdicts MAJOR, marker absent, prior approval-blocker report at `docs/reports/2026-05-11-issue-2550-approval-blocker.md`, 2026-05-15 halt comment by owner explicitly recommended removing. |
| [#2626](https://github.com/vamseeachanta/workspace-hub/issues/2626) | Posted [governance comment](https://github.com/vamseeachanta/workspace-hub/issues/2626#issuecomment-4466553167); label retained pending rerun-on-codex-fix | Plan body says plan-review, codex+gemini MAJOR with 4 architectural defects, claude UNAVAILABLE; rerun gated on [#2715](https://github.com/vamseeachanta/workspace-hub/issues/2715) / [#2721](https://github.com/vamseeachanta/workspace-hub/issues/2721). |
| [#2510](https://github.com/vamseeachanta/workspace-hub/issues/2510) | Posted [governance comment](https://github.com/vamseeachanta/workspace-hub/issues/2510#issuecomment-4466553251); then wrote marker + patched plan body Status line | User had already issued sustained-MAJOR loop-break override on 2026-05-13; this session materialized the gate-leg reconciliation. |
| [#2694](https://github.com/vamseeachanta/workspace-hub/issues/2694) | Posted [implementation-blocked comment](https://github.com/vamseeachanta/workspace-hub/issues/2694#issuecomment-4466553300); then wrote marker per user authorization | Plan body said approved (r3 loop-break), label agreed, marker was the holdout; user explicitly authorized marker creation. |
| [#2715](https://github.com/vamseeachanta/workspace-hub/issues/2715) | Posted [diagnostic update](https://github.com/vamseeachanta/workspace-hub/issues/2715#issuecomment-4466568295) + [TTY-faking follow-up](https://github.com/vamseeachanta/workspace-hub/issues/2715#issuecomment-4466840108) | Auth-layer hypothesis ruled out (`codex login status` returns instantly). Symptom is TTY-detection layer. `script -qc 'codex exec "..."' /dev/null` works reliably in 41s. |

## Hermes kanban changes

| Task ID | Action | Reason |
|---|---|---|
| `t_46df565b` | Archived | [#2685](https://github.com/vamseeachanta/workspace-hub/issues/2685) already LANDED 2026-05-15 — stale queue entry |
| `t_5c352d5d` | Archived | [#2702](https://github.com/vamseeachanta/workspace-hub/issues/2702) already CLOSED 2026-05-15 — stale queue entry |

ace-linux-1 kanban now reflects reality: 4 `blocked` entries remain ([#2528](https://github.com/vamseeachanta/workspace-hub/issues/2528), [#2626](https://github.com/vamseeachanta/workspace-hub/issues/2626), [#2550](https://github.com/vamseeachanta/workspace-hub/issues/2550), [#2694](https://github.com/vamseeachanta/workspace-hub/issues/2694)).

## Memory file changes

| Type | File | Change |
|---|---|---|
| NEW | `feedback_rca_conflated_ssh_vs_subprocess_path.md` | Diagnostic pattern for "executable not found in spawned subprocess" symptoms: read `/proc/<pid>/environ` not `echo $PATH`. Indexed in MEMORY.md. |
| REOPENED | `feedback_codex_cli_0_124_upstream_regression.md` | Status flipped from `RESOLVED on 0.130.0 (2026-05-11)` to `TTY-faking workaround identified 2026-05-16`. Operational fix is now `script -qc 'cmd' /dev/null`, not `</dev/null`. Added to MEMORY.md index. |
| UPDATED | `project_ace_linux_2_dispatch_capability.md` | kanban-worker-spawn marked ✓ verified (was ✗ blocked). Pointed at [[feedback_rca_conflated_ssh_vs_subprocess_path]] for the live diagnostic recipe. |

## Hard discoveries

1. **TTY-detection is the codex-cli 0.130.0 hang root cause.** Three diagnostic sessions across three weeks (2026-04-24 → 2026-05-11 → 2026-05-15 → 2026-05-16) finally converged. Memory entries marked RESOLVED were correct *for TTY contexts* but didn't generalize. The literal banner difference is the smoking gun:
   - Non-TTY: only `Reading additional input from stdin...` prints, then hang
   - TTY: full `OpenAI Codex v0.130.0 / workdir: / model: ...` banner prints in 41s
2. **`scripts/review/submit-to-codex.sh` is silently degraded** for all non-TTY callers (cron, Hermes worker, background bash). The wrapper's `</dev/null` advice dates from codex 0.121.0 and was never re-validated when codex versions advanced. Filed at [#2721](https://github.com/vamseeachanta/workspace-hub/issues/2721).
3. **All 4 gate-inconsistent issues had the SAME shape: missing marker file.** [#2626](https://github.com/vamseeachanta/workspace-hub/issues/2626), [#2550](https://github.com/vamseeachanta/workspace-hub/issues/2550), [#2510](https://github.com/vamseeachanta/workspace-hub/issues/2510), [#2694](https://github.com/vamseeachanta/workspace-hub/issues/2694) all carried `status:plan-approved` labels but lacked `.planning/plan-approved/<n>.md`. Three had plan-body disagreeing too; one had label+plan-body agreement with only marker as holdout. Two memory rules together ([[feedback_label_vs_planbody_gate_inconsistency]] + [[feedback_dispatch_local_marker_rationalization]]) form complete coverage of the gate-state defect class.
4. **The #2712 issue body's RCA was wrong.** It conflated SSH-non-login-session PATH (lacks `~/.local/bin`) with daemon-subprocess PATH (inherits via systemd user manager, has both `~/.local/bin` AND `~/.hermes/hermes-agent/venv/bin`). Recommended sudo symlink was belt-and-braces only, not unblocking anything currently broken. Generalized as [[feedback_rca_conflated_ssh_vs_subprocess_path]].

## Memory triggers honoured

- [[feedback_check_parallel_work]] — preflight `pgrep -af 'hermes|claude.*--print|codex exec'` at session start identified 2 Hermes TUI sessions + gateway + llm-wiki freshness shell; none collided with target work
- [[feedback_subagent_write_phantom]] — all 4 research subagents were explicitly tasked read-only; main session did all GH-mutation + file-write work
- [[feedback_never_offer_to_self_label_plan_approved]] — markers materialized ONLY after explicit user instruction "1. yes" / "2. write marker + plan"; never offered to self-create
- [[feedback_dispatch_local_marker_rationalization]] — #2694's label+plan-body agreement was specifically NOT rationalized into a self-written marker before user authorization
- [[feedback_retry_loop_sweep_contamination]] — pathspec commit form `git commit -m "..." -- <files>` used to avoid sweeping ~15 dirty auto-sync files
- [[feedback_git_status_lock_storm]] — orphan `index.lock` (0 bytes, May 16 06:00) removed after confirming no active git PIDs and no fuser holders
- [[feedback_mock_vs_live_invocation_divergence]] — codex-cli reverification done with live `timeout 90 codex exec "..."`, not against memory's prior verification claim
- [[feedback_inline_gh_issue_url]] — issue references throughout this handoff and posted comments use Markdown hyperlink form
- [[feedback_label_vs_planbody_gate_inconsistency]] — explicitly invoked across all 4 gate-recon subagent prompts; surfaced state without taking action beyond what user authorized
- [[feedback_gh_issue_close_silent_comment_drop]] — comment posted BEFORE label removal on [#2550](https://github.com/vamseeachanta/workspace-hub/issues/2550); comment posted BEFORE issue close on [#2712](https://github.com/vamseeachanta/workspace-hub/issues/2712)

## Caveats / known state

- **Hermes TUI sessions still running**: PIDs 1554086, 1557490, gateway PID 1807589, two `gpt-5.5` slash-workers (PIDs 1773579, 1810443). Earlier-day spawn; not currently executing per the slot-worker probe but they're alive. Future-session preflight `pgrep` will show them — they're not zombies.
- **Codex 0.130.0 broken for non-TTY**: any `bash -c '...'` invocation of `codex exec` will hang until [#2721](https://github.com/vamseeachanta/workspace-hub/issues/2721) lands. Until then, use `script -qc 'codex exec "..."' /dev/null` everywhere.
- **Cross-review fanout currently producing degraded verdicts**: every run from cron/background context is Codex-UNAVAILABLE silently. Treat consensus signals as 2-provider until [#2721](https://github.com/vamseeachanta/workspace-hub/issues/2721) lands.
- **Repository .git was lock-contended mid-session**: orphan `.git/index.lock` removed cleanly (0 bytes + no holding PID). If a future session hits the same, the same recipe applies. Could be promoted to a pre-commit-recovery hook later.
- **MEMORY.md was modified mid-session** by the user / linter — added [[feedback_parallel_subagent_shared_target_manifest_deferral]] index entry. Not session-blocking but indicates active memory curation in parallel.

## Open threads — next-session prompts

The following 5 prompts are ready to drop into a fresh session. Each is self-contained; numbered roughly in dependency order (1 unblocks others).

### 1. Implement [#2721](https://github.com/vamseeachanta/workspace-hub/issues/2721) wrapper retrofit (~1-2 hr, T2)

Implement [#2721](https://github.com/vamseeachanta/workspace-hub/issues/2721) — retrofit `scripts/review/submit-to-codex.sh:run_codex_exec` (line 214-220) to wrap codex invocation with `script -qc 'CODEX_BIN exec "..."' /dev/null` instead of bare `CODEX_BIN exec "..." </dev/null`. The minimal-patch sketch is in the issue body. Acceptance: cross-review fanout from cron/background context captures full Codex verdict (not just banner), plus a regression test `tests/wrappers/test_codex_tty_emulation.sh` that exercises the non-TTY path.

Preflight: read [[feedback_codex_cli_0_124_upstream_regression]] memory entry for current operational fix details. Also check `scripts/review/cross-review.sh` for any other codex invocation paths that need the same retrofit (grep for `\bcodex\b exec\|CODEX_BIN exec`). Note: digitalmodel is a SEPARATE repo per CLAUDE.md but this wrapper lives in workspace-hub.

Per [[feedback_label_vs_planbody_gate_inconsistency]] [#2721](https://github.com/vamseeachanta/workspace-hub/issues/2721) doesn't have a plan yet — this is a fresh issue. Either author a quick T2 plan first (Resource Intel + 1-3 phases) and cross-review it, OR if scope feels T1, push direct with attestation.

### 2. File upstream openai/codex issue for [#2715](https://github.com/vamseeachanta/workspace-hub/issues/2715) (~30 min, no code)

File an upstream issue at https://github.com/openai/codex/issues for the TTY-detection regression. Minimal reproducer is in [#2715](https://github.com/vamseeachanta/workspace-hub/issues/2715)'s TTY-followup comment:

```bash
# Hangs (no TTY)
bash -c 'codex exec "Reply: hi" </dev/null' &  # waits forever
# Works (with TTY emulation)
bash -c 'script -qc "codex exec \"Reply: hi\"" /dev/null' &  # 41s
```

Reference existing upstream issues that may already track this:
- [openai/codex#20919](https://github.com/openai/codex/issues/20919) (closest match)
- [openai/codex#19945](https://github.com/openai/codex/issues/19945)
- [openai/codex#14048](https://github.com/openai/codex/issues/14048)

If any of those already cover today's symptom, just add a +1 comment with the workaround instead of filing new. Post a follow-up comment on [#2715](https://github.com/vamseeachanta/workspace-hub/issues/2715) linking to whatever upstream issue you ended up at.

### 3. Implement [#2694](https://github.com/vamseeachanta/workspace-hub/issues/2694) cathodic edition-merge (~1-2 hr, T2)

Marker materialized this session (`.planning/plan-approved/2694.md`, commit `a4ac3093c`). All 3 gate-legs now agree. Plan is at `docs/plans/2026-05-13-issue-2694-cathodic-protection-edition-merge-plan.md`.

Scope: ONLY the cathodic sub-piece (6 modules per plan §Files to Change). The other 5 sub-pieces (catenary, PipeCapacity, natural-period, hydro-matrix, on-bottom stability) require separate markers.

Preflight: read `.claude/rules/calc-citation-contract.md` — DNV-RP-B401 2017 AND 2021 editions will both need `Citation` sidecar emission per the pilot at [#2685](https://github.com/vamseeachanta/workspace-hub/issues/2685). Cross-repo commit dance per plan §Cross-Repo Strategy (digitalmodel is separate git repo).

### 4. Implement [#2510](https://github.com/vamseeachanta/workspace-hub/issues/2510) python layout/CAD demo (~2-4 hr, T2)

Marker materialized this session (`.planning/plan-approved/2510.md`, commit `a4ac3093c`). Plan body Status line synced. Plan is at `docs/plans/2026-04-26-issue-2510-python-layout-cad-automation-demo.md` (r14 / sustained-MAJOR loop-break).

Preflight: this is semiconductor-CAD scope, NOT offshore-CAD ([#2327](https://github.com/vamseeachanta/workspace-hub/issues/2327)/[#2328](https://github.com/vamseeachanta/workspace-hub/issues/2328)/[#2329](https://github.com/vamseeachanta/workspace-hub/issues/2329) cover the offshore side). The 2026-05-04 r14 verdicts (Claude MINOR, Codex MAJOR, Gemini UNAVAILABLE) plus user's sustained-MAJOR override means Codex objections are out-of-scope for implementation review — they're recorded as opt-in technical debt per [[feedback_codex_sustained_major_loop]].

### 5. Rerun [#2626](https://github.com/vamseeachanta/workspace-hub/issues/2626) cross-review after [#2721](https://github.com/vamseeachanta/workspace-hub/issues/2721) lands (~30-60 min)

Gated on prompt 1. Once `submit-to-codex.sh` retrofit is in place, rerun the cross-review fanout for [#2626](https://github.com/vamseeachanta/workspace-hub/issues/2626). Plan body identifies 4 MAJOR architectural defects in Codex/Gemini r1 review that need to be patched first — read those before rerunning to budget the patch work.

If reviews come back clean: write `.planning/plan-approved/2626.md` marker (per user authorization at that point) and patch plan body Status from `plan-review` to `approved`. Then [#2626](https://github.com/vamseeachanta/workspace-hub/issues/2626) is ready for execution.

### Bootstrap recon (run at the start of any next session)

```bash
# In any order — independent reads
hermes kanban stats; hermes kanban list                            # workspace-hub queue state
pgrep -af 'hermes|claude.*--print|codex exec'                      # active parallel sessions
gh issue view 2721 --repo vamseeachanta/workspace-hub --json state # has wrapper retrofit landed?
gh issue view 2715 --repo vamseeachanta/workspace-hub --json state # upstream-fix landed?
ls .planning/plan-approved/26*.md 2>&1                             # marker state for in-flight
git log --oneline -5                                               # recent landing
```

If `.git/index.lock` exists from prior session: confirm it's 0 bytes + no holding PID + dated before session start, then `rm` and retry per [[feedback_git_status_lock_storm]].
