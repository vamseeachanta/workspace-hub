---
name: Doc-counter rules expressed as write-time computations, not frozen integers
description: When a plan modifies a phantom-counter in a wiki/docs page, the acceptance criterion must be a write-time recompute rule, not a hardcoded post-add integer
type: feedback
originSessionId: 182f4d6d-50f2-4629-b01b-4e9187fd0af1
---
When a planned change modifies a counter that depends on the current state of the repo (e.g., a `source_count` frontmatter field, a section-header pluralization like `## Sources (N pages)`, an issue-count badge in a README), the plan's acceptance criterion must be expressed as a **write-time recompute rule**, not a frozen post-add integer captured at plan-draft time.

**Why:** Codex round-2 review of workspace-hub#2659 (2026-05-09) caught a real defect: revision-2 of the plan hardcoded `source_count: 24` based on the count observed at plan-draft (`N=23`, target `N+1=24`). Between plan-draft and implementation, another ingest could have landed and shifted ground truth — the hardcoded value would then be wrong, but a literal-match acceptance criterion would still pass. The reconcile-to-ground-truth policy that resolved round-1's drift finding would have been silently undermined by stale-data fragility from round-1's own fix. Round-3 returned APPROVE only after revision-3 expressed the criterion as `N = count(sources/*.md before staging); source_count = N+1; header = "## Sources (N+1 pages)"` with the literal `24` demoted to baseline expectation.

**How to apply:**

1. **For any plan that touches a counter,** write the acceptance criterion as a rule: "at write time, compute X from live state, set value to f(X)." Do not write "set value to <hardcoded integer>."
2. **Static integer values are baseline expectations only.** They tell the reviewer "if nothing else changes, this is what the implementation should produce." They are not the criterion.
3. **The implementing agent must record observed and resolved values** in the implementation comment (issue comment, commit message, or both). This makes the rule audit-trail-verifiable post hoc.
4. **The implementing agent must surface divergence.** If the live count at write time differs from the plan's baseline, that is information to disclose, not a silent override.
5. **Counter-bump conventions can be inflation- or deflation-specific.** Marine-eng's "+1-by-convention" rule applies to *inflated* phantoms (where the convention preserves an agreed offset). Engineering's deflated phantoms required reconcile-to-ground-truth. Do not blindly apply one wiki's convention to another.
6. **Generalize beyond `source_count`.** Same rule applies to any phantom counter: `## Concepts (N pages)`, badge counts, "X open issues" in a README, total-table-row tallies in dashboards, etc.

**Concrete pattern:**

```bash
# Plan acceptance criterion (verbatim language):
# "At write time, N = count(<glob>); set <field> = f(N). Static value <X> is a 
#  baseline expectation only; the rule is the criterion."

# Implementing agent (write time):
N=$(<count-command>)
TARGET=$((N + delta))
# ... apply edit using TARGET, not the plan's frozen value ...
echo "Observed N=$N, resolved TARGET=$TARGET (plan baseline was $X)" >> implementation-comment.md
[[ "$TARGET" != "$X" ]] && echo "Divergence from plan baseline; surfaced in comment." >> implementation-comment.md
```

**Cross-references:**

- `feedback_always_adversarial_review_scale_depth.md` — adversarial review caught this pattern; it is the kind of defect that proves single-provider scoped review still pays off on T1 docs work.
- `feedback_plan_past_tense_artifact_claims.md` — related discipline (plans describe proposed work, not completed work).
- workspace-hub#2659 — origin case (Codex round-2 finding, revision-3 fix).
