# Archived Skill: `iterative-plan-hardening-with-adversarial-waves`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/iterative-plan-hardening-with-adversarial-waves`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/iterative-plan-hardening-with-adversarial-waves`
Consolidation date: 2026-04-29

---

---
name: iterative-plan-hardening-with-adversarial-waves
description: Tighten a draft plan through repeated Codex/Gemini adversarial review waves without prematurely advancing it to plan-review.
version: 1.0.0
category: workspace-hub-learned
tags: [planning, adversarial-review, governance, iteration, workspace-hub]
---

# Iterative plan hardening with adversarial waves

Use when a plan survives initial drafting but repeated adversarial review keeps returning MAJOR. Especially useful for detector/contract plans where correctness depends on exact status semantics, source boundaries, scheduler behavior, and output contracts.

## When this fits
- The issue is reopened or preserved for re-file after earlier MAJOR reviews.
- You already have one or more concrete review artifacts from Codex/Gemini.
- The plan is still draft-only and must NOT move to `status:plan-review` yet.
- The productive path is iterative tightening, not implementation.

## Core loop

1. Read the latest review artifacts first.
- Prefer the newest Codex + Gemini files.
- Extract only the current blocker set; do not keep chasing already-fixed historical findings.

2. Patch the plan, not just the summary.
For every blocker, reconcile all affected sections together:
- problem statement
- deliverable
- candidate record shape / contracts
- pseudocode
- scheduled task contract
- TDD test list
- manual verification / approval gate
- acceptance criteria
- adversarial review summary

3. Maintain one authoritative contract per concept.
Reviewers keep finding MAJOR when the same concept is defined differently in multiple sections. Unify these explicitly:
- status enum
- source dedupe policy
- cross-domain coverage policy
- exit code contract
- publication-mode activation
- locking strategy
- field derivation / mapping contract
- output-vs-summary-only behavior

4. Separate surfaces explicitly.
For detector/data plans, distinguish:
- source-side candidate inputs
- coverage-providing artifacts
- reporting/context aids
Do not blur them in one mixed list.

5. Treat MAJOR findings as governance state, not just prose feedback.
- Keep the issue OPEN but draft-only.
- Do not add `status:plan-review` while MAJOR remains.
- Post short GitHub comments summarizing the latest blocker cluster and linking the fresh review artifacts.
- If 3+ consecutive waves return MAJOR, explicitly surface the sustained-MAJOR loop in the plan/governance notes instead of pretending the next wave is routine.
- Define a termination/escalation rule: keep patching concrete contradictions or missing executable contract details; if remaining MAJOR findings are demonstrably false positives, provider-unavailable/retrieval failures, or minority dissent after valid evidence, stop the churn, document the dissent with artifact paths, and route to explicit user decision. Do not self-approve.

6. Rerun review immediately after each patch wave.
Do not leave the plan claiming blockers are fixed without a fresh wave.
Suggested naming pattern:
- `scripts/review/results/YYYY-MM-DD-vN-plan-<issue>-codex.md`
- `scripts/review/results/YYYY-MM-DD-vN-plan-<issue>-gemini.md`

7. Narrow the blocker set deliberately.
A good pass shrinks the blocker cluster. Update the plan’s review summary to reflect the newest live blockers only.

## High-value hardening patterns learned

### A. Status contracts must be single-source-of-truth
If a record/status enum exists, define it once and make every later section conform.
Typical failure mode:
- one section says a record is `gap`
- another says it is `domain-mismatch`
- pseudocode produces both
Fix by stating one canonical enum and whether a condition is:
- a terminal source-record status, or
- a summary-only diagnostic

### B. Summary-only vs YAML-emitted rows must be explicit
For edge cases like:
- wrong-domain wiki match
- duplicate wiki `doc_key`
- unresolved identity
state whether they:
- produce per-domain YAML rows, or
- appear only in `_summary.md`
Do not leave this to inference from pseudocode.

### C. Scheduler contracts need operational safety, not just commands
If the plan includes scheduled publication, explicitly define:
- required-input prechecks
- clean-worktree precondition
- lock model
- publication-mode activation path
- degraded-run publication behavior
- exit codes
- whether logs/write-side artifacts live outside repo cleanliness concerns or are guaranteed gitignored
If multiple machines are listed, say whether they are:
- one publisher + one observer/failover, or
- both publishers
A local `flock` is not a fleet-wide single-publisher guarantee.

