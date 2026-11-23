You are Claude Code working inside /mnt/local-analysis/workspace-hub.

Task: patch ONLY the #2775 planning artifacts to resolve first-round MAJOR findings. This is planning-gate work only, not implementation.

Allowed writes:
- docs/plans/2026-05-21-issue-2775-workspace-hub-sibling-sso-flow.md
- docs/plans/README.md
- optional: .planning/active/2775/plan-revision-notes.md

Forbidden writes:
- scripts/**
- tests/**
- config/**
- docs/standards/**
- any sibling repo under /mnt/local-analysis/<repo>
- ~/.hermes or any home config
- GitHub labels/issues
- git add/commit/push

Inputs:
- Existing plan: docs/plans/2026-05-21-issue-2775-workspace-hub-sibling-sso-flow.md
- Disagreement report: scripts/review/results/2026-05-21-plan-2775-disagreement.md
- Claude hardening memo: .planning/active/2775/claude-plan-hardening.md
- Codex hardening log: .planning/active/2775/logs/codex-plan-hardening-r2.log

Patch requirements:
1. Keep status as draft-needs-revision unless you can make the plan ready for re-review; do NOT claim approval-ready.
2. Remove all local approval marker requirements. Gate must be live GitHub `status:plan-approved` only, queried with `gh issue view 2775 --json labels`; any gh failure fails closed. Local markers must be explicitly ignored.
3. Replace `tests/harness/` paths with `tests/readiness/` and/or `tests/workstations/` as appropriate.
4. Make registry-vs-harness resolver-source scope explicit: this is not just adding `__TIER1_REPO_ROOT__`; it changes `sync-agent-configs.sh` to registry-first resolver with `--machine`.
5. Fix overlay/scope circularity: do not derive overlay candidates from stale Hermes template. Target scope must come from `config/workstations/registry.yaml`; overlays must be explicit typed config or eliminated. Prefer central-only plus registry-derived sibling allowlist.
6. Add dev-secondary ground-truth/field-completeness handling. Do not blindly assert `/mnt/local-analysis` is right on ace-linux-2 without live verification.
7. Add IntxLNK root-cause and apply semantics: classify regular files beginning IntxLNK as corrupted adapters, block on ntfs3, unlink/recreate only after approval+clean-state, verify with file/readlink.
8. Add property-broad broken symlink tests, workspace-hub self-symlink special case, absent registry repo not_present test, dirty repo apply block, gh fail-closed tests, unresolved-token tests.
9. Make CONTROL_PLANE_CONTRACT update required, not optional.
10. Update docs/plans/README.md row for #2775 so it no longer says approval gate requires both live label plus marker; it should say live label only and local markers ignored.
11. Add pre-review requirement: commit and push revised plan + README before rerunning Codex/Gemini/Claude review, because remote reviewers need artifacts on main.

After patching, write .planning/active/2775/plan-revision-notes.md summarizing changed sections and remaining gate state.
