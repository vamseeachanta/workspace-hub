# Plan for #2128: Wire enforcement-env and require-review-on-push into install-hooks pre-push chain

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-11
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2128
> **Review artifacts:** none yet — see Adversarial Review Summary for current-findings grounding

---

## Resource Intelligence Summary

### Existing repo code

- Found: `scripts/enforcement/install-hooks.sh` — installer copies enforcement-env to `.git/hooks/`, wires it into pre-commit, wires stage-prompt-drift into pre-push, wires learning pipeline into post-commit. Does NOT wire enforcement-env sourcing or require-review-on-push into pre-push.
- Found: `scripts/enforcement/enforcement-env.sh` — sets `FORCE_PLAN_GATE_STRICT=1`, `REVIEW_GATE_STRICT=1`, `DISABLE_ENFORCEMENT=0` as defaults. Git-tracked source of truth for enforcement strictness.
- Found: `scripts/enforcement/require-review-on-push.sh` — full review-evidence gate with commit classification, evidence checks, strict/warn/bypass modes, and latency logging.
- Found: `.git/hooks/pre-push` (live hook, lines 1-275) — already calls `require-review-on-push.sh` inline at lines 170-185, but defaults `REVIEW_GATE_STRICT` to `0` (line 176) instead of sourcing enforcement-env. Stage-prompt-drift block appended at lines 269-274, after `exit "$OVERALL_EXIT"` at line 267 — dead code.
- Found: `tests/enforcement/test_install_hooks_stage_prompt_drift.py` — 2 tests: string-presence of drift guard in pre-push, dry-run non-modification. No reachability, ordering, sourcing, or stdin-preservation checks.
- Found: `scripts/enforcement/tests/test_require_review_on_push.sh` — standalone tests for the review gate script.
- Found: `docs/governance/SESSION-GOVERNANCE.md` — documents the installer chain as if fully verified (line references: "pre-push -> review-gate -> stage-prompt-drift-gate -> repo/test gates").
- Found: `docs/standards/REVIEW_GATE_BYPASS_POLICY.md` — states `REVIEW_GATE_STRICT` defaults to `1`; contradicts the live pre-push hook's hardcoded `:-0` default.
- Found: `scripts/workflow/governance-checkpoints.yaml` — checkpoint `pre-push-review` marked `enforced: true` with note "strict mode as of 2026-04-09 (#1839)".

### Standards

| Standard | Status | Source |
|---|---|---|
| REVIEW_GATE_BYPASS_POLICY.md | active, contradicted by live hook | `docs/standards/` |
| HARD-STOP-POLICY.md | active, depends on review gate working | `docs/standards/` |

### LLM Wiki pages consulted

- N/A — no domain wiki pages are relevant to this enforcement-chain bug; current repo code, issue history, and governance docs were sufficient.

### Documents consulted

- `docs/handoffs/2026-04-10-stage-prompt-drift-exit-handoff.md` — records the push of the stage-prompt-drift suite; notes install-hooks.sh integration was delivered.
- `docs/governance/SESSION-GOVERNANCE.md` — Phase 1/2 of #1839 governance; documents advertised chain.
- `docs/standards/HARD-STOP-POLICY.md` — confirms this governance work sits under the broader session-governance enforcement umbrella.
- `docs/standards/REVIEW_GATE_BYPASS_POLICY.md` — defines strict review-gate defaults that the live pre-push hook currently contradicts.
- Issue #2128 body and comments — contain the posted adversarial findings and implementation handoff for this specific bug.
- `docs/plans/README.md` — planning index and required status semantics.

### Gaps identified

