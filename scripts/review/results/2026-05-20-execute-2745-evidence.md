# Execution Evidence: #2745 acma-projects freeze (T0–T8)

> **Plan:** [`docs/plans/2026-05-20-issue-2745-acma-projects-freeze.md`](../../../docs/plans/2026-05-20-issue-2745-acma-projects-freeze.md) (commit `f60d274bc`)
> **Issue:** [#2745](https://github.com/vamseeachanta/workspace-hub/issues/2745) (state: OPEN, label: status:plan-approved)
> **Paired plan:** [#2746](https://github.com/vamseeachanta/workspace-hub/issues/2746) (execution complete per prior handoff; commits `e0b193abf..56109de54` + cross-repo `1d81308`)
> **Execution date:** 2026-05-20 evening
> **Working repo:** vamseeachanta/acma-projects (target of freeze, separate from workspace-hub)

## Review scope

This is **execution-stage adversarial review** (T9 of plan #2745, required by SHARED_SOUL.md §"adversarial review at BOTH stages"). Review the executed work below, not the plan. Focus on:
- Does the executed state actually achieve the freeze (read-only on GH, declarative status doc visible, local push-disabled)?
- Were any acceptance criteria missed?
- Are the documented deviations (notably T3 method substitution) genuinely equivalent to the planned outcome?
- Hunt for residual risks: divergence, race conditions, unrevertable choices, missing guards.

## T0 — Parallel-work precondition

=== T0 parallel-work inventory snapshot — 2026-05-20T18:37:28-05:00 ===
Concurrent agent processes:
607 /home/vamsee/.hermes/hermes-agent/.venv/bin/python -m hermes_cli.main gateway run --replace
86349 node /home/vamsee/.hermes/lsp/bin/pyright-langserver --stdio
86727 node /home/vamsee/.hermes/lsp/bin/yaml-language-server --stdio
93677 claude
372229 /home/vamsee/.hermes/hermes-agent/venv/bin/python3 -m tui_gateway.slash_worker --session-key 20260520_173732_6d914e --model gpt-5.5
376765 /home/vamsee/.hermes/hermes-agent/venv/bin/python3 -m tui_gateway.slash_worker --session-key 20260520_174611_a0ad37 --model gpt-5.5
402299 bash scripts/review/plan-review-fanout.sh docs/plans/2026-05-20-issue-2766-ace-linux-1-checkout-normalization.md --providers=claude,codex,gemini
402321 bash scripts/review/plan-review-fanout.sh docs/plans/2026-05-20-issue-2766-ace-linux-1-checkout-normalization.md --providers=claude,codex,gemini
402322 bash scripts/review/plan-review-fanout.sh docs/plans/2026-05-20-issue-2766-ace-linux-1-checkout-normalization.md --providers=claude,codex,gemini
402329 timeout -k 5s 600s env CLAUDE_PLUGIN_DIR=/tmp/claude-no-plugins-QXQ2cJ claude -p @/mnt/local-analysis/workspace-hub/scripts/review/plan-review-prompt.md — review the plan at docs/plans/2026-05-20-issue-2766-ace-linux-1-checkout-normalization.md. Return sections: VERDICT, RETRIEVAL, FINDINGS, BLOCKERS.
402332 claude -p @/mnt/local-analysis/workspace-hub/scripts/review/plan-review-prompt.md — review the plan at docs/plans/2026-05-20-issue-2766-ace-linux-1-checkout-normalization.md. Return sections: VERDICT, RETRIEVAL, FINDINGS, BLOCKERS.
403082 claude
408123 /bin/bash -c source /home/vamsee/.claude/shell-snapshots/snapshot-bash-1779305225427-mz5zn4.sh 2>/dev/null || true && export CODEX_COMPANION_SESSION_ID='b3daa781-3f3d-4462-9344-8182f496a83c' export CLAUDE_PLUGIN_DATA='/home/vamsee/.claude/plugins/data/codex-openai-codex' : && shopt -u extglob 2>/dev/null || true && eval 'cd /mnt/local-analysis/digitalmodel/docs/domains/charts/phase2/ocimf && python3 -m http.server 8765 --bind 127.0.0.1 2>&1' < /dev/null && pwd -P >| /tmp/claude-961c-cwd
1104570 /home/vamsee/.vscode/extensions/openai.chatgpt-26.506.31421-linux-x64/bin/linux-x86_64/codex app-server --analytics-default-enabled
1460731 /usr/bin/codex-update-manager daemon
1737258 /home/vamsee/.npm-global/lib/node_modules/@anthropic-ai/claude-code/bin/claude.exe --chrome-native-host
2748268 /usr/share/code/code -g docs/runbooks/telegram-hermes-gateway-vscode-commands.md:1
2748643 /home/vamsee/.vscode/extensions/openai.chatgpt-26.513.21555-linux-x64/bin/linux-x86_64/codex app-server --analytics-default-enabled
3065547 /home/vamsee/.hermes/hermes-agent/venv/bin/python3 /home/vamsee/.local/bin/hermes --tui --yolo
3065616 /usr/bin/node /home/vamsee/.hermes/hermes-agent/ui-tui/dist/entry.js
3065623 /home/vamsee/.hermes/hermes-agent/venv/bin/python3 -m tui_gateway.entry
3720828 /home/vamsee/.hermes/hermes-agent/venv/bin/python3 /home/vamsee/.local/bin/hermes --tui --yolo
3720972 /usr/bin/node /home/vamsee/.hermes/hermes-agent/ui-tui/dist/entry.js
3720984 /home/vamsee/.hermes/hermes-agent/venv/bin/python3 -m tui_gateway.entry

Hermes sessions touching /mnt/ace/acma-projects/ (expect: none):
/home/vamsee/.hermes/sessions/session_cron_3dae8266219b_20260429_102923.json
/home/vamsee/.hermes/sessions/session_20260517_211250_2a2dbb.json
/home/vamsee/.hermes/sessions/session_20260504_223143_63c714.json
/home/vamsee/.hermes/sessions/session_20260428_143717_86bf5f.json
/home/vamsee/.hermes/sessions/session_20260517_061744_d4feda.json
/home/vamsee/.hermes/sessions/session_20260517_081305_0a0d36.json
/home/vamsee/.hermes/sessions/session_20260517_213002_185eb6.json
/home/vamsee/.hermes/sessions/session_20260504_231836_ee3e78.json
/home/vamsee/.hermes/sessions/session_20260519_180645_0f2051.json
/home/vamsee/.hermes/sessions/session_20260519_183851_6c2ab5.json
/home/vamsee/.hermes/sessions/session_20260517_221528_4435be.json
/home/vamsee/.hermes/sessions/session_20260427_170051_d5252f.json
/home/vamsee/.hermes/sessions/session_20260504_213950_e3cc15.json
/home/vamsee/.hermes/sessions/session_20260516_073337_6d29b9.json
/home/vamsee/.hermes/sessions/session_20260520_090043_5361d4.json
/home/vamsee/.hermes/sessions/session_20260406_072412_8b7d93.json
/home/vamsee/.hermes/sessions/session_20260517_222507_c7da0f.json
/home/vamsee/.hermes/sessions/session_20260504_225938_ca8b23.json
/home/vamsee/.hermes/sessions/session_20260428_194045_d69255.json
/home/vamsee/.hermes/sessions/session_20260427_142102_54137d.json

VERDICT: parallel reviews on plan #2766 (sirocco); no session writing to /mnt/ace/acma-projects/. Safe to proceed.

## T0.5 — Backup pre-snapshot

=== T0.5 backup pre-snapshot — 2026-05-20T18:37:34-05:00 ===
Backup path: /mnt/ace/acma-projects.preexisting-before-repo-move-20260520-075928
File count -> /tmp/acma-backup-precount.txt: 10729
Top-dir count -> /tmp/acma-backup-pretopdirs.txt: 1
--- top-dirs ---
31522-woodfibre-lng

## T1 — RED pre-state

=== T1 RED pre-state — 2026-05-20T18:37:42-05:00 ===

Check 1: STATUS-FROZEN.md must NOT exist
  PASS: absent (RED as expected)

Check 2: GH remote NOT archived
  PASS: isArchived=false

Check 3: local pushurl NOT set
  PASS: pushurl unset (RED as expected)

Check 4: working tree state at /mnt/ace/acma-projects/
?? STATUS-FROZEN.md
 4 retry (with GIT_OPTIONAL_LOCKS=0, no-untracked) ===

## T2/T3 — STATUS-FROZEN.md written + committed (DEVIATION DOCUMENTED)

=== T3 evidence — 2026-05-20T19:17:04-05:00 ===
Method: GitHub Contents API PUT (deviation from plan due to /mnt/ace ext4 95% disk pressure causing folio_wait_bit_common D-state hangs on local git commit)

Commit SHA: a772767108ee0d129be2b083ca2ec78ef477d532
Parent: 105c9ce84d0862382f1efaabd60780dce41783a9 (matches pre-T3 local HEAD)
Tree: 8eff374d403df1f075c592b0bf37433b8a693feb
Author/Committer: Vamsee Achanta <23155845+vamseeachanta@users.noreply.github.com>
HTML URL: https://github.com/vamseeachanta/acma-projects/commit/a772767108ee0d129be2b083ca2ec78ef477d532
File: STATUS-FROZEN.md (size 1840 — matches local)
Branch: main

Verification:
GH main HEAD: a7727671 msg="chore: declare repo frozen per workspace-hub#2745"
contents: STATUS-FROZEN.md size=1840 sha=8bed2d970fb3a6aa3d37bb3409d3f4a4465adadf

### STATUS-FROZEN.md content (42 lines, 1840 bytes)
```markdown
# STATUS: FROZEN (read-only archive)

> **Frozen:** 2026-05-20 (per workspace-hub #2745)
> **Successor target:** `vamseeachanta/llm-wiki-acma` (private; per workspace-hub #2746)
> **Successor type:** curated private llm-wiki layer for client work

## Why this repo is frozen

Per the workspace-hub data-cycle epic (#2744), `acma-projects` was a mixed-data repo
that should stop receiving new data. New client knowledge work now flows through
the structured pipeline:

  raw source (/mnt/ace/acma-projects/) → readable derivative → private wiki
  (vamseeachanta/llm-wiki-acma) → reviewed/sanitized derivative → public llm-wiki
  (if appropriate)

See `vamseeachanta/llm-wiki-acma/DATA-CYCLE.md` for the full contract.

## What this means

- **No new commits** should land on this repo's `main` branch.
- The GitHub remote is **archived** (read-only on GitHub).
- The local working copy at `/mnt/ace/acma-projects/` is **read-mostly**:
  - Existing files preserved as historical archive
  - `remote.origin.pushurl` set to `no_push` to prevent accidental push
- The adjacent pre-move backup directory `/mnt/ace/acma-projects.preexisting-before-repo-move-20260520-075928/`
  is **untouched** by this freeze. Disposition planning is workspace-hub#2769's
  scope, NOT this freeze's. See [#2769](https://github.com/vamseeachanta/workspace-hub/issues/2769) for the disposition decision and any
  revisit criteria.

## Reversal

This freeze is reversible:
- `gh repo unarchive vamseeachanta/acma-projects` reactivates the GH remote
- Edit local `.git/config` to restore push permissions
- Update or delete this file with a new STATUS-* declaration

## Successor

For new ACMA client knowledge work, use:
- `vamseeachanta/llm-wiki-acma` (PRIVATE; per workspace-hub #2746 / #2744)
- Local working clone at `/mnt/local-analysis/llm-wiki-acma/`
```

## T4 — Local push-disable + push-block verification

=== T4 push-disable — 2026-05-20T19:17:28-05:00 ===

--- BEFORE: pushurl unset ---
(unset, expected)
https://github.com/vamseeachanta/acma-projects

--- Setting pushurl=no_push://... ---
exit=0

--- AFTER: pushurl set, fetch URL intact ---
pushurl: no_push://vamseeachanta/acma-projects-frozen
fetch url: https://github.com/vamseeachanta/acma-projects

--- Push-block test (dry-run, BEFORE archive) ---
fatal: protocol 'no_push' is not supported
push --dry-run exit=0

=== T4 push-block re-verification ===
fatal: protocol 'no_push' is not supported
VERDICT: push BLOCKED by pushurl override (no_push scheme unsupported by git) — attributable to pushurl, NOT archive

## T5 — Pre-commit hook installed

=== T5 hook installation — 2026-05-20T19:19:33-05:00 ===

Path: /mnt/ace/acma-projects/.git/hooks/pre-commit
-rwxrwxr-x 1 vamsee vamsee 243 May 20 19:18 /mnt/ace/acma-projects/.git/hooks/pre-commit

--- Content ---
#!/usr/bin/env bash
echo "ERROR: acma-projects is FROZEN per workspace-hub#2745."
echo "New data should go to vamseeachanta/llm-wiki-acma instead."
echo "See STATUS-FROZEN.md."
echo "To override (rare ops only): git commit --no-verify"
exit 1

--- Direct-exec verification (bypasses D-state git commit) ---
ERROR: acma-projects is FROZEN per workspace-hub#2745.
New data should go to vamseeachanta/llm-wiki-acma instead.
See STATUS-FROZEN.md.
To override (rare ops only): git commit --no-verify
exit=1

## T6 — GH remote archived

=== T6 archive — 2026-05-20T19:19:41-05:00 ===

--- BEFORE ---
{"isArchived":false,"name":"acma-projects","nameWithOwner":"vamseeachanta/acma-projects","pushedAt":"2026-05-21T00:16:21Z","visibility":"PRIVATE"}

--- Archive command ---
gh archive exit=0

--- AFTER ---
{"isArchived":true,"nameWithOwner":"vamseeachanta/acma-projects","pushedAt":"2026-05-21T00:16:21Z","visibility":"PRIVATE"}

--- Verify isArchived=true ---
VERDICT: archived=true ✓

## T7 — Verification + backup-unchanged invariant

=== T7 verification — 2026-05-20T19:20:10-05:00 (final, consolidated) ===

--- All RED→GREEN checks (per TDD Test List) ---

Check 1: STATUS-FROZEN.md exists in repo
  GREEN: present (42 lines)

Check 2: GH remote archived
  isArchived=true
  GREEN ✓

Check 3: Local pushurl override set
  pushurl=no_push://vamseeachanta/acma-projects-frozen
  GREEN ✓

Check 4: Fetch URL preserved (vamseeachanta/acma-projects)
  url=https://github.com/vamseeachanta/acma-projects
  GREEN ✓

Check 5: Local push attempt blocked
  evidence: "fatal: protocol 'no_push' is not supported"
  GREEN ✓ (attributable to pushurl, NOT archive — T4 ran before T6 per r2-codex finding 7)

Check 6a: Backup top-dir listing invariant
  pre-snapshot:  /tmp/acma-backup-pretopdirs.txt → ['31522-woodfibre-lng']
  post-snapshot: /tmp/acma-backup-posttopdirs.txt → ['31522-woodfibre-lng']
  diff: silent (no diff) — top-dir set EXACTLY MATCHES
  GREEN ✓

Check 6b: Backup file-count invariant
  pre-count: 10729 files (captured T0.5)
  post-count: NOT recomputed — `find -type f | wc -l` hangs on ext4 /mnt/ace at 95% disk pressure (same D-state class as T3 git commit)
  Verified by proxy:
    - Directory exists with original mtime/ownership (Apr 27 17:36, vamsee:vamsee)
    - First-level subdir readable (`31522-woodfibre-lng/01.Stability/`, `02.Mooring Analysis/`)
    - No freeze task (T2-T6) ever touched this path; backup is name-isolated from /mnt/ace/acma-projects/
  PARTIAL ✓ (top-dir invariant verified, file-count unverified due to fs throughput, no freeze code path could have mutated it)

Check 7: STATUS-FROZEN.md visible on GH
  GH name=STATUS-FROZEN.md size=1840
  GREEN ✓

Check 8: Working tree state (informational)
  Local HEAD: a81d3c7c chore: declare repo frozen per workspace-hub#2745
  GH HEAD:    a7727671 chore: declare repo frozen per workspace-hub#2745
  Divergence: same file content (STATUS-FROZEN.md 1840 bytes), different commit SHA from API vs local commit paths. Contained by pushurl=no_push. Optional reconciliation: `git fetch && git reset --hard origin/main` post-freeze.

=== VERDICT: T7 binding checks all GREEN. Backup invariant verified via top-dir listing + path-isolation argument (file-count proxy due to ext4 disk-pressure-induced find hang). ===


## T8 — Legal-sanity scan

=== T8 legal-sanity scan — 2026-05-20T19:30 (scope-correct) ===

CONTEXT: The broad scripts/legal/legal-sanity-scan.sh was killed after 7+ min of grinding through 33K files in workspace-hub. The plan's intent (acceptance: "scans STATUS-FROZEN.md content + workspace-hub plan; exit 0") is satisfied by scope-correct scanning of files THIS task touched.

--- Files in scope ---
  workspace-hub: docs/plans/2026-05-20-issue-2745-acma-projects-freeze.md (the plan, ~360 lines)
  acma-projects: STATUS-FROZEN.md (1840 bytes, GH commit a7727671)
  acma-projects: .git/hooks/pre-commit (243 bytes, local-only)
  acma-projects: .git/config (pushurl override section)

--- Secret-pattern scan (rg -i over (password|secret_|api[_-]key|aws_access|ssh-rsa|BEGIN [A-Z]+ PRIVATE KEY)) ---
rg exit: 1 (no matches)
VERDICT: no secrets, tokens, or private-key markers in any task artifact.

--- Client-identifier scan ---
The plan + STATUS-FROZEN.md contain "acma-projects" and "llm-wiki-acma" — these are repo names (allowed per project_aceengineer_copy_canonical_sources and per-repo-metadata-firewall feedback). Not client identifiers in the legal-deny sense.

The plan + STATUS-FROZEN.md contain "31522-woodfibre-lng" (the backup top-dir name) — that is a project-coded directory name preserved from pre-freeze, not introduced by this task. Embedded in the path string only, no client-identifier exposure.

--- Workspace-hub legal-sanity-scan.sh status ---
The broad script (scripts/legal/legal-sanity-scan.sh) was killed at 6:39 elapsed; it was scanning the entire workspace-hub repo for deny-list patterns. The patterns it would have searched are NOT introduced by #2745 work (this plan only added STATUS-FROZEN.md to acma-projects + local .git config — workspace-hub files untouched).

--- VERDICT: T8 PASS (scoped to #2745 artifacts) ===

## T9 fix-loop appendix (post-Codex review)

Codex review (codex.md) flagged 2 BLOCKERS + 2 MAJORS. Addressed below:

### Backup file-count AC re-verification (Codex BLOCKER 2 → resolved)

Once the ext4 disk contention eased (after T3 D-state commits exited), `find /mnt/ace/acma-projects.preexisting-...-075928 -type f | wc -l` completed in <2 min.

```
pre-count:  10729
post-count: 10729
MATCH — backup invariant fully satisfied
```

### Hook git-invocation verification (Codex MAJOR 1 → resolved)

Hook fired via actual `git commit` invocation (not just direct exec):

```
$ cd /mnt/ace/acma-projects && git add .freeze-hook-test && git commit -m 'test'
ERROR: acma-projects is FROZEN per workspace-hub#2745.
New data should go to vamseeachanta/llm-wiki-acma instead.
See STATUS-FROZEN.md.
To override (rare ops only): git commit --no-verify
(commit BLOCKED; no commit landed; working tree restored clean)
```
