# WRK-1034 — Independent Codex Plan Draft
# Stage 7 and Stage 17 Hard Gate Enforcement

**Date:** 2026-03-07
**Author:** Codex (independent planning agent)
**WRK:** WRK-1034

---

## 1. Problem Statement

Stage 5 (User Review — Plan Draft) is guarded by `check_stage5_evidence_gate()` in
`verify-gate-evidence.py` and enforced at `claim-item.sh` and `close-item.sh` via the
`--stage5-check` CLI flag. The guard reads `stage5-gate-config.yaml` and fails closed if the
config or artifacts are absent.

Stages 7 (User Review — Plan Final) and 17 (User Review — Implementation) have no equivalent
gate — AI agents can advance to downstream stages without verified user-review evidence.

WRK-1034 closes this gap by adding `check_stage7_evidence_gate()` and
`check_stage17_evidence_gate()` to `verify-gate-evidence.py`, pairing each with a dedicated
config YAML, and enforcing them at the appropriate entrypoints.

---

## 2. Canonical Artifact Reference

| Gate | Canonical artifact | Required fields | Accepted decision values |
|------|--------------------|-----------------|--------------------------|
| Stage 5 | `evidence/user-review-common-draft.yaml` + `evidence/user-review-plan-draft.yaml` | `approval_decision`, `review_cycle_id` | `approve_as_is` |
| Stage 7 | `evidence/plan-final-review.yaml` | `confirmed_by`, `confirmed_at`, `decision` | `passed` |
| Stage 17 | `evidence/user-review-close.yaml` | `reviewer`, `confirmed_at`, `decision` | `approved`, `accepted`, `passed` |

Note: `user-review-close.yaml` already has a soft checker (`check_user_review_close_gate()`)
registered in the `close` phase of `run_checks()`. The Stage 17 hard gate is a separate,
fail-closed entrypoint check — analogous to how Stage 5 has both a soft gate in `run_checks()`
(the `check_stage5_evidence_gate` call inside the claim-phase checks) and a hard entrypoint
guard via `--stage5-check`.

---

## 3. Files to Create

### 3.1 `scripts/work-queue/stage7-gate-config.yaml`

Schema mirrors `stage5-gate-config.yaml` exactly. Key differences:

```
schema_version: "1.0"
owned_by_wrk: WRK-1034
activation: full                   # immediate enforcement (not disabled)
gate_activation_commit: ""         # filled at first activation commit
checker_timeout_seconds: 30
git_history_timeout_seconds: 8
emergency_bypass_until: ""
emergency_bypass_reason: ""
emergency_bypass_approved_by: ""
human_authority_allowlist:
  - user
  - vamsee
```

The `activation` enum and all other field names are identical to `stage5-gate-config.yaml` to
keep the loader helper reusable (see Section 4.2).

### 3.2 `scripts/work-queue/stage17-gate-config.yaml`

Same schema as above, `owned_by_wrk: WRK-1034`, `activation: full`.

---

## 4. Files to Modify

### 4.1 `scripts/work-queue/verify-gate-evidence.py`

#### 4.1.1 Generalise the config loader

The existing `_load_stage5_config()` is specific to `stage5-gate-config.yaml`. Extract a
generic helper:

```python
def _load_gate_config(workspace_root: Path, filename: str) -> tuple[dict | None, str]:
    """Load a stage gate config YAML by filename.
    Returns (data, "") on success or (None, error_message) on failure.
    """
    config_path = workspace_root / "scripts" / "work-queue" / filename
    if not config_path.exists():
        return None, f"{filename} not found at {config_path}"
    if yaml is None:
        return None, f"PyYAML unavailable — cannot load {filename}"
    try:
        data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        return None, f"{filename} parse error: {exc}"
    if not isinstance(data, dict):
        return None, f"{filename} root is not a mapping"
    return data, ""
```

Keep `_load_stage5_config()` as a thin wrapper that calls `_load_gate_config(...,
"stage5-gate-config.yaml")` to preserve backward-compatibility with any callers that import
the function directly.

