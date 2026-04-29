# Repo Mission / Business Brain Review Exit Handoff

Generated: 2026-04-28T21:10:17-05:00

## Current state

- Current review file: `docs/BUSINESS_BRAIN.md`.
- User requested: create future GitHub issues, document state, and prepare to exit.
- Root workspace branch: `main`, tracking `origin/main`.
- `docs/BUSINESS_BRAIN.md` contains intended edits from the Business Brain review and should be committed with this handoff if not already committed.
- At handoff creation, several provider/quota report files and `.claude/state/*` files were also modified in the root checkout; do not stage them accidentally when committing Business Brain/handoff changes.
- Subrepo state checked at exit:
  - `sabithaandkrishnaestates`: clean but `main` is ahead of `origin/main` by 1 pre-existing commit.
  - `sd-work`: uncommitted mission edit in `.agent-os/product/mission.md`.
  - `seanation`: uncommitted mission edit in `.agent-os/product/mission.md`.
  - Other reviewed subrepos checked in this exit pass were clean at their current local HEADs.

## GitHub issues created during the review wave

- #2537 — investments sanity-check/migration/retirement: https://github.com/vamseeachanta/workspace-hub/issues/2537
- #2539 — rock-oil-field Tier-1 migration/archive: https://github.com/vamseeachanta/workspace-hub/issues/2539
- #2545 — saipem useful-information extraction/archive-retirement: https://github.com/vamseeachanta/workspace-hub/issues/2545
- #2547 — seanation client-information extraction/archive: https://github.com/vamseeachanta/workspace-hub/issues/2547
- #2548 — machine/software/auth inventory and OrcaFlex/AQWA dispatch to `licensed-win-1`: https://github.com/vamseeachanta/workspace-hub/issues/2548
- #2549 — periodic Business Brain refresh from completed repo work: https://github.com/vamseeachanta/workspace-hub/issues/2549
- #2553 — repository overview docs reconciliation after mission review: https://github.com/vamseeachanta/workspace-hub/issues/2553

## New future issue created at exit

### #2553 — `docs(repo-portfolio): reconcile repository overview docs after mission review`

Purpose: continue the next review/doc sync without duplicating #2533.

Minimum scope:
- Review/update `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md`.
- Review/update or mark historical `docs/reports/2026-04-21-repo-mission-revision-sequence.md`.
- Align stale overview/report content with the updated `docs/BUSINESS_BRAIN.md` classifications.
- Keep Business Brain archive/extraction candidates consistent: `investments`, `rock-oil-field`, `seanation`, `saipem`.
- Keep Hermes/`ace-linux-1` control-plane and `licensed-win-1` OrcaFlex/AQWA dispatch assumptions consistent with #2548.

## #2533 plan-review governance state

Issue: #2533 — https://github.com/vamseeachanta/workspace-hub/issues/2533

Audit results:
- Live issue is open with labels: `enhancement`, `priority:high`, `cat:documentation`, `domain:repo-organization`.
- No local approval marker exists at `.planning/plan-approved/2533.md`.
- `docs/plans/README.md` row currently says: `draft (rev-5)`.
- Latest valid provider review artifacts are rev-4; both Codex and Gemini returned MAJOR findings there.
- Rev-5 plan edits have been made according to the plan index, but no rev-5 review artifact directory/files exist yet.

Exit conclusion:
- #2533 is **not approval-ready**.
- Do **not** apply `status:plan-review` or `status:plan-approved` until a fresh rev-5 adversarial review produces no MAJOR/high findings.
- Do **not** begin implementation of #2533 until user approval after clean plan review.

## Active task carry-forward

- q2 — Revise #2533 plan if review returns MAJOR/high findings: still in progress until rev-5 is committed/pushed and fresh Codex/Gemini review is run.
- q3 — Post final plan-review update and apply `status:plan-review` if approval-ready: pending; blocked by missing rev-5 review.
- q4 — Verify/advance digitalmodel PR #539 / workspace-hub #2462 state: pending; #2462 remains open with `status:working` and `status:plan-approved`.

