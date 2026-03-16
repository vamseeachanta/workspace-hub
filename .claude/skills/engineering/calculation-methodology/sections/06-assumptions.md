# 06 — Assumptions

## Purpose

List every assumption explicitly so reviewers can challenge them and so
future revisions know what was assumed vs measured. Assumptions are
engineering decisions that must be visible and traceable.

## Schema Fields

```yaml
assumptions:
  - string                    # each assumption is a plain string
```

> **Renderer Mapping Note:** The methodology recommends structured assumption
> objects with `id`, `statement`, `justification`, `type`, `impact`, and
> `revisit_trigger`. The renderer treats `assumptions` as a simple list of
> strings — each rendered as a numbered item. Encode justification and
> classification into the string text where important, e.g.,
> `"Uniform wall thickness assumed (conservative) — mill tolerance applied as reduction"`.

## Required Content

- Every engineering assumption used in the calculation
- Justifications encoded in the assumption text where practical
- Conservative vs best-estimate classification noted in text

## Quality Checklist

- [ ] Every assumption is a clear, testable statement
- [ ] Conservative assumptions are identified so reviewers see margin sources
- [ ] High-impact assumptions link to sensitivity analysis in section 10
- [ ] No hidden assumptions — if a parameter in section 05 is "assumed," it
      must appear here
- [ ] Each entry is a plain string (not a structured dict)

## Example Snippet

```yaml
assumptions:
  - "Pipeline is fully restrained axially beyond 2 km from ends (conservative — confirmed by anchor length calculation PRJ-CALC-005)"
  - "Corrosion allowance of 3 mm applied uniformly (conservative — based on 25-year design life at 0.1 mm/yr from CR-2026-001)"
  - "Linear coating breakdown model applies (conservative for high-quality coatings)"
  - "Uniform current density distribution over jacket surface"
```

## Common Mistakes

- Using structured dicts with `id`, `statement`, `justification` fields
  (renderer expects a simple list of strings)
- Assumption stated without justification embedded in the string
- All assumptions marked "conservative" without demonstrating why
- High-impact assumptions not carried forward to sensitivity analysis
- Assumptions buried in calculation text instead of listed here
