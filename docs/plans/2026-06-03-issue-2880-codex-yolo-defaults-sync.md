# Plan for #2880: codex yolo-equivalent permission defaults travel across machines

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-06-03
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2880
> **Client:** N/A
> **Review artifacts:** scripts/review/results/2026-06-03-plan-2880-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `config/agents/codex/config.toml` — repo-tracked Codex template; contains `model`, `model_reasoning_effort`, and `[status_line]` section only. `approval_policy` and `sandbox_mode` are absent.
- Found: `scripts/_core/sync-agent-configs.sh:221` — `managed_keys = {'model', 'model_reasoning_effort'}` in Python block 1 (main path). Yolo keys are not in this set; fresh-machine sync will not install them.
- Found: `scripts/_core/sync-agent-configs.sh:409` — identical `managed_keys` in Python block 2 (uv fallback path). Both blocks must be updated together or the fallback path remains broken.
- Found: `scripts/_core/tests/test_sync_agent_configs.sh:56` — `assert_managed_keys_root_only` validates only `model` and `model_reasoning_effort`; zero coverage for yolo keys.
- Found: `config/workstations/registry.yaml` — `dev-secondary` (ace-linux-2) declares `agent_clis: [claude]`; codex is not listed despite being active there.
- Found: `docs/session-handoffs/2026-05-30-codex-yolo-defaults-exit.md` — prior session evidence: `approval_policy = "never"` and `sandbox_mode = "danger-full-access"` verified via `codex doctor --summary` on codex-cli 0.135.0 on ace-linux-2.
- Gap: `managed_keys` expansion in `sync-agent-configs.sh` will overwrite any locally-customized values for these keys on next sync. This is intentional (the user wants the defaults to travel) but must be documented explicitly.

### Standards
Not applicable.

### LLM Wiki pages consulted
No relevant wiki pages.

### Documents consulted
- `docs/session-handoffs/2026-05-30-codex-yolo-defaults-exit.md` — exact key values and `codex doctor` verification command; confirms ace-linux-2 was hand-patched.
- `scripts/_core/sync-agent-configs.sh` (1365 lines) — full sync architecture; `sync_codex_managed_config` function; two Python blocks at lines 221 and 409 defining `managed_keys`.
- `scripts/_core/tests/test_sync_agent_configs.sh` (420 lines) — existing test structure; confirmed no tests cover `approval_policy` or `sandbox_mode`.
- Issue #2880 body — acceptance criteria, security-tradeoff declaration, and explicit constraint: "No secrets or machine-specific auth files added to repo-tracked config."

### Gaps identified
- `config/agents/codex/config.toml` missing both yolo keys.
- `managed_keys` in `sync-agent-configs.sh` does not include yolo keys — new-machine sync will not install them.
- No regression test for yolo-key propagation during sync.
- `config/workstations/registry.yaml` ace-linux-2 entry incorrectly omits codex from `agent_clis`.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-06-03 via GitHub MCP):
- `#2880` — OPEN — "feat(codex): make yolo-equivalent permission defaults travel across machines"

**File existence** (verified by resource intel agent 2026-06-03):
- EXISTS: `config/agents/codex/config.toml`
- EXISTS: `scripts/_core/sync-agent-configs.sh`
- EXISTS: `scripts/_core/tests/test_sync_agent_configs.sh`
- EXISTS: `config/workstations/registry.yaml`
- EXISTS: `docs/session-handoffs/2026-05-30-codex-yolo-defaults-exit.md`

**Line excerpts** (from resource intel agent):
```toml
# config/agents/codex/config.toml (current — missing keys)
model = "gpt-5.5"
model_reasoning_effort = "medium"

[status_line]
enabled = true
items = ["model", "project_root", "git_branch", "cwd",
         "context_window_used_percentage", "limit_5h_remaining_percentage",
         "limit_weekly_remaining_percentage", "token_count"]
```

```python
# sync-agent-configs.sh:221 — managed_keys Python block 1
managed_keys = {'model', 'model_reasoning_effort'}
# sync-agent-configs.sh:409 — managed_keys Python block 2 (uv fallback — identical)
managed_keys = {'model', 'model_reasoning_effort'}
```

