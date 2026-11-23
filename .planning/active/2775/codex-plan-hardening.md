Created the hardening memo here:

[.planning/active/2775/codex-plan-hardening.md](/mnt/local-analysis/workspace-hub/.planning/active/2775/codex-plan-hardening.md)

It includes the exact MAJOR-finding fixes, live-state corrections, revised TDD paths, `--apply` semantics using live GitHub status only, cross-repo dirty-state strategy, `sync-agent-configs.sh` behavior delta, and a unified diff snippet for the plan.

I did not edit the plan, sibling repos, live `~/.hermes`, symlinks, labels, or Git state. Verification: the memo is 195 lines and is the only file I wrote.

Cleanup audit: EXPECTED residue is the new memo under `.planning/active/2775/`. UNEXPECTED pre-existing residue remains in the repo and `/tmp` from prior work, including many modified/untracked files and stashes; I left all of that untouched per your constraints.