# Rerun-review dispatch pack — #2443, #2444, #2289

Purpose
- dispatch a fresh external adversarial re-review wave for the hardened plan artifacts
- avoid relying on stale/single-author/interim review state
- keep issue statuses conservative until new artifacts land

Targets
- #2443 — `docs/plans/2026-04-21-issue-2443-achantas-data-markdown-lint.md`
- #2444 — `docs/plans/2026-04-21-issue-2444-aceengineer-admin-ci.md`
- #2289 — `docs/plans/2026-04-21-issue-2289-bypass-rollback-recovery.md`

Expected outputs
- fresh Codex review artifact for each plan
- fresh Gemini review artifact for each plan
- optional consolidated GH comment after artifacts are reviewed

Routing / ownership
- Terminal 1: #2443 rerun review only
- Terminal 2: #2444 rerun review only
- Terminal 3: #2289 rerun review only
- zero file overlap beyond `scripts/review/results/`, which is safe because filenames differ by issue

Negative write boundaries
- T1 must not dispatch 2444 or 2289
- T2 must not dispatch 2443 or 2289
- T3 must not dispatch 2443 or 2444
- no terminal should edit plan files during this wave; this is review dispatch only

Preflight for each terminal
```bash
cd /mnt/local-analysis/workspace-hub
git status --short
```
- if the target plan file changed again since this packet was written, re-read it before dispatching

Shared reviewer stance contract
All prompts must enforce:
- adversarial reviewer
- no praise, no restatement
- approval only after affirmative verification
- cite exact file paths / sections / quoted claims
- treat plan text as claims, not truth
- use attested evidence as authoritative when injected by wrapper scripts

Issue-by-issue dispatch commands

## #2443
Plan file:
- `docs/plans/2026-04-21-issue-2443-achantas-data-markdown-lint.md`

Codex prompt:
- use `docs/plans/overnight-prompts/2026-04-22-rerun-review-wave/review-2443-codex-prompt.md`

Gemini prompt:
- use `docs/plans/overnight-prompts/2026-04-22-rerun-review-wave/review-2443-gemini-prompt.md`

Commands:
```bash
cd /mnt/local-analysis/workspace-hub
scripts/review/submit-to-codex.sh \
  --file docs/plans/2026-04-21-issue-2443-achantas-data-markdown-lint.md \
  --prompt "$(cat docs/plans/overnight-prompts/2026-04-22-rerun-review-wave/review-2443-codex-prompt.md)" \
  > scripts/review/results/2026-04-22-plan-2443-codex-r4.md

scripts/review/submit-to-gemini.sh \
  --file docs/plans/2026-04-21-issue-2443-achantas-data-markdown-lint.md \
  --prompt "$(cat docs/plans/overnight-prompts/2026-04-22-rerun-review-wave/review-2443-gemini-prompt.md)" \
  > scripts/review/results/2026-04-22-plan-2443-gemini-r4.md
```

## #2444
Plan file:
- `docs/plans/2026-04-21-issue-2444-aceengineer-admin-ci.md`

Commands:
```bash
cd /mnt/local-analysis/workspace-hub
scripts/review/submit-to-codex.sh \
  --file docs/plans/2026-04-21-issue-2444-aceengineer-admin-ci.md \
  --prompt "$(cat docs/plans/overnight-prompts/2026-04-22-rerun-review-wave/review-2444-codex-prompt.md)" \
  > scripts/review/results/2026-04-22-plan-2444-codex-r4.md

scripts/review/submit-to-gemini.sh \
  --file docs/plans/2026-04-21-issue-2444-aceengineer-admin-ci.md \
  --prompt "$(cat docs/plans/overnight-prompts/2026-04-22-rerun-review-wave/review-2444-gemini-prompt.md)" \
  > scripts/review/results/2026-04-22-plan-2444-gemini-r4.md
```

## #2289
Plan file:
- `docs/plans/2026-04-21-issue-2289-bypass-rollback-recovery.md`

Commands:
```bash
cd /mnt/local-analysis/workspace-hub
scripts/review/submit-to-codex.sh \
  --file docs/plans/2026-04-21-issue-2289-bypass-rollback-recovery.md \
  --prompt "$(cat docs/plans/overnight-prompts/2026-04-22-rerun-review-wave/review-2289-codex-prompt.md)" \
  > scripts/review/results/2026-04-22-plan-2289-codex-v7.md

scripts/review/submit-to-gemini.sh \
  --file docs/plans/2026-04-21-issue-2289-bypass-rollback-recovery.md \
  --prompt "$(cat docs/plans/overnight-prompts/2026-04-22-rerun-review-wave/review-2289-gemini-prompt.md)" \
  > scripts/review/results/2026-04-22-plan-2289-gemini-v7.md
```

Morning/output checklist
- verify each artifact exists and is non-empty
- classify each issue: APPROVE/MINOR/MAJOR
- if any MAJOR remains, do not surface for approval
- if all required external artifacts come back APPROVE/MINOR, prepare one concise GH comment per issue summarizing:
  - artifact filenames
  - latest verdicts
  - whether the plan is now approval-ready or still blocked

What you should have by the end
- 6 fresh external review artifacts total
- a clean yes/no answer on whether #2443, #2444, #2289 can move toward user approval