#### 4.1.2 Add `check_stage7_evidence_gate()`

```python
def check_stage7_evidence_gate(
    wrk_id: str, assets_dir: Path, workspace_root: Path
) -> tuple[bool | None, str]:
    """Check Stage 7 evidence gate (User Review — Plan Final).

    Canonical artifact: evidence/plan-final-review.yaml
    Required fields:   confirmed_by, confirmed_at, decision=passed

    Returns:
        (True,  detail) — gate passes
        (False, detail) — predicate failure
        (None,  detail) — infrastructure failure (exit 2 semantics)
    """
    if yaml is None:
        return None, "PyYAML unavailable — cannot validate Stage 7 evidence"

    config, config_err = _load_gate_config(workspace_root, "stage7-gate-config.yaml")
    if config is None:
        return None, config_err

    activation = str(config.get("activation", "disabled")).strip()
    human_allowlist = set(config.get("human_authority_allowlist") or [])

    if activation == "disabled":
        return True, "stage7-gate-config.yaml: activation=disabled (no enforcement)"

    evidence_dir = assets_dir / "evidence"

    # Migration exemption (same pattern as Stage 5)
    exemption_path = evidence_dir / "stage7-migration-exemption.yaml"
    if exemption_path.exists():
        ex, ex_err = _validate_exemption(exemption_path, wrk_id, human_allowlist)
        if ex_err:
            return False, ex_err
        return True, f"stage7-migration-exemption.yaml: legacy exemption approved by {ex}"

    artifact_path = evidence_dir / "plan-final-review.yaml"
    if not artifact_path.exists():
        return False, "plan-final-review.yaml missing — Stage 7 plan-final review required"

    data, yaml_err = load_yaml(artifact_path)
    if yaml_err:
        return None, f"plan-final-review.yaml parse error: {yaml_err}"
    assert data is not None

    # WRK-id consistency check (non-blocking when field absent)
    artifact_wrk = str(data.get("wrk_id", "")).strip()
    if artifact_wrk and artifact_wrk != wrk_id:
        return False, f"plan-final-review.yaml: wrk_id mismatch ({artifact_wrk} != {wrk_id})"

    # Field validation
    confirmed_by = str(data.get("confirmed_by", "")).strip()
    if not confirmed_by:
        return False, "plan-final-review.yaml: confirmed_by missing"
    # confirmed_by must be a human identity (not an agent)
    if human_allowlist and confirmed_by not in human_allowlist:
        return (
            False,
            f"plan-final-review.yaml: confirmed_by='{confirmed_by}' not in "
            f"human_authority_allowlist; agent identities are not permitted",
        )

    confirmed_at = str(data.get("confirmed_at", "")).strip()
    if not confirmed_at:
        return False, "plan-final-review.yaml: confirmed_at missing"

    decision = str(data.get("decision", "")).strip().lower()
    if decision != "passed":
        return (
            False,
            f"plan-final-review.yaml: decision='{decision}'; Stage 8+ requires decision=passed",
        )

    return (
        True,
        f"stage7 gate passed: confirmed_by={confirmed_by}, confirmed_at={confirmed_at}, "
        f"decision={decision}",
    )
```

#### 4.1.3 Add `check_stage17_evidence_gate()`

