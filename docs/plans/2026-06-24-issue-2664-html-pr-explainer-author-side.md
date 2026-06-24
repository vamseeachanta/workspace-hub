# Plan for #2664: feat(workflow): HTML PR explainer artifact (author-side)

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-06-24
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2664
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-06-24-plan-2664-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `.github/` directory — contains `ISSUE_TEMPLATE/`, `workflow-templates/`, `workflows/` subdirs (confirmed via MCP listing 2026-06-24). **No `pull_request_template.md` exists** — this plan creates it.
- Found: `docs/` directory structure — `docs/plans/`, `docs/reports/`, `docs/session-handoffs/` present. **No `docs/pr-explainers/` directory exists** — this plan creates it.
- Found: `#2663` (chore: adopt HTML as default artifact format) — currently at `status:plan-review` (confirmed in plan-review issue list 2026-06-24); the parent format policy rule. This plan references but does not depend on #2663 landing — the PR explainer convention can be documented independently of the rule file.
- Found: `#2154` (HTML publication layout renderer) and `#2432` (Claude Design adoption) — related issues referenced in #2664 body as context; confirmed via issue body; not dependencies.
- Gap: No prior `docs/pr-explainers/` directory, no `pull_request_template.md`, no existing pilot HTML explainer — all three artifacts are new creation.
- Gap: Thariq Shihipar's source article URL (`https://x.com/trq212/status/2053632475294400084`) is an external reference in the issue body — content is cited in the issue; the plan does not require fetching the live URL.

### Standards

