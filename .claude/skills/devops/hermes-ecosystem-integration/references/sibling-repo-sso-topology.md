# Sibling Repo Single-Source-of-Truth Topology

## Trigger

Use this reference after workspace-hub tier-1 repositories are moved from nested checkouts under `workspace-hub/` to sibling checkouts under a common parent such as `/mnt/local-analysis/<repo>`.

## What to Verify

1. **Repo topology**
   - Confirm tier-1 repos are siblings, not children of workspace-hub.
   - Example target shape:
     - `/mnt/local-analysis/workspace-hub`
     - `/mnt/local-analysis/digitalmodel`
     - `/mnt/local-analysis/worldenergydata`
     - `/mnt/local-analysis/CAD-DEVELOPMENTS`
     - `/mnt/local-analysis/assetutilities`

2. **Hermes external skill roots**
   - `~/.hermes/config.yaml` and `config/agents/hermes/config.yaml.template` must not render sibling repos as `workspace-hub/<repo>/.claude/skills`.
   - For sibling topology, external dirs should resolve from the workspace-hub parent directory, e.g. `/mnt/local-analysis/<repo>/.claude/skills`.
   - The Hermes template should not hardcode individual sibling repos. It should contain the central workspace-hub skill root plus a registry-rendered placeholder such as `__REGISTRY_REPO_SKILL_DIRS__`.
   - `sync-agent-configs.sh --machine <name>` should derive sibling skill dirs from `config/workstations/registry.yaml` for that machine and filter to real paths with at least one `SKILL.md`.
   - Treat missing external skill roots as a hard health-check failure; Hermes otherwise silently skips those repos.

3. **Codex/Gemini skill symlinks**
   - In a sibling repo, `.codex/skills -> ../../.claude/skills` and `.gemini/skills -> ../../.claude/skills` usually resolve to the parent directory’s missing `.claude/skills` and are broken.
   - Workspace-hub itself can use `../.claude/skills`.
   - Sibling repos need symlinks that resolve to the intended canonical skill root, or per-repo local `.claude/skills` if that repo is intentionally autonomous.
   - Verify with `test -e <repo>/.codex/skills` / `readlink -f`, not just `readlink`.

4. **AGENTS inheritance pointers**
   - Repo pointers like `../AGENTS.md` become stale when repos are siblings unless an AGENTS.md exists at the shared parent.
   - Prefer explicit sibling-aware references such as `../workspace-hub/AGENTS.md`, or carry a real repo-local AGENTS.md that names workspace-hub as canonical.
   - Before rewriting AGENTS.md, verify the file is a regular file, not a symlink, missing path, or generated pointer. Do not follow symlinks during automated remediation; emit a blocker instead.

5. **Memory bridge**
   - Adding the topology fact to Hermes memory is not enough.
   - Run the memory drift check and bridge so `.claude/memory/agents.md` carries the sibling-layout fact for repo consumers.
   - When checking a non-local machine, do not reuse the local checkout’s `scripts/memory/check-memory-drift.sh` output. Execute the probe on the target host via SSH, or explicitly report `not_present`/`fail` with the remote path as evidence.

## Governance Gate Before Confirming SSoT

When the user asks whether sibling repos now share memory, skills, and harness as a single source of truth, do **not** answer from intended architecture or memory alone.

1. Check the live remediation issue/plan state if one exists.
   - `status:needs-plan` means the SSoT flow is not approval-ready.
   - `status:plan-review` means the plan is awaiting user approval, not implemented.
   - `status:plan-approved` is required before implementation can start.
2. Check local plan/review artifacts for unresolved MAJOR findings.
   - Any MAJOR plan-review result means the answer is “not confirmed yet,” even if the topology has been partially migrated.
3. Separate three states in the reply:
   - **Topology observed**: repos are siblings under the shared parent.
   - **Flow configured/verified**: external dirs, symlinks, AGENTS pointers, and memory bridge all resolve and pass checks.
   - **Governance approved**: issue has user-approved plan state.
4. If artifacts are local/uncommitted, say so. Do not present local draft docs or review files as canonical repo state.

## Closeout Criteria

- Hermes external_dirs all exist and show nonzero active `SKILL.md` count where expected.
- Rendered Hermes config has no unresolved placeholders and no stale nested `workspace-hub/<repo>/.claude/skills` paths.
- Registry-derived sibling repos with skill roots are present in `external_dirs`; do not accept a manually curated list as proof of SSoT.
- Provider skill symlinks in sibling repos resolve successfully.
- Stale nested paths are removed from `config/agents/hermes/config.yaml.template` or explicitly documented as legacy.
- `scripts/memory/check-memory-drift.sh` reports no missing sibling-topology memory entries on the relevant machine; remote machines require remote execution or an explicit not-present/fail state.
- Repo AGENTS pointers resolve to an existing canonical contract and AGENTS remediation skips symlinked/non-regular files.
- Tools/scripts/commands are explicitly classified. Do not imply they are centralized simply because skills or memory are centralized; inspect `.claude/tools`, `.claude/commands`, `tools/`, and `scripts/` per repo and state whether they are repo-local or harness-shared.
- Any associated GitHub issue has no unresolved MAJOR plan-review findings before it is moved to `status:plan-review`, and implementation does not start until user-applied `status:plan-approved` is present.

## Answer Format for User SSoT Questions

When asked “are memory, skills, tools accessible by sibling repos as SSoT?”, answer as a status table rather than a binary unless every channel is green:

| Channel | What to verify | Possible state |
|---|---|---|
| Memory | Bridge drift + repo `.claude/memory/agents.md` freshness | SSoT / drift / not bridged |
| Hermes skills | Live `~/.hermes/config.yaml` `skills.external_dirs` vs registry repos | complete / partial / stale-template |
| Codex/Gemini skills | `.codex/skills` and `.gemini/skills` `test -e` + `readlink -f` | resolved / broken / autonomous |
| AGENTS contract | repo `AGENTS.md` pointer resolves to workspace-hub contract | resolved / stale / symlink-blocked |
| Tools/scripts/commands | per-repo inventory of `.claude/tools`, `.claude/commands`, `tools`, `scripts` | centralized / repo-local / mixed |

Use “workspace-hub is the intended control-plane/SSoT, but not fully verified” when any row is partial, broken, or drifted.