Important live finding from #2392:
- shell command structure matters. A command shaped like `... ; rc=$?; git add ...` can still dirty the checkout after a fail-closed run. Gate staging/commit/push behind explicit `rc` checks so failure paths do not mutate repo state.
- if scheduled publication is supposed to be single-publisher, do not describe it that way unless the mechanism is actually cross-machine. A checkout-local lock only prevents same-host concurrency.

### D. Config-driven plans need normative config schema
When the plan references config keys like domain maps or rules, define:
- key names
- precedence order
- collision/tie behavior
- invalid-config behavior
Otherwise reviewers correctly reject the plan as under-specified.

### E. Dedupe policy must specify field fill behavior
If records are deduplicated across multiple sources, define:
- dedupe key
- source precedence order
- whether higher-precedence wins even if empty, or first-non-empty by precedence
- conflict handling for domain/discipline
Without this, the same plan can produce different implementations.

### G. Attested evidence must cover required-input claims
When a plan's approval gate depends on a required file or live repo fact, make sure the fact is either:
- covered by the attested evidence block, or
- moved into an explicit precheck/manual verification step without pretending the plan itself already proves it.

Live finding from #2392:
- reviewers will correctly keep returning MAJOR if a required runtime input like `data/document-index/index.jsonl` is central to the plan but not actually attested in the evidence block.
- remove unneeded live-state claims if they are not attested and not load-bearing. Unverified noise creates avoidable MAJOR findings.

### H. Domain contracts must specify whether one source can map to multiple domains
For detector/coverage plans, decide explicitly whether:
- one canonical source belongs to exactly one output domain, or
- one canonical source may emit multiple domain-scoped candidates.

Do not dedupe by `doc_key` alone unless the plan also states and justifies a single-domain invariant. Otherwise reviewers will correctly flag silent suppression of real per-domain gaps.
### I. Keep review-process narration out of the implementation contract

A repeated MAJOR source in later review waves is stale process text embedded inside the plan body itself.

Avoid putting these in the plan body as if they were part of the deliverable:
- "fresh rerun still required"
- "latest verdicts were X/Y"
- "prepared for another approval pass"
- review-history ledgers that will become stale immediately
- success criteria like "the plan remains draft"

Preferred pattern:
- keep implementation contract sections clean: resource intel, deliverable, files, tests, acceptance, risks
- if review status must be mentioned, use a minimal neutral note that does not assert transient process state
- let `scripts/review/results/*` hold the real provider history
- do not cite empty or placeholder review artifacts in the plan header/body as if they were substantive evidence; reviewers will correctly treat that as misleading governance state and return MAJOR
- if the current review wave is still in progress, leave that state out of the plan contract entirely rather than narrating it inside the plan

Related approval rule:
- acceptance criteria should describe what makes the plan approval-ready, not require that it stay in `draft`.

### I1. Separate governance/pre-approval requirements from execution/TDD sections

A high-value lesson from repeated #2460 contract-plan reruns: reviewers will keep returning MAJOR if governance-state cleanup is mixed into execution-path sections.

Do NOT put approval/governance requirements inside these sections as if they were implementation work:
- `Pseudocode` / `implement_with_tdd()`
- `validate_contract_docs()`
- `Files to Change`
- `TDD Test List`
- execution-focused `Acceptance Criteria`

Typical anti-patterns:
- TDD rows that expect `plan text` as input
- validation assertions about stale GitHub labels or approval markers
- acceptance criteria that require removing `status:plan-approved`
- pseudo file rows like "Governance cleanup before any future approval reuse"
- implementation steps that tell the executor to handle a non-approved state even though execution requires approval

Preferred pattern:
- keep execution/TDD sections about final deliverables only (contract doc, checklist doc, docs index link, stale-reference guard, etc.)
- create a separate section such as `## Governance Precondition Before Any Future Approval Reuse`
- put stale approval-surface cleanup there, including label/marker cleanup or immutable revision-binding rules
- if README/index sync is only hygiene, say explicitly that it is secondary to the real approval gates

Why this matters:
- execution-phase agents cannot satisfy pre-approval governance requirements
- tests should validate deliverables, not transient planning text or workflow state
- mixing these concerns creates logical paradoxes that reviewers correctly flag as MAJOR

