# Plan for #2392: Wiki coverage-gap detector — v3 (post-iter-2 fixes + embedded evidence)

> **Status:** plan-review (iteration 3 of 3 — final)
> **Complexity:** T2
> **Date:** 2026-04-20 (v3)
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2392
> **Prior reviews:** v1 at commit `5b4c347cd` (Claude MINOR + Codex/Gemini MAJOR); v2 at commit `27821dafa` (Codex/Gemini MAJOR).

---

## Revision History

- **v1:** initial draft; convergent P1s: sha256 unenforced, AC-test gaps, unverified deps, threat model, scope.
- **v2:** added §Identity Contract / §Tier Assignment / §Threat Model / §AC↔Test Map. Still MAJOR on (a) `_summary.md` inconsistency, (b) §8.1 tolerance, (c) wiki doc_key extraction mechanism undefined, (d) "unverified claims" policy finding.
- **v3 (this revision):**
  - **M1 fix:** `_summary.md` added to Files-to-Change + Artifact Map.
  - **M1 fix:** wiki doc_key extraction mechanism defined explicitly.
  - **M1 fix:** engineering wiki §8.1 non-compliance now emitted as warning, not tolerated.
  - **M2 fix (Option α):** §Evidence block embeds actual `gh`/`ls`/`sed` output per updated template.
  - **Correction:** `code-registry.yaml` path is `data/design-codes/code-registry.yaml` (not `data/document-index/` — v2 had wrong path).

---

## Resource Intelligence Summary

### Existing repo code
- `scripts/data/document-index/provenance.py` — provenance-record writer (see line-excerpt evidence below); baseline join surface.
- `scripts/data/document-index/phase-a-index.py` — legacy md5 prefix handling for `og_standards` (see excerpt).
- `scripts/knowledge/llm_wiki.py` — wiki ingest surface; does not produce gap lists.
- Gap: no existing `detect_wiki_gaps.py` or similar (see evidence).

### Standards
Not applicable.

### LLM Wiki pages consulted
- `knowledge/wikis/engineering/CLAUDE.md` — declares `{title, tags, added, last_updated}` required (see excerpt). **This set omits `doc_key`**, which violates operating-model §8.1 baseline-floor. v3 emits a warning per affected page, rather than tolerating it.

### Documents consulted
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` §2/§3/§4/§7/§8.1.
- `data/document-index/registry.yaml`, `mounted-source-registry.yaml`, `online-resource-registry.yaml`, `dde-standards-inventory.yaml`, `standards-transfer-ledger.yaml`.
- `data/design-codes/code-registry.yaml` **(corrected path — not under `data/document-index/`)**.

### Dependency Matrix

| Issue | Relationship | Behavior if unshipped |
|---|---|---|
| #2205 | authority (CLOSED) | — always available |
| #2360 | soft | tolerate missing `doc_key` via `status: identity-unresolved` |
| #2389 | soft | tolerate missing `source_doc_key` via fallback |
| #2365 | scope-separated (OPEN) | no overlap |
| #2366 | downstream consumer (OPEN) | no blocking |

### Gaps identified
- No per-domain gap detector.
- No gap-entry shape standard.
- Wiki doc_key coverage partial (blocked by #2360).

### Evidence (embedded verification)

**Issue statuses** (via `gh issue view <n> --json number,state,title` at 2026-04-20T15:50Z):
- `#2205` — **CLOSED** — feat(knowledge): define multi-machine llm-wiki + resource/document intelligence operating model
- `#2360` — **OPEN** — feat(knowledge): update wiki CLAUDE.md files to declare doc_key in L3 frontmatter required-set
- `#2389` — **OPEN** — feat(doc-intel): thread source_doc_key through promotion pipeline and promoted artifacts
- `#2365` — **OPEN** — feat(knowledge): promote design-code registry into standards overviews and repo-target backlinks
- `#2366` — **OPEN** — feat(knowledge): add llm-wiki strengthening scorecard and prioritized action queue

