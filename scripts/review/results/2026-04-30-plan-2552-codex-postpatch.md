# Post-Patch Plan Re-Review — Issue #2552 — Codex

- Date: 2026-04-30
- Prompt: `.planning/quick/2026-04-30-plan-2552-postpatch-review-prompt.md`
- Raw output: `.planning/quick/2026-04-30-plan-2552-codex-postpatch.raw`
- Source plan reviewed: `docs/plans/2026-04-29-issue-2552-external-contributor-runbook.md`

## Raw provider output

OpenAI Codex v0.125.0 (research preview)
--------
workdir: /mnt/local-analysis/workspace-hub
model: gpt-5.5
provider: openai
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR, /home/vamsee/.codex/memories]
reasoning effort: medium
reasoning summaries: none
session id: 019ddfcc-8b75-78f3-bf24-352790a08cf4
--------
user
# Fresh Post-Patch Adversarial Plan Re-Review — Issue #2552

You are an independent adversarial reviewer for a GitHub issue plan in `/mnt/local-analysis/workspace-hub`.

## Issue
- Number: #2552
- Title: docs(security): external contributor and unsolicited paid-help response runbook
- URL: https://github.com/vamseeachanta/workspace-hub/issues/2552
- Current label state verified immediately before this prompt: open `status:plan-review`.
- Approval marker state verified immediately before this prompt: `.planning/plan-approved/2552.md` absent.

## Review scope and rules
This is a fresh re-review AFTER local plan hardening. Do not rely on older issue text, default branch content, or stale review artifacts. Use ONLY the embedded current plan text below plus the prior-blocker summary for context.

Be adversarial. Do not rubber-stamp. The goal is to decide whether this CURRENT plan is approval-ready.

Verdict meanings:
- APPROVE: no critical/high blockers; plan can move to plan-approved.
- MINOR: only non-blocking improvements; plan can move to plan-approved with notes.
- MAJOR: any blocker that must be fixed before approval.
- UNAVAILABLE: only if you cannot actually review.

## Prior blockers being re-tested
Prior final Gemini review verdict was MAJOR with blockers: permanent CI test should not enforce a historical docs/plans/README.md plan-index row; missing public-facing off-GitHub contact path in README/CONTRIBUTING. The plan has since been patched to address those issues. Review the CURRENT plan text only.

## Specific questions
1. Are all prior MAJOR blockers now substantively resolved in the current plan text?
2. Are there any new or remaining MAJOR approval blockers?
3. Are acceptance criteria and verification commands concrete enough for a worker to execute without guessing?
4. Does the plan avoid inappropriate approval/label mutation before evidence exists?
5. Does the plan preserve the issue scope without leaking follow-up work into this tranche?

## Required output format
Start with exactly one line:
`Verdict: APPROVE|MINOR|MAJOR|UNAVAILABLE`

Then include:
- Summary: 2-5 bullets.
- Findings: severity-ranked list. For each finding include Severity, Evidence from plan text, Impact, Required fix.
- Prior blocker resolution: bullet checklist of each prior blocker and whether resolved.
- Approval recommendation: one of `approval-ready`, `approval-ready-with-minor-notes`, `not-approval-ready`, or `review-unavailable`.

## Current plan text under review