### I2. For stale approval-surface evidence, make the evidence self-contained

When a plan claims a live approval label or local approval marker is stale for the current draft revision, make that claim self-contained in the evidence block.

Include concrete evidence such as:
- live label command result excerpt (`gh issue view ... labels/state`)
- local marker contents
- local marker mtime
- current plan mtime
- latest review-artifact verdict tuple for the current draft lineage

Do not rely on reviewers being able to re-open local files in their environment. A provider may have sandbox limits or quota limits and still demand affirmative verification.

### I3. If revision-binding is allowed, require an immutable binding contract

Do not say merely "revision-bind approval".
Require the binding to name:
- exact approved plan file path
- exact approved plan git commit SHA or SHA256 content hash
- exact approved review-artifact paths plus provider verdicts
- exact approval-storage surface used

Otherwise reviewers will correctly say the stale-approval-reuse hazard is reduced but not closed.

### I2. Reconcile review-artifact paths and wave state everywhere after each rerun

A common late-wave failure is partial state refresh: one section points at the newest timestamped review artifacts while another still references an older wave or a placeholder filename.

After every rerun wave, reconcile all of these together:
- front-matter `Review artifacts:` line
- Artifact Map review-artifact rows
- Acceptance Criteria review-artifact references
- Adversarial Review Summary wave number and verdict text

Rules:
- use one canonical timestamped artifact set per wave
- do not leave `YYYYMMDD...` placeholders once real artifacts exist
- do not mix Wave N filenames in one section with Wave N-1 filenames in another
- if the current draft already incorporates a fix, remove future-tense bullets like "will reconcile in next revision"

Typical failure signals:
- Claude/Codex return MAJOR because the plan cites two different review-artifact timestamps
- the plan body says a reconciliation is still pending even though the summary table already shows it as done
- acceptance criteria mention stale artifact files after a newer rerun is already on disk

### I3. Force summary tables to match the body after every review wave

Later MAJOR reviews often come from summary drift rather than real design defects.

High-risk sections to reconcile after each patch wave:
- `Path Decision Summary`
- `Files to Change`
- `TDD Test List`
- `Acceptance Criteria`
- `Adversarial Review Summary`

Required rule:
- if the body changes a preferred branch, default path, or skip strategy, immediately update every summary table that restates that decision

Examples from live use:
- Cluster A body changed from default workflow edit to conditional/plugin-diagnosis-first, but the summary table still advertised the old default
- Cluster C body changed from file-wide skip to class-surgical skip, but the summary table still described module-level/file-wide skip
- TDD rows were revised, but the review summary still described them as if the old checks remained

### I4. Replace weak `collect-only` proofs with runtime proofs when the defect is fixture/setup visibility

For pytest-related plans, `--collect-only` is not enough when the real failure happens during fixture resolution or test setup.

Rule:
- if the defect is about missing fixtures, setup wiring, or class-vs-module fixture scope, require at least one runtime verification from each affected class/path
- use `collect-only` only to prove collection safety or import safety, not fixture correctness by itself

Example pattern:
- one runtime check for the still-supported class/test that should PASS
- one runtime check for the legacy or deferred class/test that should SKIP cleanly (or PASS after repoint), but must not error on fixture/setup

### I5. Prefer job-scoped CI verification over global log grep for matrix workflows

For GitHub Actions matrix jobs, global `gh run view --log | grep ...` checks are fragile because logs interleave multiple jobs and can create false positives/negatives.

Rule:
- when a plan's proof depends on step order or step success in one matrix cell, use job-scoped evidence
- prefer `gh run view --json jobs` and inspect the specific job's `steps` array
- only use global logs as a fallback when job-scoped data is unavailable, and state that fallback explicitly

Use this especially for:
- proving one step occurs before another
- proving a specific matrix cell reached a named step
- proving a specific step had `conclusion=success`

### I6. Add pre-edit failing proofs for workflow-order fixes

When a plan changes CI step order, later reviewers may return MAJOR if the plan only specifies the post-edit assertion.

Rule:
- include both:
  - a pre-edit assertion proving the current order is wrong
  - a post-edit assertion proving the new order is correct

This keeps the workflow fix aligned with TDD discipline rather than relying only on narrative evidence.

