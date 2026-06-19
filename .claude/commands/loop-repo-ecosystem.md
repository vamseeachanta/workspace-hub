---
name: loop-repo-ecosystem
description: "Run a Forward-Future-style autonomous loop against a named ecosystem repo. Spine-of-3 (error-sweep, adversarial-review, loop-harness) plus optional docs/changelog/quality/cleanup/seo loops. Iterates work→verify until a stop condition, honoring ecosystem guardrails (PR-only repos, never self-merge digitalmodel, advisory-only on workspace-hub, hand-verify codex)."
argument-hint: "--type <loop> --repo <name> [--cadence now|nightly|weekly] [--verify self|independent|codex] [--max-iters N] [--lane claude|codex] [--run <inner-loop>] [--dry-run]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent, ToolSearch, ScheduleWakeup
---

## Loop: Repo Ecosystem

You are running one autonomous **loop** from the Forward Future Loop Library, scoped to a single repo in this ecosystem. Parse `$ARGUMENTS`, resolve the repo, then execute the loop's iterate-until-done playbook under the guardrails below. **Default to a single dry-run pass that prints the plan unless the user passed real flags.**

### 0. Parse arguments (from `$ARGUMENTS`)

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--type <loop>` | yes | — | Which loop (see registry §2). Aliases accepted. |
| `--repo <name>` | yes | — | Ecosystem repo (see registry §1). |
| `--cadence now\|nightly\|weekly` | no | `now` | `now` = iterate this session. `nightly`/`weekly` = propose a schedule, don't auto-register. |
| `--verify self\|independent\|codex` | no | per-loop default | Verification gate (§3). `independent` = fresh `Agent` reviewer; `codex` = delegate verify to codex. |
| `--max-iters N` | no | `5` | Hard ceiling on iterations. Always bounded — never infinite. |
| `--lane claude\|codex` | no | `claude` | Who does the heavy work. Heavy compute → `codex` (then hand-verify). |
| `--run <inner-loop>` | only for `loop-harness` | — | The loop that `loop-harness` wraps with independent verification. |
| `--dry-run` | no | off | Print the resolved plan + stop condition + guardrails; make no changes. |

If `--type` or `--repo` is missing, print the registries (§1, §2) and stop. If flags look absent/exploratory, treat as `--dry-run`.

### 1. Repo registry + guardrails

Resolve `ECOSYSTEM_ROOT` once, then `REPO_PATH="$ECOSYSTEM_ROOT/<repo>"`:
!`ECOSYSTEM_ROOT="$(cd "$(git rev-parse --show-toplevel 2>/dev/null || echo .)/.." && pwd)"; echo "ECOSYSTEM_ROOT=$ECOSYSTEM_ROOT"; ls -d "$ECOSYSTEM_ROOT"/*/.git 2>/dev/null | sed 's#/.git##' | xargs -n1 basename | tr '\n' ' '; echo`

Per-repo guardrail flags (the loop MUST honor these — they override any generic loop behavior):

| Repo | Visibility | Write policy | Loop notes |
|---|---|---|---|
| `digitalmodel` | PUBLIC | **PR-only, NEVER self-merge** | CI baseline is RED (engine + native segfault) — compare PR check set vs bare main before calling a regression. Calc changes need citation sidecar. |
| `worldenergydata` | PUBLIC | PR-only | Public federal data only. |
| `assetutilities` / `assethold` | PUBLIC | PR-only | — |
| `aceengineer-website` | PUBLIC | PR-only | Primary `seo` target. PostHTML stack. |
| `workspace-hub` | PUBLIC | **ADVISORY-ONLY** | Umbrella. Loops here may open issues/PRs but **never auto-commit fixes**. No client PII, ever. |
| `deckhand` / `deckhand-live` | PRIVATE | PR-only, live bot host | Primary `error-sweep` target (gateway.log + audit ndjson). Shared-clone hazard: verify HEAD before commit. Deploy ≠ merge. |
| `deckhand-sandbox` | PUBLIC | PR-only | Demo gallery. |
| `llm-wiki*` | PRIVATE | PR-only | Vendor-licensed standards; wiki-sibling routing rules apply. |
| `aceengineer-strategy` / `*-admin` / `achantas-data` / `investments` | PRIVATE | PR-only | Client/financial PII lives here — keep it here. |

Any repo not listed → treat as PR-only, no self-merge, ask before writing.

### 2. Loop registry

**Spine-of-3 (primary):**

- **`error-sweep`** (FF #004) — *default verify: independent.* Review recent production logs → trace each error to root cause → fix → verify the fix clears the log signature. Default target `deckhand`. Stop when no new error signatures remain or `--max-iters` hit.
  Inputs to read: gateway/service logs, audit ndjson. One iteration = pick the top-severity unresolved signature, reproduce, patch on a branch, verify, open PR.

- **`adversarial-review`** / alias `clodex` (FF #019) — *default verify: independent.* Run an **adversarial** code review (defect-hunting stance, default to non-APPROVE) over the working tree or a target diff → fix findings → re-review. Default target `digitalmodel`/`worldenergydata`. One iteration = review → triage findings by severity → fix MAJORs on a branch → re-review until a clean pass or `--max-iters`. If `--lane codex` produced the code, **hand-verify** (codex has silently broken engines before).

- **`loop-harness`** (FF #020) — *default verify: independent, mandatory.* The meta-wrapper: run `--run <inner-loop>` on the given cadence, but **gate shipping behind an independent verifier** that did not do the work. One iteration = run inner loop → independent `Agent` (or codex) verifies the artifact → ship (open PR) only on PASS; on FAIL, feed findings back as the next iteration's input. Requires `--run`.

**Optional (kept available):**

- **`docs-sweep`** (FF #001, nightly) — reconcile docs/wiki to the day's code changes. Feeds the bot↔wiki flywheel. Targets `digitalmodel`, `llm-wiki`.
- **`changelog`** (FF #008, nightly) — append a changelog entry from the day's merged changes. Slots into the existing 3am cron cadence.
- **`quality-streak`** (FF #009) — run scenarios; on failure document + fix until **N consecutive passes** (`--max-iters` = N). Target = Deckhand chat-rating harness.
- **`repo-cleanup`** (FF #012) — prune merged branches, stale PRs, dead worktrees until tree is current. **Advisory-only on workspace-hub.** Never delete unpushed/unique work — check `stash-archive/*` branches first.
- **`seo`** (FF #006) — SEO/GEO audit → fix indexability/answer-readiness gaps. Target `aceengineer-website`.
- **`batch-release`** (FF #013) — review pending merged-but-undeployed changes, exclude stale work, assemble a deploy set in correct merge order (compute-clone sync + redeploy gate).
- **`coverage`** (FF #005) — add tests toward a coverage target. **GATED: refuse on digitalmodel until the CI baseline is green** — print the gate and stop; suggest `error-sweep` first.

Unknown `--type` → print this registry and stop.

### 3. Verification gate (every iteration)

No iteration "ships" (opens a PR / writes an advisory) until verification passes:

- `self` — you re-check your own work against the stop condition. Lowest assurance; only for read-only/advisory loops.
- `independent` — dispatch a **fresh `Agent`** reviewer with an adversarial brief (it can't see this conversation — brief it like a smart colleague who just arrived). Default for all code-modifying loops.
- `codex` — delegate verification to codex (`codex exec`), then **hand-verify the codex output yourself** before trusting it.

A loop that can't pass verification within `--max-iters` stops and reports the unresolved delta — it does **not** lower the bar to claim success.

> **Gate exemption.** A loop is operational automation, not issue implementation — it does **NOT** route through the Issue→Plan→Approve→Implement gate. The human-merge step on its PR (and advisory-only on workspace-hub) is the control point. The plan→approve gate still applies if a loop's *finding* spawns a separate tracked issue for non-loop work.

### 4. Execution

1. Echo the resolved plan: `type`, `repo`, `REPO_PATH`, cadence, verify mode, max-iters, lane, stop condition, and the active guardrails for that repo. If `--dry-run` (or exploratory invocation): **stop here.**
2. Confirm the repo is clean / on the expected HEAD (`git -C "$REPO_PATH" status --short`, log -1). For `deckhand` verify HEAD first (shared-clone hazard).
3. For `--cadence now`: run the iterate-until-done loop, bounded by `--max-iters`. Use `ScheduleWakeup` only if an iteration must wait on an external signal (CI, a licensed run); otherwise iterate inline. Track iterations with TaskCreate/TaskUpdate.
4. For `--cadence nightly|weekly`: do NOT auto-register. Emit the exact `cron`/scheduler line and the loop invocation it would run, and ask the user to approve registration. (Per ecosystem cron rules: register via Python subprocess, not the blocked `crontab` binary.)
5. Code-modifying loops produce a **branch + PR** — never a direct push to a protected main, never a self-merge on `digitalmodel`. workspace-hub loops produce an **issue or advisory artifact**, not a commit.
6. Close out transactionally: report iterations run, what shipped (PR links as Markdown), what remains, and clean-state evidence. Render `#NNNN` as hyperlinks.

### 5. Stop conditions (never loop forever)

Stop and report when ANY holds: stop condition met · `--max-iters` reached · verification fails twice on the same finding · the repo's write policy would be violated · an external dependency (license, CI, quota) blocks progress. Always name the remaining delta on exit.

---
**Examples**
- `/loop-repo-ecosystem --type error-sweep --repo deckhand --verify independent --max-iters 3`
- `/loop-repo-ecosystem --type adversarial-review --repo digitalmodel --lane codex` (codex works, you hand-verify; PR only)
- `/loop-repo-ecosystem --type loop-harness --repo worldenergydata --run adversarial-review --verify independent`
- `/loop-repo-ecosystem --type docs-sweep --repo digitalmodel --cadence nightly` (proposes a schedule)
- `/loop-repo-ecosystem --type repo-cleanup --repo workspace-hub` (advisory-only)