```markdown
# Plan for #2552: External contributor and unsolicited paid-help response runbook

> **Status:** plan-review (2026-04-30 reviewer blockers patched in plan text; T1 deferred-review approval candidate only if user explicitly accepts single-author evidence, otherwise requires fresh cross-provider re-review with no MAJOR)
> **Complexity:** T1
> **Date:** 2026-04-29
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2552
> **Review artifacts:** `scripts/review/results/2026-04-29-plan-2552-claude.md` (canonicalized from single-author Claude review), `scripts/review/results/2026-04-29-plan-2552-codex.md` (UNAVAILABLE timeout), `scripts/review/results/2026-04-29-plan-2552-gemini.md` (MAJOR but appears stale-workspace/false-negative on files present in this checkout), `scripts/review/results/2026-04-29-plan-2552-disagreement.md`, `scripts/review/results/2026-04-30-plan-2552-{codex,gemini}-final.md` (MAJOR; patched by this revision; requires fresh rerun or explicit user waiver).

---

## Resource Intelligence Summary

### Existing repo code

- Found: `docs/security/aceengineer-website-orphan-path-verification-2026-04-20.md` — only file in `docs/security/`. No external-contributor policy, no response runbook, no templates exist. Confirms gap.
- Found: `docs/governance/TRUST-ARCHITECTURE.md` — canonical agent-plan gate governance doc. Defines Category A (autonomous), Category B (plan gate), Category C (user-only) actions. Runbook should be cross-referenced from here because handling external interactions is a Category B/C decision point.
- Found: `docs/governance/SESSION-GOVERNANCE.md` — session-level governance. Not directly relevant but confirms `docs/governance/` is the canonical location for policy.
- Gap: `docs/security/external-contributor-runbook.md` — does not exist.
- Gap: No issue-comment templates anywhere in `docs/security/` or `docs/governance/` for declining/redirecting external requests.

### Standards

Not applicable — this is a documentation/policy issue.

### LLM Wiki pages consulted

No relevant wiki pages for external contributor policy.

### Documents consulted

- `docs/handoffs/github-collaborator-only-lockdown-2026-04-29.md` — confirms trigger event: an external GitHub account (not a current collaborator) commented on [#2401](https://github.com/vamseeachanta/workspace-hub/issues/2401) offering paid implementation help. Current public repo state: all 10 public `vamseeachanta/*` repos have `collaborators_only` interaction limits with `six_months` expiry (expires 2026-10-29). No response was posted to the external commenter. Handoff explicitly recommended planning this runbook.
- Issue [#2546](https://github.com/vamseeachanta/workspace-hub/issues/2546) (CLOSED/completed) — full context of the emergency lockdown that preceded this runbook need. Defines the protection applied and its limitations.
- Issue [#2550](https://github.com/vamseeachanta/workspace-hub/issues/2550) (OPEN, sibling — `chore(security): codify public repo interaction-limit renewal in scheduled tasks`) — durability mechanism for the same lockdown. Drafted in the same plan-commit SHA `2734c103b` as this plan; the runbook should reference renewal as the durability counterpart so that operators reading the runbook know where the time-bound protection is re-applied.
- Issue [#2401](https://github.com/vamseeachanta/workspace-hub/issues/2401) (OPEN) — the triggering issue where the external commenter appeared. Issue body confirms the comment appeared even after `cat:ai-orchestration` and `cat:harness` labels were on the issue. Running example for the runbook's "example scenario" section, referenced by issue number rather than by individual username.

### Gaps identified

- No `docs/security/external-contributor-runbook.md` — must be built from scratch.
- No issue-comment templates for declining/redirecting — must be written.
- `docs/governance/TRUST-ARCHITECTURE.md` has no cross-reference to external-interaction policy — one-line reference should be added.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-29T04:30Z initial; #2550 + label re-confirmed 2026-04-29T17:46Z via single-author review):
- `#2546` — CLOSED (completed) — `chore(security): restrict public repo interactions to collaborators only`
- `#2552` — OPEN, label `status:plan-review` — `docs(security): external contributor and unsolicited paid-help response runbook`
- `#2550` — OPEN, label `status:plan-review` — `chore(security): codify public repo interaction-limit renewal in scheduled tasks` (sibling durability mechanism — same `2734c103b` plan-commit SHA)
- `#2401` — OPEN — `feat(doc-intel): MCP server multi-agent registration — Claude / Gemini / Hermes` (the triggering issue)

**File existence** (`ls` 2026-04-29T04:30Z):
- EXISTS: `docs/security/aceengineer-website-orphan-path-verification-2026-04-20.md`
- EXISTS: `docs/governance/TRUST-ARCHITECTURE.md`
- EXISTS: `docs/handoffs/github-collaborator-only-lockdown-2026-04-29.md`
- MISSING (new — this plan creates): `docs/security/external-contributor-runbook.md`

**Gap proof** (`ls docs/security/`):
```
aceengineer-website-orphan-path-verification-2026-04-20.md
```
→ No runbook file, no templates. Confirms no prior art.

<!-- Verification: count distinct sources: (1) issue body #2552 + (2) handoff doc + (3) #2546 closeout + (4) docs/security/ gap proof + (5) TRUST-ARCHITECTURE.md. Count: 5 → satisfies ≥3 -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-29-issue-2552-external-contributor-runbook.md` |
| Runbook (to be created on approval) | `docs/security/external-contributor-runbook.md` |
| Structural lint tests (to be created on approval) | `tests/security/test_runbook_external_contributor.py` |
| TRUST-ARCHITECTURE cross-ref (to be added on approval) | `docs/governance/TRUST-ARCHITECTURE.md` (one-line addition) |
| Plan review — Claude single-author (autofeed) | `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-review-2552-20260429-1246.md` (EXISTS) |
| Plan review — Claude (canonical slot) | `scripts/review/results/2026-04-29-plan-2552-claude.md` (EXISTS; restored from single-author review) |
| Plan review — Codex (canonical slot) | `scripts/review/results/2026-04-29-plan-2552-codex.md` (UNAVAILABLE timeout; no substantive signal) |
| Plan review — Gemini (canonical slot) | `scripts/review/results/2026-04-29-plan-2552-gemini.md` (MAJOR, but stale-workspace false-negative claims conflict with files present in this checkout) |

---

## Deliverable

A `docs/security/external-contributor-runbook.md` file that covers all four external-interaction scenarios with decision criteria, response templates, and a lightweight collaborator/paid-pilot intake path, plus a one-line cross-reference in `docs/governance/TRUST-ARCHITECTURE.md` and a public-facing pointer in the repository `README.md` so legitimate contributors can discover the off-GitHub contact path while interaction limits are active.

---

## Pseudocode

Trivial — see Files to Change. No algorithmic logic; this is a pure documentation artifact.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/security/external-contributor-runbook.md` | main runbook with decision tree + templates |
| Create | `tests/security/test_runbook_external_contributor.py` | structural lint tests — file existence, scenario coverage, template presence (incl. `HIDE_CHECKLIST`), TRUST-ARCHITECTURE cross-reference |
| Modify | `docs/governance/TRUST-ARCHITECTURE.md` | add one-line cross-reference under a new "External Interaction Policy" pointer |
| Modify | `README.md` | add a concise public-facing external-contributor contact-path pointer while public repos are under `collaborators_only` interaction limits |
| Update | `docs/plans/README.md` | add this plan to index as a one-time process artifact; do not create a permanent CI test that hard-codes this historical plan row |

---

## Runbook document outline

The runbook must cover these four scenarios (from issue AC):

1. **Unsolicited paid-help offer** — e.g., the external GitHub account that commented on [#2401](https://github.com/vamseeachanta/workspace-hub/issues/2401) offering paid implementation help (referenced by issue number; do NOT name the individual inline in the runbook output — see AC). Decision criteria: is the account a known collaborator? If no: do NOT reply publicly, do NOT engage, use GitHub's "Hide comment" option or "Report" for spam. If yes (existing collaborator asking to be compensated): route to private channel, not public issue.

2. **Suspected spam / bot comment** — automated scraper / generic solicitation. Decision: hide immediately via GitHub UI, report if it recurs.

3. **Legitimate external contributor request** — someone with a genuine patch or proposal, but not a collaborator. Decision: route through a "Contributor Interest" template asking them to describe scope + sign off on the project's CLA/license posture. Do NOT grant `write` access until reviewed; use fork-and-PR path instead. **Caveat (mandatory in runbook):** while public repos are under the `collaborators_only` interaction limit (currently active through 2026-10-29 — see [#2550](https://github.com/vamseeachanta/workspace-hub/issues/2550) for renewal codification and `docs/handoffs/github-collaborator-only-lockdown-2026-04-29.md` for the lockdown handoff), non-collaborators cannot comment on issues, open issues, or open PRs against the public repos at all. Scenario 3 actions therefore require either a temporary lift of the interaction limit, a prior collaborator invitation, or an off-GitHub contact route published from `README.md`; the runbook must instruct the operator to make that choice consciously rather than following the default fork-and-PR pattern.

4. **Paid external execution request** — structured proposal to implement a scoped issue. Decision: requires (a) scope definition, (b) NDA/confidentiality acknowledgement for private-context repos, (c) payment approval from owner, (d) fork + PR-only access (no direct push), (e) PR review gate held by owner before merge.

**Required templates in the runbook:**
- `DECLINE_TEMPLATE` — 2-line response for politely-closing a public solicitation if engagement is warranted (default is hide, not reply)
- `CONTRIBUTOR_INTEREST_TEMPLATE` — reply to a legitimate contributor directing them to fork + PR + contact
- `HIDE_CHECKLIST` — 5-step checklist: locate comment → "Hide" in GitHub UI → log in a private note → check for follow-up comments → optionally report if account is suspect

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_runbook_file_exists` | file was created at the canonical path | filesystem check | `docs/security/external-contributor-runbook.md` exists |
| `test_runbook_covers_four_scenarios` | document contains all 4 scenario headers | file content | headings matching "unsolicited", "spam", "legitimate contributor", "paid" (case-insensitive) |
| `test_runbook_contains_templates` | templates section present | file content | `DECLINE_TEMPLATE`, `CONTRIBUTOR_INTEREST_TEMPLATE`, AND `HIDE_CHECKLIST` strings all present (no template silently omitted) |
| `test_trust_architecture_crossref` | TRUST-ARCHITECTURE.md references the runbook | file content | `external-contributor-runbook` present in TRUST-ARCHITECTURE.md |
| `test_readme_external_contributor_pointer` | repository README publishes a discoverable off-GitHub contact-path pointer while interaction limits are active | file content | `external-contributor-runbook` or `external contributor` plus a contact-path phrase present in `README.md` |

These are structural lint tests (`grep`-level), runnable as `pytest` with `pathlib` + `re`. Appropriate for a T1 documentation issue.

---

## Acceptance Criteria

- [ ] `docs/security/external-contributor-runbook.md` exists and covers all 4 scenarios (unsolicited paid-help, spam, legitimate contributor, paid-pilot intake)
- [ ] Runbook includes `DECLINE_TEMPLATE`, `CONTRIBUTOR_INTEREST_TEMPLATE`, AND `HIDE_CHECKLIST` copy-paste blocks (none of the three may be silently omitted)
- [ ] Runbook references [#2546](https://github.com/vamseeachanta/workspace-hub/issues/2546), [#2401](https://github.com/vamseeachanta/workspace-hub/issues/2401), AND [#2550](https://github.com/vamseeachanta/workspace-hub/issues/2550) — #2546/#2401 as the triggering example, #2550 as the sibling renewal-enforcement counterpart (per issue AC + single-author review F4)
- [ ] Runbook references [#2401](https://github.com/vamseeachanta/workspace-hub/issues/2401) by issue number for the example scenario; does NOT name the individual external commenter inline (defensive — per single-author review L1)
- [ ] Runbook Scenario 3 carries an explicit caveat: while `collaborators_only` interaction limits are active (currently through 2026-10-29 — see [#2550](https://github.com/vamseeachanta/workspace-hub/issues/2550)), Scenario 3 fork-and-PR actions require temporary lift of the limit, prior collaborator invitation, or a README-published off-GitHub contact route (per single-author review F5 plus 2026-04-30 re-review)
- [ ] Runbook preserves public-repo security posture: no collaborator access without explicit owner approval
- [ ] `docs/governance/TRUST-ARCHITECTURE.md` has a one-line cross-reference to the runbook
- [ ] `README.md` has a concise public-facing pointer for legitimate external contributors, including the off-GitHub contact route or a link to the runbook, so Scenario 3 is discoverable even while `collaborators_only` is active
- [ ] Permanent structural tests do NOT hard-code the historical `docs/plans/README.md` row for this plan; plan-index verification is a one-time execution check only
- [ ] All 5 structural tests pass: `uv run pytest tests/security/test_runbook_external_contributor.py -v`
- [ ] No regression: `uv run pytest tests/` passes (run from repo root; the repo IS `workspace-hub`, so `workspace-hub/tests/` would resolve to a non-existent nested path)
- [ ] Plan listed in `docs/plans/README.md` index (process artifact, paired with Files-to-Change `docs/plans/README.md` row; per single-author review L3)

---

## Adversarial Review Summary

<!-- Updated 2026-04-29T13:10Z (autofeed plan-patch lane). Single-author Claude review complete; Codex/Gemini fanout NOT YET RUN. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (single-author, autofeed `feed1` lane) | MINOR_PATCH_NEEDED → patches applied this revision | F1 pytest path (`workspace-hub/tests/` → `tests/`), F2 missing test-file Files-to-Change row, F3 `HIDE_CHECKLIST` absent from AC + test, F4 sibling [#2550](https://github.com/vamseeachanta/workspace-hub/issues/2550) reference missing, F5 Scenario 3 needs collaborators_only caveat, F6 docs/security location should be resolved up-front, plus L1 (no-inline-username) and L3 (README index AC). All addressed in this plan revision. Review artifact: `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-review-2552-20260429-1246.md`. |
| Codex | UNAVAILABLE (2026-04-30 batch2 fanout) | `scripts/review/results/2026-04-29-plan-2552-codex.md` timed out / stdin-hang and contributed no substantive signal. |
| Gemini | MAJOR (2026-04-30 batch2 fanout; likely stale workspace) | `scripts/review/results/2026-04-29-plan-2552-gemini.md` reports missing `docs/handoffs/...` and missing autofeed artifact, but both exist in this isolated checkout. Treat as invalid stale-workspace evidence; do not count as approval evidence, but also do not treat the false file-existence findings as substantive plan blockers. |

**Overall result:** SINGLE-AUTHOR MINOR PATCHED plus 2026-04-30 reviewer blocker patch — T1 deferred-review approval candidate if the user explicitly accepts single-author evidence; full cross-provider approval remains blocked until fresh Codex/Gemini reruns return no MAJOR. The user has two paths:

1. **T1 deferred-review path** (faster): user approves on the strength of this single-author Claude review + the F1–F6/L1/L3 patches landed in this revision. T1 documentation issue eligibility is precedent-supported. No fanout required.
2. **Full cross-AI fanout** (slower, higher confidence): rerun Codex/Gemini against this exact revised artifact (prefer EOF-safe stdin-file prompts for Codex because older lanes showed stdin stalls); after Codex+Gemini return MINOR-or-better, user approves.

The plan remains at `status:plan-review` — no self-promotion, no `.planning/plan-approved/2552.md` marker created by this lane.

---

## Risks and Open Questions

- **Risk:** Scenario 1 default (hide, don't reply) may be wrong if the external commenter has already been seen by others. Recommendation is hide-not-reply for the default case; explicit reply templates are provided for edge cases where engagement is warranted. Flag for user during approval.
- **Resolved (was Open — now closed per single-author review F6, 2026-04-29):** Runbook will live at `docs/security/external-contributor-runbook.md`. Rationale: (a) issue title says `docs(security):`, (b) `docs/security/` taxonomy already exists and is the discoverability target for anyone investigating the interaction-limit setup that triggered this work, (c) one-line policy artifacts do not warrant promoting a new `docs/ops/runbooks/` taxonomy. The Files-to-Change table commits to `docs/security/`; downstream batch agents must NOT relocate.
- **Decision:** The paid-pilot intake path does not include a formal NDA template in this tranche. The runbook records intake *requirements* (NDA/confidentiality acknowledgement, payment approval, etc.) and leaves actual NDA drafting to a follow-up legal/template issue if requested.
- **Decision:** The repository `README.md` must publish a concise off-GitHub contact pointer for legitimate external contributors; otherwise Scenario 3 is not discoverable while `collaborators_only` blocks public GitHub interaction.
- **Decision:** Do not create a permanent CI test for the `docs/plans/README.md` historical plan row. Verify the plan index once during execution, but keep durable tests focused on the runbook, governance cross-reference, README discoverability, and template/scenario coverage.

---

## Complexity: T1

Single new markdown file plus a one-line edit to an existing governance doc. No new modules, no tests with real logic, no config changes. The structural lint tests are included as good practice but are trivially passable on file creation.

```

warning: Codex's Linux sandbox uses bubblewrap and needs access to create user namespaces.
codex
Verdict: MAJOR

- Summary:
  - The permanent CI historical-plan-row blocker is resolved in the current text.
  - The README/public contact blocker is only partially resolved because the plan still does not specify an actual off-GitHub contact route.
  - Verification commands are mostly concrete, but the README/contact-path acceptance leaves too much discretion for the worker.
  - The plan correctly avoids approval marker creation and label promotion before evidence/user approval.

- Findings:
  - Severity: MAJOR
    - Evidence from plan text: `README.md has a concise public-facing pointer ... including the off-GitHub contact route or a link to the runbook`; test expects only ``external-contributor-runbook` or `external contributor` plus a contact-path phrase`.
    - Impact: A worker can satisfy this with vague text or a repo-local link without publishing a real off-GitHub contact mechanism. That does not substantively fix the prior blocker: legitimate contributors still may have no usable route while `collaborators_only` blocks GitHub interaction.
    - Required fix: Name the required contact route explicitly, or require a concrete placeholder format approved by the owner, e.g. `contact: <specific email/contact form/website path>`. The README AC and test should assert that concrete route, not just a “contact-path phrase.”

- Prior blocker resolution:
  - Permanent CI test should not enforce historical `docs/plans/README.md` row: resolved. Current plan says the plan index is one-time execution verification only and durable tests must not hard-code the historical row.
  - Missing public-facing off-GitHub contact path in README/CONTRIBUTING: not fully resolved. README is now in scope, but the plan does not define the actual off-GitHub path strongly enough.

- Approval recommendation: not-approval-ready
2026-04-30T19:10:39.650531Z ERROR codex_core::session: failed to record rollout items: thread 019ddfcc-8b75-78f3-bf24-352790a08cf4 not found
tokens used
30,121
Verdict: MAJOR

- Summary:
  - The permanent CI historical-plan-row blocker is resolved in the current text.
  - The README/public contact blocker is only partially resolved because the plan still does not specify an actual off-GitHub contact route.
  - Verification commands are mostly concrete, but the README/contact-path acceptance leaves too much discretion for the worker.
  - The plan correctly avoids approval marker creation and label promotion before evidence/user approval.

- Findings:
  - Severity: MAJOR
    - Evidence from plan text: `README.md has a concise public-facing pointer ... including the off-GitHub contact route or a link to the runbook`; test expects only ``external-contributor-runbook` or `external contributor` plus a contact-path phrase`.
    - Impact: A worker can satisfy this with vague text or a repo-local link without publishing a real off-GitHub contact mechanism. That does not substantively fix the prior blocker: legitimate contributors still may have no usable route while `collaborators_only` blocks GitHub interaction.
    - Required fix: Name the required contact route explicitly, or require a concrete placeholder format approved by the owner, e.g. `contact: <specific email/contact form/website path>`. The README AC and test should assert that concrete route, not just a “contact-path phrase.”

- Prior blocker resolution:
  - Permanent CI test should not enforce historical `docs/plans/README.md` row: resolved. Current plan says the plan index is one-time execution verification only and durable tests must not hard-code the historical row.
  - Missing public-facing off-GitHub contact path in README/CONTRIBUTING: not fully resolved. README is now in scope, but the plan does not define the actual off-GitHub path strongly enough.

- Approval recommendation: not-approval-ready
