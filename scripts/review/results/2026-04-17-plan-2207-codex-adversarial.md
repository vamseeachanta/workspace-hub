# Adversarial Review: #2207 Standards/Codes Provenance + Reuse Contract

> **Reviewer:** Codex (cross-provider second opinion per planning-skill Step 3)
> **Date:** 2026-04-17
> **Transcribed by:** Claude — Codex's sandbox blocked both the GitHub-connector write and the local patch write. Findings below are Codex's; Claude has spot-verified each load-bearing claim against live repo state and recorded the verification stamps inline.
> **Deliverable under review:** `docs/document-intelligence/standards-codes-provenance-reuse-contract.md`
> **Sibling Claude review:** `scripts/review/results/2026-04-17-plan-2207-claude-adversarial.md` — Codex was tasked to find what Claude missed, not to confirm.

## Stance declaration

Codex was dispatched with the planning-skill reviewer-stance contract: assume defects until proven otherwise, no praise, no restatement, evidence-first, treat cited claims as assertions to verify. Codex returned MAJOR with four new findings, none overlapping the seven from the Claude pass.

## Verdict: **MAJOR** — not approval-ready

Three of the four findings target identity/lifecycle assumptions the contract treats as already-true; live code disagrees.

---

## Finding C1 — MAJOR: `content_hash` is not uniformly SHA-256

**Claim under review (Section 3.1, table row 1):** "`content_hash` ... **This IS the `doc_key`.**" The `doc_key` is defined in Section 3.1 as the SHA-256 hex digest.

**Codex evidence:** `scripts/data/document-index/phase-a-index.py:135-139` preserves a legacy MD5 identity for some `og_standards` records:

```python
if content_hash and not content_hash.startswith(("sha256:", "md5:")):
    if len(content_hash) == 32:
        content_hash = f"md5:{content_hash}"    # legacy MD5 from og_standards
    elif len(content_hash) == 64:
        content_hash = f"sha256:{content_hash}"
```

**Claude verification (2026-04-17):** Confirmed at the cited line numbers. `phase-a-index.py` actively writes `md5:`-prefixed values into the `content_hash` field for 32-char inputs.

**Why this is a defect:** The contract's central identity rule — "`content_hash` IS the `doc_key`, where `doc_key` = SHA-256 hex digest" — is **already false** in the live registry. Anti-pattern 8.5 ("prefix inconsistency") prescribes "the canonical `doc_key` is the bare 64-character hex digest" — but the live code emits 32-char MD5 values for og_standards. An implementation following Section 8.5's "strip the prefix and treat as bare hex" rule would silently treat MD5 hashes as SHA-256 doc_keys, joining unrelated documents.

**Required fix:** The contract must either (a) define a migration plan to re-hash all `md5:`-prefixed records to SHA-256 before claiming `content_hash` is a doc_key, or (b) treat `md5:`-prefixed records as a separate identity namespace that must be excluded from `doc_key` joins until migrated. Section 3.1's mapping cannot stand as written.

---

## Finding C2 — MAJOR: `summary_ref` / wiki `source_ref` examples don't match the live summary writer

**Claim under review (Section 4.2, `summary_ref` row):** "Path to the summary JSON file (`summaries/<doc_key>.json`)."
**Same claim restated (Section 6.3 frontmatter example):** `source_ref: data/document-index/summaries/a1b2c3d4e5f6....json` (bare hex digest, no prefix).

**Codex evidence:** The live summary writer keys files by the prefixed hash string, not bare hex.

**Claude verification (2026-04-17):**
```
$ ls data/document-index/summaries/ | head -3
sha256:3aa1fdc3e2c73e1f9c3bb476e5eb663a7742518462bf1abefcbe26b7efd87fd4.json
sha256:5e5f61e785295f0ac849399bb302cb5192ca84c108e6a57e82b8cc83b8b431af.json
sha256:b576ada30e9ccea727ecab10e1f2a0e435613b25147e3bbb2b3f3d2b718766fd.json
```

**Why this is a defect:** Anti-pattern 8.5 forbids prefix inconsistency, then Section 6.3's own example perpetuates it by showing a bare-hex path that does not exist on disk. An implementer building the wiki promotion pipeline literally from the example will write back-link paths that resolve to nothing. Combined with Finding C1 (some hashes are MD5), the actual filename pattern is `{md5,sha256}:<hex>.json`.

