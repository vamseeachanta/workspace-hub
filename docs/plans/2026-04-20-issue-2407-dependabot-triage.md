# Plan for #2407: Triage 29 Dependabot Vulnerabilities on aceengineer-website

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-20
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2407
> **Review artifacts:** (not yet dispatched — deferred per caller)

---

## Resource Intelligence Summary

### Existing repo code

- Found: `aceengineer-website/package.json` (root `vamseeachanta/aceengineer-website`) — only 7 dev-only deps: `clean-css`, `jest`, `jest-environment-jsdom`, `posthtml`, `posthtml-expressions`, `posthtml-include`, `purgecss`. **None** of the 29 reported vulnerable packages appear as direct dependencies.
- Found: `aceengineer-website/package-lock.json` — the only lockfile currently tracked in `main` per `gh api .../git/trees/main?recursive=1`.
- Gap/anomaly: all 29 dependabot alerts report `dependency.manifest_path = "ref/py_react_sql/client/yarn.lock"`. That subtree is **no longer present in the current `main` tree** (verified via `git/trees/main?recursive=1` — zero entries matching `^ref/`). It was deleted in commit `06f38714 "refactor: transform to static site with PostHTML partials"`. The alerts are therefore pointing at an orphan yarn.lock from repo history.

### Standards

Not applicable — supply-chain / marketing-site concern, no engineering-calculation standards.

### Documents consulted

- `docs/gtm/gtm-plan-30day.md` — Week-3 cold-email campaign drives prospects to aceengineer.com; vulnerable supply chain is a reputational risk even if not technically exploitable.
- `docs/plans/2026-04-19-issue-2346-prospect-data-pipeline.md` row 243 — reaffirms `aceengineer-website/` is a nested separate git repo requiring two distinct pushes (workspace-hub + aceengineer-website).
- `docs/plans/2026-04-20-issue-2391-sitemap-404-fix.md` — precedent for cross-repo plan discipline (plan in workspace-hub, fix in aceengineer-website).
- Issue #2407 body — breaks the 29 vulns down to 1 critical / 15 high / 12 medium / 1 low, flags campaign timing.

### Gaps identified

- No prior triage artifact for aceengineer-website supply chain exists in `docs/security/` — directory itself does not exist; plan will create it.
- No lockfile-audit script lives in the repo; triage will be manual (one-time, 29 rows).
- Commit `06f38714` removed the `ref/py_react_sql/` tree but dependabot has not dismissed the alerts — dismissal pathway (manual vs auto) must be decided during triage.

### Evidence (embedded verification)

**Issue status** (verified 2026-04-20 via `gh issue view 2407`):
- `#2407` — OPEN — "sec(aceengineer-website): triage 29 dependabot vulns — 1 critical, 15 high"; labels: `priority:high`, `cat:infrastructure`, `domain:gtm`.

**Dependabot alert totals** (`gh api repos/vamseeachanta/aceengineer-website/dependabot/alerts?state=open --paginate | jq 'length'`): **29** — matches issue body.

**Severity distribution** (`jq '[.[].security_advisory.severity] | group_by(.) | map({k:.[0], n:length})'`):
- critical: 1
- high: 15
- medium: 12
- low: 1

**Manifest paths** (`jq '[.[].dependency.manifest_path] | unique'`):
- `ref/py_react_sql/client/yarn.lock` — **all 29 alerts** point at this single path.

**Current-tree check** (`gh api repos/vamseeachanta/aceengineer-website/git/trees/main?recursive=1 | jq -r '.tree[] | select(.path|test("^ref")) | .path'`): empty — `ref/` does not exist in `main`.

**Path removal commit** (`gh api ".../commits?path=ref/py_react_sql/client/yarn.lock&per_page=5"`):
- `06f38714` — refactor: transform to static site with PostHTML partials.
- `bff9969b` — Clean up reference files and add new project directories.

**Root package.json deps** (`gh api .../contents/package.json | base64 -d | jq '.dependencies,.devDependencies'`):
- dependencies: `{}` (empty)
- devDependencies: `clean-css`, `jest`, `jest-environment-jsdom`, `posthtml`, `posthtml-expressions`, `posthtml-include`, `purgecss`.

**Relationship field** (`jq '[.[].dependency.relationship] | unique'`): `["transitive"]` — all 29 are transitive, zero direct.

