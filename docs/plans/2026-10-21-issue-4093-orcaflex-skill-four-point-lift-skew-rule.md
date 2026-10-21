# Plan for #4093: Skill: add a four-point lift skew-load review rule to the OrcaFlex installation-analysis skill

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-10-21
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/4093
> **Client:** N/A
> **Lane:** lane:claude

---

## Resource Intelligence Summary

### Existing repo code

- EXISTS: `.agents/skills/engineering/marine-offshore/orcaflex/installation-analysis/SKILL.md` — section "Crane wire and sling configuration" mentions crane wire but contains no rigging load-sharing guidance; no skew load factor is defined anywhere in the file
- MISSING: No rule in the skill (or any sibling skill under `.agents/skills/engineering/marine-offshore/`) mentions "skew load factor", "four-point lift", or static indeterminacy of sling splits
- EXISTS: `.agents/skills/engineering/marine-offshore/orcaflex/SKILL.md` — parent skill index; installation-analysis is registered as a sub-skill

### Standards

| Standard | Status | Source |
|---|---|---|
| DNV-RP-H103 Modelling and Analysis of Marine Operations | Local copy available | `data/document-index/online-resource-registry.yaml` entry + local backup at `/mnt/ace/docs/_standards/SNAME/hydrostatics-stability/DNV-RP-H103-Marine-Operations-2010.pdf` |

### LLM Wiki pages consulted

- No relevant wiki pages found for four-point lift or skew load factor in the workspace-hub knowledge base

### Documents consulted

- Issue #4093 — full problem statement; provides the exact rule content to add including standard citation requirements and CoG offset guidance
- digitalmodel#2666 (CLOSED) — "Lifting: SKL applied as a flat factor on an equal sling split; add leg count, CoG share and a cited default" — confirms the defect class: agents were incorrectly using equal 25/25/25/25 splits
- digitalmodel#2667 (CLOSED) — "Lifting: four-point single-hook lift skew calculator (sling stiffness, length and padeye tolerances, payload flexibility)" — the calculator implementation this rule should reference
- `data/document-index/online-resource-registry.yaml` — DNV-RP-H103 entry confirms the standard is indexed and locally available

### Gaps identified

- No existing skew-load guidance in any skill file; this is a net-new rule block
- The skill index entry for `installation-analysis` will need re-verification after edit (skill-index CI check may flag description drift — monitor)

### Evidence (embedded verification)

**Issue statuses** (verified 2026-10-21 via `gh issue view`):
- `#4093` — OPEN — Skill: add a four-point lift skew-load review rule to the OrcaFlex installation-analysis skill
- `digitalmodel#2666` — CLOSED — Lifting: SKL applied as a flat factor on an equal sling split
- `digitalmodel#2667` — CLOSED — Lifting: four-point single-hook lift skew calculator

**File existence** (`ls` 2026-10-21):
- EXISTS: `.agents/skills/engineering/marine-offshore/orcaflex/installation-analysis/SKILL.md`
- EXISTS: `.agents/skills/engineering/marine-offshore/orcaflex/SKILL.md`

**Gap proofs**:
- `grep -ri "skew" .agents/skills/` → no matches → confirms no existing skew rule
- `grep -ri "four-point" .agents/skills/` → no matches → confirms no four-point lift guidance

**Reproduction proofs**: N/A — documentation issue; no runtime failure to reproduce

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-10-21-issue-4093-orcaflex-skill-four-point-lift-skew-rule.md` |
| Skill file (changed) | `.agents/skills/engineering/marine-offshore/orcaflex/installation-analysis/SKILL.md` |
| Plan review — Claude | `scripts/review/results/2026-10-21-plan-4093-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-10-21-plan-4093-codex.md` |

---

## Deliverable

A "Four-point lift: skew load review" section in `.agents/skills/engineering/marine-offshore/orcaflex/installation-analysis/SKILL.md` that names the source standard and edition, specifies the minimum code value by leg count, requires the CoG-offset term to be separated from the skew factor, references the digitalmodel calculator, and explicitly prohibits accepting an equal 25/25/25/25 split.

---

## Files to Change

1. `.agents/skills/engineering/marine-offshore/orcaflex/installation-analysis/SKILL.md` — add one new section "## Four-point lift: skew load review" after the existing "Crane wire and sling configuration" bullet in the "When to Use" or within the body; include all five rules from the issue body verbatim, plus links to digitalmodel#2666 and digitalmodel#2667.

---

## TDD Test List

T1 — no dedicated test file required. Acceptance is verified by reading the skill file after the edit. The skill-index coherence CI check will catch any description-field drift if the frontmatter is accidentally modified.

1. **Verify rule block present**: `grep -c "skew load factor" .agents/skills/engineering/marine-offshore/orcaflex/installation-analysis/SKILL.md` returns ≥1
2. **Verify standard cited**: `grep "DNV-RP-H103\|DNVGL-ST-N001\|EN 13852" SKILL.md` returns ≥1 (accepts any commonly cited lifting standard)
3. **Verify calculator reference**: `grep "digitalmodel.*2667\|2667\|2666" SKILL.md` returns ≥1
4. **Verify equal-split prohibition**: `grep -i "25/25/25/25\|equal.*split\|never accept" SKILL.md` returns ≥1
5. **Verify frontmatter unchanged**: `head -15 SKILL.md` still shows `name: orcaflex-installation-analysis` with `version: 1.0.0` and `updated: 2026-01-17` unchanged (or updated to today if policy requires)

---

## Acceptance Criteria

- The rule appears in the skill, names a lifting standard by number and edition, and uses a code value no lower than the minimum for four-leg lifts.
- The CoG-offset term is explicitly identified as separate from the skew factor.
- The section references digitalmodel#2666 and/or digitalmodel#2667 as the calculator implementation.
- The prohibition on equal 25/25/25/25 splits from a perfect-geometry model is stated explicitly.
- The skill-index CI check passes (frontmatter fields not corrupted).
- The skill's index entry (in `.agents/skills/engineering/marine-offshore/orcaflex/installation-analysis/SKILL.md`) still resolves via the parent skill index.

---

## Risks and Open Questions

1. **Standard edition**: The issue says "name the skew load factor's source standard and edition". DNV-RP-H103 addresses marine operations including lift analysis but may not be the canonical lifting standard for leg-count SKL factors. DNVGL-ST-N001 Section 9 is the more specific reference for SKL. The plan author cannot read the licensed standard; the implementer should cite the exact section and edition they verify.
2. **Frontmatter `updated` field**: The skill has `updated: 2026-01-17`. If the harness validates this field strictly, it may need to be bumped to today. Check CI behaviour before committing.
3. **Scope**: Issue body says "for stiff payloads, run sling-length tolerance cases (perturbed sling lengths, or the calculator in vamseeachanta/digitalmodel#2667 once it exists)". digitalmodel#2667 is now CLOSED so the calculator exists; the rule should reference it as available, not "once it exists".