- **Gap 1 (enforcement-env not sourced in pre-push):** `install-hooks.sh` Step 2 wires enforcement-env into pre-commit only. No equivalent step for pre-push. The live pre-push hook hardcodes `REVIEW_GATE_STRICT:-0`, contradicting the enforcement-env default of `1`.
- **Gap 2 (require-review-on-push not in installer):** `install-hooks.sh` has no step that wires `require-review-on-push.sh` into pre-push. The live hook has it inline (not installer-managed), meaning fresh installs on other machines won't have it.
- **Gap 3 (dead code — stage-prompt-drift after exit):** `install-hooks.sh` uses `cat >>` which appends after any existing `exit`. The live hook's `exit "$OVERALL_EXIT"` at line 267 makes the appended drift guard (lines 269-274) unreachable.
- **Gap 4 (tests verify strings, not behavior):** Existing tests check that `require-stage-prompt-drift.sh` appears as text in the hook file. They don't verify execution ordering, reachability (code not after an exit), enforcement-env sourcing, or stdin preservation for push ref data.
- **Gap 5 (docs claim verified chain):** `SESSION-GOVERNANCE.md` and the installer's summary log describe the full chain as operational, but it is not.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-11-issue-2128-install-hooks-pre-push-chain-drift.md` |
| Installer under fix | `scripts/enforcement/install-hooks.sh` |
| Existing runtime hook reference | `scripts/hooks/pre-push.sh` |
| Tests | `tests/enforcement/test_install_hooks_stage_prompt_drift.py` |
| Governance docs | `docs/governance/SESSION-GOVERNANCE.md` |
| Plan review — Claude | not yet created |
| Plan review — Codex | not yet created |
| Plan review — Gemini | not yet created |

---

## Deliverable

A fixed `install-hooks.sh` that produces a pre-push hook with the complete, ordered, reachable enforcement chain — sourcing `enforcement-env`, calling `require-review-on-push.sh`, and calling `require-stage-prompt-drift.sh` — all BEFORE the hook's exit statement, with end-to-end tests proving ordered execution and preserved stdin ref data.

---

## Pseudocode

### install-hooks.sh — new Step 3 (wire full pre-push chain)

```
function wire_pre_push_chain(pre_push_path, dry_run):
    content = read(pre_push_path)
    
    # 3a: Source enforcement-env at top of hook (after set -euo pipefail)
    if "enforcement-env" not in content:
        insert_after_shebang_block(content, ENFORCEMENT_ENV_SOURCE_BLOCK)
    
    # 3b: Wire require-review-on-push BEFORE exit
    if "require-review-on-push.sh" not in content:
        insert_before_final_exit(content, REVIEW_GATE_BLOCK)
    
    # 3c: Wire stage-prompt-drift guard BEFORE exit
    if "require-stage-prompt-drift.sh" not in content:
        insert_before_final_exit(content, DRIFT_GUARD_BLOCK)
    
    # 3d: Fix any existing dead-code blocks (after exit)
    remove_blocks_after_final_exit(content)
    
    write(pre_push_path, content)
```

### Insertion strategy

```
function insert_before_final_exit(content, block):
    # Find the LAST `exit "$OVERALL_EXIT"` or `exit $?` line
    # Insert block on the line(s) immediately before it
    # This ensures reachability
    
    lines = content.split('\n')
    last_exit_index = find_last_exit_line(lines)
    lines.insert(last_exit_index, block)
    return '\n'.join(lines)
```

### Test: end-to-end installed chain

```
function test_installed_chain_executes_in_order(tmp_path):
    repo = make_repo(tmp_path)
    create_stub_scripts(repo)  # enforcement-env, review-gate, drift-gate
    
    run(install-hooks.sh, cwd=repo)
    
    pre_push = read(repo / ".git/hooks/pre-push")
    
    # Verify ordering: enforcement-env sourced BEFORE review gate, review gate BEFORE drift gate
    env_pos = position_of("enforcement-env", pre_push)
    review_pos = position_of("require-review-on-push.sh", pre_push)
    drift_pos = position_of("require-stage-prompt-drift.sh", pre_push)
    exit_pos = position_of_last("exit", pre_push)
    
    assert env_pos < review_pos < drift_pos < exit_pos
    
    # Verify no blocks exist AFTER final exit
    assert no_executable_lines_after(exit_pos, pre_push)
    
    # Execute the hook with stdin ref data and verify it's preserved
    result = run_hook_with_stdin(repo, "refs/heads/main LOCAL_OID refs/heads/main REMOTE_OID")
    assert result.returncode in (0, 1)  # gate verdict, not crash
    assert "enforcement-env" in stub_execution_log(repo)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/enforcement/install-hooks.sh` | Replace append-only pre-push patching with reachable insertion or regeneration that wires enforcement-env, review-gate, and drift-gate before the final exit, while preserving downstream repo/test gates and stdin behavior. |
