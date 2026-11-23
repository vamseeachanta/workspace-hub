# Plan for #3139: reconcile scanner-vs-report skill universe (3,180 vs 833) + the `_archived` collision

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-06-15
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3139
> **Client:** N/A
> **Project:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-06-15-plan-3139-claude.md | ...-codex.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/skills/skill-invocation-scanner.py` — `discover_skills(skills_root)` (line 95) walks `rglob("SKILL.md")` with **no exclusions** → 3,180 skills; `derive_short_name(skill_md_path)` (line 105) does a **minimal single-line `name:` frontmatter parse** (no yaml dep), falling back to dir basename, lowercased.
- Found: `scripts/skills/skill-usage-report.py` — `scan_skills(skills_dir)` (line 78) walks `rglob("SKILL.md")` but **excludes `{_archive, _core, _internal}`** as path parts (line 87) → 833 skills; derives `short_name = canonical_name.lower()` where `canonical_name = fm.get("name", dir-basename)` (lines 150–153) via a **full `yaml.safe_load` frontmatter parse** (line 60).
- Found: established shared-library pattern in the same directory — `scripts/skills/audit_skill_lib.py` and `scripts/skills/skill_tier_lib.py` are pure underscore-named libs with **no PEP-723 header**, imported by sibling scripts via plain `from audit_skill_lib import ...` (e.g. `skill-tier-report.py:24-25`, `skill_tier_lib.py:13`, `audit-skills.py:23`). This is the template for the new shared identity module.
- Gap: there is no shared module that both scripts import for (a) the skill universe and (b) the short_name derivation; each re-implements both independently.

### Standards
Not applicable — harness/infrastructure issue, no engineering standard involved.

### LLM Wiki pages consulted
No relevant wiki pages — this is workspace-hub harness tooling, not wiki content (Client: N/A).

### Documents consulted
- `docs/plans/2026-06-15-issue-3112-skill-invocation-instrumentation.md` — the immediate predecessor; #3139 is its follow-on (the scanner→report short_name join shipped in #3112 BUG-2).
- Issue #3139 (body) — alleges scanner walks 3,180 / report walks 833; the short_name join silently carries/misses ~2,300 skills; `gmail-data-extraction` collision arises because the report excludes `_archive` but not `_archived`.
- Issue #3137 (OPEN) — "capture Skill-tool calls (id→short_name resolution)" — depends on a clean scanner→report short_name chain.
- Issue #3138 (OPEN) — "backfill historical events from transcripts" — writes into the scanner's session-log format consumed by the scanner; depends on the universe both scripts agree on.
- `tests/skills/test_skill_invocation_scanner.py` + `tests/skills/test_skill_usage_report_filters.py` — both load their target script via `importlib.util.spec_from_file_location` (hyphenated filenames); the report-filter test already asserts `_core`/`_internal` exclusion. New tests follow this exact loader idiom.

### Gaps identified
- No single-source-of-truth module for the skill universe or short_name key.
- The exclusion set `{_archive, _core, _internal}` does not cover `_archived` (with a trailing "d"), so 6 archived email skills leak into the report universe — producing the `gmail-data-extraction` collision.
- The two `derive_short_name` implementations are independent parsers (one minimal hand-roll, one full yaml). They agree on current data but can silently diverge on future edge-case frontmatter — a latent join-break.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-06-15 via `gh issue view`):
- `#3139` — OPEN — Skill-invocation: reconcile scanner-vs-report skill universe (3,180 vs 833) — follow-on to #3112
- `#3137` — OPEN — Skill-invocation: capture Skill-tool calls (id→short_name resolution) — follow-on to #3112
- `#3138` — OPEN — Skill-invocation: backfill historical events from transcripts — follow-on to #3112

**File existence** (verified 2026-06-15):
- EXISTS: `scripts/skills/skill-invocation-scanner.py`
- EXISTS: `scripts/skills/skill-usage-report.py`
- EXISTS: `scripts/skills/audit_skill_lib.py`, `scripts/skills/skill_tier_lib.py` (shared-lib precedent, no PEP-723 header)
- EXISTS: `tests/skills/test_skill_invocation_scanner.py`, `tests/skills/test_skill_usage_report_filters.py`
- MISSING (new — this plan creates): `scripts/skills/_skill_identity.py`
- MISSING (new — this plan creates): `tests/skills/test_skill_identity.py`

