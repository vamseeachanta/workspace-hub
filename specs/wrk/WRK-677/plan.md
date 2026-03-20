# WRK-677 Plan: governance(review) — strengthen claim gate metadata

**Source WRK:** WRK-677
**Route:** C (complex)
**Created:** 2026-03-02
**Status:** final (post cross-review)

---

## Objective

Harden the claim gate so every `claim-evidence.yaml` contains verifiable, fresh metadata:
`session_owner`, `agent_fit`, `quota_snapshot` (ISO8601 timestamp + pct_remaining),
`blocking_state`, and `metadata_version`. Add a claim gate check to `verify-gate-evidence.py`
(currently absent). Enrich `claim-item.sh` to emit all new fields automatically with safe
defaults.

---

## Cross-Review Resolutions

**Codex P1 — backwards-compat rule:**
Use `metadata_version: "1"` as the explicit discriminator:
- Claim file present + `metadata_version: "1"` → hard-fail on any missing required field
- Claim file absent or `metadata_version` absent → WARN only (legacy item)
No date-based logic; the version field is the single source of truth.

**Codex P2 — template path:**
`.claude/work-queue/assets/WRK-656/claim-evidence-template.yaml` IS the canonical template.
WRK-656 is the active governance parent that owns all orchestrator gate artefacts. Documented
with an inline comment in the template.

**Codex P2 — claim-item.sh hardening:**
Add normalization: provider defaults to `"unknown"`, blocked_by coerced to list,
quota source absent → `status: "unknown"`, all fields have deterministic placeholders.

**Gemini P2 — ISO8601 consistency:**
Pin to `strftime("%Y-%m-%dT%H:%M:%SZ")` everywhere — no microseconds, Z suffix, UTC.

**Gemini P2 — quota unknown vs unavailable:**
`status: "unknown"` when quota source is absent → verifier emits WARN, not FAIL.
`status: "rate-limited"` or `status: "quota-exceeded"` → verifier hard-fails.

---

## Phase 1 — Metadata Schema

**File:** `.claude/work-queue/assets/WRK-656/claim-evidence-template.yaml`

New fields (after `alternate_provider`):

```yaml
metadata_version: "1"              # discriminator: "1" = hardened; absent = legacy
session_owner: "claude|codex|gemini"
agent_fit:
  capability_match: "matched|partial|undocumented"
  rationale: "Route C / execution_workstations=[dev-primary] / provider=claude"
blocking_state:
  blocked: false
  blocked_by: []
  notes: ""
quota_snapshot:
  timestamp: "2026-03-02T10:00:00Z"      # strftime("%Y-%m-%dT%H:%M:%SZ")
  provider: "claude|codex|gemini"
  status: "available|rate-limited|quota-exceeded|unknown"
  pct_remaining: null                    # integer 0-100, or null if unavailable
  source: "config/ai-tools/agent-quota-latest.json"
```

Add `claim_gate` to `gate_evidence`:

```yaml
gate_evidence:
  claim_gate:
    metadata_version_ok: true
    session_owner_ok: true
    quota_ok: true           # true when status==available or unknown
    unblocked: true
    verified_at: "2026-03-02T10:00:00Z"
    notes: ""
```

---

## Phase 2 — Verifier Claim Gate

**File:** `scripts/work-queue/verify-gate-evidence.py`

New `check_claim_gate(assets_dir)` function (~35 lines):

```python
def check_claim_gate(assets_dir):
    claim_file = assets_dir / "claim-evidence.yaml"
    if not claim_file.exists():
        return None, "claim-evidence.yaml absent (legacy item)"   # → WARN

    import yaml
    data = yaml.safe_load(claim_file.read_text())
    version = str(data.get("metadata_version", ""))
    if version != "1":
        return None, f"metadata_version={version!r} (legacy — WARN only)"  # → WARN

    # Hard checks for version "1" items
    errors = []
    if not data.get("session_owner"):
        errors.append("session_owner missing")
    qs = data.get("quota_snapshot", {})
    qs_status = qs.get("status", "")
    if qs_status in ("rate-limited", "quota-exceeded"):
        errors.append(f"quota_snapshot.status={qs_status!r}")
    bs = data.get("blocking_state", {})
    if bs.get("blocked"):
        errors.append(f"blocking_state.blocked=true, blocked_by={bs.get('blocked_by')}")
    if errors:
        return False, "; ".join(errors)
    return True, f"version=1, owner={data['session_owner']}, quota={qs_status}"
```

Gate result mapping:
- `None` → print WARN line, do not count as failure
- `False` → print MISSING line, count as failure
- `True` → print OK line

---

## Phase 3 — claim-item.sh Enrichment

**File:** `scripts/work-queue/claim-item.sh`

Extend the Python inline block with:

```python
# session_owner — from frontmatter provider
session_owner = get_value("provider") or "unknown"

# agent_fit — derived from route + workstations + provider
exec_ws = get_value("execution_workstations") or "unknown"
capability_match = "matched" if session_owner != "unknown" else "undocumented"
agent_fit_rationale = (
    f"Route {route or '?'} / execution_workstations={exec_ws} / provider={session_owner}"
)

# blocking_state — from frontmatter blocked_by
blocked_by_raw = get_value("blocked_by") or "[]"
blocked_by_list = [x.strip().strip("-").strip()
    for x in blocked_by_raw.strip("[]").split(",") if x.strip().strip("-").strip()]
is_blocked = len(blocked_by_list) > 0

# quota_snapshot — from agent-quota-latest.json
now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
quota_pct = None
quota_status = "unknown"
if Path(quota_file).exists():
    try:
        import json
        qdata = json.loads(Path(quota_file).read_text())
        for agent in qdata.get("agents", []):
            if agent.get("provider") == session_owner:
                quota_pct = agent.get("pct_remaining")
                quota_status = "available" if quota_pct is None or quota_pct > 10 else "rate-limited"
                break
        else:
            quota_status = "available"   # file present but provider not found → optimistic
    except Exception:
        quota_status = "unknown"
```

Write to claim-evidence.yaml using `strftime("%Y-%m-%dT%H:%M:%SZ")` for all timestamps.

---

## Files Changed

| File | Action | Lines |
|------|--------|-------|
| `.claude/work-queue/assets/WRK-656/claim-evidence-template.yaml` | EDIT — add 5 fields + claim_gate | +25 |
| `scripts/work-queue/verify-gate-evidence.py` | EDIT — add claim_gate check | +35 |
| `scripts/work-queue/claim-item.sh` | EDIT — enrich Python block | +30 |
| `specs/wrk/WRK-677/plan.md` | CREATE (this file) | — |
| `.claude/work-queue/assets/WRK-677/` | Gate artifacts | — |

---

## Test Strategy

1. `verify-gate-evidence.py WRK-677` → exit 0 (happy path).
2. `claim-item.sh` on a test item → confirm all 5 new fields in output YAML.
3. Regression — legacy item (WRK-675, no `metadata_version`) → WARN not FAIL.
4. Regression — `quota_snapshot.status: rate-limited` → gate FAIL.
5. Regression — `blocking_state.blocked: true` → gate FAIL.
6. Edge — `quota-source absent` → `status: "unknown"` → WARN.
7. Edge — malformed `blocked_by` (string not list) → coerced to list, no crash.
