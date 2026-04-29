# Terminal 3 — DORIS Codes & Specs metadata-only promotion plan (issue #2543)

> **Run:** 2026-04-28 overnight Elements wave, Terminal 3
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2543
> **Outcome:** plan-review (NOT plan-approved); ready for adversarial review
> **Permission boundary respected:** no writes to `/mnt/ace/**`, `knowledge/wikis/**`, `docs/plans/README.md`, `scripts/**`, `.gitignore`, or any Terminal 1/2/4 paths.

## Files written

| Path | Purpose |
|---|---|
| `docs/plans/2026-04-28-issue-2543-elements-doris-codes-standards-plan.md` | Canonical plan with resource intelligence, artifact map, scope, pseudocode, TDD, acceptance criteria, risks, approval boundary |
| `.planning/intel/elements-overnight-wave/doris-codes-standards-inventory-plan.md` | Metadata-only inventory + license-risk matrix + governance cross-checks |
| `.planning/intel/elements-overnight-wave/doris-codes-standards-families.tsv` | Machine-readable families table: family / count / paths / wiki target / license risk / extraction policy |
| `docs/plans/overnight-prompts/2026-04-28-elements-wave/results/terminal-3-doris-codes.md` | This file |

## What was decided

- **Posture:** metadata-first, licensing-aware. Zero raw standards content into git/wiki.
- **Wiki output proposed (deferred — only after `status:plan-approved`):**
  - 1 faceted-index page under `wiki/sources/` (extends the existing #2535 source page).
  - 3 pointer pages under `wiki/sources/` for `TechStreet Drop`, `Company Specs`, `DeepStar` — each with explicit no-extraction banner.
  - 1 optional `wiki/standards/bv-ship-offshore-rules.md` publisher landing stub (only if a verified `revision` value can be supplied; otherwise skip).
- **No per-code-id pages** for API / ASME / DNV / ISO / ASTM in this pass — explicit deferral with rationale.
- **License-risk classification (conservative):**
  - CRITICAL — `TechStreet Drop` (12,266 files, licensed-aggregator drop), `Company Specs` (15,864 files, NDA-bound), `Perry's Chemical Engineers Handbook` (311 files, McGraw-Hill copyrighted). No OCR, no clause copy, sometimes no wiki page.
  - HIGH — `BV Ship and Offshore Rules` (5,325), `API` (746 top-level), `ASME` (130), `DnV` (149), `DeepStar` (113), embedded ISO/ASTM/ABS/IEC/NACE/AWS/AWWA references.
  - LOW — NORSOK (1 mention; volume too low to merit a page).
- **Out of scope:** OCIMF and CSA — confirmed absent from this corpus by grep (0 tokens). Boundary against `acma-codes` / #2227 / #2471 documented.
- **Frontmatter contract from #2471 forward-adopted:** any future `wiki/standards/*` page emitted will carry `code_id`, `publisher`, `revision`. No revision → no page.

## What was deliberately NOT done

- No OCR or text extraction against any DORIS codes file.
- No copy of raw PDFs/images/scans into git or `wiki/raw/`.
- No edits to `/mnt/ace`.
- No edits to `knowledge/wikis/engineering-standards/wiki/` content (the proposed pages are deferred to a future approved implementation issue).
- No edits to Terminal 1/2/4 paths.
- No `status:plan-approved` label applied (user-in-loop gate is intact).
- No copyright opinion or fair-use claim authored in any artifact; license posture stated conservatively only.
- No author of an OCIMF or CSA page in this wiki — those remain governed by `acma-codes` / #2227 / #2471.

## Key uncertainties surfaced (kept in plan, not resolved)

1. **TechStreet Drop publisher mix** — counts per publisher require per-file-name iteration that is itself a license-sensitive operation; not done here.
2. **Company Specs client mix** — folder names likely contain client identifiers; even *listing* them in a wiki page risks confidentiality leak. Plan keeps client list out.
3. **BV Rules revision** — BV reissues consolidated rule notes semi-annually; without a verified revision in hand, the BV standards page is deferred to a follow-up.
4. **Residual ~293 unclassified top-level entries** — distribution unknown; could change risk posture if a NORSOK or NACE collection is hiding inside.
5. **Embedded mention counts** for API (~7,516) and ASME (~5,221) are heavily inflated by long-pathname substring matches; treat as *occurrence-anywhere on JSON line*, not file counts. Top-level dir counts (746 API, 130 ASME) are the trustworthy file numbers.

## Verification (commands run within sandbox)

- `gh issue view 2543` → OPEN, scope/deliverables/acceptance criteria match plan output.
- `gh issue view 2540` → OPEN umbrella, terminal-3 boundary respected.
- `gh issue view 2227` → OPEN with `status:plan-approved`; corpus check confirms 0 OCIMF / 0 CSA tokens here, so this plan does not touch #2227's territory.
- `Grep "bucket": "doris-codes-specs"` over `elements-ingested-files.jsonl` → 35,197 records confirmed (matches batch JSONL totals).
- Token-anywhere greps over the same JSONL captured the family counts cited in the inventory plan and TSV.
- Read of `engineering-standards/CLAUDE.md` confirmed the `code_id` / `publisher` / `revision` frontmatter contract.
- Read of `engineering-standards/wiki/sources/elements-doris-codes-specs.md` confirmed the existing #2535 page and prevented duplication.
- `ls knowledge/wikis/engineering-standards/wiki/standards` → empty directory (no contradiction risk for the deferred BV stub).
- Post-write file-existence: all four required output paths exist and are non-empty.

## Status / next action

- Issue #2543 stays at **plan-review**.
- Recommend adversarial review next (Claude + Codex + Gemini against the plan) before user approves. Note: per project memory, Codex CLI 0.124.0 has an open stdin-hang regression (#2479) — fall back to Codex web/Workbench if `codex exec` blocks. Gemini sandbox overlay-blindness is also a known false-positive source for sparse-checkout claims.
- Implementation phase should be a separate follow-up issue with its own plan; this plan only authorizes the *shape* of that future work and never the ingestion itself.

## Sandbox observations (non-blocking, for the wave coordinator)

- The session was correctly scoped to read-only on `/mnt/ace`; `ls /mnt/ace/doris/codes` was blocked, so all DORIS-codes inspection used the previously-indexed `elements-ingested-files.jsonl` instead. This is the right behaviour for a planning-only terminal.
- Inline `python3 -c` and `Write` to `/tmp/` were also sandbox-blocked, which forced metadata extraction through the `Grep` tool exclusively. Results were sufficient because the engineering-standards batch JSONL already carried the top-level-sample histogram and content-kind/extension counts at corpus level.

## No blockers

Terminal 3 ran clean. No blockers, no dependency on Terminals 1/2/4.