Source count: 5 (issue body + gh alerts API + gh contents API + gh git/trees API + gtm-plan-30day.md). ✓ ≥3.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-20-issue-2407-dependabot-triage.md` |
| Triage deliverable | `docs/security/aceengineer-website-vuln-triage-2026-04-20.md` |
| Index update | `docs/plans/README.md` (new row) |
| Follow-up fix-implementation issue | filed after triage (TBD number) — cross-references #2407 |
| Plan review — Claude/Codex/Gemini | deferred per caller instruction; would land at `scripts/review/results/2026-04-20-plan-2407-*.md` |

---

## Deliverable

A classified triage table `docs/security/aceengineer-website-vuln-triage-2026-04-20.md` will list each of the 29 open dependabot alerts with severity, GHSA ID, package, manifest_path, direct-vs-transitive, exploitability assessment in this app's usage context, recommended fix action, and estimated effort — plus a documented fix-cadence decision (single sweep PR vs staged by severity vs dismiss-with-rationale) and a filed follow-up implementation issue cross-referencing #2407.

---

## Pseudocode

Triage-document structure (one row per vuln, 29 rows total):

```
HEADER
  title: aceengineer-website dependabot triage — 2026-04-20
  scope: 29 open alerts (state=open) from gh api .../dependabot/alerts
  evidence snapshot: severity counts, manifest-path summary, current-tree status

SECTION 1 — SUMMARY FINDINGS
  - all 29 alerts target a single manifest: ref/py_react_sql/client/yarn.lock
  - that subtree is NOT in current main (deleted at commit 06f38714)
  - root package.json deps intersection with vuln list: empty
  - implication: runtime exposure on aceengineer.com is zero; reputational exposure
    is whatever survives in git history (dependabot reads default branch only,
    so history-only means dependabot should auto-dismiss once no lockfile path matches)

SECTION 2 — TRIAGE TABLE (29 rows)
  columns:
    | # | severity | GHSA | CVE (if any) | package | ecosystem | manifest_path
      | direct/transitive | vulnerable_range | first_patched
      | exploitability-in-this-app (enum: runtime / build / test / unused / orphan-path)
      | recommended-action (enum: upgrade / replace / remove-unused
        / dismiss-as-orphan-path / accept-risk-with-rationale)
      | effort (enum: S / M / L) | notes |

SECTION 3 — CRITICAL DEEP DIVE
  - GHSA-v62p-rq8g-8h59 pbkdf2 <= 3.1.2 — verify advisory summary,
    confirm transitive parent chain in the historical yarn.lock (read the
    file at commit 06f38714~1 via `gh api .../contents?ref=<sha>`),
    confirm orphan-path status, decide dismiss-as-orphan vs formal reinstate-and-patch.

SECTION 4 — HIGH-SEVERITY BATCH
  - 15 rows — same orphan-path disposition expected.
  - any row that turns out to NOT be orphan-path gets escalated.

SECTION 5 — FIX-CADENCE DECISION
  Decision tree:
    if ALL 29 orphan-path-confirmed:
      -> action = dismiss-with-rationale ("fixed in 06f38714 — path removed")
         via `gh api ... -X PATCH -f state=dismissed -f dismissed_reason=fix_started`
         (one-liner script operates on alert numbers 15-46)
    else:
      -> split: orphan-path rows dismissed;
         remaining rows staged by severity (critical immediate, high within 7 days,
         medium/low bundled in a single sweep PR)

