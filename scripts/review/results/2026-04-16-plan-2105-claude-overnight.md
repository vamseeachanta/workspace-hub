# Overnight Claude Review — Plan #2105

> **Date:** 2026-04-16
> **Context:** Overnight planning review pass
> **Plan reviewed:** `docs/plans/2026-04-13-issue-2105-freshness-cadences-and-staleness-signals.md`
> **Prior reviews:** Subagent MAJOR (2026-04-13), Codex MAJOR (2026-04-14), Gemini MAJOR (2026-04-14), Claude MAJOR (2026-04-15)

## Verdict: MAJOR (unresolved)

## Assessment

All four prior reviews returned MAJOR. The plan was correctly rolled back from premature approval. The Adversarial Review Summary documents 6 specific required revisions, none of which have been addressed since the last review.

### Unresolved blockers

1. **Threshold naming collision:** Plan uses `current / warn / stale` vocabulary that collides with the live scanner/dashboard constants. No resolution specified.
2. **Missing Knowledge/Intelligence retrieval:** Plan should consume #2207 (provenance contract) and #2209 (durable/transient boundary) as required sources per the issue-class bundle. These are absent.
3. **Scanner scope decision:** Whether the existing doc-only staleness scanner should be extended to non-doc intelligence assets, or whether separate handling is needed, is unresolved.
4. **Source-of-truth precedence:** The relationship between the canonical cadence matrix, registry freshness metadata, and existing scanner/dashboard outputs is not explicit.
5. **#2250 dependency:** The downstream reconciliation of stale intelligence summary artifacts is not surfaced as an explicit risk/dependency.
6. **Acceptance criteria weakness:** Current criteria prove artifact existence but not semantic consistency of the threshold vocabulary.

### Retrieval adequacy

- **insufficient** — Missing required Knowledge/Intelligence sources (#2207, #2209). Existing staleness scanner/dashboard machinery is referenced but threshold vocabulary collision is not resolved.

### Recommendation

**needs-revision** — All 6 documented revision requirements must be addressed before re-review. The plan needs a substantive rewrite of:
- Threshold vocabulary resolution section
- Resource Intelligence Summary with #2207/#2209 evidence
- Scanner scope decision
- Strengthened acceptance criteria

**Execute tomorrow?** No — requires substantive rewrite.