**Required fix:** Either (a) update the Section 6.3 example and Section 4.2 description to show the prefixed form (`summaries/sha256:<hex>.json`), or (b) commit to the bare-hex canonical form and add a back-population task to rename every existing summary file. (a) is consistent with current code; (b) is consistent with anti-pattern 8.5 but is a much larger migration.

---

## Finding C3 — MAJOR: `status` is overloaded — the contract redefines a field that already has unrelated meaning in the repo

**Claim under review (Section 4.1):** "`status` — Processing status: `indexed`, `summarized`, `extracted`, `promoted`."

**Codex evidence:** The repository already uses `status` as a field name in classification and ledger contexts with unrelated semantics. The contract introduces a new processing-lifecycle meaning under the same name without acknowledging the existing usage or providing a disambiguation/namespace rule.

**Why this is a defect:** This compounds Claude Finding 1 (status enum omits `gap`). If `status` already means different things in different files (e.g., classification status in some, ledger status in others, processing lifecycle in this contract), then any conformance check (#2206) that reads "the `status` field" will produce false positives or false negatives depending on which file it's pointed at. The contract needs a per-namespace field name (e.g., `processing_status` or `pipeline_status`) or an explicit declaration of which files this enum applies to.

**Required fix:** Rename the field in the contract to `processing_status`, OR add a Section 4.1 sub-section that enumerates exactly which surfaces (`index.jsonl`, `summaries/*.json`, etc.) carry this `status` enum and which (e.g., ledger rows) carry a different `status`.

---

## Finding C4 — MAJOR: `discovered` semantics drift from `provenance.py` actual behavior

**Claim under review (Section 4.1, `discovered` row):** "ISO 8601 timestamp — When this document was first indexed."

**Codex evidence:** `scripts/data/document-index/provenance.py` stamps `discovered` at merge time when the input record does not already carry one.

**Claude verification (2026-04-17):** `provenance.py:65,82,94`:
```python
def _build_provenance_entry(rec, *, discovered: Optional[str] = None, ...):
    ...
    "discovered": discovered or _now_iso(),
    ...
def _now_iso(): return datetime.now(timezone.utc).isoformat()
```
Confirmed: the field falls back to "now at merge time" when no upstream `discovered` value is present. Whether the input `discovered` value is reliably populated by every Phase-A writer is itself unverified — but the fallback path overwrites the contract's promised semantics.

**Why this is a defect:** "First-indexed" is a one-time stamp; "merge time" updates whenever provenance is re-merged. The contract treats `discovered` as immutable provenance truth (Section 4.3 places it under L2 ownership as part of "extraction lineage"). Live code allows it to drift on every merge run.

**Required fix:** Either (a) tighten `provenance.py` to require an upstream `discovered` value and refuse to stamp at merge time, or (b) update Section 4.1 to acknowledge that `discovered` is "earliest available timestamp, falling back to merge time when no upstream value is present" — and add a separate `first_indexed_at` field if the original semantics are needed.

---

## Verified claims (what Codex checked and what passed)

- The `doc_key` rule in #2205 Section 3 is a content-based identity rule. Section 3 of the contract correctly inherits this — no redefinition.
- The pyramid layer ownership in Section 4.3 mirrors #2205 Section 2 (with the borderline `wiki_refs` placement noted by Claude Finding 4 — Codex did not pursue further).
- The decision tree in Section 5.1 has a defensible structure (the artifact-existence guard added per the 2026-04-11 review is present).
- The anti-pattern catalog in Section 8 is correctly scoped to provenance/identity concerns (does not bleed into #2206 conformance or #2208 retrieval).

## Disagreements with Claude review

None — the four findings above are non-overlapping with the seven in the Claude artifact. Codex has no objection to any Claude finding.

## Finding count: 4 MAJOR, 0 MINOR. Combined with Claude's pass: **3 MAJOR + 4 MAJOR + 4 MINOR = 11 outstanding findings.**

## Recommendation

Do not advance to `status:plan-approved`. The cumulative evidence shows the contract treats several already-shipped behaviors (MD5 identity, prefixed summary filenames, merge-time `discovered` stamping, `gap` status) as if they did not exist. A revision is required, not a label move. Suggest a single coordinated revision pass that addresses all 11 findings rather than incremental patches.

## Process note

Codex was unable to write this artifact directly. The findings above are Codex's; the verification stamps and this transcription wrapper are Claude's. If a stronger cross-provider audit trail is needed, re-running Codex via a path that does not require sandbox file writes (e.g., capturing its analysis to stdout and committing that) would produce a Codex-authored artifact rather than a Claude transcription.