```python
def check_stage17_evidence_gate(
    wrk_id: str, assets_dir: Path, workspace_root: Path
) -> tuple[bool | None, str]:
    """Check Stage 17 evidence gate (User Review — Implementation).

    Canonical artifact: evidence/user-review-close.yaml
    Required fields:   reviewer, confirmed_at, decision in {approved, accepted, passed}

    Returns:
        (True,  detail) — gate passes
        (False, detail) — predicate failure
        (None,  detail) — infrastructure failure (exit 2 semantics)
    """
    if yaml is None:
        return None, "PyYAML unavailable — cannot validate Stage 17 evidence"

    config, config_err = _load_gate_config(workspace_root, "stage17-gate-config.yaml")
    if config is None:
        return None, config_err

    activation = str(config.get("activation", "disabled")).strip()
    human_allowlist = set(config.get("human_authority_allowlist") or [])

    if activation == "disabled":
        return True, "stage17-gate-config.yaml: activation=disabled (no enforcement)"

    evidence_dir = assets_dir / "evidence"

    # Migration exemption
    exemption_path = evidence_dir / "stage17-migration-exemption.yaml"
    if exemption_path.exists():
        ex, ex_err = _validate_exemption(exemption_path, wrk_id, human_allowlist)
        if ex_err:
            return False, ex_err
        return True, f"stage17-migration-exemption.yaml: legacy exemption approved by {ex}"

    artifact_path = evidence_dir / "user-review-close.yaml"
    if not artifact_path.exists():
        return False, "user-review-close.yaml missing — Stage 17 implementation review required"

    data, yaml_err = load_yaml(artifact_path)
    if yaml_err:
        return None, f"user-review-close.yaml parse error: {yaml_err}"
    assert data is not None

    artifact_wrk = str(data.get("wrk_id", "")).strip()
    if artifact_wrk and artifact_wrk != wrk_id:
        return False, f"user-review-close.yaml: wrk_id mismatch ({artifact_wrk} != {wrk_id})"

    reviewer = str(data.get("reviewer", "")).strip()
    if not reviewer:
        return False, "user-review-close.yaml: reviewer missing"
    if human_allowlist and reviewer not in human_allowlist:
        return (
            False,
            f"user-review-close.yaml: reviewer='{reviewer}' not in "
            f"human_authority_allowlist; agent identities are not permitted",
        )

    confirmed_at = str(data.get("confirmed_at", "")).strip()
    if not confirmed_at:
        return False, "user-review-close.yaml: confirmed_at missing"

    decision = str(data.get("decision", "")).strip().lower()
    if decision not in {"approved", "accepted", "passed"}:
        return (
            False,
            f"user-review-close.yaml: decision='{decision}'; must be approved|accepted|passed",
        )

    return (
        True,
        f"stage17 gate passed: reviewer={reviewer}, confirmed_at={confirmed_at}, "
        f"decision={decision}",
    )
```

#### 4.1.4 Add shared `_validate_exemption()` helper

Consolidates the exemption-checking logic that Stage 5 has inline and that Stages 7 and 17
will also need:

```python
def _validate_exemption(
    exemption_path: Path, wrk_id: str, human_allowlist: set[str]
) -> tuple[str | None, str]:
    """Validate a migration exemption YAML.
    Returns (approved_by, "") on success or (None, error_msg) on failure.
    """
    try:
        ex = yaml.safe_load(exemption_path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        return None, f"{exemption_path.name} parse error: {exc}"
    if not isinstance(ex, dict):
        return None, f"{exemption_path.name} root is not a mapping"
    approved_by = str(ex.get("approved_by", "")).strip()
    if not approved_by:
        return None, f"{exemption_path.name}: approved_by missing"
    if human_allowlist and approved_by not in human_allowlist:
        return (
            None,
            f"{exemption_path.name}: approved_by='{approved_by}' not in "
            f"human_authority_allowlist; agent identities are not permitted",
        )
    if not str(ex.get("approval_scope", "")).strip():
        return None, f"{exemption_path.name}: approval_scope missing"
    ex_wrk = str(ex.get("wrk_id", "")).strip()
    if ex_wrk and ex_wrk != wrk_id:
        return None, f"{exemption_path.name}: wrk_id mismatch ({ex_wrk} != {wrk_id})"
    return approved_by, ""
```

Also refactor `check_stage5_evidence_gate()` to use `_validate_exemption()` instead of its
inline block, reducing duplication.

#### 4.1.5 Add CLI dispatch handlers `_run_stage7_check()` and `_run_stage17_check()`

Pattern identical to `_run_stage5_check()`:

```python
def _run_stage7_check(args: list[str]) -> int:
    """Handle --stage7-check <WRK-id> invocation.
    Exit codes: 0=pass, 1=predicate fail, 2=infra fail
    """
    if len(args) < 1:
        print("Usage: verify-gate-evidence.py --stage7-check WRK-<id>", file=sys.stderr)
        return 2
    wrk_id = args[0]
    workspace_root = Path(__file__).resolve().parents[2]
    queue_dir = workspace_root / ".claude" / "work-queue"
    assets_dir = queue_dir / "assets" / wrk_id
    if not assets_dir.is_dir():
        print(f"✖ Stage 7 check: assets directory not found for {wrk_id}", file=sys.stderr)
        return 2
    ok, detail = check_stage7_evidence_gate(wrk_id, assets_dir, workspace_root)
    if ok is None:
        print(f"✖ Stage 7 gate infrastructure failure for {wrk_id}: {detail}", file=sys.stderr)
        return 2
    if not ok:
        print(f"✖ Stage 7 gate predicate failure for {wrk_id}: {detail}", file=sys.stderr)
        return 1
    print(f"✔ Stage 7 gate passed for {wrk_id}: {detail}")
    return 0


def _run_stage17_check(args: list[str]) -> int:
    """Handle --stage17-check <WRK-id> invocation.
    Exit codes: 0=pass, 1=predicate fail, 2=infra fail
    """
    if len(args) < 1:
        print("Usage: verify-gate-evidence.py --stage17-check WRK-<id>", file=sys.stderr)
        return 2
    wrk_id = args[0]
    workspace_root = Path(__file__).resolve().parents[2]
    queue_dir = workspace_root / ".claude" / "work-queue"
    assets_dir = queue_dir / "assets" / wrk_id
    if not assets_dir.is_dir():
        print(f"✖ Stage 17 check: assets directory not found for {wrk_id}", file=sys.stderr)
        return 2
    ok, detail = check_stage17_evidence_gate(wrk_id, assets_dir, workspace_root)
    if ok is None:
        print(f"✖ Stage 17 gate infrastructure failure for {wrk_id}: {detail}", file=sys.stderr)
        return 2
    if not ok:
        print(f"✖ Stage 17 gate predicate failure for {wrk_id}: {detail}", file=sys.stderr)
        return 1
    print(f"✔ Stage 17 gate passed for {wrk_id}: {detail}")
    return 0
```

#### 4.1.6 Update `main()` dispatch

```python
def main() -> None:
    args = sys.argv[1:]
    if args and args[0] == "--stage5-check":
        sys.exit(_run_stage5_check(args[1:]))
    if args and args[0] == "--stage7-check":
        sys.exit(_run_stage7_check(args[1:]))
    if args and args[0] == "--stage17-check":
        sys.exit(_run_stage17_check(args[1:]))
    # ... existing phase-check path unchanged
```

---

### 4.2 `scripts/work-queue/claim-item.sh`

Stage 7 guards Stage 8 (Cross-Review), and `claim-item.sh` is the canonical Stage 6→8
transition gatekeeper. Add the Stage 7 check immediately after the existing Stage 5 block
(lines ~38–60):

```bash
# --- Stage 7 evidence gate (canonical checker — plan-final review required) -----
# claim-item.sh advances work past Stage 6 into cross-review. The user must have
# confirmed plan-final-review.yaml before AI agents can proceed.
stage7_exit=0
stage7_output="$(uv run --no-project python "$STAGE5_CHECKER" \
    --stage7-check "$WRK_ID" 2>&1)" || stage7_exit=$?
if [[ "$stage7_exit" -eq 1 ]]; then
    echo "✖ Stage 7 evidence gate FAILED (predicate failure) for ${WRK_ID}:" >&2
    echo "$stage7_output" >&2
    echo "Complete Stage 7 plan-final review before claiming." >&2
    exit 1
elif [[ "$stage7_exit" -eq 2 ]]; then
    echo "✖ Stage 7 evidence gate FAILED (infrastructure failure) for ${WRK_ID}:" >&2
    echo "$stage7_output" >&2
    echo "Repair the Stage 7 gate infrastructure before claiming." >&2
    exit 2
fi
```