### I7. Keep cross-repo execution contracts explicit inside the plan

For workspace-hub plans that modify another repo, reviewers will keep returning MAJOR unless the plan states exactly how execution crosses repo boundaries.

Required contract fields:
- target repo for implementation
- target implementation branch naming convention
- whether implementation rebases onto current target-repo `main` or another landed branch
- whether workspace-hub planning commits are separate from target-repo implementation commits
- PR/merge sequencing when the follow-on depends on an earlier landed issue in the target repo

Do not leave this implicit just because the issue originated in workspace-hub.
A plan that is otherwise technically correct can still be non-executable if the branch/merge path is ambiguous.

### I8. Investigative default branches must still be executable, not just diagnostic

A repeated MAJOR pattern in late review waves is a plan choosing an investigative branch as the default (for example plugin-loading diagnosis) without saying what concrete files/settings will be inspected, what fixes are allowed, and when to stop and fall back.

If a preferred branch starts with "diagnose first", also specify:
- exact config surfaces to inspect first
- allowed remediation actions inside current issue scope
- explicit stop condition where implementation must fall back or re-plan
- acceptance condition for the investigative branch itself

Otherwise the branch is only a thought, not an executable plan.

### I9. Deliverable text must be no weaker than acceptance criteria

Another recurring late-wave failure: the Deliverable section allows a softer outcome (for example "reduced residual failures") while Acceptance Criteria require full elimination of named failure signatures.

Rule:
- if Acceptance says the exact blockers must disappear, Deliverable must say the same
- if Deliverable allows partial success, Acceptance must explicitly allow that same partial outcome
- do not mix "green or reduced" wording in Deliverable with strict named-signature removal in Acceptance

When these differ, reviewers correctly return MAJOR because the plan has two success definitions.

### I10. Evidence-derived default branches should use provenance checks, not stale local repro assumptions

For CI/test plans, local reproductions are often useful but can become misleading if they were run in a stale or differently-provisioned environment.

Pattern:
- establish CI-log evidence first
- add a local provenance step proving whether the local env actually matches the CI install path
- only then choose between install-layer fixes vs plugin-loading/configuration fixes

If local provenance shows the package imports successfully under the CI-style install path, do not keep treating a missing local fixture repro as authoritative. Shift the default branch to plugin-loading/config diagnosis unless CI logs prove package absence.

### I11. Replace shell-escape-sensitive path checks with Python when filenames contain backslashes

When a plan's verification depends on detecting literal backslashes in git paths, shell and grep escaping are too error-prone.

Observed failure mode:
- reviewers keep returning MAJOR because commands like `grep -F '\\'` or `grep -c '\\\\'` can be read/implemented inconsistently and produce false clean/dirty results.

Rule:
- prefer `uv run --no-project python` one-liners for path-character checks
- explicitly count `"\\" in path` over `git ls-tree --name-only` or `git ls-files`
- use git/blob assertions for preservation checks rather than shell globs

This is much more robust for pathological filenames and makes the gate auditable.

### I12. Use job-scoped CI verification for matrix workflows, and verify fail-fast assumptions explicitly

For matrix GitHub Actions plans, global log grep is fragile and reviewers will often ask whether another matrix leg can cancel the target proof leg.

Rule:
- verify whether `strategy.fail-fast: false` is already set; if not, decide whether it must enter scope
- prefer job-scoped `gh run view --json jobs` checks over global `--log` scans
- tie proof to a specific job name and step array rather than mixed matrix logs
- if using global logs as fallback, document that fallback explicitly and why it is safe

This is especially important when the close gate depends on one named matrix leg completing a specific step.

### I13. Narrow acceptance to the CI lane actually evidenced

A recurring late-wave MAJOR source is overclaiming across the whole matrix or workflow when the evidence only covers one job.

Rule:
- if logs/evidence only show one named job or one Python version lane, make that the primary acceptance lane
- mention sibling lanes only as conditional follow-on scope when the same failure signatures are evidenced there too
- do not claim repo-wide or workflow-wide resolution from one job's proof

This is especially important for follow-up issues created after a previous fix exposed a smaller residual failure set.

### I14. If default remediation is a skip/defer path, require tracker-first ordering