**Reproduction proofs** (verify-against-repo-state — issue alleges a count/collision mismatch, so reproduction is mandatory):

Universe counts (`uv run --no-project python` over `.claude/skills`):
```
SCANNER universe (discover_skills, NO exclusions): 3180
REPORT universe (scan_skills, exclude _archive/_core/_internal): 833
In scanner but NOT in report: 2347
```

Gap breakdown (why 3180 → 833):
```
total: 3180
_archive: 2166
_core (not in _archive): 53
_internal (not _archive/_core): 128
_archived (survives report exclusion): 6
report-visible: 833
```

Collisions — short_name colliding across distinct rel-paths, in BOTH universes (the 2 colliders survive the report exclusion):
```
[gmail-data-extraction]
    email/_archived/gmail-data-extraction      <- leaks: report excludes _archive, NOT _archived
    email/gmail-data-extraction
[session-corpus-audit]
    coordination/session-corpus-audit          <- two genuinely distinct skills, same basename
    workspace-hub/session-corpus-audit
```

`_archived` (with the trailing "d") directories that the report's `{_archive}` exclusion misses:
```
email/_archived/gmail-data-extraction
email/_archived/gmail-email-to-repo-extraction
email/_archived/gmail-extract-and-clean
email/_archived/gmail-extract-archive
email/_archived/gmail-touchbase
email/_archived/gmail-unsubscribe
total _archived SKILL.md: 6
```

short_name derivation divergence between the two parsers, over the 833 report-visible skills:
```
report-visible short_name DIVERGENCES scanner-vs-report: 0
```
- Reproduced at: 2026-06-15 (current `.claude/skills` tree).
- Failure mode observed matches issue claim: YES for universe gap (3180 vs 833) and the `gmail-data-extraction` `_archived` collision. PARTIALLY for the join "carry/miss": the scanner already keys its OUTPUT by short_name and aggregates colliders (scanner `classify()` lines 144–156), and `apply_invocation_demotion` only acts on skills the report classified, so today the practical leak is bounded — but the **two universes genuinely differ** and the **short_name key is derived twice independently**, which is the structural defect to close. Divergence count is 0 today (latent, not active) — the fix is preventive (single derivation) plus correctness (`_archived` exclusion).

<!-- Source count: issue #3139 + #3112 plan + #3137/#3138 + 2 test files + live filesystem reproduction = 6+ distinct sources. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-06-15-issue-3139-skill-universe-reconciliation.md |
| Shared identity module (new) | `scripts/skills/_skill_identity.py` |
| Shared-module tests (new) | `tests/skills/test_skill_identity.py` |
| Scanner (modified) | `scripts/skills/skill-invocation-scanner.py` |
| Report (modified) | `scripts/skills/skill-usage-report.py` |
| Parity/collision tests (new) | `tests/skills/test_skill_universe_parity.py` |
| Plan review — Claude | scripts/review/results/2026-06-15-plan-3139-claude.md |
| Plan review — Codex | scripts/review/results/2026-06-15-plan-3139-codex.md |

---

## Deliverable

A single shared module `scripts/skills/_skill_identity.py` providing one `discover_skills(skills_root, exclusions=...)` and one `derive_short_name(skill_md_path)`, imported by BOTH `skill-invocation-scanner.py` and `skill-usage-report.py`, so the two scripts iterate the identical skill universe (with `_archived` correctly excluded) and key the short_name join from one derivation — with TDD parity and collision coverage.

---

## Pseudocode

`scripts/skills/_skill_identity.py` (pure lib, no PEP-723 header, no required third-party deps — mirrors `audit_skill_lib.py`):

```
DEFAULT_EXCLUSIONS = frozenset({"_archive", "_archived", "_core", "_internal"})

def discover_skills(skills_root, exclusions=DEFAULT_EXCLUSIONS):
    root = Path(skills_root)
    out = []
    for skill_md in root.rglob("SKILL.md"):
        parts = skill_md.parts
        if any(x in parts for x in exclusions):
            continue
        out.append(skill_md.parent.relative_to(root).as_posix())
    return sorted(out)

def derive_short_name(skill_md_path):
    # ONE canonical derivation: frontmatter `name` lowercased, else dir basename.
    # Use the same minimal single-line `name:` parse the scanner already uses so
    # the lib carries NO yaml dependency (scanner has none); report keeps yaml for
    # its OTHER frontmatter fields (related_skills/see_also) but routes the
    # short_name through this function.
    p = Path(skill_md_path)
    basename = p.parent.name
    name = _read_frontmatter_name(p)   # single-line `name:`; tolerant of quotes
    return ((name or basename).strip() or basename).lower()
```

