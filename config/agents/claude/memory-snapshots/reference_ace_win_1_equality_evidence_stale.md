---
name: reference_ace_win_1_equality_evidence_stale
description: ace-win-1 equality evidence is stale — last collected 2026-06-28; it self-publishes under Git Bash so a Linux box cannot refresh it. Records its last-known capabilities + the exact remediation.
metadata: 
  node_type: memory
  type: reference
  originSessionId: acc706a9-81c2-44f9-bdd1-a7840f58259d
---

Fleet-assessment finding, 2026-07-11 (dev-primary / ace-linux-1). On the reconciled matrix, **ace-win-1's snapshot is the stalest of the 4 machines**: `.claude/state/equality-ace-win-1.yaml` `generated_at: 2026-06-28T19:26:28` (~13 days old) while dev-primary/ace-win-2/dev-secondary are all ≤1 day. It cannot be refreshed from Linux — each Windows box **self-publishes** its own evidence under Git Bash (there is no repo-sync on Windows; see [[project_equality_matrix_reconcile_2026_07]]). So this is an on-box operator action, not something ace-linux-1 can drive.

**Last-known evidence (the 06-28 snapshot):**
- **Host** `ace-win-1`, Windows, `checkout_sha ccaf40b01`, clean (behind/ahead 0).
- **Compute** — the fleet's heavy iron: 64 cores, 256 GiB RAM (233 GiB avail), 1095 GB disk free. GPU is only ASPEED WDDM (no CUDA).
- **Solvers** — `orcaflex` present (root), `aqwa` present, `ansys` present; `orcawave` absent. This is the ANSYS/AQWA licensed box.
- **Data access** — assetutilities / digitalmodel / worldenergydata siblings; assethold nested.
- **Harness gaps (the actionable part):**
  - providers: only `claude: present`; **codex / gemini / hermes absent**.
  - `gh_auth: absent` — cannot push PRs or authenticate GitHub from the box.
  - `readiness_overall: missing`; provider_harness collectors all `unknown (collector_unavailable)`.
  - scheduler: `has_repo_sync: false`, `has_parity_review: false`, `job_count: 0` — **no Windows Task Scheduler jobs** (so nothing re-collects/publishes automatically → the 13-day staleness). Tracked as #2815 / #2998.
  - session_curation `last_curated_at: null` — `curate-session-memory.ps1` has never run here, so ace-win-1 contributes no session-curation evidence (4 dimension groups MISSING-EVIDENCE).

**Remediation (run ON ace-win-1, in Git Bash):**
1. `gh auth login` (closes the `gh_auth: absent` gap).
2. `bash scripts/readiness/collect-equality.sh && bash scripts/readiness/publish-equality.sh --rebuild` — regenerates + self-publishes fresh evidence to origin/main (the disposable-sparse-worktree publish path works from Windows too). This alone clears the staleness. See [[feedback_always_update_equality_matrix]].
3. Install a Windows Task Scheduler job (equivalent of Linux repo-sync / equality cron) so collect+publish recurs — the durable fix for #2815; until then ace-win-1 will re-stale after every manual run.
4. Optional per fleet intent: install codex / gemini / hermes if this box should be a full multi-provider node; today it is Claude-only + solver host.

**One-line status for the matrix:** ace-win-1 = heavy ANSYS/AQWA/OrcaFlex compute node, Claude-only, no scheduler, no gh auth → evidence goes stale between manual runs; needs an on-box collect+publish and a scheduler job. Not a Linux-side fix.