When a plan's default safe path is to skip or defer a legacy-only test surface, reviewers will keep returning MAJOR unless the plan makes the accountability step happen before the code edit.

Rule:
- create the follow-up tracker issue before any skip-based implementation change
- make that ordering explicit in the steps, not just in notes or risks
- state what future re-enable/repoint decision the tracker owns

This prevents "silent burial" plans where a skip lands without durable follow-through.

### I15. Use line-level evidence to justify legacy-only skip boundaries

If a plan proposes skipping a whole file or class rather than repointing it immediately, support that with direct source evidence.

Good evidence pattern:
- identify the import path the test expects
- identify the instantiated class/module in setup
- identify repeated calls/patches against the legacy-only method or symbol
- show the modern implementation path separately

If the file is entirely bound to the legacy path/method, say so plainly. That turns a contested skip into an evidence-backed temporary boundary rather than a convenience shortcut.

### I16. Make adjacent fix clusters conditional when one branch can eliminate another failure surface

Reviewers often flag plans that treat every surfaced failure as mandatory work even when one chosen branch can remove the need for another branch.

Rule:
- if Cluster B only matters when Cluster C remains active, say B is conditional after C
- update Deliverable, Path Decision Summary, Files to Change, TDD, and Acceptance together to reflect that conditionality
- do not leave all clusters sounding mandatory if the preferred branch intentionally defers one surface

This keeps the plan executable and prevents reviewers from reading it as unnecessary scope expansion.

### I17. For cross-repo execution plans, make delivery contract mandatory, not advisory

A recurring late-wave MAJOR source is a technically solid fix plan whose repo-delivery path is only implied.

Required contract fields:
- target implementation repo
- mandatory execution branch name/pattern
- PR target branch
- upstream-push vs fork fallback
- separation between workspace-hub planning commits and target-repo implementation commits
- rebase/conflict behavior when the plan depends on already-landed upstream state

Do not say a branch name is merely "recommended" if the executor really needs one deterministic path.
Reviewers will keep returning MAJOR until the delivery path is executable end-to-end.

### I18. Use signature-based close gates when full-suite green is out of scope

Another repeated late-wave failure pattern is mixing:
- scoped blocker removal as the real issue goal, and
- full-suite success as the written pass/fail gate.

Rule:
- if unrelated failures are allowed to remain, the hard close gate must be signature-based
- named blocker signatures should disappear from targeted local checks plus the primary CI lane
- the full-suite command may still run, but only as observational audit unless the issue truly owns all remaining failures

Keep Deliverable, TDD, and Acceptance aligned:
- hard gate = disappearance of named blocker signatures
- full-suite run = audit surface for discovering unrelated residual failures

### I19. For grep-filtered pytest proofs, add `set -o pipefail` and capture logs

Reviewers correctly distrust plan commands like `pytest ... | grep ...` when shell failure handling is implicit.

Rule:
- use `set -o pipefail` before grep-filtered test commands
- prefer `2>&1 | tee /tmp/<name>.log | grep ...` so both exit behavior and evidence capture are explicit
- do not use `|| true` on the primary RED proof unless the plan explicitly explains why non-failing command status is intentional

This prevents false-green plan logic when pytest crashes before emitting the expected text.

### I20. Bound exploratory repoint branches to enumerated candidate paths

A plan that says "discover the new module" without naming where to look is still not executable.

Rule:
- if a repoint/relink path is optional, enumerate the exact candidate directories/modules to inspect
- define the search surface as a finite list of paths/patterns
- if no hit is found within that exact surface, state the fallback outcome explicitly (for example: repoint is off the table for this plan, use skip/defer path instead)

This turns a fuzzy discovery step into a deterministic gate.

### I21. Skip/defer governance should prefer tracker-first, but must not create impossible execution deadlocks

Tracker-first ordering is valuable, but reviewers may flag over-coupled governance when issue-creation capability becomes a hard non-code blocker with no bounded fallback.

Rule:
- prefer creating the follow-up tracker before skip-based edits
- verify repo read/write capability concretely before depending on tracker creation
- if tracker creation is temporarily unavailable, define the bounded fallback explicitly:
  - keep the skip reason/comment referencing the parent issue
  - document the blocker immediately on the governing issue
  - do not silently merge/close as though the tracker existed

This preserves accountability without making the plan non-executable under temporary GitHub capability limits.

