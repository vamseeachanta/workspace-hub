## Verdict

MAJOR

## Retrieval

- Re-read draft v3 against all r2 privacy/transaction blockers.
- Rechecked the canonical approval-authority gate, builder precedence, staged scanner behavior, provider review policy, and closeout ordering.

## Findings

1. The simplified approval preflight accepted stale/forged label-marker pairs and did not bind actor, freshness, plan SHA, revision, or HEAD.
2. The first equality fence and tree comparison were not in a compound fail-closed block; branch/HEAD were not fenced around HEAD-relative scanners.
3. Degraded T2 review incorrectly allowed two same-provider agents instead of two distinct providers.
4. Cleanup ran before owner verification/issue close and was not repeated afterward.
5. Candidate proof did not explicitly require committed blob OIDs to equal already-scanned manifest OIDs.

## Blockers

- Use the canonical approval authority and preserve legacy builder precedence.
- Make scan/delivery/branch/HEAD/tree fences compound fail-closed.
- Require provider diversity; repeat cleanup after final close.

## Disposition

Draft v4 incorporates all findings. Fresh re-review remains required.