Note: The variable `STAGE5_CHECKER` already points to `verify-gate-evidence.py`; reuse it
(no new path variable needed).

---

### 4.3 `scripts/work-queue/close-item.sh`

Stage 17 guards Stage 18 (Reclaim) and Stage 19 (Archive). `close-item.sh` is the canonical
close transition. Add the Stage 17 check immediately after the existing Stage 5 block
(lines ~98–120):

```bash
# --- Stage 17 evidence gate (canonical checker — impl review required) -----------
# close-item.sh advances work to archive. The user must have confirmed
# user-review-close.yaml before AI agents can close the WRK.
stage17_exit=0
stage17_output="$(uv run --no-project python "$STAGE5_CHECKER" \
    --stage17-check "$WRK_ID" 2>&1)" || stage17_exit=$?
if [[ "$stage17_exit" -eq 1 ]]; then
  echo "✖ Stage 17 evidence gate FAILED (predicate failure) for ${WRK_ID}:" >&2
  echo "$stage17_output" >&2
  echo "Complete Stage 17 implementation review and evidence before closing." >&2
  exit 1
elif [[ "$stage17_exit" -eq 2 ]]; then
  echo "✖ Stage 17 evidence gate FAILED (infrastructure failure) for ${WRK_ID}:" >&2
  echo "$stage17_output" >&2
  echo "Repair the Stage 17 gate infrastructure before closing." >&2
  exit 2
fi
```

---

### 4.4 `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md`

Two changes:

**a) HARD GATE notices**

Immediately before the Stage 7 description block, insert:

```
> HARD GATE: Stage 7 requires evidence/plan-final-review.yaml (confirmed_by, confirmed_at,
> decision=passed) verified by a human authority before any agent may call claim-item.sh.
> claim-item.sh will exit 1 if this artifact is absent or incomplete.
```

Immediately before the Stage 17 description block, insert:

```
> HARD GATE: Stage 17 requires evidence/user-review-close.yaml (reviewer, confirmed_at,
> decision=approved|accepted|passed) verified by a human authority before any agent may
> call close-item.sh. close-item.sh will exit 1 if this artifact is absent or incomplete.
```

**b) Exit checklists**

After each gate notice, add an exit checklist:

Stage 7 exit checklist:
- evidence/plan-final-review.yaml created with confirmed_by (human identity), confirmed_at (ISO-8601), decision=passed
- wrk_id field set correctly (or omitted)
- Artifact committed to git before running claim-item.sh
- claim-item.sh Stage 7 gate output shows: `✔ Stage 7 gate passed`

Stage 17 exit checklist:
- evidence/user-review-close.yaml created with reviewer (human identity), confirmed_at (ISO-8601), decision=approved|accepted|passed
- wrk_id field set correctly (or omitted)
- Artifact committed to git before running close-item.sh
- close-item.sh Stage 17 gate output shows: `✔ Stage 17 gate passed`

---

## 5. Test Cases (10 minimum)

All tests live in the existing test file for `verify-gate-evidence.py` (likely
`tests/work-queue/test_verify_gate_evidence.py` or similar). Use `tmp_path` pytest fixture to
build minimal fixture directories.

### Stage 7 gate tests

| # | Scenario | Expected result |
|---|----------|-----------------|
| T-1 | `stage7-gate-config.yaml` activation=disabled | `(True, "activation=disabled (no enforcement)")` |
| T-2 | `plan-final-review.yaml` absent, activation=full | `(False, "plan-final-review.yaml missing — Stage 7 plan-final review required")` |
| T-3 | Artifact present, decision=passed, all fields populated, human in allowlist | `(True, "stage7 gate passed: ...")` |
| T-4 | Artifact present, decision=rejected | `(False, "decision='rejected'; Stage 8+ requires decision=passed")` |
| T-5 | Artifact present, `confirmed_by` is an agent identity not in allowlist | `(False, "confirmed_by=... not in human_authority_allowlist")` |
| T-6 | Artifact present, `confirmed_by` missing | `(False, "confirmed_by missing")` |
| T-7 | `stage7-gate-config.yaml` absent | `(None, "stage7-gate-config.yaml not found at ...")` |
| T-8 | `stage7-migration-exemption.yaml` present with valid `approved_by` from allowlist | `(True, "stage7-migration-exemption.yaml: legacy exemption ...")` |

