# Fresh-session resume prompt — machine-equality (#2801) family

Paste into a new session. You have NO memory of prior work — re-derive state via preflight.

```text
Resume the machine-equality (#2801) family on workspace-hub.

PREFLIGHT:
  cd /mnt/local-analysis/workspace-hub && git fetch origin
  git show origin/chore/handoff-2026-05-28:docs/session-handoffs/2026-05-28-machine-equality-family-handoff.md   # full handoff
  for n in 2801 2851 2817 2814 2815 2816; do gh issue view $n --json number,state,labels -q '"#\(.number) \(.state) [\([.labels[].name|select(startswith("status:"))]|join(","))]"'; done
  git branch --show-current   # if on a foreign/stale branch, WORK IN A WORKTREE off origin/main — never edit files in it

STATE (verify, don't trust blindly):
  #2801 merged (PR #2810); OPEN pending owner verify+close; 2/4 machines reported.
  #2851 freshness guard: T2-reviewed, status:plan-approved LABEL but .planning marker MISSING -> not implementable; branch feat/2851-freshness-guard.
  #2817 RE-SCOPED -> plan-approval gate trusts label-actor authority; plan-review; 5 Codex MAJORs open + Gemini pending; branch feat/2817-label-authority (feat/2817-approve-helper SUPERSEDED).
  #2814/2815/2816 open, needs-plan.

GUARDRAILS:
  issue-planning-mode gate: plan -> adversarial review (T1/T2/T3=1/2/3 providers) -> USER approves -> implement TDD.
  NEVER self-approve; NEVER create a .planning/plan-approved/<N>.md marker yourself — ask the user.
  Codex: env -u CLAUDECODE bash scripts/review/submit-to-codex.sh ... | Gemini: env GEMINI_CLI_TRUST_WORKSPACE=true bash scripts/review/submit-to-gemini.sh ...

FIRST STEP: #2851 — if its marker exists, implement TDD-first in a clean worktree -> code-review -> PR; else ask the user for the marker. Confirm thread choice with the user before starting.
```