### I22. Separate technical acceptance from workflow gates

Late MAJOR churn often comes from mixing two different ideas in one acceptance checklist:
- technical deliverable proof
- workflow/admin preconditions

Rule:
- keep `Acceptance Criteria` focused on observable issue outcomes: named failure signatures removed, bounded reruns clean, target CI lane verified, etc.
- move process items into a separate section such as `Workflow Gates` or `Approval Gates`
- typical workflow-only items to separate:
  - `status:plan-review` / `status:plan-approved`
  - `.planning/plan-approved/<issue>.md` marker
  - review-wave convergence requirement
  - README/index consolidation ownership
  - user approval / no-self-approval reminders

This reduces reviewer confusion about what proves the issue is technically solved versus what merely authorizes execution.

### I23. If the default branch is a stabilization skip, say whether closure is allowed on skip-only remediation

A recurring late-wave MAJOR source is a plan that says a skip/defer branch is the default implementation path while acceptance criteria forbid closure unless replacement supported-path coverage exists.

Rule:
- decide explicitly whether the issue is:
  - a stabilization-only issue that may close on tracked skip/defer, or
  - a closure-requires-replacement-coverage issue
- state that same rule consistently in:
  - Deliverable
  - Path Decision Summary
  - pseudocode stop/continue rules
  - Acceptance Criteria
- if closure requires replacement supported-path automated evidence, say the default skip path may stabilize legacy failures but cannot close the issue by itself
- if no supported path is found, say whether execution stops and returns to planning, or whether the issue intentionally closes as tracked deferral

Do not leave the plan saying both at once.

### I24. Temporary diagnostic CI changes must be explicitly non-mergeable

When a plan allows a temporary diagnostic workflow/job edit to learn something about CI state, reviewers will keep returning MAJOR unless the plan states what happens to that diagnostic change.

Rule:
- mark any temporary diagnostic CI edit as NON-MERGEABLE
- require its deciding evidence to be copied into execution notes or PR body
- require the diagnostic change/commit to be removed before the final PR/merge
- if the diagnostic still leaves branch selection ambiguous, define a hard stop or follow-up rather than allowing a prolonged debug loop

This prevents audit drift where a repo accumulates debug-only workflow noise inside the implementation branch.

### I25. Investigative branches need a bounded exit rule, not just a list of surfaces

A plan that says "inspect these 4 surfaces" is still under-specified if it does not say what happens after those inspections.

Rule:
- for investigate-first branches, define an exit rule such as:
  - inspect named surfaces
  - use one local provenance step
  - permit at most one diagnostic CI run if still ambiguous
  - then either apply one bounded in-scope fix, or stop and open a follow-up / return to planning
- do not allow the issue to linger in open-ended investigation inside the implementation plan

This converts diagnostic intent into an actually executable branch.

### J. Machine-checkable policy plans need one canonical schema artifact
When a plan introduces status/compliance/budget fields, reviewers keep returning MAJOR unless the plan names:
- one authoritative schema-bearing artifact
- exact required fields
- allowed enum values
- nullability / no-history behavior
- whether other artifacts derive from that schema or merely mirror it

Do not spread the contract vaguely across "JSON/scorecard outputs" or similar plural wording.
Choose one canonical JSON artifact and state the derivative relationship explicitly.

### J1. Keep cron-owned audit entrypoints separate from manual closeout tools

A lesson from #2488 skill-housekeeping planning: reviewers will reject a plan that lets a scheduled/read-only audit script also write tracked closeout docs via a mode flag. A mode flag alone is not a sufficient isolation story for cron-owned paths.

Rule:
- keep the scheduled/default audit entrypoint local-only, read-only, and backward-compatible with existing wrapper flags
- put tracked report rendering, terminal disposition validation, and human closeout gates in a separate manual script/module
- add wrapper tests proving the cron command parses unchanged and never invokes manual closeout behavior
- make manual closeout hard-fail on untrusted git inventory, sparse checkout, or partial manifests even when the weekly audit merely warns

### J2. For ignored-file promotion plans, require force-add evidence or a full re-include cascade

If a file is untracked because a parent directory is ignored, a single `!path/to/file` `.gitignore` negation usually does not work. Git cannot re-include a file while its parent directory remains excluded.