**Gap proofs:**
- `grep "approval_policy\|sandbox_mode" config/agents/codex/config.toml` → 0 matches → keys absent in template.
- `grep "approval_policy\|sandbox_mode" scripts/_core/sync-agent-configs.sh` (managed_keys blocks) → 0 matches → keys not managed by sync.

**Reproduction proof:**
```
# From session handoff 2026-05-30-codex-yolo-defaults-exit.md:
# Before local patch on ace-linux-2:
#   codex doctor --summary → "restricted fs + enabled network · approval OnRequest"
# After local ~/.codex/config.toml patch:
#   codex doctor --summary → "unrestricted fs + enabled network · approval Never"
# repo config/agents/codex/config.toml UNCHANGED → fresh machine will not have these defaults
```
- Failure mode: fresh-machine sync does not install yolo defaults. Matches issue claim: YES.

<!-- Verification: 5 distinct sources: issue body (#2880), config.toml, sync-agent-configs.sh, test_sync_agent_configs.sh, session-handoffs/2026-05-30. Count: 5 ✓ -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-06-03-issue-2880-codex-yolo-defaults-sync.md` |
| Template | `config/agents/codex/config.toml` |
| Sync script | `scripts/_core/sync-agent-configs.sh` |
| Tests (modified) | `scripts/_core/tests/test_sync_agent_configs.sh` |
| Registry | `config/workstations/registry.yaml` |
| Plan review — Claude | `scripts/review/results/2026-06-03-plan-2880-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-06-03-plan-2880-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-06-03-plan-2880-gemini.md` |

---

## Deliverable

`config/agents/codex/config.toml` declares yolo-equivalent defaults, `sync-agent-configs.sh` treats `approval_policy` and `sandbox_mode` as managed keys, so a fresh Codex install synced from the repo arrives in yolo mode on any machine where codex is active.

---

## Pseudocode

```
# 1. config/agents/codex/config.toml — append after model_reasoning_effort:
approval_policy = "never"
sandbox_mode = "danger-full-access"
# SECURITY: danger-full-access removes all filesystem restrictions.
# Applies to interactive operator sessions on trusted machines only.
# Never set this in .codex/agents/*.toml (agent-role configs).

# 2. sync-agent-configs.sh — expand managed_keys in BOTH Python blocks (lines 221, 409):
managed_keys = {
    'model',
    'model_reasoning_effort',
    'approval_policy',    # new
    'sandbox_mode',       # new
}

# 3. tests/test_sync_agent_configs.sh — new test function:
test_yolo_keys_propagate_on_fresh_sync():
    TMPDIR=$(mktemp -d)
    cp config/agents/codex/config.toml $TMPDIR/template.toml
    # target has no yolo keys
    cat > $TMPDIR/target.toml <<EOF
model = "gpt-4o"
EOF
    run sync_codex_managed_config with template=$TMPDIR/template.toml target=$TMPDIR/target.toml
    grep -q 'approval_policy = "never"' $TMPDIR/target.toml   || fail
    grep -q 'sandbox_mode = "danger-full-access"' $TMPDIR/target.toml || fail

test_yolo_keys_model_local_override_preserved():
    # model in target differs from template — local override must be preserved
    target has: model = "gpt-4o"
    template has: model = "gpt-5.5"
    after sync: target model must still be "gpt-4o" (managed but not forced)
    # (matches existing managed_keys semantics: upsert if absent, preserve if present)
    NOTE: verify what the existing semantics actually are for managed_keys —
          if managed_keys always overwrite, document that explicitly in the AC.
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `config/agents/codex/config.toml` | Add `approval_policy = "never"` and `sandbox_mode = "danger-full-access"` with inline security comment |
| Modify | `scripts/_core/sync-agent-configs.sh:221` | Add `'approval_policy'` and `'sandbox_mode'` to `managed_keys` in Python block 1 |
| Modify | `scripts/_core/sync-agent-configs.sh:409` | Same addition in Python block 2 (uv fallback) — must match block 1 exactly |
| Modify | `scripts/_core/tests/test_sync_agent_configs.sh` | Add `test_yolo_keys_propagate_on_fresh_sync` and `test_yolo_keys_no_agent_role_leakage` test cases; update `assert_managed_keys_root_only` to expect 4 managed keys |
| Modify | `config/workstations/registry.yaml` | Add `codex` to `dev-secondary` (ace-linux-2) `agent_clis` list |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_yolo_keys_propagate_on_fresh_sync` | approval_policy + sandbox_mode are written to a target that lacks them | template with both keys; target without them | target contains both keys with correct values after sync |
| `test_yolo_keys_uv_fallback_path_also_managed` | Python block 2 (uv fallback) also propagates yolo keys | same scenario, exercising uv fallback path | same as above — both blocks must behave identically |
| `test_yolo_keys_no_agent_role_leakage` | yolo keys are NOT written to `.codex/agents/*.toml` agent-role configs | agent-role config file in scope | agent-role config unchanged; only `~/.codex/config.toml` target receives them |
| `test_managed_keys_count_now_four` | `assert_managed_keys_root_only` accepts 4 managed keys | post-sync target | passes without error for `model`, `model_reasoning_effort`, `approval_policy`, `sandbox_mode` |

---

## Acceptance Criteria

- [ ] `config/agents/codex/config.toml` contains `approval_policy = "never"` and `sandbox_mode = "danger-full-access"` with a security comment.
- [ ] `managed_keys` in `sync-agent-configs.sh` includes `approval_policy` and `sandbox_mode` in **both** Python blocks (lines ~221 and ~409).
- [ ] New tests in `test_sync_agent_configs.sh` pass: yolo keys propagate on fresh sync; agent-role configs (`.codex/agents/*.toml`) are not affected.
- [ ] `config/workstations/registry.yaml` `dev-secondary` (ace-linux-2) `agent_clis` includes `codex`.
- [ ] Security tradeoff explicit in `config/agents/codex/config.toml` comment: `danger-full-access` is for trusted interactive operator sessions only, not agent-role configs.
- [ ] `codex doctor --summary` on ace-linux-2 post-sync reports `unrestricted fs · approval Never` — record the output as a comment on issue #2880.
- [ ] No secrets, tokens, or machine-specific auth strings in any repo-tracked file.
- [ ] All existing `sync-agent-configs.sh` tests continue to pass (no regression).
- [ ] Review artifacts posted to `scripts/review/results/`.

---

## Adversarial Review Summary

<!-- Filled after adversarial review. Do not post to GitHub until populated. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | — | — |
| Codex | — | — |
| Gemini | — | — |

**Overall result:** pending

---

## Risks and Open Questions

- **Risk:** Expanding `managed_keys` will overwrite any locally-customized `approval_policy` or `sandbox_mode` on next sync. This is the intended behavior per the issue, but must be documented in the config comment.
- **Risk:** Two identical Python blocks (`managed_keys` at lines 221 and 409) — if only one is updated, the uv-fallback path will silently diverge. Plan explicitly requires both; tests must cover both paths.
- **Risk:** `danger-full-access` removes all filesystem sandbox. If this config value accidentally propagates to agent-role `.codex/agents/*.toml` configs (not the user-session `~/.codex/config.toml`), it removes sandbox protection from automated sessions. The `test_yolo_keys_no_agent_role_leakage` test is the guard.
- **Open:** The `managed_keys` semantics (upsert-if-absent vs. always-overwrite) must be verified against the existing code before writing tests. The test pseudocode above flags this; the implementer must read the Python block logic at lines 221–250 before finalizing test assertions.
- **Open:** ace-linux-1 may also have codex installed but is also missing from the registry. Fixing the registry for ace-linux-2 only is scoped here. A follow-on issue should audit all Linux machines.
- **Open:** No bootstrap doc update is included. The AC requires the implementer to comment the `codex doctor --summary` verification on the issue; a separate bootstrap guide update is out of scope.

---

## Complexity: T2

**T2** — 5 files modified; touches a 1365-line sync script with embedded Python (`managed_keys` expansion in 2 places); TDD changes in an existing bash test harness. No new modules; all changes are targeted additive edits. Two-provider adversarial review (Claude + Codex) appropriate given the Codex-specific scope.