| Extend | `tests/enforcement/test_install_hooks_stage_prompt_drift.py` | Expand the current installer tests from string-presence checks into installed-hook E2E coverage for sourcing, ordering, reachability, idempotency, dry-run behavior, and preserved stdin ref data. |
| Reference / inspect | `scripts/hooks/pre-push.sh` | Use the tracked runtime hook as the behavioral baseline for downstream repo/test gates and stdin buffering expectations. |
| Modify | `docs/governance/SESSION-GOVERNANCE.md` | Align the documented pre-push chain with the actual installed hook behavior after the fix. |
| Update | `docs/plans/README.md` | Add this plan to index. |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_enforcement_env_sourced_in_pre_push` | enforcement-env sourcing block appears in pre-push after install | Fresh repo with pre-push stub | Pre-push contains `source.*enforcement-env` before any gate calls |
| `test_review_gate_wired_into_pre_push` | require-review-on-push.sh call appears in pre-push after install | Fresh repo with pre-push stub | Pre-push contains `require-review-on-push.sh` |
| `test_drift_guard_wired_into_pre_push` | stage-prompt-drift guard appears in pre-push after install | Fresh repo with pre-push stub | Pre-push contains `require-stage-prompt-drift.sh` |
| `test_chain_order_enforcement_env_before_review_before_drift` | enforcement-env < review-gate < drift-gate in line ordering | Fresh repo, run installer | `pos(enforcement-env) < pos(review-gate) < pos(drift-guard)` |
| `test_all_gates_before_final_exit` | no gate block appears after the last `exit` line | Fresh repo, run installer | No executable lines after final `exit` |
| `test_dead_code_cleanup` | if existing pre-push has blocks after exit, installer moves them | Pre-push with drift guard after exit (like current live state) | Drift guard moved above exit; nothing after exit |
| `test_stdin_preserved_through_chain` | push ref data on stdin is not consumed by early gates | Fresh repo, run hook with piped stdin | All gates receive or can read ref data |
| `test_idempotent_double_install` | running installer twice produces identical pre-push content | Fresh repo, install x2 | Content identical after 1st and 2nd run |
| `test_dry_run_does_not_modify` | --dry-run reports what would change but modifies nothing | Fresh repo, --dry-run | Pre-push unchanged; stdout describes planned changes |
| `test_existing_drift_test_reachability` | (in existing test file) drift guard is before exit | Fresh repo, run installer | `require-stage-prompt-drift.sh` line number < exit line number |

---

## Acceptance Criteria

- [ ] `bash scripts/enforcement/install-hooks.sh` on a fresh repo produces pre-push with enforcement-env sourced, review-gate called, drift-guard called — all before final exit
- [ ] Running installer on existing live repo (with dead-code drift guard after exit) moves the drift guard above exit and wires missing components
- [ ] `uv run pytest tests/enforcement/test_install_hooks_stage_prompt_drift.py -v` — expanded installer-chain tests pass
- [ ] `uv run pytest tests/enforcement/test_stage_prompt_drift_status.py -v` — status/doctor coverage still passes after installer changes
- [ ] `uv run pytest tests/enforcement/ -v` — no regressions in enforcement test suite
- [ ] Installer summary log (lines 153-156) matches actual installed chain
- [ ] `docs/governance/SESSION-GOVERNANCE.md` updated to reflect #2128 fix
- [ ] docs/plans/README.md updated with this plan entry

---

## Adversarial Review Summary

> **Note:** No plan-specific review artifacts exist yet under `scripts/review/results/` for issue #2128. The findings below are grounded in current issue investigation and implementation handoff analysis, not formal adversarial review submissions. This section documents the evidence base used to draft the plan and will be replaced by provider review verdicts once adversarial review is conducted.

| Source | Type | Key findings |
|---|---|---|
| Issue investigation | Current finding | install-hooks.sh Step 3 uses `cat >>` append, which places new blocks after any existing `exit` — confirmed dead code in live `.git/hooks/pre-push` lines 269-274 |
| Issue investigation | Current finding | install-hooks.sh has no step to source enforcement-env in pre-push (only pre-commit gets it); no step to wire require-review-on-push.sh at all |
| Issue investigation | Current finding | Live pre-push hook hardcodes `REVIEW_GATE_STRICT:-0` (line 176), contradicting enforcement-env.sh default of `1` and REVIEW_GATE_BYPASS_POLICY.md which states strict is the default |
| Handoff analysis | Implementation finding | `docs/handoffs/2026-04-10-stage-prompt-drift-exit-handoff.md` records install-hooks.sh integration as delivered but did not verify reachability in the installed hook |
| Test gap analysis | Current finding | `test_install_hooks_stage_prompt_drift.py` checks `"require-stage-prompt-drift.sh" in pre_push` (string presence) but not `line_number(drift_guard) < line_number(exit)` (reachability) |
| Doc drift analysis | Current finding | `SESSION-GOVERNANCE.md` and installer summary log (line 155) both claim `pre-push -> review-gate -> stage-prompt-drift-gate -> repo/test gates` — a chain that is not produced by the installer |

**Overall status:** DRAFT — pending formal adversarial review before promotion to `plan-review`.

**Critical implementation note from findings:**
The `insert_before_final_exit` strategy is the key architectural decision. The current `cat >>` approach is fundamentally broken for hooks that already have an exit statement. The fix must use sed/awk insertion before the exit line, not append. The stdin-preservation concern (finding #6 from the issue) arises because the pre-push hook reads stdin to get push ref data (lines 53-56 in live hook) — any gate script that also reads stdin would consume the data. The review gate and drift gate must NOT read stdin; they should receive OIDs as arguments.

---

## Risks and Open Questions

- **Risk:** The live `.git/hooks/pre-push` already has an inline review-gate block (lines 170-185) that is NOT installer-managed. The installer must detect this existing block and either (a) skip wiring if already present, or (b) replace it with the installer-managed version that sources enforcement-env for the correct default. Recommend option (a) with a log message noting the existing inline block.
- **Risk:** stdin consumption — pre-push receives push ref data on stdin (local_ref, local_oid, remote_ref, remote_oid). The existing hook reads and buffers it at lines 53-56. Any sub-script that reads stdin without the hook first buffering it would lose this data. Current architecture buffers stdin into `PUSH_LINES` before any gates run, so this is safe — but tests must verify this invariant holds after the fix.
- **Risk:** The live hook's inline `REVIEW_GATE_STRICT:-0` default at line 176 contradicts `enforcement-env.sh` and `REVIEW_GATE_BYPASS_POLICY.md`. If enforcement-env is sourced early in the hook, the `:-0` fallback becomes irrelevant because the variable is already set to `1`. But if someone removes the env sourcing later, the hook silently degrades to advisory mode. Consider changing the inline default to `:-1` as defense-in-depth.
- **Open:** Should install-hooks.sh also fix the live hook's inline `REVIEW_GATE_STRICT:-0` default, or only add the enforcement-env sourcing and trust the env to override it? Recommend: change the inline default to `:-1` AND add enforcement-env sourcing.
- **Open:** Should the installer create a backup of the existing pre-push hook before modifying it? Current behavior for pre-commit and post-commit does not back up. Recommend: add a `.bak` copy for pre-push given the complexity of the modifications.
- **Umbrella:** This issue is tracked under #1839 (session governance enforcement). The fix should reference both #2128 and #1839 in commit messages.

---

## Complexity: T2

**T2** — modifies one installer script with non-trivial insertion logic (before-exit vs. append), substantially expands the existing installer test module, and updates one governance doc. No broad architectural change, but the insertion strategy requires careful handling of existing hook state, dead-code cleanup, idempotency, and stdin-preservation behavior.