Rule:
- prefer targeted `git add -f <path>` for approved one-off promotions from ignored namespaces
- record the ignore rule/line and final `git ls-files` evidence in the disposition ledger
- do not propose broad `.gitignore` relaxations for private/vendor/generated namespaces inside a reconciliation plan
- only allow `.gitignore` changes if the plan explicitly specifies a full multi-line re-include cascade and that change is separately reviewed

### J3. Review/triage status is not a terminal disposition

For filesystem-only reconciliation, a path being "reviewed" is not enough to remove loss risk. Reviewers will correctly flag plans where a reviewed hash suppresses unresolved inventory findings.

Rule:
- non-terminal states may annotate a finding, but must still appear as unresolved local inventory
- terminal states need explicit semantics such as promoted/tracked, consolidated into a tracked path, archived intentionally, deleted as junk, or ignored transient with rationale
- terminal states should include pre-action content hash, final path/status, scan attestation, and any force-add/user-authorization evidence needed for ignored or personal paths
- personal/private ignored paths need an explicit authorization field; if unavailable, the plan must choose archive/delete/ignore with rationale rather than promotion

### J4. Align active-loss filters with the issue definition, not legacy helper constants

When extending an existing detector, legacy constants like `EXCLUDED_DIRS` may serve an older duplicate/collision pipeline and should not be silently reused for a new loss-risk signal.

Rule:
- define the new active-loss filter by exact path segments and state how it differs from legacy filters
- if an existing policy already defines archive aliases (for example `category_alias_families.archive.aliases`), either consume that policy surface or add a test proving the new filter's alias set cannot drift from it
- avoid adding compatibility-only diagnostics as permanent recurring schema fields unless there is a named consumer/follow-up issue; otherwise keep them local to tests or issue-specific evidence
- for legacy duplicate/collision behavior, assert delta against a pre-change baseline rather than absolute zero if pre-existing findings may remain
- if `_core`/`_internal` are informational namespaces, decide explicitly whether that is only a metadata flag or whether it suppresses active loss-risk; avoid reusing an `informational` field name ambiguously

### J5. Do not overbuild recurring audit plans with manual-closeout machinery

A lesson from #2488 skill-housekeeping planning: repeated MAJOR reviews came from mixing a small recurring audit extension with a broad manual reconciliation framework, disposition ledgers, trust-attestation schemas, issue-body drift schemas, and custom exit-code contracts.

Rule:
- keep the recurring audit change as small as possible: deterministic local inventory, stable JSON/Markdown fields, baseline compatibility, and wrapper safety
- move one-time disposition/closeout into a bounded issue-specific helper only when the issue genuinely needs it
- make the helper's CLI invokable and tested end-to-end, but do not route cron through it
- do not let a terminal disposition hide a live filesystem-only path from the recurring inventory; recurring audit remains filesystem truth, closeout report remains human disposition truth
- for ignored/private paths, choose a default non-promotion disposition unless the user separately authorizes tracking after scan/redaction

### J6. Match policy schema shape exactly; do not invent dotted pseudo-paths

Reviewers will reject plans that describe config keys in a shape the actual YAML does not use.

Rule:
- inspect the real policy shape before naming keys; if `weekly_summary_sections` is a list of objects with `id`, write "`weekly_summary_sections` entry `id: filesystem_only_inventory`", not `weekly_summary_sections.filesystem_only_inventory`
- distinguish a flat YAML key such as `v2.rules: {"family.rule-id": ...}` from nested YAML
- add cross-key tests that reflect the real structure, not an invented shorthand
- if output order is intentionally canonical/literal, call it that; do not label it "policy-driven" unless tests prove the renderer consumes policy order

### J7. Approval-gate review evidence needs a concrete artifact-production path

A plan can be technically sound but still fail review if it requires timestamped, SHA-bound review artifacts without saying how those artifacts are produced from existing fanout tooling.

Rule:
- do not require changes to the review fanout script unless the issue owns that tool
- instead, define a gate-runner copy step: copy latest non-empty fanout/fallback stdout into timestamped immutable files and prepend `Reviewed-Commit:` plus `Plan-SHA256:` metadata
- define unavailable-provider artifacts explicitly: attempted command, stdout/stderr byte counts, raw-error path if present, and the same reviewed-commit/hash metadata
- if provider CLI output is empty or sandbox-broken, record it as provider infrastructure state and use the repo review policy to decide whether it blocks the gate
- never cite mutable/empty review files as if they were approval evidence