SECTION 6 — FOLLOW-UP IMPLEMENTATION ISSUE
  - filed on `vamseeachanta/workspace-hub` (coordination) with body containing
    triage table link + fix cadence, and cross-ref to #2407.
  - if any rows require actual code/lockfile change, the fix lands on
    `vamseeachanta/aceengineer-website` per cross-repo discipline.
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/security/aceengineer-website-vuln-triage-2026-04-20.md` | triage deliverable (29-row classified table + decision) |
| Create | `docs/security/` (new directory) | first artifact under security governance |
| Update | `docs/plans/README.md` | add row for #2407 plan |
| File (GitHub) | follow-up implementation issue | references #2407; scope = execute fix-cadence decision |
| (No repo edits in `aceengineer-website` during triage itself) | — | triage is docs-only; any lockfile change is deferred to the follow-up fix issue |

---

## TDD Test List

Not applicable. Triage is a document deliverable with no executable code. The downstream fix-implementation plan (follow-up issue) will carry TDD coverage when it exists — e.g. post-fix `npm audit --production` return code, dependabot-alert-count regression check, build-green verification on `aceengineer-website`.

---

## Acceptance Criteria

- [ ] All 29 alerts enumerated in `docs/security/aceengineer-website-vuln-triage-2026-04-20.md` — one row each, keyed by alert `number` + `GHSA ID`.
- [ ] The 1 critical vuln (pbkdf2 GHSA-v62p-rq8g-8h59) has an explicit exploitability verdict (runtime / build / test / orphan-path) backed by evidence from the historical yarn.lock.
- [ ] Each of the 15 high-severity vulns has an explicit fix decision (upgrade / replace / dismiss-as-orphan / accept-risk).
- [ ] Fix-cadence decision documented (one-sweep PR vs staged vs dismiss-all) with rationale.
- [ ] Follow-up fix-implementation issue filed on `vamseeachanta/workspace-hub` cross-referencing #2407, with triage-doc link in body.
- [ ] `docs/plans/README.md` updated with #2407 row.
- [ ] Plan committed with conventional-commit message `docs(plans): #2407 draft — dependabot triage plan for aceengineer-website (29 vulns)` and pushed to `origin/main`.

---

## Adversarial Review Summary

Deferred per caller. Will populate after cross-review dispatch if the user requests.

---

## Risks and Open Questions

- **Risk (primary):** orphan-path hypothesis is wrong — if any file in current `aceengineer-website/main` still transitively requires `ref/py_react_sql/client/`, dismissal-as-orphan is incorrect. Triage step 1 must re-verify via `grep -r "py_react_sql" aceengineer-website/` against the checked-out `main` before recommending dismissal. If the hypothesis survives verification, dismissal is the cheapest correct disposition; if it fails, the 29 alerts revert to standard severity-staged triage.
- **Risk:** dependabot alerts for paths deleted from `main` may not auto-dismiss — alert lifecycle may require manual `gh api -X PATCH dependabot/alerts/N state=dismissed dismissed_reason=fix_started` per alert. Plan should budget ~30 minutes for the dismissal sweep if that path is chosen.
- **Risk:** some transitive vulns may require major-version bumps of direct deps — irrelevant under the orphan-path hypothesis but material if hypothesis is rejected and triage falls back to real remediation.
- **Risk:** Jest/build tooling vulns are often medium-severity but easy fixes — if any reappear in the current `package.json` + `package-lock.json` (not in this alert set but a near-future possibility), prioritize as quick-wins.
- **Risk:** GHSA data may overclaim severity — triage must note "verify exploitability" for the critical (pbkdf2) and for the highest-CVSS high (node-forge ×4, lodash/lodash.template ×2, picomatch, semver, serialize-javascript, path-to-regexp, minimatch ×3, flatted ×2), independently of the orphan-path finding, because the follow-up fix issue may inherit a subset of them if the orphan hypothesis is partially rejected.
- **Risk (cross-repo):** triage artifact lives in workspace-hub; any actual lockfile/package.json edits land on `aceengineer-website`. Two distinct pushes; Vercel auto-rebuild triggers on `aceengineer-website` push only; rollback is `git revert` on each repo independently.
- **Rollback:** triage deliverable is docs-only — `git revert` on workspace-hub; zero runtime impact, zero build-system impact, zero dependency-graph impact.
- **Open question:** should dismissal-as-orphan be batched via a scripted loop or a single GitHub-UI session? (Cheapest = scripted, least auditable = UI; resolved during triage by the operator.)
- **Open question:** does dependabot surface alerts on non-default branches or historical commits? (If yes, even path-deletion does not dismiss; only state=dismissed does. Plan treats this as the conservative default.)

---

## Complexity: T2

**T2** — 29 distinct alerts to classify with per-row exploitability judgment and evidence citation against a nested separate repo. No code changes in this plan itself, but the deliverable is substantive (triage table + fix-cadence decision + follow-up issue filing) and non-trivial — it is not a one-line doc edit. Downstream fix implementation is a separate plan with its own complexity classification once the triage conclusion is known.

