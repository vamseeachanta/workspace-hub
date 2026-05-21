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
   - Treat missing external skill roots as a hard health-check failure; Hermes otherwise silently skips those repos.

3. **Codex/Gemini skill symlinks**
   - In a sibling repo, `.codex/skills -> ../../.claude/skills` and `.gemini/skills -> ../../.claude/skills` usually resolve to the parent directory’s missing `.claude/skills` and are broken.
   - Workspace-hub itself can use `../.claude/skills`.
   - Sibling repos need symlinks that resolve to the intended canonical skill root, or per-repo local `.claude/skills` if that repo is intentionally autonomous.
   - Verify with `test -e <repo>/.codex/skills` / `readlink -f`, not just `readlink`.

4. **AGENTS inheritance pointers**
   - Repo pointers like `../AGENTS.md` become stale when repos are siblings unless an AGENTS.md exists at the shared parent.
   - Prefer explicit sibling-aware references such as `../workspace-hub/AGENTS.md`, or carry a real repo-local AGENTS.md that names workspace-hub as canonical.

5. **Memory bridge**
   - Adding the topology fact to Hermes memory is not enough.
   - Run the memory drift check and bridge so `.claude/memory/agents.md` carries the sibling-layout fact for repo consumers.

## Closeout Criteria

- Hermes external_dirs all exist and show nonzero active `SKILL.md` count where expected.
- Provider skill symlinks in sibling repos resolve successfully.
- Stale nested paths are removed from `config/agents/hermes/config.yaml.template` or explicitly documented as legacy.
- `scripts/memory/check-memory-drift.sh` reports no missing sibling-topology memory entries.
- Repo AGENTS pointers resolve to an existing canonical contract.
