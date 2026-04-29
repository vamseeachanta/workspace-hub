# Plan for #2552: External contributor and unsolicited paid-help response runbook

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-04-29
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2552
> **Review artifacts:** scripts/review/results/2026-04-29-plan-2552-claude.md | ...-codex.md | ...-gemini.md

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

- `docs/handoffs/github-collaborator-only-lockdown-2026-04-29.md` — confirms trigger event: external account `Baijack-star` commented on #2401 offering paid implementation help. Current public repo state: all 10 public `vamseeachanta/*` repos have `collaborators_only` interaction limits with `six_months` expiry (expires 2026-10-29). No response was posted to the external commenter. Handoff explicitly recommended planning this runbook.
- Issue #2546 (CLOSED/completed) — full context of the emergency lockdown that preceded this runbook need. Defines the protection applied and its limitations.
- Issue #2401 (OPEN) — the triggering issue where `Baijack-star` commented. Issue body confirms the comment appeared even after `cat:ai-orchestration` and `cat:harness` labels were on the issue. Running example for the runbook's "example scenario" section.

### Gaps identified

- No `docs/security/external-contributor-runbook.md` — must be built from scratch.
- No issue-comment templates for declining/redirecting — must be written.
- `docs/governance/TRUST-ARCHITECTURE.md` has no cross-reference to external-interaction policy — one-line reference should be added.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-29T04:30Z):
- `#2546` — CLOSED (completed) — `chore(security): restrict public repo interactions to collaborators only`
- `#2552` — OPEN — `docs(security): external contributor and unsolicited paid-help response runbook`
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
| Runbook | `docs/security/external-contributor-runbook.md` |
| TRUST-ARCHITECTURE cross-ref | `docs/governance/TRUST-ARCHITECTURE.md` (one-line addition) |
| Plan review — Claude | `scripts/review/results/2026-04-29-plan-2552-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-29-plan-2552-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-29-plan-2552-gemini.md` |

---

## Deliverable

A `docs/security/external-contributor-runbook.md` file that covers all four external-interaction scenarios with decision criteria, response templates, and a lightweight collaborator/paid-pilot intake path, plus a one-line cross-reference in `docs/governance/TRUST-ARCHITECTURE.md`.

---

## Pseudocode

Trivial — see Files to Change. No algorithmic logic; this is a pure documentation artifact.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/security/external-contributor-runbook.md` | main runbook with decision tree + templates |
| Modify | `docs/governance/TRUST-ARCHITECTURE.md` | add one-line cross-reference under a new "External Interaction Policy" pointer |
| Update | `docs/plans/README.md` | add this plan to index (executor step) |

---

## Runbook document outline

The runbook must cover these four scenarios (from issue AC):

1. **Unsolicited paid-help offer** — e.g., `Baijack-star` on #2401. Decision criteria: is the account a known collaborator? If no: do NOT reply publicly, do NOT engage, use GitHub's "Hide comment" option or "Report" for spam. If yes (existing collaborator asking to be compensated): route to private channel, not public issue.

2. **Suspected spam / bot comment** — automated scraper / generic solicitation. Decision: hide immediately via GitHub UI, report if it recurs.

3. **Legitimate external contributor request** — someone with a genuine patch or proposal, but not a collaborator. Decision: route through a "Contributor Interest" template asking them to describe scope + sign off on the project's CLA/license posture. Do NOT grant `write` access until reviewed; use fork-and-PR path instead.

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
| `test_runbook_contains_templates` | templates section present | file content | "DECLINE_TEMPLATE" and "CONTRIBUTOR_INTEREST_TEMPLATE" strings present |
| `test_trust_architecture_crossref` | TRUST-ARCHITECTURE.md references the runbook | file content | `external-contributor-runbook` present in TRUST-ARCHITECTURE.md |

These are structural lint tests (`grep`-level), runnable as `pytest` with `pathlib` + `re`. Appropriate for a T1 documentation issue.

---

## Acceptance Criteria

- [ ] `docs/security/external-contributor-runbook.md` exists and covers all 4 scenarios (unsolicited paid-help, spam, legitimate contributor, paid-pilot intake)
- [ ] Runbook includes both `DECLINE_TEMPLATE` and `CONTRIBUTOR_INTEREST_TEMPLATE` copy-paste blocks
- [ ] Runbook references #2546 and #2401 as the triggering example (per issue AC)
- [ ] Runbook preserves public-repo security posture: no collaborator access without explicit owner approval
- [ ] `docs/governance/TRUST-ARCHITECTURE.md` has a one-line cross-reference to the runbook
- [ ] All 4 structural tests pass: `uv run pytest tests/security/test_runbook_external_contributor.py -v`
- [ ] No regression: `uv run pytest workspace-hub/tests/` passes

---

## Adversarial Review Summary

<!-- Filled in after Step 4 completes. Do not post to GitHub until this section is populated. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | — | — |
| Codex | — | — |
| Gemini | — | — |

**Overall result:** pending

---

## Risks and Open Questions

- **Risk:** Scenario 1 default (hide, don't reply) may be wrong if the external commenter has already been seen by others. Recommendation is hide-not-reply for the default case; explicit reply templates are provided for edge cases where engagement is warranted. Flag for user during approval.
- **Open:** Should the runbook live under `docs/security/` or `docs/ops/runbooks/`? The `docs/ops/` directory already has an `ollama-assessment.md` and `hermes-weekly-cross-machine-parity-checklist.md`, suggesting ops runbooks could go there. However, `docs/security/` is thematically correct. Recommend `docs/security/` for discoverability by anyone investigating the interaction-limit setup, but accept user redirect.
- **Open:** Does the paid-pilot intake path require a formal NDA template? Out of scope for this runbook — the runbook records the intake *requirements* (NDA/confidentiality acknowledgement, payment approval, etc.) but does not draft the NDA itself. Flag for follow-up if the user wants a template.

---

## Complexity: T1

Single new markdown file plus a one-line edit to an existing governance doc. No new modules, no tests with real logic, no config changes. The structural lint tests are included as good practice but are trivially passable on file creation.
