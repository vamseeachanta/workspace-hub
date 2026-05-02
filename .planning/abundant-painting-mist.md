# Clearance-Prep Report: #2541 (SESA) + #2544 (Woodfibre)

> **Lane:** provider-capacity-aware-20260501-0613
> **Date:** 2026-05-01
> **Author:** Claude (read-only planning lane)
> **Intended deliverable path:** `/mnt/local-analysis/agent-logs/provider-capacity-aware-20260501-0613/results/claude-elements-clearance-prep.md`
> **Sandbox constraint:** the target path is outside `/mnt/local-analysis/workspace-hub` — Write tool blocked. This report is captured here; operator must `cp` to the intended location.

---

## 1. Verdict: Safe to Dispatch Now vs Blocked

| Item | Status | Rationale |
|------|--------|-----------|
| SESA #2541 adversarial review | **BLOCKED** | No `scripts/review/results/2026-04-28-plan-2541-{claude,codex,gemini}.md` exist. Adversarial review was never dispatched. |
| Woodfibre #2544 adversarial review | **BLOCKED** | Same — no review artifacts exist. |
| SESA extraction / wiki-page emission | **HARD BLOCKED** | `docs/governance/sesa-extraction-clearance-2026.md` does not exist. 2026-04-29 addendum makes this a fail-closed prerequisite. |
| Woodfibre extraction / wiki-page emission | **HARD BLOCKED** | `docs/governance/woodfibre-extraction-clearance-2026.md` does not exist. Addendum requires named ACMA/project-owner sign-off. |
| SESA planning artifacts (dossier + TSV) | **SAFE — already landed** | `.planning/intel/elements-overnight-wave/sesa-candidate-dossier.md` and `sesa-first-tranche.tsv` exist on disk. |
| Woodfibre planning artifacts (scout + TSV) | **SAFE — already landed** | `.planning/intel/elements-overnight-wave/woodfibre-corpus-scout.md` and `woodfibre-first-tranche.tsv` exist on disk. |
| Adversarial review dispatch (read-only review agents) | **SAFE to dispatch** | Review agents only read the plan + write review result files. Can proceed now. |
| Applying `status:plan-approved` label | **BLOCKED** | User-in-loop gate. No lane may self-approve. |

**Summary:** The only action safe to dispatch now is the adversarial review round for both plans. Everything downstream (extraction, wiki writes, label changes) remains blocked until the user provides approval and the governance clearance documents are created by the data owner.

---

## 2. SESA #2541 — Clearance Dossier Template

### Required Fields

| Field | Description | Example |
|-------|-------------|---------|
| `approver_name` | Full name of the person granting extraction clearance | — |
| `approver_role` | One of: `project-owner`, `data-owner`, `client-authorized-reviewer`, `legal-IP-delegate` | — |
| `approval_date` | ISO 8601 date | `2026-05-XX` |
| `allowed_extraction_level` | Per-row enum: `metadata-only` \| `curated-fields` \| `short-quote-approved` \| `abstract-approved` | — |
| `prohibited_content_classes` | List of content types never to extract | See below |
| `vendor_tbe_policy` | Explicit yes/no + conditions for vendor/TBE material | — |
| `expiration_or_review_condition` | When this clearance lapses | — |
| `tranche_rows_covered` | Row numbers from `sesa-first-tranche.tsv` that this clearance covers | `1-20` or subset |

### Approver Role Choices (acceptable)

- `project-owner` — the person accountable for DORIS 62092 SESA deliverables
- `data-owner` — the custodian of the Elements archive with disposition authority
- `client-authorized-reviewer` — a downstream client representative who owns the IP
- `legal-IP-delegate` — legal counsel authorized to grant redistribution rights

A generic "project lead" or "engineer" is **insufficient** per the 2026-04-29 addendum.

### Prohibited Content Classes (default deny-list)

1. Full document body text (raw PDF/DOCX dumps)
2. Numerical tables from engineering calculations
3. Vendor proprietary data (PIETRO, RMT VALVOMECCANICA brochure content)
4. NDA-marked material (any page bearing a confidentiality banner)
5. Standards body copyrighted text (DNV-ST-F101, API 6DSS, ASME B16.5, ASTM A-series)
6. Personnel names, contact details, compensation
7. Commercial/pricing information
8. Full drawings (DWG/image reproductions)
9. Email/MSG correspondence bodies
10. Database (.db) content

### Tranche Row Inventory Requirements (no source text)

Each row in `sesa-first-tranche.tsv` (20 rows) must appear in the clearance record with:
- `row_number` (1-20)
- `absolute_path` (pointer only — the path from the TSV)
- `document_identifier` (filename or DORIS doc-number)
- `allowed_extraction_level` (one of the four enums above)
- `prohibited_content` (row-specific overrides to the default deny-list)
- `approver` (may reference a blanket approver or per-row name)
- `approval_date`