Scanner integration:
```
from _skill_identity import discover_skills, derive_short_name   # importlib path-injected sys.path
# delete local discover_skills + derive_short_name; classify() calls the imports.
```

Report integration:
```
from _skill_identity import discover_skills, derive_short_name
# scan_skills(): iterate discover_skills(skills_dir) instead of inline rglob+exclusion;
# set short_name = derive_short_name(skill_md) instead of canonical_name.lower().
# Keep the yaml frontmatter parse for related_skills/see_also/body_refs — only the
# universe walk and the short_name KEY move to the shared lib.
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/skills/_skill_identity.py` | single source of truth: `discover_skills` + `derive_short_name` + `DEFAULT_EXCLUSIONS` (incl. `_archived`) |
| Create | `tests/skills/test_skill_identity.py` | unit tests for the shared lib (exclusions, short_name derivation, `_archived` fix) |
| Create | `tests/skills/test_skill_universe_parity.py` | parity test: scanner-universe == report-universe; collision test |
| Modify | `scripts/skills/skill-invocation-scanner.py` | import shared `discover_skills`/`derive_short_name`; delete local copies; keep output keyed by short_name |
| Modify | `scripts/skills/skill-usage-report.py` | route `scan_skills` universe walk + short_name key through shared lib; keep yaml parse for other frontmatter fields |
| Update | docs/plans/README.md | add this plan to the index (done at implementation time, not now) |

Note on import mechanics for two standalone scripts: both scripts are loaded by tests via `importlib.util.spec_from_file_location` and run in production via `uv run --no-project python scripts/skills/<script>.py`. A sibling-file `import _skill_identity` resolves because the script's own directory is on `sys.path[0]` when run directly — exactly how `skill-tier-report.py` already does `from audit_skill_lib import ...` and `from skill_tier_lib import ...`. The shared module carries **no PEP-723 header** (it is a lib, never executed directly), so the report's PEP-723 block (`dependencies = ["pyyaml"]`) is unaffected; the scanner stays dependency-free because the shared lib uses only stdlib. For the test loader, `test_skill_identity.py` imports the lib by injecting `scripts/skills` onto `sys.path` (or via `spec_from_file_location`), and the scanner/report test loaders gain the same `sys.path` insertion so their `import _skill_identity` resolves under pytest.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_discover_excludes_archive | `_archive` path part excluded | tree with `_archive/x/SKILL.md` + `dev/y/SKILL.md` | only `dev/y` |
| test_discover_excludes_archived | **`_archived` (trailing d) excluded** (the bug fix) | tree with `email/_archived/gmail-data-extraction/SKILL.md` + `email/gmail-data-extraction/SKILL.md` | only `email/gmail-data-extraction` |
| test_discover_excludes_core_internal | `_core` + `_internal` excluded | tree with each | neither present |
| test_discover_no_exclusions_opt_out | passing `exclusions=frozenset()` returns everything | full tree | all SKILL.md dirs |
| test_derive_short_name_from_frontmatter | uses `name:` lowercased | `---\nname: Foo-Bar\n---` | `foo-bar` |
| test_derive_short_name_fallback_basename | no frontmatter → dir basename | dir `my-skill`, no `---` | `my-skill` |
| test_derive_short_name_quoted | strips quotes on `name:` | `name: "Baz"` | `baz` |
| test_derive_short_name_unreadable | unreadable file → basename | OSError on read | basename lowercased |
| test_scanner_uses_shared_universe | scanner `discover_skills` == lib `discover_skills` | live skills tree | identical sorted lists |
| test_report_uses_shared_universe | report `scan_skills` keys == lib `discover_skills` | live skills tree | identical sets |
| test_universe_parity_scanner_eq_report | **the core AC**: scanner universe == report universe | live `.claude/skills` | equal sets, no `_archived` leak |
| test_no_archived_collision | `gmail-data-extraction` no longer collides | live tree | single rel-path for that short_name |
| test_known_genuine_collision_aggregated | `session-corpus-audit` (two real skills) still aggregates safely, with warning | live tree | scanner aggregates; warning emitted; report keys both full_rel but join is conservative |
| test_short_name_single_derivation | scanner short_name == report short_name for every report-visible skill | live tree | zero divergences |