**File existence** (`ls -la` at 2026-04-20T15:51Z):
```
EXISTS: scripts/data/document-index/provenance.py
EXISTS: scripts/data/document-index/phase-a-index.py
EXISTS: scripts/knowledge/llm_wiki.py
EXISTS: data/document-index/registry.yaml
EXISTS: data/document-index/mounted-source-registry.yaml
EXISTS: data/document-index/online-resource-registry.yaml
EXISTS: data/document-index/dde-standards-inventory.yaml
EXISTS: data/document-index/standards-transfer-ledger.yaml
EXISTS: data/design-codes/code-registry.yaml
EXISTS: knowledge/wikis/engineering/CLAUDE.md
MISSING: data/document-index/code-registry.yaml  (v2 cited this path incorrectly; v3 uses data/design-codes/)
```

**Line excerpts:**

`sed -n '80,85p' scripts/data/document-index/provenance.py`:
```
"path": record.get("path", ""),
"host": record.get("host", "unknown"),
"discovered": discovered or _now_iso(),
}
# Preserve og_db_id when the source is og_standards
if record.get("og_db_id") is not None:
```

`sed -n '133,140p' scripts/data/document-index/phase-a-index.py`:
```
size_bytes = row["file_size"] or 0
content_hash = row["content_hash"]
if content_hash and not content_hash.startswith(("sha256:", "md5:")):
    if len(content_hash) == 32:
        content_hash = f"md5:{content_hash}"    # legacy MD5 from og_standards
    else:
        content_hash = f"sha256:{content_hash}"
```

`head -25 knowledge/wikis/engineering/CLAUDE.md` — Frontmatter Schema table shows required fields:
```
| `title` | **required** | string | Page title |
| `tags` | **required** | list | Classification tags, e.g. `[cfd, openfoam]` |
| `added` | **required** | date | ISO date when page was created |
| `last_updated` | **required** | date | ISO date of last modification |
```
→ **`doc_key` is NOT in required set**, violating §8.1 baseline-floor. Detector emits a warning per page lacking `doc_key`.

**Gap proofs:**
- `ls scripts/knowledge/*gap*` → "No such file or directory" (2026-04-20T15:51Z) → confirms no existing detector.
- `ls scripts/knowledge/detect*` → "No such file or directory" → confirms no `detect_*` module.
- `grep -c "CFR" data/document-index/standards-transfer-ledger.yaml` → 0 (not relevant to this plan, but referenced elsewhere).

---

## Identity Contract (§3 compliance)

All `doc_key` values read or emitted MUST conform to operating-model §3:
- Canonical: `sha256:<64-hex>`.
- Legacy `md5:<hex>` accepted for reads only (per §3 table, per `phase-a-index.py:135-137` excerpt above).
- Bare-hex rejected with clear error.
- Path-only identity forbidden.

For sources lacking any `doc_key`, tool emits `status: identity-unresolved` rather than fabricating one.

**Wiki doc_key extraction mechanism** (resolved from v2 ambiguity):
1. For each `knowledge/wikis/*/wiki/**/*.md`, parse YAML frontmatter (PyYAML, safe_load).
2. Look for top-level `doc_key` field.
3. If present and matches `^(sha256|md5):[0-9a-f]+$` → valid; add to wiki_doc_keys set.
4. If present but non-conforming → emit warning, mark page as `identity-non-conforming`, do NOT add to set.
5. If absent → emit §8.1 warning (baseline-floor violation), mark page as `identity-missing`, do NOT add to set.

Tests:
- `test_sha256_doc_key_accepted`
- `test_md5_doc_key_accepted_read_only`
- `test_bare_hex_doc_key_rejected`
- `test_path_only_identity_forbidden`
- `test_missing_doc_key_emits_section_8_1_warning`
- `test_nonconforming_doc_key_emits_warning_not_added_to_set`

---

## Cross-Machine Tier Assignment (§7)

