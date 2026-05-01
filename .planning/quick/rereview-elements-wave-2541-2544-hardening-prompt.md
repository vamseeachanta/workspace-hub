# Focused Re-review Request: Elements plans #2541-#2544 after hardening commit bdafe39cd

You are an adversarial reviewer. This is a focused re-review after a prior Codex+Gemini review found blockers. Review whether the new addenda resolve the blockers sufficiently for a user approval shortlist.

Do NOT approve implementation. Decide only whether each issue is approval-ready for the explicitly bounded subset described by the addendum.

Prior synthesis:
- #2541 had MAJOR blockers: SESA clearance unresolved, vendor/TBE controls weak, persisted full-text `.txt` intermediates.
- #2542 had MAJOR blockers: not test-first, broad full-text conversion, standards pages in wrong namespace, OCR risk.
- #2543 had MINOR findings: public revision/source metadata, no cleanup language, structured no-extraction frontmatter.
- #2544 had mixed MAJOR/APPROVE: extraction/abstract publication too broad; pointer/scout metadata-only subset needs separation and clearance schema.

Required output:
| Issue | Verdict after hardening (APPROVE/MINOR/MAJOR) | Approval-ready bounded subset | Remaining blockers |
Then recommended execution order and whether user approval should be requested now.


---

## Issue #2541
Path: `docs/plans/2026-04-28-issue-2541-elements-sesa-curated-extraction-plan.md`

### Addendum under re-review
```markdown
## Adversarial Review Resolution Addendum (2026-04-29)

This addendum is authoritative over earlier pseudocode if there is any conflict.

### Clearance gate: hard block before extraction
- **No SESA extraction, source page publication, concept page publication, comparison page publication, or quote/snippet emission may occur until SESA citeability is confirmed and recorded.**
- Required clearance record: `docs/governance/sesa-extraction-clearance-2026.md` or an issue comment on #2541 from the responsible project/data owner explicitly allowing the named tranche rows and extraction level.
- The clearance record must include: approver name/role, approval date, allowed extraction level per row, prohibited content classes, and whether vendor/TBE material is allowed.

### No persisted full-text intermediates
- Replace any earlier instruction to write extracted text such as `.planning/intel/elements-deep-extraction/sesa/<slug>.txt`.
- Implementation may only persist bounded structured outputs: per-row YAML/JSON metadata, allowed short fields, and authored wiki summaries.
- Tests must fail if repo artifacts contain full extracted document bodies, raw text dumps, or copied source documents.

### Vendor/TBE brochure policy
- Vendor/TBE rows are excluded from tranche-1 extraction unless row-level clearance explicitly allows them.
- Default allowed fields are limited to file path, file name, byte size, document type, vendor name if visible in the file name/metadata, and a one-sentence non-technical reason for deferral.
- Prohibited by default: body text, tables, specifications, quoted clauses, equipment details, and screenshots/images.

### Test-first additions
Before any wiki write, add failing tests or validation checks proving:
1. clearance record exists and covers every row selected for extraction;
2. no full-text `.txt`/raw extraction dump is written under `.planning/` or `knowledge/`;
3. vendor/TBE rows without clearance remain metadata-only;
4. `knowledge/wikis/lng-projects/wiki/index.md` and `log.md` are updated sequentially, not concurrently with #2544.


```

---

## Issue #2542
Path: `docs/plans/2026-04-28-issue-2542-elements-doris-university-training-plan.md`

