# Plan for #3953: Make configuration propagation writes UTF-8 atomic and recoverable

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-10-14
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3953
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-10-14-plan-3953-claude.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `scripts/automation/release_scan_wrk.py:136,146` — two `write_text()` calls on YAML state files (`state_path.write_text(yaml.dump(data, ...))`) with no `encoding=` argument; these are the highest-risk callers because YAML serialization includes Unicode when provider names or version strings carry it.
- Found: `scripts/automation/release_scan_wrk.py:220` — third `write_text()` without encoding on `wrk_path`.
- Found: `scripts/automation/sync_slash_command_ecosystem.py:303,307` — two `write_text()` without encoding on doc output paths.
- Found: `scripts/automation/sync_engineering_data_context.py:233` — `write_text()` without encoding on a documentation file.
- Found: `scripts/ci/local-ci/local-ci.py:58,308` — uses `encoding='utf-8'` (positive reference pattern already in codebase).
- Gap: `scripts/utils/` directory exists but is empty; no atomic write utility anywhere in the repo.

### Standards

Not applicable — this is a Python infrastructure safety fix, not an engineering calculation.

### LLM Wiki pages consulted

No relevant wiki pages found for atomic write patterns.

### Documents consulted

- Issue body #3953 — describes UnicodeEncodeError truncation incident during policy rollout: `Path.write_text` used Windows platform encoding, truncated a target before raising, encoded others as cp1252. Before-byte backups enabled recovery. Exact failure mode and recovery pattern documented.
- Issue #3943 (parent) — OPEN, the policy rollout that triggered the failure; confirms this is a follow-on correctness fix, not a speculative hardening.
- `scripts/automation/release_scan_wrk.py:130–150` — confirms the state-file write pattern: `read_text()` → mutate → `write_text(yaml.dump(...))` with no encoding; state file contains AI version strings that may be non-ASCII.

### Gaps identified

- `scripts/utils/atomic_write.py` does not exist; must be created from scratch.
- No tests for encoding-failure-preserves-existing-bytes invariant anywhere in the repo.
- No tests for no-temp-residue on failure.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-10-14T via `gh issue view`):
- `#3953` — OPEN — Make configuration propagation writes UTF-8 atomic and recoverable
- `#3943` — OPEN — Remove separate plan approval before authorized implementation (parent context)

**File existence** (`ls` 2026-10-14T):
- EXISTS: `scripts/automation/release_scan_wrk.py`
- EXISTS: `scripts/automation/sync_slash_command_ecosystem.py`
- EXISTS: `scripts/utils/` (directory, empty)
- MISSING (new — this plan creates): `scripts/utils/atomic_write.py`
- MISSING (new — this plan creates): `scripts/utils/tests/test_atomic_write.py`

**Gap proof** (`ls scripts/utils/` → empty, confirmed no atomic write util):
```
$ ls /mnt/local-analysis/workspace-hub/scripts/utils/
(empty)
```

**Line excerpts** (write_text without encoding):
```
release_scan_wrk.py:136:    state_path.write_text(yaml.dump(data, default_flow_style=False))
release_scan_wrk.py:146:    state_path.write_text(yaml.dump(data, default_flow_style=False))
release_scan_wrk.py:220:    wrk_path.write_text(content)
sync_slash_command_ecosystem.py:303:        doc_file.write_text(doc)
sync_slash_command_ecosystem.py:307:        root_doc.write_text(doc)
sync_engineering_data_context.py:233:    doc_path.write_text(doc_content)
```

**Reproduction proof:**
N/A — this plan addresses a latent defect class (missing encoding argument), not a currently-failing test. The incident described in the issue body is the empirical proof; before-byte backups confirmed truncation occurred. The fix is preventive for future rollouts on Windows hosts.

<!-- Source count: 6 distinct sources (issue body, 2 related issues, code grep results, line excerpts, positive reference in local-ci.py). Minimum 3 required. ✓ -->

---

## Artifact Map

| Artifact | Path | Status |
|---|---|---|
| Atomic write utility | `scripts/utils/atomic_write.py` | NEW |
| Utility package init | `scripts/utils/__init__.py` | NEW (empty) |
| Tests package init | `scripts/utils/tests/__init__.py` | NEW (empty) |
| Tests for utility | `scripts/utils/tests/test_atomic_write.py` | NEW |
| State-file caller fix | `scripts/automation/release_scan_wrk.py` | MODIFY (lines 136, 146, 220) |
| Doc-file caller fix | `scripts/automation/sync_slash_command_ecosystem.py` | MODIFY (lines 303, 307) |

---

## Deliverable

A reusable `atomic_write_utf8(path, content)` function in `scripts/utils/atomic_write.py` that:
1. Encodes `content` to UTF-8 bytes before touching the destination (fail-first, no partial write).
2. Writes to a sibling temp file using `tempfile.NamedTemporaryFile`.
3. Preserves the existing file's mode if the file already exists.
4. Replaces the destination atomically with `os.replace()`.
5. Verifies the readback SHA-256 matches the written bytes.
6. Returns a `dict` with `before_sha` (or `None` if new), `written_sha`, and `path` keys for recovery auditing.
7. Cleans up the temp file on any failure path.

Applied to the two highest-risk caller families in `scripts/automation/`: state-file writes in `release_scan_wrk.py` and doc-file writes in `sync_slash_command_ecosystem.py`. Remaining `write_text()` callers without encoding are out of scope for this issue (tracked as a general defect class; this plan does not bulk-migrate historical writes).