| Artifact | Path | Tier | Authority |
|---|---|---|---|
| L2 registries | `data/document-index/*.yaml` | 1 git-tracked | authoritative |
| L2 design-code registry | `data/design-codes/code-registry.yaml` | 1 git-tracked | authoritative |
| L3 wiki pages | `knowledge/wikis/**/*.md` | 1 git-tracked | authoritative |
| Analysis reports | `docs/reports/*.md` | 1 git-tracked | authoritative |
| Mounted sources (path metadata only) | `/mnt/ace/**` via registry | 2 shared-mount | referenced not read |
| Gap YAML outputs | `docs/reports/wiki-coverage-gaps/*.yaml` | 1 git-tracked | authoritative |
| **Summary output** | **`docs/reports/wiki-coverage-gaps/_summary.md`** | **1 git-tracked** | **authoritative** |

Detector does not read `/mnt/ace/` directly. Tier-3 local-cache explicitly out of scope (tested).

---

## Threat Model

**Input surfaces:** YAML registries, markdown files.
**Trust boundaries:** all inputs git-tracked. Shared-mount metadata (paths from registry) treated as opaque strings; never dereferenced by detector.
**Mitigations:** frontmatter parse errors → skip + log; schema mismatch → fail-closed; output path allowlist.
**Mount-metadata validation:** detector validates that strings claiming to be paths match `^[/A-Za-z0-9._\-]+$` before recording them in output; non-conforming mount paths flagged with `status: mount-path-invalid`.

**Tests:**
- `test_malformed_frontmatter_does_not_crash`
- `test_schema_mismatch_fails_closed`
- `test_output_path_allowlist_enforced`
- `test_mount_metadata_validation` (new — addresses v2 Codex finding on trust boundary)

---

## AC ↔ Test Map

