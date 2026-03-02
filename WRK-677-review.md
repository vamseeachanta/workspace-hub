# Cross-Review: WRK-677 Hardened Claim Gate Metadata

Verdict: REQUEST_CHANGES

## Findings

### 1. [BUG] Block-style `blocked_by` missed in `claim-item.sh`
The `get_value` function in the `claim-item.sh` Python block uses a simple regex that only captures values on the same line as the key.
```python
def get_value(field: str) -> str:
    m = re.search(rf"^{re.escape(field)}:[ 	]*(.*)$", frontmatter, re.MULTILINE)
    return m.group(1).strip() if m else ""
```
If `blocked_by` is formatted as a YAML block (e.g., in `WRK-595.md`), it returns an empty string, leading to `is_blocked: false` in `claim-evidence.yaml`. This allows items with blockers to bypass the gate if they are still in `pending/`.

### 2. [LOGIC] Inconsistent state on verification failure
`claim-item.sh` updates the `.md` file's frontmatter (setting `status: working`) *before* running the validator.
```bash
# Python block writes back to path (the .md file)
path.write_text(f"---
{frontmatter.rstrip()}
---
{body}", encoding="utf-8")
...
# Then validator runs
if ! python3 "$VERIFY_SCRIPT" "$WRK_ID"; then
  exit 1
fi
```
If validation fails, the file remains in `pending/` but its internal state is "corrupted" with `status: working` and new reference fields. The file update should only happen after a successful gate run.

### 3. [GAP] `session_owner: "unknown"` passes hardened check
In `claim-item.sh`, `session_owner` defaults to `"unknown"` if `provider` is missing.
In `verify-gate-evidence.py`, `check_claim_gate` only checks `if not data.get("session_owner")`. Since `"unknown"` is truthy, it passes the check.
For "hardened" metadata version 1, it should probably reject `"unknown"` to ensure a valid agent is identified.

### 4. [UX/ROBUSTNESS] Details vs. OK mismatch in Workstation Gate
In `verify-gate-evidence.py`, the workstation gate uses `has_nonempty_field` (which handles blocks correctly) for the `ok` status, but uses `get_field` (which doesn't) for the `details` string.
```python
"ok": has_nonempty_field(front, "plan_workstations") and ...,
"details": f"plan_workstations={get_field(front, 'plan_workstations') or 'missing'}, ..."
```
This results in a confusing status: `OK (plan_workstations=missing, ...)` when block-style workstations are used.

## Recommendations
- Improve `get_value` in `claim-item.sh` to handle YAML blocks or use a proper YAML parser.
- Move the `.md` file update in `claim-item.sh` to after the successful verification.
- Update `verify-gate-evidence.py` to reject `"unknown"` session owners for version 1 metadata.
- Sync `get_field` in `verify-gate-evidence.py` with the block-aware logic used in `has_nonempty_field`.
