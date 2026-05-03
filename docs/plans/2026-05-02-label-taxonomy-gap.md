# Workspace-Hub Label Taxonomy Gap (2026-05-02)

Triggered by Lane 2's umbrella-issue [#2585](https://github.com/vamseeachanta/workspace-hub/issues/2585) (`tracker(digitalmodel-tests): 26 collect_ignore entries`), which currently carries only `domain:testing`. Lane 2's plan referenced four labels that may or may not exist in the workspace-hub taxonomy. This plan enumerates the existing taxonomy, decides on a prefix family, and proposes the minimum set of additions — **read-only audit, no labels are created here.**

Source data: `gh label list --repo vamseeachanta/workspace-hub --limit 500 --json name,description,color` (278 labels total, captured 2026-05-02 to `/tmp/wh-labels.json`).

## Existing taxonomy (278 labels)

| Family | Count | Color convention | Notes |
|---|---|---|---|
| `domain:*` | 161 | almost all `#c5def5` (pale blue), description boilerplate `Domain: <name>` | dominant family; covers engineering subjects, repos (`domain:assetutilities`), and cross-cutting concerns |
| `cat:*` | 40 | mixed (`#c5def5`, `#EDEDED`, a few hand-picked) | older, partly overlapping with `domain:*` |
| no-prefix | 23 | per-label | mix of GitHub defaults (`bug`, `enhancement`, …) and workflow markers (`wrk-item #0075ca`, `solver #0e8a16`, `llm-wiki #0E8A16`, `repo-readiness #FBCA04`, `enforcement #fbca04`, `maintenance #0052CC`, `review-backlog #f9d0c4`, `dark-intelligence #5319E7`) |
| `machine:*` | 10 | `#FBCA04` family | per-host routing |
| `status:*` | 8 | per-state semantic color | `pending #c5def5`, `working #1d76db`, `done #0e8a16`, `blocked #d93f0b`, `closed #6e7781`, `plan-review #FFA500`, `plan-approved #2EA44F`, `needs-data #B60205` |
| `wip:*` | 6 | — | work-in-progress phases |
| `priority:*` | 5 | `#d4c5f9` | priority levels |
| `pipeline:*` | 5 | per-stage | sales/business pipeline |
| `type:*` | 4 | `#bfdadc` / `#c5def5` / `#d4c5f9` | client-segment + workflow types |
| `discrepancy:*` | 4 | red/yellow | engineering defect categorisation |
| `agent:*` | 4 | — | agent-specific routing |
| `route:*` | 3 | — | dispatch routing |
| `cadence:*` | 3 | yellow | recurring schedules |
| `scope:*` | 1 | — | release scoping |
| `claude:*` | 1 | — | adapter-specific |

**`status:*` full list** (relevant for `status:needs-plan`):
`status:pending`, `status:working`, `status:done`, `status:blocked`, `status:closed`, `status:plan-review` (`#FFA500`), `status:plan-approved` (`#2EA44F`), `status:needs-data` (`#B60205`).

**`domain:*` matches for the requested labels:**
- `domain:testing` — **exists** (`#c5def5`, "Domain: testing")
- `domain:test-coverage` — exists
- `domain:assetutilities` — exists (precedent for repo-as-domain)
- `domain:digitalmodel` — **does not exist**

**No `area:*` family exists at all.** Zero labels carry that prefix.

**No `tracker` / `umbrella` / `epic` / `meta` label exists.** Closest semantic neighbours are no-prefix workflow markers: `wrk-item`, `solver`, `repo-readiness`, `llm-wiki`.

## Decision: which prefix family wins?

**`domain:*` wins decisively** for subject/repo scoping (161 labels vs. 0 for `area:*`). Lane 2 was correct to fall back to `domain:testing` — that label already exists and matches convention.

**Implication for the four requested labels:**

