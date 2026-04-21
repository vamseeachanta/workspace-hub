# #2347 mechanical-only pilot — scoping analysis (2026-04-21)

**Context:** Claude-CLI rollout umbrella #2425 v2, post-MAJOR adversarial review. This document is scoping only — not a plan, no label changes, no body edits.

## Scope-narrowed deliverable (1 paragraph)

Rewrite the bodies of **#2016** and **#1669 only** (drop #117 + #191) so each reflects actual shipped-artifact reality as of 2026-04-21. Reconciliation is restricted to three mechanical dimensions: (a) sub-issue **state** (`Open` → `CLOSED` flips via `gh issue view N --json state`), (b) **file-path presence** on `main` (`docs/strategy/gtm/vessel-installation-contractors/*.md` etc. — literal path existence, no content judgment), and (c) **deprecated-schema stripping** per the explicit policy below. No semantic judgment of outreach checkboxes. No recursion beyond depth-1 sub-issue state lookups. Output is two `gh issue edit --body-file` operations, each preceded by a pre-edit body snapshot committed to `scripts/review/pre-edit/`.

## Concrete file targets — #2016

Source body: 122 lines (verified via `gh issue view 2016`). Mechanical edits only:

| Edit target | Location (lines) | Mechanical check | Est. flips |
|---|---|---|---|
| TIER 1 demo matrix rows | 62–74 (13 lines) | `gh issue view {1871,1872,1873,1874,1930,1931,1831,1832,1809,1792,1904,1932,1798,1799} --json state` | ~10 of 14 are CLOSED per review spot-check |
| TIER 2 scanner fixes | 80–82 | `gh issue view {1707,1708,1709,1971} --json state` | likely 2–4 flips |
| TIER 3 outreach table | 87–92 | state-only for #191/#117/#1669/#197 (do NOT rewrite acceptance criteria) | 0–1 flips |
| TIER 4 pipeline modules | 97–101 | state-only for #1834–1837 | spot-check needed |
| CRITICAL PATH diagram | 105–115 | strike-through CLOSED sub-issues; preserve graph shape | visual only |
| RELATED ISSUES footer | 118–121 | #108/#1670/#1671/#898 state verify — already marks #1670/#1671/#898 CLOSED correctly | 0–1 flips |
| Stale "Last updated" date | line 51 | bump to 2026-04-21 | 1 line |

**Total estimated mechanical diff:** ~25–35 lines changed out of 122.

## Concrete file targets — #1669

Source body: ~95 lines (verified). Much narrower scope:

| Edit target | Mechanical check | Est. flips |
|---|---|---|
| `Files to Create` section (lines ~79–85) | `ls docs/strategy/gtm/vessel-installation-contractors/` — currently only `email-templates.md` exists; README/prospect-list/value-proposition/capability-summary missing | Flip from "to Create" framing to "partially shipped — 1 of 5" table |
| `References` section (`docs/strategy/engineering-chatbot-oilgas-pitch.md`) | `ls` — **file exists** | No flip; preserve |
| Phase 1/2/3 checkboxes | **Do NOT touch.** These are outreach-action checkboxes; mechanical pilot cannot judge. | 0 |
| Target-companies list (Tier 1/2/3) | No state to reconcile | 0 |

**Total estimated mechanical diff:** ~10–15 lines (single section rewrite).

## Strip-vs-preserve policy for deprecated WRK-schema

