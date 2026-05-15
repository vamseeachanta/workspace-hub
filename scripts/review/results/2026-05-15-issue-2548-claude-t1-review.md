---
issue: 2548
date: 2026-05-15
reviewer: Claude code-reviewer agent
review_tier: T1 (Codex unavailable per #2715 — codex-cli 0.130.0 stdin-hang)
commits_reviewed:
  - 920c143c8 — feat(ops): add docs/ops/machine-inventory.md
  - f401b193d — fix(registry): correct dev-secondary workspace_root path
  - 70688d25f — chore(docs): slim BUSINESS_BRAIN.md and point to inventory
verdict: MINOR
---

# T1 review — issue #2548 control-plane machine inventory

## Verdict

**MINOR** — the three commits achieve the documented plan ACs and the inventory doc is genuinely useful. However, the `dev-secondary.workspace_root` fix in `f401b193d` is **half-done**: it corrects the registry but leaves four other call-sites pointing at the now-canonically-wrong `/mnt/workspace-hub`. None of these call-sites are exercised by the reviewed commits' verification commands, so the regression is silent. Suitable to land + follow-up issue, not a re-roll.

## Findings

### MINOR-1 — `dev-secondary.workspace_root` fix is incomplete; 4 call-sites still hardcode the old path
**Where:**
- `config/tmux/start-session.sh:19` — `case "$HOST" in ace-linux-2) WS_ROOT="/mnt/workspace-hub" ;;`
- `scripts/cron/comprehensive-learning-nightly.sh:30,33` — comment + `rsync ace-linux-2:/mnt/workspace-hub/.claude/state/sessions/`
- `scripts/readiness/compare-harness-state.sh:29` — `local ace2_hub="/mnt/workspace-hub"`
- `scripts/readiness/harness-config.yaml:43` — `ws_hub_path: /mnt/workspace-hub`

**Why this matters:** the commit message for `f401b193d` justifies the registry fix by citing "registry-driven tooling … was looking at a non-existent directory on ace-linux-2." That problem persists in the four files above, which do NOT read `registry.yaml` and instead hardcode the old path. Specifically:
- `start-session.sh` will create a tmux session in a non-existent directory the moment a user invokes it on ace-linux-2.
- `comprehensive-learning-nightly.sh` rsync target points at a non-existent remote path → silent zero-byte sync (the `|| true` swallows the error).
- `compare-harness-state.sh` and `harness-config.yaml` are part of the harness-readiness comparison loop and will report degraded state for the wrong reason.

**Why I'm flagging MINOR not MAJOR:** the inventory doc itself is unaffected, the registry fix is correct as-is, and the hardcoded-path call-sites pre-date #2548 (they were already wrong before this issue). #2548's plan didn't claim to fix them. But if the cited motivation ("registry-driven tooling looks at non-existent directory") is the actual driver, the audit should be widened in a follow-up issue rather than declared closed here.

**Suggested fix:** open a small follow-up issue to either (a) replace the four hardcoded paths with a `yq`-driven lookup against `registry.yaml`, or (b) at minimum update the four literals to `/mnt/local-analysis/workspace-hub` as a quick patch. Option (a) prevents the next drift; option (b) is one-line-per-file.

### MINOR-2 — verification claim V2 is narrowly scoped and misleading
**Where:** implementation comment on #2548 (2026-05-15T04:10:48Z), V2 says "No stale `mnt/workspace-hub` in registry — PASS."

**Why this matters:** the V2 grep was apparently scoped to `config/workstations/registry.yaml` only. A repo-wide grep (`grep -rn "/mnt/workspace-hub" config/ scripts/ docs/ .claude/`) returns 5 hits in `config/` and `scripts/` — the four files in MINOR-1 plus a stale entry in `config/ai-tools/provider-kanban.json` (historical, harmless). The verification check, as worded, is technically true but creates a false sense of completeness. Future audits should grep the whole tree for the stale path, not just the one file being edited.

### MINOR-3 — BUSINESS_BRAIN.md slim drops the "multi" placeholder row without explicit migration note
**Where:** `docs/BUSINESS_BRAIN.md` pre-slim row 12: `| multi | — | — | Issues spanning all machines |`

**Why this matters:** the dropped row was a placeholder for cross-cutting issue triage, not a real machine. `grep -rn "machine: multi\|target: multi\|\"multi\"" .claude/ scripts/ config/` returns nothing relevant in the reviewed paths, so no code is broken. But the inventory doc explicitly says it covers "all 8 known machines (6 in registry.yaml + home-win + acma-ws014)" — the "multi" placeholder is silently absent from both inventory and BUSINESS_BRAIN.md. If future agents look up "what does 'multi' mean as an issue label?", they'll find no documentation. Prefer either: keep the placeholder in BUSINESS_BRAIN.md, or add a single line in inventory.md explaining "'multi' as an issue/label scope is not a machine — it indicates the work spans all machines."

**Severity:** lowest of the three findings. Could be batched into the follow-up issue from MINOR-1.

## Verifications I did NOT flag

The following passed under my scrutiny:

- **OrcaFlex dry-run claim is verifiable.** `queue/job-schema.yaml` exists, accepts `orcawave|orcaflex`, polling cadence documented; `scripts/solver/submit-job.sh` validates against exactly those two values; `queue/failed/wamit-val-hemisphere/result.yaml` exists on disk and confirms the loop has executed at least once for OrcaWave. The "evidence on disk" citation in `machine-inventory.md:149` is real.
- **AQWA gap is documented well enough for handoff.** Lines 155-166 of `machine-inventory.md` quote the schema rejection, name #2641 as the tracking issue, and explicitly scope-out resolution. A future dispatch agent could pick up #2641 and know exactly which file to extend.
- **Line count claim (BUSINESS_BRAIN.md 203 → 190) is true.** `git show 70688d25f^:docs/BUSINESS_BRAIN.md | wc -l` = 203, `git show 70688d25f:docs/BUSINESS_BRAIN.md | wc -l` = 190. Restores the documented "keep under 200 lines" cap.
- **No leaked secrets.** No tokens, credentials, or auth state values in any of the three diffs.
- **No over-broad permissions.** Inventory doc is read-only documentation; registry fix is a one-line value change; BUSINESS_BRAIN.md slim is content removal.
- **Hardcoded paths quarantined correctly.** Inventory doc uses semantic placeholders throughout, with absolute paths confined to a single allowlisted reference block (lines 174-181) per `coding-style.md` §Path Handling.
- **Windows-host (`ssh: null`) honesty.** licensed-win-1 and licensed-win-2 rows correctly mark AI-provider auth as "unverified — no SSH" rather than asserting unverifiable claims. This is the right posture per `feedback_adversarial_review_stance`.
- **home-win and acma-ws014 stub correctness.** Rows 107-127 explicitly mark these as "add to registry.yaml before scheduling work" rather than fabricating capability data. Correct.
- **`f401b193d` registry change is the right path.** Verified `/mnt/local-analysis/workspace-hub` exists on this host (currently running the review on ace-linux-2 per the dev-secondary entry); `/mnt/workspace-hub` does not exist.

## Verification commands I ran

```bash
# Diff inspection
git show --stat 920c143c8 f401b193d 70688d25f
git show f401b193d -- config/workstations/registry.yaml
git show 70688d25f -- docs/BUSINESS_BRAIN.md

# Path-fix completeness audit
ls -la /mnt/local-analysis/workspace-hub /mnt/workspace-hub  # confirms only first exists
grep -rn "/mnt/workspace-hub" config/ scripts/ docs/ .claude/ | grep -v ".git/"

# Line count claim
git show 70688d25f^:docs/BUSINESS_BRAIN.md | wc -l   # → 203
git show 70688d25f:docs/BUSINESS_BRAIN.md | wc -l    # → 190
wc -l docs/ops/machine-inventory.md                  # → 190

# OrcaFlex dispatch claim verification
ls /mnt/local-analysis/workspace-hub/queue/
ls /mnt/local-analysis/workspace-hub/queue/failed/wamit-val-hemisphere/
cat /mnt/local-analysis/workspace-hub/queue/job-schema.yaml | head -40
cat /mnt/local-analysis/workspace-hub/scripts/solver/submit-job.sh

# "multi" placeholder reference check
grep -rn '"multi"\|machine: multi\|target: multi' .claude/ scripts/ config/

# Issue context
gh issue view 2548 --repo vamseeachanta/workspace-hub --json comments
gh issue list --repo vamseeachanta/workspace-hub --state open --search "codex-cli 0.130"  # → #2715
```

## Recommendation

**Land the work + open a follow-up; do NOT close #2548 yet.**

Rationale:
1. The three commits as-shipped are correct, internally consistent, and the inventory doc is high quality.
2. MINOR-1 is the only finding that touches running code (the other two are documentation-shape issues). It is a pre-existing problem (not introduced by these commits) but the issue's own justification text widens the implicit scope to "registry-driven tooling sees the right path." That implicit scope is not yet met.
3. Acceptable closure path: open a follow-up issue (suggest "fix(ops): replace hardcoded `/mnt/workspace-hub` in 4 callsites; replace with registry lookup or canonical path") and link it in the #2548 closeout comment. Once the follow-up is filed, #2548 can close.
4. No blocker for merging — these commits are already on `origin/main`. This is an after-the-fact T1 standing in for the unavailable Codex T1.

User decision required:
- Open the follow-up issue and close #2548? (recommended)
- Wait for Codex availability (#2715) and re-run T1 there for cross-confirmation?
- Treat MINOR-3 as not worth tracking? (defensible — it's a placeholder absence)