| AC | Test(s) |
|---|---|
| All tests pass | `pytest tests/knowledge/test_detect_wiki_gaps.py` |
| No regression | CI |
| <5 min runtime | `test_runtime_budget_under_five_min` |
| ≥1 gap YAML per domain on first run | `test_first_run_emits_per_domain_yaml` (fixture covers ≥3 domains); real-corpus smoke test during reviewer approval (not automated) |
| Weekly cron | `test_cron_config_parses_and_schedules_weekly` |
| `_summary.md` written | `test_summary_md_written_with_per_domain_counts` |
| §3 identity | `test_sha256_*`, `test_md5_*`, `test_bare_hex_*`, `test_path_only_*` |
| §8.1 warnings | `test_missing_doc_key_emits_section_8_1_warning` |
| Tier-3 exclusion | `test_tier3_local_cache_excluded` |
| Threat tests | listed in Threat Model |
| Review artifacts posted | reviewer-task (not automated) |

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-20-issue-2392-wiki-coverage-gap-detector.md` |
| Tests | `tests/knowledge/test_detect_wiki_gaps.py` |
| Implementation | `scripts/knowledge/detect_wiki_gaps.py` |
| Config | `config/ai-tools/wiki-gap-detection.yaml` |
| Per-domain outputs | `docs/reports/wiki-coverage-gaps/<domain>.yaml` |
| **Summary output** | `docs/reports/wiki-coverage-gaps/_summary.md` |
| Output README | `docs/reports/wiki-coverage-gaps/README.md` |

---

## Deliverable

A `detect_wiki_gaps.py` CLI emitting per-domain gap YAML + `_summary.md` under `docs/reports/wiki-coverage-gaps/`, with strict `sha256:` identity handling, §8.1 violation warnings, §7 tier classification, and fail-closed error semantics.

---

## Pseudocode

```
function detect_gaps(config):
    l2_sources = union of load_and_validate(registry) for registry in [
        "data/document-index/registry.yaml",
        "data/document-index/mounted-source-registry.yaml",
        "data/document-index/online-resource-registry.yaml",
        "data/document-index/dde-standards-inventory.yaml",
        "data/document-index/standards-transfer-ledger.yaml",
        "data/design-codes/code-registry.yaml"   # corrected path
    ]
    analysis_reports = scan("docs/reports/*.md") filtered by L3-eligibility heuristic

    wiki_doc_keys = set()
    section_8_1_warnings = []
    for page in glob("knowledge/wikis/*/wiki/**/*.md"):
        fm = parse_frontmatter_safe(page)  # YAML safe_load
        key = fm.get("doc_key")
        if key is None:
            section_8_1_warnings.append({page, reason="missing doc_key (§8.1 baseline-floor)"})
            continue
        if re.match(r"^(sha256|md5):[0-9a-f]+$", key):
            wiki_doc_keys.add(key)
        else:
            section_8_1_warnings.append({page, reason=f"non-conforming doc_key: {key}"})

    gaps_by_domain = defaultdict(list)
    for source in l2_sources ∪ analysis_reports:
        validate_mount_metadata_string(source.path)  # threat-model check
        key = source.doc_key
        identity_status = classify_identity(key)  # ok | legacy-read-only | identity-unresolved | non-conforming
        if key not in wiki_doc_keys:
            gaps_by_domain[classify_discipline(source)].append(
                gap_entry(source, identity_status, tier=classify_tier(source))
            )

    for domain, entries in gaps_by_domain.items():
        atomic_write_yaml(f"docs/reports/wiki-coverage-gaps/{domain}.yaml", entries)
    atomic_write_markdown("docs/reports/wiki-coverage-gaps/_summary.md",
        render_summary(gaps_by_domain, section_8_1_warnings))
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/knowledge/detect_wiki_gaps.py` | main |
| Create | `tests/knowledge/test_detect_wiki_gaps.py` | tests |
| Create | `config/ai-tools/wiki-gap-detection.yaml` | config |
| Create | `docs/reports/wiki-coverage-gaps/README.md` | output format |
| **Create** | **`docs/reports/wiki-coverage-gaps/_summary.md`** (first run by CLI, committed in subsequent runs) | **summary output (iter-2 M1 fix)** |
| Modify | `config/scheduled-tasks/schedule-tasks.yaml` | weekly schedule |

---

## TDD Test List

(All v2 tests plus new M1-addressing tests:)
- `test_summary_md_written_with_per_domain_counts` (NEW — M1 `_summary.md` consistency)
- `test_missing_doc_key_emits_section_8_1_warning` (NEW — M1 §8.1 enforcement)
- `test_nonconforming_doc_key_emits_warning_not_added_to_set` (NEW)
- `test_mount_metadata_validation` (NEW — threat-model iter-2 finding)
- ... (all 20 v2 tests retained)

---

## Acceptance Criteria

All v2 ACs plus:
- [ ] `_summary.md` emitted with per-domain counts + §8.1 warning summary
- [ ] Engineering wiki pages lacking `doc_key` produce §8.1 warnings (not tolerated)
- [ ] Wiki doc_key extraction uses YAML frontmatter parse, not regex on body
- [ ] Mount-metadata strings validated before recording

---

## Adversarial Review Summary

| Provider | Verdict | Artifact |
|---|---|---|
| Claude v1 | MINOR | `2026-04-20-plan-2392-claude.md` |
| Codex v1 | MAJOR | `2026-04-20-plan-2392-codex.md` |
| Gemini v1 | MAJOR | `2026-04-20-plan-2392-gemini.md` |
| Codex v2 | MAJOR | `2026-04-20-v2-plan-2392-codex.md` |
| Gemini v2 | MAJOR | `2026-04-20-v2-plan-2392-gemini.md` |
| Codex v3 | PENDING | — |
| Gemini v3 | PENDING | — |

---

## Risks and Open Questions

- **Risk:** §8.1 warnings may flood output until #2360 lands. Mitigation: summary shows counts; not a blocker.
- **Open:** Should `_summary.md` be committed on every run or only when counts change? Plan default: commit when changed (idempotency-friendly).

---

## Complexity: T2