## Business Brain changes needing final user review

`docs/BUSINESS_BRAIN.md` now reflects:
- Only one confirmed paid Codex/OpenAI account at `$200/month`.
- Hermes on `ace-linux-1` as primary control plane.
- Machine inventory requirement for installed programs, licenses, provider auth, repo checkout/readiness, run commands, and safe dispatch surfaces.
- `licensed-win-1` as initial licensed engineering worker for OrcaFlex and AQWA runs dispatched from `ace-linux-1`.
- Provider auth policy: all AI providers should be authenticated on worker machines where practical while `ace-linux-1` remains control plane.
- Repository classification updates from the mission review wave.
- New Portfolio Refresh Obligation to periodically update Business Brain from completed repo work.

## Reviewed mission docs and user decisions

Reviewed/no-change or changed during this wave:
- `docs/plans/2026-04-27-issue-2533-repo-portfolio-mission-objective-review.md` — user said no changes to opened plan, but plan remains in rev-5 governance work.
- `OGManufacturing/.agent-os/product/mission.md` — reusable code should primarily live in `digitalmodel`; OGManufacturing remains manufacturing/domain/project context.
- `aceengineer-admin/.agent-os/product/mission.md` — no changes.
- `acma-projects/.agent-os/product/mission.md` — ACMA naval architecture consulting/client project data and delivery context.
- `assethold/.agent-os/product/mission.md` — no changes.
- `assetutilities/.agent-os/product/mission.md` — no changes.
- `client_projects/.agent-os/product/mission.md` — no changes.
- `doris/.agent-os/product/mission.md` — Doris engineering consulting client/project repo.
- `frontierdeepwater/.agent-os/product/mission.md` — startup project data; AceEngineer 5% shareholder stake.
- `hobbies/.agent-os/product/mission.md` — no changes.
- `investments/.agent-os/product/mission.md` — private short-lived triage/migration repo; route to `assethold`/`achantasdata`; retire within 3 months only after verified no-loss migration.
- `rock-oil-field/.agent-os/product/mission.md` — active triage only; sanity-check and migrate useful code/data/analysis to Tier-1 repos; archive/retire if possible.
- `sabithaandkrishnaestates/.agent-os/product/mission.md` — investment management plus admin/finance/tax/entity records.
- `saipem/.agent-os/product/mission.md` — engineering installation contractor project repo; extract useful info and archive/retire over time.
- `sd-work/.agent-os/product/mission.md` — Sabitha Deepthimahanti bio/pharmacy work docs only; restricted/on-demand.
- `seanation/.agent-os/product/mission.md` — client repo; extract useful data/information then archive.
- `teamresumes/.agent-os/product/mission.md` — opened then skipped/no changes unless revisited.

## Recommended next session sequence

1. Ask user whether to stop here or open next review doc.
2. If continuing review, open `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md` first, then `docs/reports/2026-04-21-repo-mission-revision-sequence.md`.
3. Keep #2553 for overview/report reconciliation; do not create another duplicate issue for the same scope.
4. Before committing, inspect each repo/subrepo status separately. Root `git status` will not show all nested repo mission edits.
5. Commit/push only intended docs/mission changes; avoid staging provider/quota report churn or `.claude/state/*` files unless explicitly desired.
6. Resume #2533 q2 only after mission review/documentation exit work is parked: commit/push rev-5 plan, run fresh rev-5 Codex+Gemini review, then decide q3.
7. Resume q4 after #2533 governance is stable or explicitly deferred.

## Stop conditions

- Stop before implementation for #2533 until clean plan review and user approval.
- Stop before exposing private/client details in GitHub issue bodies or public comments.
- Stop before archiving/retiring any repo until no-loss migration manifests and destination verification exist.
- Stop before dispatching OrcaFlex/AQWA work to `licensed-win-1` until #2548 produces a verified machine/software/license/auth inventory and smoke-test command surface.
