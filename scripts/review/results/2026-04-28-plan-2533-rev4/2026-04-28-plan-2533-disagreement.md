# Disagreement report — plan #2533 (2026-04-28)

## Verdicts

| Provider | Verdict |
|---|---|
| codex | MAJOR |
| gemini | MAJOR |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### codex

- Plan has contradictory review-artifact paths. The header says fresh rev-4 evidence is “expected under `scripts/review/results/2026-04-28-plan-2533-rev4/`”, and the review summary says rev-4 “stopped binding the plan header to stale root-level rev-1 artifacts.” But `## Artifact Map` still lists `scripts/review/results/2026-04-28-plan-2533-codex.md`, `...-gemini.md`, and `...-disagreement.md`. GitHub code search found no matching rev4 or root-level artifacts. This leaves the hard gate ambiguous about which artifacts supersede prior MAJOR reviews.
- Plan’s live inventory root is not reconciled with an explicitly cited source. `collect_repo_inventory()` says to enumerate immediate-child git repos at “parent of workspace-hub checkout” by default. `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md` says “All repositories are located as subdirectories of the workspace-hub root” and shows `[25 managed repositories]/` under `workspace-hub/`. The plan cites that overview as inventory evidence but does not document why its local enumeration default intentionally contradicts the overview’s repository-location claim. That can silently miss the required live snapshot, depending on actual checkout topology.
- `## Artifact Map` marks `docs/README.md` as optional under “Discovery links”, but `## Files to Change` and Acceptance Criteria make `docs/README.md` cleanup mandatory. This inconsistency is smaller than the artifact-path issue, but it weakens execution because an implementer following the artifact map could skip a required stale-authority cleanup.

### gemini

- Plan §Files to Change mandates "Verify/update the existing #2533 plan-index row status only; do not duplicate the row", enforced by `test_plan_index_has_single_2533_row`. Grep confirms no row for `2533` currently exists in `docs/plans/README.md`. The implementation will fail because the required existing row is absent.
- Plan §Files to Change, §TDD Test List, and §Acceptance Criteria explicitly scope the `docs/README.md` discoverability cleanup strictly to `.agent-os/product/mission.md`. However, `docs/README.md` lines 298-302 actively link to four files (`mission.md`, `tech-stack.md`, `roadmap.md`, `decisions.md`). Removing only the `mission.md` reference leaves three active links to `.agent-os/product/`, violating `docs/standards/CONTROL_PLANE_CONTRACT.md` which designates the entire `.agent-os/` directory as legacy.
- Plan §Deliverable and §Files to Change direct the creation of two new YAML registries (`repo-portfolio-inventory.yaml` and `repo-mission-evidence.yaml`) under a new `docs/registry/` directory. The canonical home for registries in the workspace is `data/document-index/` (which already houses `intelligence-accessibility-registry.yaml`, `conference-registry.yaml`, etc., as cited in `docs/ROUTING_INDEX.md`). Inventing a new `docs/registry/` directory creates architectural drift.

