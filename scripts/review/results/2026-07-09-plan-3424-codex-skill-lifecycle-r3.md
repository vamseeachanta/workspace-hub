## Verdict

MAJOR

## Retrieval

- Re-read draft v3 against all r2 lifecycle blockers.
- Probed the live full index: 408 skills have descriptions plus richer legacy trigger sections; 434 backfill entries also have descriptions.
- Rechecked the canonical plan-approval gate and marker/parity surfaces.
- Rechecked staged delivery, completeness classification, and closeout artifact ordering.

## Findings

1. A global description promotion would replace 408 richer legacy routes and promote 434 legacy backfills without a corpus audit.
2. The proposed approval helper duplicated the canonical gate while omitting actor, bot, freshness, plan/revision/HEAD, and marker-hash authority.
3. Scan fences did not prove the exact delivery set; omitted untracked new files could remain unstaged while `git write-tree` bound an incomplete tree.
4. Completeness class was preselected as evidence rather than auto-derived from changed files and a deterministic package map.
5. Completeness JSON/HTML artifacts were created after final scans/review and could be committed without those gates.

## Blockers

- Bound description promotion to an audited modern-minimal subset and preserve legacy precedence/weights.
- Extend the canonical approval gate; do not create a weaker parallel helper.
- Add exact NUL-safe delivery-manifest enforcement.
- Derive completeness class and review/scan its final artifacts.

## Disposition

Draft v4 incorporates all findings. Fresh re-review remains required.