### Addendum under re-review
```markdown
## Adversarial Review Resolution Addendum (2026-04-29)

This addendum is authoritative over earlier pseudocode if there is any conflict.

### TDD is test-first, not post-condition-only
- Implementation must begin by adding failing validation tests/checks for page schema, source path allowlists, extraction allowlists, no raw assets, no unresolved standards citations, and no copied full-text training material.
- Post-generation checks alone are insufficient and must not be treated as TDD compliance.

### Metadata-first curated extraction
- Replace any broad instruction that each artifact will be converted to full wiki text content.
- Tranche-1 output is metadata-first plus curated, authored summaries only.
- Per-artifact IP screening is required before any slide text, speaker notes, calculation text, figures, or standard-derived excerpts are summarized.
- Default prohibited: full deck text, copied figures, standard excerpts/clauses, screenshots, and OCR-derived text.

### Standards namespace and citation resolver
- Standards pages must target `knowledge/wikis/engineering-standards/wiki/standards/` as the canonical namespace, not `knowledge/wikis/engineering/wiki/standards/`.
- Engineering/training concept pages may cross-link to engineering-standards pages.
- A standards stub may only be created from public publisher metadata with revision/source/date fields; if revision metadata is unknown, fail closed and leave an unresolved citation note.

### OCR out of scope for tranche 1
- OCR fallback is explicitly out of scope for this tranche unless separately approved per artifact.
- Text-layer failures should result in metadata-only treatment, not OCR.


```

---

## Issue #2543
Path: `docs/plans/2026-04-28-issue-2543-elements-doris-codes-standards-plan.md`

### Addendum under re-review
```markdown
## Adversarial Review Resolution Addendum (2026-04-29)

This addendum is authoritative over earlier pseudocode if there is any conflict.

### Public-source metadata requirements
- Any BV or other standards stub must include `revision_source`, `verified_on`, and a public URL/source citation.
- If public revision metadata is unavailable, do not create the standards page; record a deferred/unverified row instead.

### No cleanup/removal in this plan
- Retention, deletion, or removal recommendations are out of scope for #2543.
- Perry's Handbook or any other duplicate/removal decisions must remain with #2534 or a later cleanup-specific issue after the 2026-05-28 retention gate.

### Structured no-extraction policy
- Wiki pages generated by this plan must include structured frontmatter such as `extraction_policy: metadata-only` and `raw_copy_allowed: false`.
- Validation must check exact frontmatter values rather than weak substring matches.
- Any standards family counts emitted as wiki facts must be marked approximate or regenerated during implementation with command/date evidence.


```

---

## Issue #2544
Path: `docs/plans/2026-04-28-issue-2544-elements-woodfibre-scout-plan.md`

### Addendum under re-review
```markdown
## Adversarial Review Resolution Addendum (2026-04-29)

This addendum is authoritative over earlier pseudocode if there is any conflict.

### Split approval: pointer/scout metadata only first
- The approval-ready subset for #2544 is **metadata pointer/scout output only**.
- No document abstract extraction, technical summary extraction, direct quote extraction, table extraction, or figure extraction may occur under #2544 until a separate extraction plan is written after clearance.

### Clearance authority and row-level schema
- `docs/governance/woodfibre-extraction-clearance-2026.md` remains a hard prerequisite for any post-scout extraction.
- Accepted approvers must be explicitly named by role: ACMA project owner, client-authorized reviewer, or legal/IP delegate. A generic "project lead" is insufficient.
- Row-level clearance must record: source path, document identifier, approver, approval date, allowed extraction level (`metadata-only`, `curated-fields`, `short-quote-approved`, `abstract-approved`), prohibited content, and expiration/review condition.

### No persisted full-text or default quotes
- Implementation must not persist full extracted PDF/DOCX/TXT text in `.planning/`, `knowledge/`, or any git-tracked path.
- Extraction, if later approved, must be streaming/bounded with strict page/character caps and no intermediate full-text files.
- Direct quotes are prohibited by default; no 2 KB quote allowance exists unless row-level clearance explicitly sets `short-quote-approved`.

### Sequential LNG wiki updates
- Because #2541 and #2544 both touch `knowledge/wikis/lng-projects/wiki/index.md` and `log.md`, execute them sequentially and rebase/revalidate between them.
- #2544 should run after #2541 only if both retain separate clearance records and non-overlapping page names.


```