### J8. Review-artifact metadata contracts must bind producer input, metadata, and parser authority

When hardening a plan that changes review-artifact provenance or stale-SHA detection, reviewers will keep returning MAJOR unless the plan defines the whole evidence chain, not just a parser rule.

Rule:
- require a strict metadata header at byte zero; do not recover machine trust from quoted/fenced body text or body `## Verdict` sections
- require machine fields such as `Issue`, `Plan-Path`, `Provider`, `Perspective`, `Verdict`, `Plan-SHA256`, `Plan-Commit`, `Reviewed-Revision`, and `Reviewed-At`
- bind provider input and metadata to the same immutable plan snapshot; read the plan once, hash those bytes, and feed every provider from those same bytes
- emit a real git commit SHA only when the reviewed snapshot equals the committed plan blob; otherwise use an explicit `WORKTREE:<plan_sha256>` draft sentinel
- treat `WORKTREE:*` artifacts as diagnostic only, not clean Lane A/B approval evidence
- cover every producer path that can create plan-review artifacts, including fanout success/failure stubs and adjacent submit-wrapper/cross-review failure paths, or explicitly exclude those paths from ingestion
- preserve raw provider stdout/stderr after the metadata header when raw output is part of the evidentiary contract
- make provider CLI trust/sandbox flags concrete and testable; avoid vague wording like “set appropriate trust flags”

Typical tests:
- quoted/body `Plan-SHA256` ignored
- missing header `Verdict` is metadata-incomplete
- malformed timestamp and abbreviated commit SHA rejected
- provider/perspective mismatch is untrusted
- duplicate current artifacts with conflicting verdict/status/SHA block clean evidence
- fanout metadata SHA matches the exact bytes sent to each provider

### J9. Separate draft-content blockers from promotion/retrievability blockers

When iteratively hardening a local draft, adversarial reviewers may return MAJOR for two different classes of issues:
- true plan-content defects that must be patched before the next rerun
- promotion/readiness defects such as missing peer-provider artifacts, local artifacts not yet committed to `main`, or provider sandbox failures (`bwrap`/network/retrieval errors) that prevent independent verification

Rule:
- patch true content defects immediately
- do not keep rewriting the implementation contract merely to satisfy a reviewer that cannot retrieve local files if the current run used the exact inline artifact
- record retrieval failures as environment/review-infrastructure limitations, not as design facts
- keep the issue `draft` / not `status:plan-review` until required provider artifacts exist and are committed/retrievable
- if the plan cites live repo facts, either include self-contained attested evidence for those facts or move them to explicit prechecks/manual verification steps
- missing Claude/Gemini/Codex artifacts are gate blockers for promotion, but not necessarily content blockers during a targeted single-provider hardening loop

This prevents churn where the plan is repeatedly rewritten for non-content findings while still preserving the hard gate that no issue advances without clean, retrievable review evidence.

### K. Runtime replacement plans need behavior-preservation proof, not just string-removal tests
If a plan changes launcher/runtime forms (for example `python3` -> `uv run --no-project python`), tests that only prove the old string disappeared are insufficient.
Also define at least one check that the new invocation form is valid for the named callsites, based on one or more of:
- file-local runtime contract (standalone uv script header, stdlib-only launcher, external-tool bootstrap path)
- an execution/smoke expectation
- an explicit rule that the script must not depend on the project environment

Otherwise reviewers will correctly say the new command form is asserted rather than verified.

- Post a concise issue comment after each meaningful wave.
- Include the new artifact paths and current blocker cluster.
- Say explicitly whether the issue should remain draft-only.
- Keep the issue open, but do not advance labels prematurely.

## Commit hygiene
For docs-only revision waves:
- commit the plan file plus the new review artifacts together
- use a commit message like:
  - `docs(plans): continue #NNNN adversarial revision wave`
  - `docs(plans): add #NNNN v8 review wave`

## Stop condition
The plan is ready to advance only when:
- latest Codex/Gemini reviews are no worse than MINOR, and
- the blocker cluster is empty or explicitly downgraded, and
- the acceptance/verification sections no longer contradict the pseudocode/contracts.

Until then, keep it draft-only.