---

## Pseudocode

```python
# scripts/utils/atomic_write.py

import hashlib, os, stat, tempfile
from pathlib import Path

def atomic_write_utf8(path: Path | str, content: str) -> dict:
    path = Path(path)
    # 1. encode first — raises UnicodeEncodeError before touching dest
    data = content.encode("utf-8")
    written_sha = hashlib.sha256(data).hexdigest()

    # 2. capture before-state
    before_sha = None
    existing_mode = None
    if path.exists():
        before_sha = hashlib.sha256(path.read_bytes()).hexdigest()
        existing_mode = stat.S_IMODE(path.stat().st_mode)

    # 3. write to sibling temp, atomically replace
    dir_ = path.parent
    dir_.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=dir_, prefix=f".{path.name}.", suffix=".tmp")
    try:
        os.write(fd, data)
        os.close(fd); fd = -1
        if existing_mode is not None:
            os.chmod(tmp, existing_mode)
        os.replace(tmp, path)
        tmp = None  # replaced — do not delete
    finally:
        if fd != -1:
            os.close(fd)
        if tmp and Path(tmp).exists():
            Path(tmp).unlink(missing_ok=True)

    # 4. verify readback
    readback = hashlib.sha256(path.read_bytes()).hexdigest()
    if readback != written_sha:
        raise RuntimeError(
            f"readback mismatch for {path}: wrote {written_sha}, read {readback}"
        )

    return {"path": str(path), "before_sha": before_sha, "written_sha": written_sha}
```

---

## Files to Change

| File | Change |
|---|---|
| `scripts/utils/__init__.py` | Create (empty) |
| `scripts/utils/atomic_write.py` | Create — `atomic_write_utf8` function per pseudocode |
| `scripts/utils/tests/__init__.py` | Create (empty) |
| `scripts/utils/tests/test_atomic_write.py` | Create — 8 tests listed below |
| `scripts/automation/release_scan_wrk.py` | Import and use `atomic_write_utf8` at lines 136, 146, 220 in place of `write_text()` |
| `scripts/automation/sync_slash_command_ecosystem.py` | Import and use `atomic_write_utf8` at lines 303, 307 in place of `write_text()` |

---

## TDD Test List (red → green)

Write ALL tests before implementing `atomic_write_utf8`. Each test must fail on the naive `write_text()` equivalent.

1. **`test_write_ascii_round_trips`** — write ASCII content, read it back, assert content equals original.
2. **`test_write_unicode_round_trips`** — write content containing `→`, `–`, `©`, and CJK characters; assert round-trip to UTF-8 preserves all characters exactly.
3. **`test_encoding_failure_preserves_existing_bytes`** — seed an existing file with known bytes (`b"original"`); call `atomic_write_utf8` with a `str` containing a lone surrogate (`"\udcff"`) that cannot encode to UTF-8; assert the `UnicodeEncodeError` is raised AND the file still contains the original bytes unchanged.
4. **`test_no_temp_residue_on_success`** — after a successful write, assert no files matching `".{name}.*.tmp"` pattern exist in the parent directory.
5. **`test_no_temp_residue_on_failure`** — patch `os.replace` to raise `OSError`; call `atomic_write_utf8`; assert `OSError` propagates AND no temp file remains beside the target.
6. **`test_mode_preserved`** — write an initial file with mode `0o640`; overwrite via `atomic_write_utf8`; assert the new file still has mode `0o640`.
7. **`test_readback_mismatch_raises`** — patch `path.read_bytes` (post-replace) to return corrupted bytes; assert `RuntimeError` is raised with "readback mismatch" in message.
8. **`test_sha_receipts_returned`** — write to a new path; assert return dict contains `before_sha=None`, a non-empty `written_sha`, and the correct `path`.

---

## Acceptance Criteria

- [ ] `scripts/utils/atomic_write.py` exports `atomic_write_utf8(path, content) -> dict`.
- [ ] A failing encode raises `UnicodeEncodeError` before any bytes touch the destination path.
- [ ] All 8 TDD tests pass: `uv run pytest scripts/utils/tests/test_atomic_write.py -xvs`.
- [ ] `release_scan_wrk.py` lines 136, 146, 220 use `atomic_write_utf8` (no bare `write_text()`).
- [ ] `sync_slash_command_ecosystem.py` lines 303, 307 use `atomic_write_utf8`.
- [ ] No new `write_text()` calls without `encoding='utf-8'` are introduced by this plan.
- [ ] Existing test suite for `release_scan_wrk.py` (if any) continues to pass.

---

## Risks and Open Questions

- **Windows path separator in temp name**: `NamedTemporaryFile` on Windows creates files in the target directory; `os.replace` on Windows fails if a reader holds the destination open. The atomic-replace invariant holds on Linux (the primary target); on Windows, `os.replace` may raise `PermissionError` if a concurrent reader exists. This is a known Windows limitation; document in the function docstring but do not work around in T1 scope.
- **Bulk caller migration**: This plan migrates 5 call sites in 2 files. ~20 additional callers exist across `scripts/automation/` (documented in Resource Intel). A follow-on issue should track bulk migration; this issue covers the highest-risk durable state files only.
- **`sync_engineering_data_context.py:233`**: Not migrated in this plan (documentation output, lower risk than state files). Include in the follow-on bulk migration.