The clearance record must NOT contain: file content, quotes, table data, figure descriptions, or any text extracted from the source documents.

---

## 3. Woodfibre #2544 — Clearance Dossier Template

### Required Fields

| Field | Description |
|-------|-------------|
| `approver_name` | Must be explicitly named (not role-generic) |
| `approver_role` | One of: `ACMA-project-owner`, `client-authorized-reviewer`, `legal-IP-delegate` |
| `approval_date` | ISO 8601 |
| `allowed_extraction_level` | Per-row enum: `metadata-only` \| `curated-fields` \| `short-quote-approved` \| `abstract-approved` |
| `prohibited_content` | Per-row list |
| `expiration_or_review_condition` | When this clearance lapses |
| `tranche_rows_covered` | Row numbers from `woodfibre-first-tranche.tsv` (15 rows) |

### Named Approver Requirement

The 2026-04-29 addendum is explicit: "Accepted approvers must be explicitly named by role: ACMA project owner, client-authorized reviewer, or legal/IP delegate. A generic 'project lead' is insufficient." The clearance document must include the individual's name, not just a role title.

### Excluded Subdirs/Classes (never extract, regardless of clearance)

| Exclusion | Rationale |
|-----------|-----------|
| `05.Deliverables/DEMOLITION/CAPRICORN/` | Third-party prior-vessel-owner IP |
| `05.Deliverables/DEMOLITION/TAURUS/` | Third-party prior-vessel-owner IP |
| All `.sim` files (1,383 files / 1.85 TB) | OrcaFlex time-history binaries — catastrophic if extracted |
| All `.r001`–`.r003` files | OrcaFlex restart files |
| All `.sldprt` / `.scdoc` files | SolidWorks CAD binaries |
| All `.wbpz` / `.osav` / `.esav` / `.rst` / `.mechdb` / `.dspsymb` files | ANSYS FEA binaries |
| All `.db` files | Database files — PII/retention risk |

### Pointer-Only Scope

Per the addendum, #2544's approval-ready subset is **metadata pointer/scout output only**. No document abstract extraction, technical summary extraction, direct quote extraction, table extraction, or figure extraction may occur under #2544 until a separate extraction plan is written after clearance. The 2 KB inline-quote allowance mentioned in original pseudocode is **revoked** by the addendum unless row-level clearance explicitly sets `short-quote-approved`.

---

## 4. Exact Next Operator Questions/Actions Needed

### Before adversarial review can run:

1. **Confirm review dispatch is authorized** — The plans are at `status:plan-review` but no review agents have run. Operator: confirm this lane (or another) may dispatch Claude/Codex/Gemini review agents against both plans.

### Before any extraction can proceed:

2. **Identify the SESA data owner** — Who is the person with disposition authority over the DORIS 62092 SESA corpus on the Elements drive? What is their role relationship to the workspace-hub project?

3. **Identify the Woodfibre (ACMA 31522) data owner** — Is this the same person or a different authority? The plan references "ACMA project owner" — is there a specific individual?

4. **Decide vendor/TBE brochure policy for SESA** — The plan flags PIETRO and RMT VALVOMECCANICA material. Should vendor brochure rows be permanently excluded from tranche-1, or is there a clearance path?

5. **Decide SESA citeability** — Open question from the plan: "Is SESA project information freely citeable inside the workspace-hub wiki?" This is prerequisite to any extraction.

6. **Decide Woodfibre public-filing overlap** — Open question: is there a BC OGC/EAO public regulatory filing that already publishes comparable summaries? If so, abstracts can cite the public filing (eliminating clearance friction).

7. **Decide Rev JRA handling for SESA** — Should Rev JRA markup PDFs be merged into the base-revision source page or kept as separate review pages?

8. **Create governance clearance documents** — After questions 2-7 are answered, the operator must author:
   - `/mnt/local-analysis/workspace-hub/docs/governance/sesa-extraction-clearance-2026.md`
   - `/mnt/local-analysis/workspace-hub/docs/governance/woodfibre-extraction-clearance-2026.md`

   These are user-signed hard-gate artifacts. No AI lane may create or imply approval for them.

9. **Set `status:plan-approved` on #2541 and #2544** — Only after adversarial review passes AND governance clearance docs exist.

---

## 5. Worker-Lane Guardrails

### What future Claude/Codex/Gemini lanes MUST NOT do:

| Guardrail | Applies to | Rationale |
|-----------|-----------|-----------|
| Must not create `docs/governance/sesa-extraction-clearance-2026.md` | All AI lanes | User-signed hard-gate artifact |
| Must not create `docs/governance/woodfibre-extraction-clearance-2026.md` | All AI lanes | User-signed hard-gate artifact |
| Must not apply `status:plan-approved` label to #2541 or #2544 | All AI lanes | User-in-loop gate (per `feedback_never_offer_to_self_label_plan_approved.md`) |
| Must not extract, persist, or emit full document text from SESA or Woodfibre sources | All AI lanes | Addendum: "no persisted full-text intermediates" |
| Must not write `.txt` raw extraction dumps to `.planning/` or `knowledge/` | All AI lanes | Addendum explicitly revokes earlier `.planning/intel/elements-deep-extraction/sesa/<slug>.txt` instruction |
| Must not emit direct quotes without row-level `short-quote-approved` clearance | All AI lanes | Addendum revokes the 2 KB inline-quote allowance |
| Must not extract from DEMOLITION/CAPRICORN/TAURUS subdirs | All AI lanes (Woodfibre) | Third-party IP exclusion |
| Must not extract `.sim`/`.r00X`/`.sldprt`/`.wbpz`/ANSYS binaries | All AI lanes (Woodfibre) | Binary exclusion — catastrophic if ingested |
| Must not extract vendor/TBE material without explicit row-level clearance | All AI lanes (SESA) | Vendor brochure policy unresolved |
| Must not run #2541 and #2544 wiki writes concurrently | All AI lanes | Sequential execution required per addendum (shared `index.md`/`log.md`) |
| Must not emit standards-body copyrighted text into wiki source pages | All AI lanes | Calc-citation contract + standards exclusion in plan |
| Must not include personnel names, pricing, or NDA-marked content | All AI lanes | Default prohibited content class |
| Must not claim extraction has occurred or describe proposed wiki pages in past tense | All AI lanes | Per `feedback_plan_past_tense_artifact_claims.md` |
| Must verify clearance doc exists programmatically before any wiki write | Implementation lanes | Test-first gate: `test -f docs/governance/...-clearance-2026.md` |

### Positive obligations for implementation lanes (when eventually unblocked):

- Run `llm_wiki.py lint --wiki lng-projects` after every wiki write
- Run `llm_wiki.py status --wiki lng-projects` to verify structural integrity
- Rebase and revalidate between #2541 and #2544 wiki writes (sequential constraint)
- Emit extraction-level metadata in structured YAML/JSON, never raw text dumps
- Cap any approved extraction at page/character bounds (streaming, not full-text)
- Include provenance `sources:` frontmatter pointing to `/mnt/ace/...` absolute path (no byte copy)

---

## Sandbox Write Failure Notice

**Cannot write to intended deliverable path:**
```
/mnt/local-analysis/agent-logs/provider-capacity-aware-20260501-0613/results/claude-elements-clearance-prep.md
```

**Reason:** The path is outside the workspace-hub sandbox (`/mnt/local-analysis/workspace-hub`). The Write tool is restricted to the working directory.

**Recovery action:** Operator should copy this report from the plan file or use:
```bash
mkdir -p /mnt/local-analysis/agent-logs/provider-capacity-aware-20260501-0613/results/
cp /mnt/local-analysis/workspace-hub/.planning/abundant-painting-mist.md \
   /mnt/local-analysis/agent-logs/provider-capacity-aware-20260501-0613/results/claude-elements-clearance-prep.md
```

---

## Implementation Plan (for this planning session)

This is a read-only report. No code changes, no GitHub mutations, no label changes.

**Files read:**
- `/mnt/local-analysis/workspace-hub/docs/plans/2026-04-28-issue-2541-elements-sesa-curated-extraction-plan.md` (264 lines, includes 2026-04-29 addendum)
- `/mnt/local-analysis/workspace-hub/docs/plans/2026-04-28-issue-2544-elements-woodfibre-scout-plan.md` (344 lines, includes 2026-04-29 addendum)

**Files confirmed present (planning artifacts):**
- `/mnt/local-analysis/workspace-hub/.planning/intel/elements-overnight-wave/sesa-candidate-dossier.md`
- `/mnt/local-analysis/workspace-hub/.planning/intel/elements-overnight-wave/sesa-first-tranche.tsv`
- `/mnt/local-analysis/workspace-hub/.planning/intel/elements-overnight-wave/woodfibre-corpus-scout.md`
- `/mnt/local-analysis/workspace-hub/.planning/intel/elements-overnight-wave/woodfibre-first-tranche.tsv`

**Files confirmed absent (correctly blocked):**
- `/mnt/local-analysis/workspace-hub/docs/governance/sesa-extraction-clearance-2026.md` — NOT present
- `/mnt/local-analysis/workspace-hub/docs/governance/woodfibre-extraction-clearance-2026.md` — NOT present
- `/mnt/local-analysis/workspace-hub/scripts/review/results/2026-04-28-plan-2541-*.md` — NOT present
- `/mnt/local-analysis/workspace-hub/scripts/review/results/2026-04-28-plan-2544-*.md` — NOT present