---

## Acceptance Criteria

- [ ] All new tests pass: `uv run pytest tests/skills/test_skill_identity.py tests/skills/test_skill_universe_parity.py -v`
- [ ] No regression: `uv run pytest tests/skills/ -v` (existing scanner/report/demotion tests still green)
- [ ] `discover_skills` is called by BOTH scripts; the inline `rglob`+exclusion in `scan_skills` and the inline `discover_skills`/`derive_short_name` in the scanner are deleted (no duplicate definitions).
- [ ] Empirical parity re-check: scanner universe count == report universe count after the fix (both exclude `_archive`, `_archived`, `_core`, `_internal`); `_archived` 6 skills are now excluded from BOTH; `gmail-data-extraction` collision is gone.
- [ ] `session-corpus-audit` (a genuine two-skill collision, not an archive artifact) is still handled conservatively (aggregated + warned), not silently dropped.
- [ ] Review artifacts posted to scripts/review/results/.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | (pending) | |
| Codex | (pending) | |

**Overall result:** (pending)

Revisions made based on review:
- (none yet — draft)

---

## Risks and Open Questions

- **Risk (exclusion-set semantics change):** moving the scanner from "no exclusions" to the shared `{_archive,_archived,_core,_internal}` set drops 2,347 skills from the scanner's universe. This is the *intended* reconciliation, but any consumer relying on the scanner emitting rows for archived skills would change. Verified consumer: `apply_invocation_demotion` only acts on skills the report classified — so dropping archived skills from the scanner has no demotion-behavior regression. Confirm no other reader of `.claude/state/skill-invocations/*.json` expects archived rows.
- **Risk (`_archived` is the only "d" variant, today):** the fix adds the literal `_archived`. If future archive dirs use yet another spelling (`_archive_2024`, `_deprecated`), they would leak again. Mitigation: document the exclusion set as the single SSoT in `_skill_identity.py`; consider a prefix rule (`startswith("_archive")`) as a follow-on if churn warrants — NOT in this scope (could over-exclude an intentional `_archives-meta` skill; keep explicit literals for now).
- **Risk (genuine basename collisions persist):** `session-corpus-audit` exists under two real paths (`coordination/` and `workspace-hub/`). Excluding `_archived` does NOT resolve it — it is a true short_name clash. The scanner already aggregates colliders conservatively (a skill used under either path counts as used). This plan preserves that behavior and keeps the warning; it does NOT attempt to disambiguate genuine clashes (that is a separate naming-policy question — flag for the user if disambiguation is wanted).
- **Risk (PEP-723 / dependency surface):** the shared lib must stay stdlib-only so the scanner remains dependency-free; the report keeps `pyyaml` for its other frontmatter fields. Verify the lib does not import yaml.
- **Open:** should `session-corpus-audit` be renamed to disambiguate (e.g., `workspace-hub-session-corpus-audit`)? Out of scope for #3139; flag for user.

### Prerequisite flag for #3137 / #3138

This issue is very likely a **prerequisite** for clean delivery of #3137 and #3138:
- **#3137** (capture Skill-tool calls, `<plugin>:<name>` → short_name resolution) must normalize ids to the SAME short_name key the scanner→report chain uses. If the universe/short_name derivation is forked across two scripts, #3137 would have to pick one and risk re-introducing the join gap. Landing #3139 first gives #3137 a single `derive_short_name` to target.
- **#3138** (backfill historical events) writes events into the scanner's session-log format keyed by rel-path / short_name. It should reuse the shared `discover_skills`/`derive_short_name` to avoid a third independent derivation. Landing #3139 first gives it the canonical helper to import.

Recommendation: **land #3139 before #3137 and #3138.**

---

## Complexity: T2

**T2** — new shared module + two existing scripts modified + multi-file TDD (3 new test files). Harness tooling, single repo, no cross-provider systemic change. Adversarial review at 2 providers (Claude + Codex).
