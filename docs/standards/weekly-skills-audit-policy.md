# Weekly Skills Audit — Classification and Ranking Policy

> **Authoritative source:** `config/skills/weekly-audit-policy.yaml`
> This document is explanatory only. If any rule here conflicts with the YAML,
> the YAML governs. Issue: #2282.

---

## Purpose

This policy defines how the weekly skills audit classifies, ranks, and reports
skill-ecosystem findings. It is consumed by the #2281 implementation so that
classification decisions are deterministic and reproducible across agents and runs.

---

## Classification Buckets (highest → lowest priority)

| Priority | Bucket | When it applies |
|---|---|---|
| 1 | `exact-duplicate` | Same canonical name (`name:` frontmatter) regardless of path |
| 2 | `canonical-wrapper-pair` | One skill is a thin stub that explicitly redirects to another |
| 3 | `adjacent-specialization` | Same broad domain, distinct scope — both substantive, neither a stub |
| 4 | `generic-leaf-collision` | Same leaf directory name, different canonical names, no deeper overlap |
| 5 | `needs-human-review` | Signals absent, incomplete, or contradictory (fallback) |

**Precedence rule:** the first bucket (lowest priority number) whose required signals
are all present and no excluded signals are present wins. If `conflicting_signals` is
detected the finding always routes to `needs-human-review` regardless of other criteria.
If no bucket matches, `needs-human-review` is the fallback.

---

## Classification Signals

| Signal | Meaning |
|---|---|
| `canonical_names_match` | Both frontmatter `name` values are identical strings |
| `is_stub` | One skill has minimal content (<5 non-frontmatter lines) redirecting elsewhere |
| `references_other_canonical` | One skill's body names the other's canonical name as alias/redirect |
| `leaf_dir_match` | Both skills share the same leaf directory name |
| `scope_differs` | Skills demonstrably differ in scope, audience, or domain depth |
| `both_substantive` | Both skills carry independent substantive content |
| `conflicting_signals` | Signals are mutually contradictory; cannot be resolved automatically |

---

## Severity Rubric

| Severity | Meaning |
|---|---|
| `high` | Active functional conflict or likely user confusion today |
| `medium` | Structural inconsistency that could cause confusion over time |
| `low` | Cosmetic or naming inconsistency; minimal operational impact |

---

## Confidence Rubric

| Confidence | Meaning |
|---|---|
| `high` | All signals explicitly detected; human review unlikely to change outcome |
| `medium` | At least one signal inferred from heuristic; spot-check recommended |
| `low` | Signals missing, inferred, or contradictory; treat as provisional |

---

## Finding Schema

Every finding must carry these fields:

```
finding_key          str   deterministic key (canonical_names + classification)
classification       str   one of the five bucket names
severity             str   high | medium | low
confidence           str   high | medium | low
canonical_names      list  frontmatter name of each involved skill
paths                list  repo-relative paths of each involved skill
summary              str   one-line human-readable description
recommended_action   str   suggested remediation
escalation_state     str   no-escalation | candidate
is_new               bool  true if not present in prior run
is_changed           bool  true if in prior run but materially changed
```

---

## Carry-Forward Rules

| Rule | Condition | Action | Weekly section |
|---|---|---|---|
| `unchanged` | Identical across runs | Compact carry-forward | suppressed/carry-forward |
| `changed` | Any change trigger fired | Surface explicitly | changed |
| `suppressed` | Manually suppressed | Compact carry-forward | suppressed/carry-forward |
| `resolved` | No longer detected | Remove from active | (none) |

**Change triggers:** severity, confidence, escalation_state, canonical_names, or paths differ.

A finding that is still present but worsened (e.g., severity went from medium→high) must
appear in the **changed** section, not hidden under compact carry-forward.

---

## Escalation (v1 — binary)

| State | Condition |
|---|---|
| `candidate` | severity=high AND confidence=high |
| `no-escalation` | everything else |

The escalation_state is computed from current severity and confidence each run.
Given identical inputs the result is always identical (idempotent).
Multi-tier models are deferred until weekly signal quality is proven.

---

## Weekly Summary Sections

Every weekly report must include all five sections (even if empty):

1. **New Findings** — `is_new == true`
2. **Changed Findings** — `is_changed == true AND is_new == false`
3. **Unresolved High-Confidence** — not new, not changed, confidence=high, severity in [high, medium]
4. **Suppressed / Carry-Forward** — unchanged + manually suppressed (compact)
5. **Operational Errors** — run errors and skipped inputs

---

## Fixture Examples

See the `fixtures:` block in `config/skills/weekly-audit-policy.yaml` for one
canonical example per bucket. These fixtures are the test inputs for
`tests/skills/test_weekly_skills_audit_policy.py`.
