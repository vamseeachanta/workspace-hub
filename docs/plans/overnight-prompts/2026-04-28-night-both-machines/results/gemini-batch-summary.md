Agent loading error: Failed to load agent from /mnt/local-analysis/workspace-hub/.gemini/agents/gsd-debugger.md: Validation failed: Agent Definition:
Unrecognized key(s) in object: 'permissionMode'Agent loading error: Failed to load agent from /mnt/local-analysis/workspace-hub/.gemini/agents/gsd-executor.md: Validation failed: Agent Definition:
Unrecognized key(s) in object: 'permissionMode'# Action Reconnaissance Report

Here is the requested reconnaissance report based on the provided issue context.

## Issue #2295: 2025 TX franchise No Tax Due + PIR
* **Current State:** Tax filing preparation for SKEstates and AceEngineer is required by May 15, 2026. SKEstates data exists in YAML; AceEngineer data needs to be modeled. A handover prompt is ready at `sabithaandkrishnaestates/taxes/2025/tx-franchise-handover-prompt.md`. 
* **Gaps/Blockers:** AceEngineer YAML data file must be created first. Human approval is strictly required before final Webfile submission.
* **Recommended Next Status/Labels:** `status:plan-approved` (ready for local data prep).
* **Exact Next Implementation Prompt:**
  > "Read the SKEstates YAML data file as a template. Create the `tx-franchise-filing-data.yaml` file for AceEngineer Inc using the revenue and entity data provided in issue #2295. Once created, execute the steps in `sabithaandkrishnaestates/taxes/2025/tx-franchise-handover-prompt.md` to prepare the Webfile submissions. Stop and prompt for human review before any external submission is made."
* **Verification Commands:**
  ```bash
  cat sabithaandkrishnaestates/taxes/2025/tx-franchise-filing-data.yaml
  cat aceengineer/taxes/2025/tx-franchise-filing-data.yaml
  ls -la taxes/2025/filed/
  ```

## Issue #2501: chore(planning): #2105 governance-lock — handoff vs live-state
* **Current State:** A discrepancy exists between a handoff document stating v5 planning is needed for #2105, and the live GitHub state which shows #2105 as `status:plan-approved`. 
* **Gaps/Blockers:** Strictly blocked on user clarification regarding whether to execute the v4 plan or initiate a v5 planning session.
* **Recommended Next Status/Labels:** `status:blocked`, `status:needs-clarification`.
* **Exact Next Implementation Prompt:**
  > "Read the user's response to the clarification request on #2501. If the user confirms #2105 is ready to execute, update labels, schedule the execution routine for #2105, and subsequently unblock #2483 and #2484. If the user requests a v5 plan, initiate a new planning session for #2105."
* **Verification Commands:**
  ```bash
  gh issue view 2105 --json labels,state
  gh issue view 2501 --comments
  ```

## Issue #2254: fix(provider-telemetry): improve Claude and Gemini quota observability
* **Current State:** A plan is drafted at `docs/plans/2026-04-26-issue-2254-claude-gemini-quota-observability.md` with 19 TDD tests mapped out. It is currently in a draft state waiting for human review on two specific policy questions (absent confidence routing behavior and Anthropic key location).
* **Gaps/Blockers:** Waiting for human answers to the two policy questions and final plan approval.
* **Recommended Next Status/Labels:** `status:plan-review`.
* **Exact Next Implementation Prompt:**
  > "Incorporate the user's answers to the two policy questions on #2254 into the plan at `docs/plans/2026-04-26-issue-2254-claude-gemini-quota-observability.md`. Transition the issue to `status:plan-approved`. Then, implement the quota extraction logic and the 19 TDD tests exactly as defined in the plan."
* **Verification Commands:**
  ```bash
  pytest tests/ # or appropriate test runner defined in the plan
  scripts/ai/assessment/query-quota.sh --refresh --json
  ```

## Issue #2519: feat(hermes): orchestrate AI provider usage and workstation dispatch
* **Current State:** Prompt packs for parallel execution on `ace-linux-1` and `ace-linux-2` have been generated and merged (`docs/plans/machine-prompts/2026-04-27/`). There is extreme urgency to burn down expiring Codex credits in the next 24 hours. `ace-linux-2` is restricted to local execution due to a broken GitHub auth token.
* **Gaps/Blockers:** Awaiting the dispatch of the prompt packs. Full delegation to `ace-linux-2` is partially blocked by #2520.
* **Recommended Next Status/Labels:** `status:executing`.
* **Exact Next Implementation Prompt:**
  > "Initialize the Hermes workstation dispatch sequence. Dispatch the `ace-linux-1-continuous-parallel-work-prompt.md` to `ace-linux-1` to handle GitHub mutations and control-plane tasks. Concurrently, dispatch the `ace-linux-2-continuous-parallel-work-prompt.md` to `ace-linux-2` via a login shell (`ssh ace-linux-2 'bash -lc ...'`) for local Codex-heavy execution, ensuring no GitHub mutations are attempted on ace-linux-2."
* **Verification Commands:**
  ```bash
  cat docs/reports/provider-work-queue.md
  # Check Codex burn-down
  scripts/ai/assessment/query-quota.sh --refresh --json | grep codex
  ```

## Issue #2520: fix(workstations): repair and gate ace-linux-2 GitHub auth
* **Current State:** `ace-linux-2` has an invalid GitHub CLI token, preventing it from performing autonomous repository mutations (comments, PRs, labels).
* **Gaps/Blockers:** Requires manual intervention to re-authenticate `gh` on the remote machine. A pre-delegation readiness script needs to be authored.
* **Recommended Next Status/Labels:** `status:in-progress` or `status:blocked` (on manual auth).
* **Exact Next Implementation Prompt:**
  > "Create the pre-delegation readiness check script for `ace-linux-2` as specified in #2520. The script must be runnable from `ace-linux-1` and verify SSH BatchMode, login-shell PATHs, Hermes configuration, Codex CLI presence, GH auth status, and repo canonical path presence. Output a clear PASS/FAIL matrix."
* **Verification Commands:**
  ```bash
  ssh -o BatchMode=yes ace-linux-2 'bash -lc "gh auth status"'
  ./scripts/workstations/ace-linux-2-preflight-check.sh
  ```

---

## Ranked Summary

Ranked by **next-action readiness** and **AI-credit value** (specifically targeting the urgent Codex expiry):

1. **#2519 (Hermes Workstation Dispatch)**
   * **Readiness:** High (Prompt packs are merged and ready for dispatch).
   * **Value:** Critical. High AI-credit value as it directly addresses the urgent ~24-hour Codex credit expiry burn-down.
2. **#2295 (TX Franchise Tax Prep)**
   * **Readiness:** High (Data creation can start immediately, clear templates exist).
   * **Value:** High. Real-world hard deadline (May 15), highly bounded and structural task perfectly suited for AI generation.
3. **#2520 (Repair ace-linux-2 GH Auth)**
   * **Readiness:** Medium (Needs a human `gh auth login` step, but the pre-flight script can be coded immediately).
   * **Value:** High. Unblocks full autonomous delegation for the secondary workstation, which scales overall throughput.
4. **#2254 (Provider Telemetry)**
   * **Readiness:** Medium (Waiting on human review for two policy questions).
   * **Value:** Medium-High. Essential for future AI cost optimization, but less urgent than the immediate Codex expiry.
5. **#2501 (Governance-lock Handoff)**
   * **Readiness:** Low (Strictly blocked on user clarification).
   * **Value:** Low. Administrative blocker requiring human input before any AI action can proceed.