### Stage 17 gate tests

| # | Scenario | Expected result |
|---|----------|-----------------|
| T-9 | `stage17-gate-config.yaml` activation=disabled | `(True, "activation=disabled (no enforcement)")` |
| T-10 | `user-review-close.yaml` absent, activation=full | `(False, "user-review-close.yaml missing — Stage 17 implementation review required")` |
| T-11 | Artifact present, decision=approved, all fields valid | `(True, "stage17 gate passed: ...")` |
| T-12 | Artifact present, decision=pending | `(False, "decision='pending'; must be approved|accepted|passed")` |
| T-13 | Artifact present, reviewer not in allowlist | `(False, "reviewer=... not in human_authority_allowlist")` |

### CLI dispatch tests (via subprocess or monkeypatching)

| # | Scenario | Expected exit code |
|---|----------|--------------------|
| T-14 | `--stage7-check WRK-XXXX` with gate passing | `0` |
| T-15 | `--stage7-check WRK-XXXX` with missing artifact | `1` |
| T-16 | `--stage17-check WRK-XXXX` with gate passing | `0` |
| T-17 | `--stage17-check WRK-XXXX` with missing artifact | `1` |

Total: 17 test cases (well above AC-8 minimum of 10).

---

## 6. Exit Code Convention

Must match the existing Stage 5 pattern throughout:

| Code | Meaning | Trigger conditions |
|------|---------|-------------------|
| 0 | Gate passes (or activation=disabled) | Evidence present and valid, or gate disabled |
| 1 | Predicate failure | Missing artifact, wrong field value, wrong decision, identity not in allowlist |
| 2 | Infrastructure failure | Config file missing, PyYAML unavailable, assets directory missing |

Callers (claim-item.sh, close-item.sh) must treat both exit 1 and exit 2 as fail-closed
blocking outcomes, as documented in the existing comments.

---

## 7. Field Name Canonical Reference

### `evidence/plan-final-review.yaml` (Stage 7)

| Field | Type | Required | Accepted values | Notes |
|-------|------|----------|-----------------|-------|
| `confirmed_by` | string | yes | human identity from allowlist | Agent identities rejected |
| `confirmed_at` | string | yes | ISO-8601 datetime | Non-empty string is sufficient |
| `decision` | string | yes | `passed` | Case-insensitive comparison |
| `wrk_id` | string | no | `WRK-NNN` | If present, must match invocation WRK-id |

### `evidence/user-review-close.yaml` (Stage 17)

| Field | Type | Required | Accepted values | Notes |
|-------|------|----------|-----------------|-------|
| `reviewer` | string | yes | human identity from allowlist | Agent identities rejected |
| `confirmed_at` | string | yes | ISO-8601 datetime | Non-empty string is sufficient |
| `decision` | string | yes | `approved`, `accepted`, `passed` | Case-insensitive comparison |
| `wrk_id` | string | no | `WRK-NNN` | If present, must match invocation WRK-id |

Note: Stage 17 uses `reviewer` (not `confirmed_by`) and accepts three decision values
(`approved|accepted|passed`) consistent with the existing `check_user_review_close_gate()`
soft checker. Do NOT unify field names between Stage 7 and Stage 17 artifacts as doing so
would break existing evidence files.

---

## 8. Interaction with Existing Soft Gates

`check_user_review_close_gate()` already runs as a soft gate in `run_checks()` under the
`close` phase. The new `check_stage17_evidence_gate()` is a separate hard entrypoint guard.
Both will read the same `user-review-close.yaml` artifact. This is intentional:

