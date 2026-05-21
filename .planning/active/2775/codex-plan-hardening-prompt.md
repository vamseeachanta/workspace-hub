You are Codex CLI working inside /mnt/local-analysis/workspace-hub.

Task: approval-safe planning work only for GitHub issue #2775. DO NOT implement code, DO NOT edit sibling repos, DO NOT touch live ~/.hermes config, DO NOT change symlinks. You may inspect files and produce a repo-local planning artifact only.

Context:
- Current issue #2775 is OPEN with label status:needs-plan.
- Existing plan: docs/plans/2026-05-21-issue-2775-workspace-hub-sibling-sso-flow.md
- Latest disagreement report: scripts/review/results/2026-05-21-plan-2775-disagreement.md
- All reviewers returned MAJOR; implementation is blocked.
- Goal from user: make workspace-hub the single source of truth for memory, skills, and harness flow across sibling repos, while using Codex/Claude CLI to speed up planning/hardening.

Your job:
1. Inspect the plan, disagreement report, and actual source files referenced by the findings:
   - config/workstations/registry.yaml
   - scripts/readiness/harness-config.yaml
   - config/agents/hermes/config.yaml.template
   - scripts/_core/sync-agent-configs.sh
   - docs/standards/CONTROL_PLANE_CONTRACT.md
   - docs/plans/README.md
2. Produce a concise hardening memo at .planning/active/2775/codex-plan-hardening.md with:
   - exact changes needed to resolve each MAJOR finding;
   - any live-state corrections from inspecting actual files;
   - a proposed revised TDD test list and paths;
   - exact approval-gate semantics for --apply (live GitHub status only vs local marker);
   - exact cross-repo source-control/dirty-state strategy;
   - exact sync-agent-configs.sh behavior delta needed.
3. If you believe the plan file itself should be patched, include a unified diff snippet in the memo, but do not directly patch the plan.

Constraints:
- Read-only except writing .planning/active/2775/codex-plan-hardening.md.
- No git add/commit/push.
- No gh issue edit.
- No label changes.
- No implementation files under scripts/, tests/, config/, docs/standards except reading.
- Be adversarial and specific. No praise.