- **#2016 footer reference** `#108 — WRK-148: ACE-GTM parent strategy stream (Stage 17)` — **preserve verbatim.** The WRK-prefix lives in the *target* issue #108's own text; #2016 is only citing it. Stripping here would desync the citation from what `gh issue view 108` actually shows.
- **#1669** — no WRK-schema content in body; no action needed.
- **Out-of-scope (#117)** — legacy `WRK-470 / Stage 17 / <details>` scaffolding lives in #117's own body. That's the undecided policy call from the scoping review (finding #7). Deferring it by dropping #117 from this pilot is the correct move — do **not** attempt to rule on strip-vs-preserve for #117 as part of this pilot.

**Rule of thumb for this pilot:** touch WRK tokens only when they appear in a bullet we are already flipping state on. Never rewrite a WRK reference standalone.

## Rollback-safe `gh issue edit` procedure

Addresses scoping-review finding #4 (`gh issue edit --body` atomic overwrite with no dry-run):

```
# Pre-edit snapshot (committed BEFORE edit)
mkdir -p scripts/review/pre-edit
gh issue view 2016 --json body,updatedAt --repo vamseeachanta/workspace-hub \
  > scripts/review/pre-edit/2016-pre-$(date -u +%Y%m%dT%H%M%SZ).json
git add scripts/review/pre-edit/2016-pre-*.json && git commit -m "chore(pre-edit): snapshot #2016 body before #2347 reconcile"

# Diff preview (human eyeball)
diff <(jq -r '.body' scripts/review/pre-edit/2016-pre-*.json) scripts/review/pre-edit/2016-proposed.md

# Apply via --body-file (never --body inline)
gh issue edit 2016 --body-file scripts/review/pre-edit/2016-proposed.md --repo vamseeachanta/workspace-hub

# Post-edit verify
gh issue view 2016 --json body --repo vamseeachanta/workspace-hub \
  | diff - scripts/review/pre-edit/2016-proposed.md  # expect empty diff

# Rollback (if verify fails or post-hoc concern)
gh issue edit 2016 --body-file <(jq -r '.body' scripts/review/pre-edit/2016-pre-*.json) --repo vamseeachanta/workspace-hub
```

Same procedure for #1669. Both pre-edit snapshots committed before any `gh issue edit`.

## Coordination with #2323 fanout — status check

**Verified:** `/mnt/local-analysis/worktrees/workspace-hub-issue-2323` is on branch `issue-2323-cross-ai-review-fanout` at `dec771e1e`. Label state: `status:plan-approved`. Commit log shows:
- `scripts/review/plan-review-fanout.sh` — **exists and implemented** (cycles 4–12 landed)
- `scripts/review/plan-review-prompt.md` — shared adversarial-stance prompt landed (cycle 3)
- Plan file marked `Status → implemented` in latest two commits
- Regression tests + disagreement report plumbing in place (cycles 8–12)

**Recommendation: coordinate, don't wait.** #2323's fanout targets *plan files* (`docs/plans/*.md`) for cross-provider adversarial review of plans. #2347's mechanical pilot targets *issue bodies* — a different artifact class. #2323 is useful for reviewing the *plan file* that will be drafted for #2347 (i.e., run `plan-review-fanout.sh docs/plans/2026-04-21-issue-2347-mechanical-pilot.md`), not as a dependency of the body-edit work itself. No blocking overlap. #2323's landing means the adversarial-review step for #2347's plan is already cheap.

## Ready for concrete plan draft? **Conditional Yes.**

**Why conditional, not unqualified yes:** the three MAJOR blockers from the scoping review are addressable in the plan itself rather than requiring upstream work:

1. **Scope narrowing** — addressed above (drop #117/#191; depth-1 only; no outreach-checkbox flips).
2. **Semantic-vs-mechanical split** — addressed above (Phase 1/2/3 outreach checkboxes in #1669 explicitly not touched; #1669 edit scoped to the `Files to Create` section only).
3. **#2405 attestation over-application** — addressed by either (a) writing the plan under `docs/plans/` so `scripts/review/attest-plan-claims.sh` has a valid target, or (b) dropping the "validates #2405 thesis" framing and positioning this as a pre-attestation mechanical cleanup. Recommend (b) — attestation is designed for plan claims, not issue bodies; over-claiming it weakens the signal.

**What's still required before plan-draft is worthwhile:**
- User decision on (a) vs (b) for the attestation framing.
- User confirmation that "depth-1 only, no sub-issue-body recursion" is the acceptable scope bound (otherwise the 30+ sub-issue cascade re-opens).
- User selection of #2347 as the pilot (per umbrella v2's "no recommendation" stance, this selection is explicit, not inferred).

If those three user decisions land, the plan file is a ~2-hour draft (concrete file targets + rollback procedure are already specified above; the plan just wires them into an `issue-planning-mode` template with adversarial-review and verify sections).

## Out of scope for this pilot (explicit)

- #117 body rewrite (defer; WRK-schema policy call unresolved)
- #191 body rewrite (defer; acceptance criteria are outreach-semantic)
- Sub-issue body reconciliation (depth ≥2) — only sub-issue *state* is checked
- Any new attestation infra for tracker bodies
- Automated (non-human-approved) `gh issue edit` — every edit is human-eyeballed diff → explicit apply