- The soft gate (`run_checks`) validates during the full evidence summary pass.
- The hard gate (`--stage17-check`) is the fail-closed entrypoint enforcer.
- Neither gate is redundant; they serve different callers.

Similarly, `check_plan_confirmation()` reads `plan-final-review.yaml`-like content from a
plan markdown file. The Stage 7 artifact `evidence/plan-final-review.yaml` is a YAML sidecar
that captures the post-review user confirmation explicitly. No conflict.

---

## 9. Rollout Sequence

1. Add `_load_gate_config()` generic helper and `_validate_exemption()` helper.
2. Refactor `_load_stage5_config()` to delegate to `_load_gate_config()`.
3. Refactor `check_stage5_evidence_gate()` to use `_validate_exemption()` (no behavioural change).
4. Add `check_stage7_evidence_gate()` and `check_stage17_evidence_gate()`.
5. Add `_run_stage7_check()` and `_run_stage17_check()` CLI handlers.
6. Update `main()` dispatch.
7. Create `stage7-gate-config.yaml` with `activation: full`.
8. Create `stage17-gate-config.yaml` with `activation: full`.
9. Update `claim-item.sh` with Stage 7 guard block.
10. Update `close-item.sh` with Stage 17 guard block.
11. Update `work-queue-workflow/SKILL.md` with HARD GATE notices and exit checklists.
12. Write 17 tests. Run `uv run --no-project python -m pytest` to confirm green.

---

## 10. Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| Existing WRKs in flight lack the new artifacts | `activation: full` for NEW gates is safe because no WRKs currently pass through Stage 7/17 without those artifacts being present; legacy WRKs can use migration-exemption files |
| Stage 5 config loader duplication | Addressed by extracting `_load_gate_config()` before adding new checkers |
| `user-review-close.yaml` field name ambiguity (`reviewer` vs `confirmed_by`) | Soft gate already uses `reviewer`; hard gate must match to avoid forcing re-creation of existing artifacts |
| `confirmed_at` vs `reviewed_at` field name inconsistency | The task brief specifies `confirmed_at` for Stage 17; the existing soft checker uses `reviewed_at`. These must be reconciled — confirm with human which field name to enforce before implementation. |

### Clarification needed before implementation

The existing `check_user_review_close_gate()` (lines 357–376) uses `reviewed_at` as the
timestamp field:

```python
missing = [key for key in ("reviewer", "reviewed_at", "decision") if ...]
```

The WRK-1034 brief specifies `confirmed_at`. These are inconsistent. Three options:

- **Option A**: Use `reviewed_at` in the hard gate to match the existing soft gate (no artifact breakage).
- **Option B**: Use `confirmed_at` in the hard gate as specified in the brief, and accept that the two gates check different fields (risk of silent gap if old artifacts use `reviewed_at`).
- **Option C**: Accept both `reviewed_at` and `confirmed_at` (union check) in the hard gate.

Recommendation: **Option A** — align with the existing soft gate's field name (`reviewed_at`)
to avoid artifact fragmentation. Update the WRK-1034 brief to correct the field name if needed.

---

## 11. Summary of Files Changed

| File | Action | Reason |
|------|--------|--------|
| `scripts/work-queue/verify-gate-evidence.py` | Modify | Add helpers + two new gate functions + two CLI handlers |
| `scripts/work-queue/stage7-gate-config.yaml` | Create | Gate activation config for Stage 7 |
| `scripts/work-queue/stage17-gate-config.yaml` | Create | Gate activation config for Stage 17 |
| `scripts/work-queue/claim-item.sh` | Modify | Add Stage 7 guard block after Stage 5 block |
| `scripts/work-queue/close-item.sh` | Modify | Add Stage 17 guard block after Stage 5 block |
| `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md` | Modify | HARD GATE notices + exit checklists for Stages 7 and 17 |
| `tests/work-queue/test_verify_gate_evidence.py` (or equivalent) | Modify | Add 17 new test cases |

Total: 2 new files, 5 modified files.
