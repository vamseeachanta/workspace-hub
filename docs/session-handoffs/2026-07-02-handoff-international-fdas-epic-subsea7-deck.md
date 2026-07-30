# Session handoff — 2026-07-02 — International field-dev epic (wed #713) + Subsea7 deck wording pass

**Session:** Claude Code main, dev-primary (`ace-linux-1`). **Scope:** worldenergydata international epic intake + planning; aceengineer-strategy deck edits.

## Delivered (all pushed / on GitHub)

### 1. worldenergydata — international field development analysis epic
- **Epic [#713](https://github.com/vamseeachanta/worldenergydata/issues/713)** filed with children **#714–#723** (all `status:needs-plan` except #714): foundations (#714 FDAS extraction + fiscal decks, #715 adapter contract), country chains (#716 Norway pilot, #717 UK, #718 Brazil, #719 Canada offshore, #720 Mexico T3), new sources (#721 Australia, #722 missing-sources), #723 cross-country benchmark. Country chains carry `lane:codex` (user heavy-token delegation directive); exactly one lane label per issue (#3029).
- **Architecture facts (Explore-verified):** `field_development/` engine (#567) is already source-agnostic (`FieldConcept` schema, non-US basin priors). FDAS economics is the coupled piece — inside the bsee member, single `bsee_adapter.py`, per-dev-system US-GoM assumptions (`config.py:36-39`). Scheduler onboarding = `AbstractJob` + `_LAZY_EXPORTS` + #462 contract.
- **Web research (live-verified, posted as issue comments):**
  - [#721 Australia](https://github.com/vamseeachanta/worldenergydata/issues/721): NO national well-level production DB; NOPIMS OData (wells/seismic) + NOPTA shapefiles + GA bathymetry (T1 metadata); production composite = AEMO GBB daily facility CSVs + SA PEPS-SA monthly well/pool + QLD/WA aggregates; offshore liquids history = open-data gap.
  - [#722 missing sources](https://github.com/vamseeachanta/worldenergydata/issues/722): ranked — Argentina (T1, well-level monthly CKAN API) and Netherlands NLOG (T1-T2, per-well monthly JSON REST) best; Colombia SODA T1; Denmark/Ghana T2; India NDR paid/CLOSED (demoted); Malaysia paywalled; Indonesia Cloudflare-blocked; `itie-congo.org` = hijacked domain (use itie.cg).
- **[#714](https://github.com/vamseeachanta/worldenergydata/issues/714) plan v3 at `status:plan-review` — AWAITING USER APPROVAL.** Full plan + evidence posted as issue comments. T2 adversarial review: r1 Claude **MAJOR** (per-dev-system royalty map required; stale ADR-0001 "bsee<->fdas cycle" doc refuted — zero fdas→bsee imports; mkdocs.yml src root; orphaned cost dep; sliding-scale seam; declarative fields) + r2 Codex **MAJOR** 12 findings (pyyaml dep, package-data/install matrix, enumeration gates G1-G3, strict deck schema, scoped baseline, concrete follow-ons). All folded; r3 inline per cross-review routing. Key v3 decisions: v1 royalty models `flat|none` only; **Brazil deck deferred to #718**; 3 decks (us_gom/norway/uk); parity = component-vector comparison across all 4 dev systems; standalone = local-path installs.
- Cross-ref comment posted on llm-wiki [#803](https://github.com/vamseeachanta/llm-wiki/issues/803) (catalog layer vs ingestion layer boundary).

### 2. aceengineer-strategy — Subsea7 FDG deck wording pass (VA-directed)
- **PR [#141](https://github.com/vamseeachanta/aceengineer-strategy/pull/141) squash-merged → main `cd39248`**: slide-1 tagline → "Deterministic workflows — every number traces to a reproducible run."; ALL FDG/product-comparison references removed (grep-verified 0 `FDG`/`your`); second-person wording genericized (lookup-table "case in, answer out", offer "case of the team's choosing… nothing to install", close "a pressing need", "How can I help?"). deck.html/PDF/PPTX re-rendered via `npx @marp-team/marp-cli`.
- **HANDOVER: a parallel session now owns presentation curation** (user directive). This session made no further strategy-repo changes after #141. The shared checkout is on that session's branch `pipeline/subsea7-preread-oceanplan` with a dirty `pre-read-one-pager.html` — **theirs, do not touch**. Parallel session should `git pull` main to pick up cd39248 before further deck edits.

### 3. Memory
- New topic `project_wed_international_field_dev_epic.md` + MEMORY.md index line; MEMORY.md compacted 22.9KB → 13.3KB (hook-triggered; detail preserved in topic files).

## Repo states & dirty exceptions (audit)
- **workspace-hub**: `git status` HANGS (>2 min; detached-HEAD/mid-rebase per dde work — pre-existing). This handoff was published via sparse worktree from `origin/main`, not the main checkout. `.claude/state/*` churn at session start = autorun collectors, untouched.
- **worldenergydata**: checkout on stale branch `feat/wf-api-3286-worldenergydata-adopt` + 1 old stash (2026-06-26) — pre-existing, this session made NO working-tree writes (all work via `gh`).
- **aceengineer-strategy**: parallel-session-owned (see above); my merged branch ref deleted locally + remotely.
- **Scratchpad**: session-scoped files only (plan-714-v1/v2/v3, issue bodies, research) — canonical copies live as GitHub issue comments; scratchpad auto-expires.

## No-external-action status
No emails sent, nothing published outside GitHub issues/PRs in the user's own repos. No crons/schedules created. Two stray background greps stopped at closeout.

## Next steps (in order)
1. **USER: approve wed #714** — `gh issue edit 714 --repo vamseeachanta/worldenergydata --remove-label "status:plan-review" --add-label "status:plan-approved"` + `.planning/plan-approved/714.md` marker → then TDD implementation (plan §Artifact Map; commit canonical plan file to wed `docs/plans/` with the PR).
2. Plan #715 (adapter contract), then Norway pilot #716.
3. Presentation curation continues in the parallel session (deck base = strategy main `cd39248`).
4. Ops note: `submit-to-codex.sh` default 300s times out on this box — use `CODEX_TIMEOUT_SECONDS=900`.
