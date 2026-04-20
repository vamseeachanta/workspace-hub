# Final Integrator Review: 2026-04-19 revision of #2207 Provenance + Reuse Contract

> **Role:** Integrator (4-role agent team, per revision dispatch prompt)
> **Date:** 2026-04-19
> **Deliverable:** `docs/document-intelligence/standards-codes-provenance-reuse-contract.md` (revised 2026-04-19)
> **In-run adversarial review:** `scripts/review/results/2026-04-19-revision-2207-claude-review.md` (MINOR verdict; no MAJOR remaining)

## Verdict: **APPROVE**

The revised contract is internally consistent with the amended parent operating model and faithfully addresses the 11 findings from the 2026-04-17 cross-provider review. Three MINOR observations from the in-run review are documented and do not warrant additional revision under the dispatch prompt's scope constraints.

## Internal-consistency check

| Axis | Before revision | After revision | Verdict |
|---|---|---|---|
| Identity form | SHA-256 only; bare-hex canonical | `<algorithm>:<hex>`; `sha256:` canonical, `md5:` legacy read-only | Consistent with parent §3 |
| Status vocabulary | 4-value enum, misses live `gap` | 7-value parent superset, includes `gap` and evidence | Consistent with parent §3 |
| Merge-time timestamp | `discovered`, "first-indexed" semantic (false) | `merged_at`, merge-time semantic (true) | Consistent with parent §3 + live code |
| Frontmatter authority | §6.3 "required-set" prescribed | §6.3 "recommended fields, wiki `CLAUDE.md` binds" | Consistent with parent §8.1 |
| Anti-pattern 8.3 | Claimed `# content-hash:` satisfies traceability (false) | Distinguishes output-integrity stamp from source traceability; second field required | Consistent with live promoter code |
| Anti-pattern 8.5 | Prefix-strip + bare-hex canonical | Full-string comparison; bare-hex is a violation | Consistent with parent §3 + live filenames |
| `processing_status` scope | Undefined which surfaces | Enumerated surfaces; unrelated `status` fields called out | Consistent with Codex C3 intent |
| `path` scope | "Primary path (highest-priority alias)" undefined | Machine-local `(path, host)` pair; `provenance[]` authoritative for cross-host | Consistent with live `provenance.py` |
| `wiki_refs` ownership | L3 owns (ambiguous vs. parent §2) | Back-link field materialized at L2; L3 emits, L2 stores | Consistent with parent §2 forbidden-ownership row |

No self-contradictions found on any axis.

## Amendment coverage

All five amendments (A–E from the dispatch prompt) are applied, with evidence documented in §12 Revision history:

- A. `<algorithm>:<hex>` identity — §3.1, §3.2, §8.5
- B. Status vocabulary superset — §4.1.3, §5.1
- C. `merged_at` rename — §4.1, §4.1.2, §4.2, §10 Q3
- D. Frontmatter reframed — §6.3 (+ §1, §2 delegation statements)
- E. Cross-references updated — §2

## Finding coverage

All 11 findings have explicit disposition in §12:

- 7 FIXED (F1, F2, F3, F4, F5, C1, C2, C3, C4) — 9 actually; §12 shows 9 FIXED
- 1 PARTIAL (F6) — grandfather policy documented; concrete issue filing is out of scope
- 1 FIXED out-of-contract (F7) — cross-provider review executed; this revision addresses both reviewers

The PARTIAL on F6 is correct under dispatch constraints: the dispatch prompt forbids new GitHub-issue creation beyond the §2207 summary comment, so filing a Phase E back-population follow-on issue is genuinely out of scope.

## Scope-boundary check

No forbidden paths touched:

- Parent operating model: unchanged
- Sibling contracts (#2206, #2209): unchanged
- `data/document-index/*`: unchanged
- `scripts/data/document-index/*.py` writers: unchanged
- `.claude/**`, `.codex/**`, `config/**`, `tests/**`: unchanged

Only allowed-write-path files modified:

- `docs/document-intelligence/standards-codes-provenance-reuse-contract.md` (primary)
- `scripts/review/results/2026-04-19-revision-2207-claude-review.md` (new)
- `scripts/review/results/2026-04-19-revision-2207-final-review.md` (this file)
- `.planning/plan-approved/2207.md` (to be created in STEP 5)

## Quality-bar compliance

- Internally consistent with amended parent §3 namespace, status, and `merged_at` rules: **yes, verbatim**.
- Section 8.1 authority delegation respected (contract recommends, wiki `CLAUDE.md` binds): **yes, stated in §1, §2, §6.3, §10 Q8**.
- Every 2026-04-17 finding has explicit disposition: **yes, §12 table**.
- No drift into code-side rename implementation: **yes, explicitly deferred to future issue in §10 Q3, §11 item 2, §12**.

## Residual risks to surface to the dispatcher

1. **F6 fully resolved only by filing a follow-on issue** — Phase E `doc_key` back-population for `standards-transfer-ledger.yaml`. This revision grandfathers legacy entries; ending the grandfather period needs a concrete issue, ownership assignment, and mount access.
2. **Engineering wiki `CLAUDE.md` does not yet declare `doc_key`** — the parent baseline floor from §8.1 requires `{title, last_updated, doc_key}`, but `knowledge/wikis/engineering/CLAUDE.md` currently declares only `{title, tags, added, last_updated}`. The engineering wiki maintainer must update their `CLAUDE.md` separately. This is called out in §10 Q8 but is not actionable from this contract.
3. **`merged_at` rename in `provenance.py` is deferred** — live writers still emit `discovered`. Readers compliant with this contract must accept both field names indefinitely. The rename is a future code-side issue.
4. **`source_doc_key` is aspirational, not implemented** — §8.3 declares the field required for proper traceability, but no promoter currently emits it. Section 9.3 and Section 11 item 4 capture the follow-on implementation work.

These residuals are documented in the contract itself, so they are not hidden from downstream consumers.

## Recommendation

Proceed to STEP 5 (marker + commit) and STEP 6 (GitHub comment).