1. `tracker` — no existing umbrella/tracker label. Goes in the **no-prefix workflow-marker** family alongside `wrk-item`, `solver`, `repo-readiness`. → **CREATE `tracker`**.
2. `area:testing` — DO NOT create. The intended label `domain:testing` already exists and is already applied to [#2585](https://github.com/vamseeachanta/workspace-hub/issues/2585). Lane 2's fallback was correct.
3. `repo:digitalmodel` — rename to `domain:digitalmodel` per `domain:assetutilities` precedent. Does not exist. → **CREATE `domain:digitalmodel`**.
4. `status:needs-plan` — fits the existing `status:*` family as the intermediate state between issue-filed and `status:plan-review`. Does not exist. → **CREATE `status:needs-plan`**.

## Proposed additions

| Name | Description | Color | Family-match (cited label) | Creation command |
|---|---|---|---|---|
| `tracker` | Umbrella/parent issue aggregating multiple child fixes — closes only when all linked work items resolve. | `FBCA04` | `repo-readiness` (`#FBCA04`, "Daily readiness tracker") — same workflow-marker family, same tracker semantics | `gh label create "tracker" --description "Umbrella/parent issue aggregating multiple child fixes — closes only when all linked work items resolve." --color FBCA04 --repo vamseeachanta/workspace-hub` |
| `domain:digitalmodel` | Domain: digitalmodel — sibling-repo scope marker for issues whose primary code lives in `digitalmodel/`. | `c5def5` | `domain:assetutilities` (`#c5def5`) — exact-precedent for sibling-repo-as-domain | `gh label create "domain:digitalmodel" --description "Domain: digitalmodel — sibling-repo scope marker for issues whose primary code lives in digitalmodel/." --color c5def5 --repo vamseeachanta/workspace-hub` |
| `status:needs-plan` | Issue filed and triaged, awaiting plan draft — precedes `status:plan-review`. | `FBCA04` | `status:plan-review` is `#FFA500` (orange = awaiting human review) and `status:plan-approved` is `#2EA44F` (green = ready to execute); `status:needs-plan` should be a lighter "attention but not blocking" yellow `#FBCA04` matching `enforcement` / `repo-readiness` to read as "earlier phase than plan-review" without overlapping the orange/green cells | `gh label create "status:needs-plan" --description "Issue filed and triaged, awaiting plan draft — precedes status:plan-review." --color FBCA04 --repo vamseeachanta/workspace-hub` |

`area:testing` — **not proposed.** `domain:testing` already exists.

## Proposed [#2585](https://github.com/vamseeachanta/workspace-hub/issues/2585) re-labeling

Current labels on [#2585](https://github.com/vamseeachanta/workspace-hub/issues/2585): `domain:testing` only.

Once the labels above are created, [#2585](https://github.com/vamseeachanta/workspace-hub/issues/2585) should carry:

- `tracker` — it's the umbrella for 26 child fixes
- `domain:testing` — already applied, keep
- `domain:digitalmodel` — its 26 child fixes are all under `digitalmodel/tests/`
- `status:needs-plan` — assuming children are not yet planned; otherwise `status:plan-review` once a plan lands

**This plan does not act on [#2585](https://github.com/vamseeachanta/workspace-hub/issues/2585) — re-labeling is left to the user or to a follow-up labeled-as-`status:plan-approved` execution issue.**

## Open questions

1. **`cat:*` vs `domain:*` deprecation.** `cat:*` (40 labels) overlaps heavily with `domain:*` (161). Several `cat:` labels have empty descriptions (`cat:AI`, `cat:analysis`, `cat:bugfix`, …). A separate audit issue could mark `cat:*` deprecated and migrate active uses to `domain:*`. Out of scope here — surfaced for visibility only.
2. **`status:needs-plan` cadence with batch agents.** The CLAUDE.md planning workflow is `Issue → Resource Intel → Plan → Adversarial Review → status:plan-review → USER APPROVES → status:plan-approved → Implement`. `status:needs-plan` would slot before `status:plan-review`. Confirm whether batch agents should auto-pick `status:needs-plan` issues to draft plans, or whether plan-drafting stays main-session only — affects whether the description should mention "batch-eligible".
3. **`tracker` color drift.** Both `tracker` and `repo-readiness` would be `#FBCA04`. If the user prefers visual disambiguation, candidate alternates are `#5319E7` (matches `dark-intelligence` — also a no-prefix workflow marker) or `#0E8A16` (matches `llm-wiki` / `solver`). Default chosen: `#FBCA04` because tracker semantics align tightly with `repo-readiness`.
4. **No `repo:*` family — should one exist?** Currently sibling-repo scoping is done via `domain:<repo-name>` (`domain:assetutilities`, would-be `domain:digitalmodel`). A formal `repo:*` family would be cleaner long-term but is a larger taxonomy migration. Out of scope — defer to a separate proposal.
