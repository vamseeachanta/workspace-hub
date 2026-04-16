# Overnight Claude Review — Plan #2129

> **Date:** 2026-04-16
> **Context:** Overnight planning review pass
> **Plan reviewed:** `docs/plans/2026-04-11-issue-2129-issue-state-drift-redundancy-audit.md`
> **Prior reviews:** Claude MAJOR (2026-04-15), Codex MAJOR (2026-04-15), Gemini MAJOR (2026-04-15)

## Verdict: MAJOR (unresolved)

## Assessment

All three providers returned MAJOR on 2026-04-15. The plan is ambitious (T3 complexity) and covers 4 bounded detection categories across GitHub issue state and local artifacts. However, multiple structural issues remain unresolved.

### Unresolved blockers

1. **CLI contract missing:** No concrete `--audit` / `--hygiene` CLI entry point is defined for `review-open-issues.py`. How the audit mode is invoked is unspecified.
2. **Acceptance criteria depend on live repo examples:** The plan requires surfacing "at least one current-repo example for each required category." This makes acceptance non-deterministic — it depends on live state, not fixtures.
3. **Weekly-review integration is documentation-only:** Gemini flagged that adding a docs reference is not a real integration; need an actual invocation point or consumption contract.
4. **Artifact intake is too loose:** Codex flagged that `docs/plans/**/results/*.md` is too broad; parser eligibility markers and scope bounds are underspecified.
5. **Output schema underspecified:** Sort order, timestamp policy, and deterministic evidence rules for duplicate and parent-child heuristics need tightening.
6. **#2217/#2218 hardening:** Known false-positive hardening from follow-up issues must be folded into plan scope or explicitly excluded.

### Retrieval adequacy

- **adequate** — 12+ sources cited with concrete findings. The gap analysis is strong.

### Recommendation

**needs-revision** — T3 complexity with 6 unresolved MAJOR findings from three providers. Revision scope is substantial.

**Execute tomorrow?** No — requires substantive revision addressing CLI contract, deterministic acceptance, and real weekly-review integration.
