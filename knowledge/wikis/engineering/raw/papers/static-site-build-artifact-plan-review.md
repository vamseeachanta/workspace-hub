# Archived Skill: `static-site-build-artifact-plan-review`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/static-site-build-artifact-plan-review`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/static-site-build-artifact-plan-review`
Consolidation date: 2026-04-29

---

---
name: static-site-build-artifact-plan-review
description: Plan-review pattern for static-site fixes where the deployed artifact is generated from source files (e.g. sitemap/robots/static assets). Prevents review churn by separating durable regression checks from one-time migration verification and by validating built output, not just source files.
version: 1.0.0
---

# Static-site build-artifact plan review

Use when:
- a website repo serves generated `dist/` output from source files
- the planned change edits a source artifact like `sitemap.xml`, `robots.txt`, or other static content
- reviewers may challenge whether validating the source file alone is enough

## Problem this solves

A recurring review failure mode is drafting a plan that only verifies the source file after edit, while production actually serves a built/copied artifact from `dist/`.

Another recurring failure mode is mixing:
1. durable regression tests that should live forever, and
2. one-time migration verification steps that depend on pre-edit state.

This produced repeated `MAJOR` plan-review findings on #2357 even though the code change itself was tiny.

## Required planning pattern

### 1. Verify the production surface, not just the source file
If the site is deployed from built output:
- identify the build path explicitly (`build.js`, bundler, copy step, etc.)
- include validation of the built/deployed artifact (`dist/...`) in the plan
- do not stop at "edited source file looks right"

For sitemap-style changes, include all of:
- source file verification
- post-build `dist/...` verification
- if applicable, post-deploy HTTP verification

Example planning language:
- source: `aceengineer-website/sitemap.xml`
- built artifact: `aceengineer-website/dist/sitemap.xml`
- production URL: `https://www.example.com/sitemap.xml`

### 1A. Resolve source/generated/legacy HTML contracts explicitly
For generated static sites, do not assume the only non-source surface is root `*.html`.

Before a plan is approval-ready, classify **all** HTML surfaces:
- canonical source: e.g. `content/**/*.html` and shared partials
- generated deploy output: e.g. `dist/**/*.html`
- checked-in legacy/non-authoritative HTML outside both source and deploy output, e.g. root `*.html`, `blog/**`, `calculators/**`, `case-studies/**`, `demos/**`, `samples/**`, or other historical generated trees

Then state exactly which happens to legacy checked-in HTML:
- sync it during implementation, **or**
- declare it non-authoritative and update tests/docs/scans so it cannot create false failures or stale pass conditions.

Also inspect existing tests and docs for the old contract. If tests read root/legacy pages directly or assert old branding/content, the plan must include updating those tests. If README/deploy/architecture docs still describe root HTML as authoritative, include conditional docs updates when choosing the non-authoritative path.

### 1B. For brand/content cleanup, scan visible body labels too
When the task is brand identity, naming, or copy cleanup, do not limit scope to nav/footer/metadata/schema. Reviewers may find visible in-page labels that remain stale.

Approval-ready plans should specify the target contexts:
- visible chrome
- page titles
- consumer-facing body labels/headings/CTAs
- OG/Twitter metadata
- JSON-LD/schema identity fields
- built output equivalents

Use a precise allowlist for historical/legal prose so tests are not brittle, but do not exclude visible consumer-facing body labels by accident.

### 2. Split validation into two classes
Always separate:

#### A. Durable regression checks
These should keep running after the issue ships.
Examples:
- every parsed `<loc>` uses `https://www...`
- each `<url>` has exactly one `<loc>`
- no duplicate `<loc>` values
- expected key entries still exist
- build output matches normalized source expectations

#### B. One-time migration verification
These are specific to the current edit and depend on pre-edit state.
Examples:
- before/after row count preserved
- metadata unchanged row-for-row
- pre-edit vs post-edit comparison
- issue-body/path drift note recorded in closeout

Do not present one-time migration checks as if they are permanent Jest-style regression tests unless you define a stable fixture/baseline.

### 3. If a check depends on pre-edit state, specify the snapshot source
Never leave this vague.
Do not say only "compare before vs after".

Specify:
- how the pre-edit snapshot is captured
- where it lives temporarily
- which command performs the comparison
- where the evidence is reported

Best practice:
- capture the on-disk file before mutation during execution
- do not rely on `git show HEAD:path` unless the plan explicitly proves that is the correct baseline for the execution context
- record the comparison result in the implementation summary / issue comment

### 4. Resolve build-tool dependencies during planning, not during implementation
If validation requires a tool like `xmllint`:
- check availability during planning
- record the result in the plan's evidence section
- if unavailable, either choose an approved fallback now or stop and revise the plan

Do not leave "xmllint or some other validator" as an implementation-time choice if review is already demanding a deterministic gate.

### 5. Use XML-aware/structure-aware validation for structure claims
If the plan claims things like:
- each `<url>` has exactly one `<loc>`
- metadata unchanged row-for-row
- all locs are non-empty and canonical

prefer XML-aware parsing or clearly defined structured extraction rather than loose regex-only checks.

Regex is acceptable for narrow negative checks, but reviewers may return `MAJOR` if structure claims are backed only by fragile pattern matching.

### 6. Avoid brittle absolute snapshots unless the absolute value is itself the invariant
Reviewers pushed back on hard-coding a current count like `39` as an acceptance criterion.

Prefer:
- before/after count preserved for this execution diff
instead of:
- count must equal `39`

unless the absolute count is truly part of the requirement.

## Plan template snippet

Use this structure in plans for static-site source→build→deploy changes:

### Durable merge blockers
- source artifact content is normalized/correct
- built artifact exists and reflects the normalized source
- structural invariants pass (unique entries, canonical host, required entries present)
- deterministic validator passes (e.g. `xmllint --noout ...`)

### One-time execution verification
- pre-edit snapshot captured from on-disk file before mutation
- before/after count preserved
- before/after metadata comparison passes
- execution evidence recorded in issue/implementation summary

## Trigger phrases from reviewers that mean you should apply this skill
- "verify the built artifact, not just the source file"
- "before/after evidence is underspecified"
- "this is a one-time migration check, not a durable regression test"
- "hard-coded count is brittle"
- "structure claims need parser-based verification"

## Outcome goal
A plan should be approval-ready when it:
- proves the production-facing artifact path
- cleanly separates permanent regression tests from migration-only checks
- names exact validation tools and snapshot sources
- avoids brittle snapshot-only acceptance criteria
