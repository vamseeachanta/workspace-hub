# tier1-repos.sh — canonical tier-1 repo manifest
# Sourced by install-pre-commit-hook-cross-repo.sh and check-pre-commit-hook-drift.sh.
# Plain bash-source format (no yq / python-yaml dependency) per workspace-hub#2722
# Codex r2 finding #4: bootstrap-machine.sh must run on minimal-toolchain systems.
#
# Seeded from workspace-hub#2411 7-repo audit (issuecomment-4467824635, 2026-05-16).

TIER1_REPOS=(
  "workspace-hub"
  "digitalmodel"
  "assetutilities"
  "worldenergydata"
  "assethold"
  "aceengineer-website"
  "llm-wiki"
)