| Standard | Status | Source |
|---|---|---|
| HTML-first artifact convention | pending (parent rule #2663 at plan-review) | `feedback_html_default_artifact`, `#2663` |
| No new skill without 5+ uses | convention | `#2664` issue body: "No new skill is created" |

### LLM Wiki pages consulted

- No relevant wiki pages — this is a repo workflow convention issue, not an engineering domain topic.

### Documents consulted

- `#2664` issue body (2026-05-12) — full artifact contract spec: location `docs/pr-explainers/`, trigger at PR creation, 6 minimum content sections, PR body `## Reviewer guide` link, regeneration on push; verified OPEN 2026-06-24
- Issue comment 4481324848 (2026-05-18) — user's implementation prompt; no plan or implementation produced
- Issue comment 4672197453 (2026-06-10) — AI triage note confirming "nothing implemented" and "Depends on #2663's artifact-format rule landing" (soft dependency, not a hard blocker)
- `#2663` issue — at `status:plan-review`; provides parent HTML rule context
- `docs/plans/_template-issue-plan.md` — plan template followed in this document

### Gaps identified

- `docs/pr-explainers/README.md` — must be created from scratch per the issue's artifact contract spec
- `.github/pull_request_template.md` — must be created; no existing PR template in repo
- Pilot HTML explainer — must be generated for one real PR during implementation; the exact PR is not predetermined (implementer picks the next harness-touching PR or the PR that merges this change itself)
- Generation prompt — the issue cites Thariq's verbatim prompt; implementer records it in the README as the canonical one-liner

### Evidence (embedded verification)

**Issue statuses** (verified 2026-06-24 via MCP):
- `#2664` — OPEN — feat(workflow): HTML PR explainer artifact (author-side)
- `#2663` — OPEN, `status:plan-review` — chore(harness): adopt HTML as default artifact format (confirmed in plan-review list 2026-06-24)

**File existence** (confirmed 2026-06-24 via MCP directory listing):
- EXISTS: `.github/ISSUE_TEMPLATE/` (dir)
- EXISTS: `.github/workflows/` (dir)
- MISSING (new — this plan creates): `.github/pull_request_template.md`
- MISSING (new — this plan creates): `docs/pr-explainers/README.md`
- MISSING (new — this plan creates): `docs/pr-explainers/<date>-<pr>-explainer.html` (pilot)

**Gap proofs**:
- `.github/` listing (MCP 2026-06-24): only `ISSUE_TEMPLATE`, `workflow-templates`, `workflows` — no `pull_request_template.md` present
- `docs/pr-explainers/` does not appear in `docs/` directory listing — confirmed MISSING

**Reproduction proofs**: N/A — this is a new feature / convention issue; no runtime failure to reproduce. Skip-allowed per issue-planning-mode: "N/A — governance/documentation issue with no runtime failure mode".

<!-- Verification: 5 distinct sources consulted (issue body, 2 issue comments, #2663 at plan-review, MCP .github listing). Minimum 3 met. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-06-24-issue-2664-html-pr-explainer-author-side.md` |
| Convention doc | `docs/pr-explainers/README.md` |
| PR template | `.github/pull_request_template.md` |
| Pilot explainer | `docs/pr-explainers/YYYY-MM-DD-pr-NNN-explainer.html` (created during implementation) |
| Plan review — Claude | `scripts/review/results/2026-06-24-plan-2664-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-06-24-plan-2664-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-06-24-plan-2664-gemini.md` |

---

## Deliverable

`docs/pr-explainers/README.md` documents the author-side HTML PR explainer contract, `.github/pull_request_template.md` gains a `## Reviewer guide` section that references the explainer path, and at least one pilot HTML explainer exists for a real PR demonstrating the convention end-to-end.

---

## Pseudocode

```
Step 1 — Create docs/pr-explainers/README.md:
  write artifact contract:
    location: docs/pr-explainers/<date>-pr-<number>-explainer.html
    trigger: at PR creation time, or after substantial rewrite
    minimum sections: title+branch+target, per-file diff with line annotations,
      focus-callout (1-3 spots), severity-coded findings, SVG if logic-flow matters,
      out-of-scope section
    PR body link: under "## Reviewer guide" heading
    regeneration: on every push (not authoritative — diff is)
  write tradeoffs section:
    explainer is NOT authoritative (diff is)
    stale risk on force-push; convention = regenerate on each push
    optional for most PRs; recommended for harness/orchestration changes
    no new skill until 5+ uses warrant it
  write generation one-liner:
    "Help me review this PR by creating an HTML artifact that describes it..."
    (verbatim prompt from Thariq Shihipar's article, already in issue body)

Step 2 — Create .github/pull_request_template.md:
  standard PR sections (Summary, Test plan, Checklist)
  add section: ## Reviewer guide
    [ ] Explainer attached at docs/pr-explainers/<date>-pr-<this-pr-number>-explainer.html
    (optional — recommended for harness/orchestration changes)

Step 3 — Generate pilot HTML explainer:
  pick the next available harness-touching PR (or the PR merging this issue itself)
  run the generation one-liner from the README against that PR's diff
  save result to docs/pr-explainers/<date>-pr-<number>-explainer.html
  verify it contains: diff view, inline annotations, focus callout, severity coding
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/pr-explainers/README.md` | Artifact contract, tradeoffs, one-liner prompt, and convention documentation |
| Create | `.github/pull_request_template.md` | Adds `## Reviewer guide` section to all future PRs |
| Create | `docs/pr-explainers/<date>-pr-<NNN>-explainer.html` | Pilot — proves the convention works end-to-end |

Note: No skill file is created per the issue's explicit constraint ("No new skill is created"). If a natural skill emerges after 5+ uses, file a follow-on.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_readme_exists` | README file created | `docs/pr-explainers/README.md` | file exists, non-empty |
| `test_readme_has_location_contract` | Location spec documented | README content | contains `docs/pr-explainers/` |
| `test_readme_has_six_content_sections` | All 6 minimum content sections listed | README content | contains title/branch, per-file diff, focus callout, severity, SVG, out-of-scope |
| `test_readme_has_tradeoffs` | Tradeoffs/not-authoritative noted | README content | contains "not authoritative" or equivalent |
| `test_readme_has_one_liner` | Generation prompt present | README content | contains verbatim Thariq prompt excerpt |
| `test_pr_template_exists` | PR template created | `.github/pull_request_template.md` | file exists |
| `test_pr_template_has_reviewer_guide` | Reviewer guide section present | PR template content | contains `## Reviewer guide` |
| `test_pilot_html_exists` | Pilot explainer created | `docs/pr-explainers/*.html` | at least one HTML file present |
| `test_pilot_html_has_required_sections` | Pilot has diff + callouts | pilot HTML content | contains diff/annotation markers and focus callout |

Tests are shell grep assertions (`grep -q "pattern" file || exit 1`) runnable as `bash tests/workflow/test_html_pr_explainer.sh`.

---

## Acceptance Criteria

- [ ] `docs/pr-explainers/README.md` exists and covers all 6 minimum content sections from the issue body
- [ ] `docs/pr-explainers/README.md` includes the verbatim (or lightly cleaned) Thariq one-liner generation prompt
- [ ] `docs/pr-explainers/README.md` includes a tradeoffs/not-authoritative section with staleness warning
- [ ] `.github/pull_request_template.md` exists and contains a `## Reviewer guide` heading with explainer path convention
- [ ] At least one pilot `docs/pr-explainers/*.html` file exists for a real PR
- [ ] Pilot HTML contains rendered diff annotations and at least one focus callout
- [ ] No new skill file created (per issue constraint: file a follow-on if 5+ uses warrant one)
- [ ] `#2663` soft dependency noted in README but convention does not require #2663 to land first

---

## Adversarial Review Summary

<!-- Pending — to be dispatched via scripts/review/plan-review-fanout.sh after status:plan-review is set. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | TBD | — |
| Codex | TBD | — |
| Gemini | TBD | — |

**Overall result:** Pending

---

## Risks and Open Questions

- **Risk:** `pull_request_template.md` will appear in every future PR's diff when the template is first added to the repo — this is expected one-time noise; note in the PR description.
- **Risk:** Pilot HTML generation requires Claude Code or equivalent to be running with access to a real PR diff — if no suitable PR is available at implementation time, the implementer may use the PR that merges this issue itself (self-documenting bootstrap).
- **Risk:** The `## Reviewer guide` section in the PR template may be ignored by contributors who don't know about the explainer convention — the README and template together document the opt-in nature; enforcement is not proposed.
- **Open:** Should the PR template also link to the README for the convention? Yes — add a parenthetical `(see docs/pr-explainers/README.md)` so the template is self-documenting.
- **Open:** Does the pilot HTML need to be regenerated if the PR it documents is later force-pushed? No — the pilot is evidence of the convention working, not a live document. Note this in the README.
- **Open:** Dependency on `#2663` landing: the README should reference #2663's rule file path once it lands, but should not hard-block on it. Note as a follow-up cleanup: "once #2663 lands, update README to reference the formal rule at `.claude/rules/artifact-format.md`".

---

## Complexity: T2

**T2** — 3 new files across 3 distinct locations (`docs/pr-explainers/README.md`, `.github/pull_request_template.md`, pilot HTML); requires a live pilot generation step that cannot be fully pre-scripted; multi-file scope with cross-cutting concern (all future PRs affected by template addition).
