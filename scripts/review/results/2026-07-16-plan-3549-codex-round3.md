## Verdict
MAJOR

## Retrieval
- Read `docs/plans/2026-07-16-issue-3549-registry-connection-helpers.md` lines 1–400.
- Read `docs/superpowers/specs/2026-07-15-3549-registry-connection-helpers-design.md` lines 1–356.
- Read merged runbook `24d6c66d:docs/ops/remote-linux-access.md`.
- Read `src/workspace_hub/workstations/resolver.py` lines 1–135.
- Read `scripts/enforcement/install-hooks.sh` lines 1–308.
- Read all tracked files under `scripts/operations/connection/` and grepped them, `config/tabby/`, `config/workstations/registry.yaml`, and `docs/modules/cli/` for target and identity literals.
- Inspected `config/workstations/registry.yaml` and `config/tabby/config.yaml`.
- Read `.github/workflows/enforcement-gate.yml`, `.github/workflows/completeness-gate.yml`, `scripts/workflow/completeness_score.py`, and `scripts/workflow/render_completeness_html.py`.
- Read prior round-two artifacts under `scripts/review/results/*3549*round2.md`.
- Queried live GitHub state for issues #3549, #3550, #3435, #3552 and PR #3553.
- Queried the official Gitleaks v8.30.1 release and asset metadata; verified the checksum-manifest digest cited by the plan.
- Ran PyYAML duplicate-key probes for registry and overlay shapes; both silently retained the last value.
- Ran the inherited workstation command from plan lines 84–90; this sparse review worktree produced missing-file errors, so it could not independently reproduce the claimed full-checkout baseline.
- Inspected tracked-tree contents at current HEAD and merged commit `24d6c66d`, including the two `.fuse_hidden*` connection files.

## Findings
1. The strict-schema contract does not reject duplicate YAML mapping keys. Plan lines 143–159 and design lines 205–213 require complete validation before hashing, but the test matrix at plan lines 227–230 covers unknown keys and wrong types—not duplicate keys. `src/workspace_hub/workstations/resolver.py:38-50` uses `yaml.safe_load`, which empirically parsed duplicate `ssh` and duplicate overlay `address` fields by silently retaining the final value. This permits ambiguous security policy and attestation content to enter the supposedly strict snapshot. Both registry and overlay loaders need duplicate-key rejection tests and a rejecting loader.

2. Fallback freshness semantics are under-specified. The design defines `max_age_seconds`, `verified_at`, and `expires_at` at `docs/superpowers/specs/2026-07-15-3549-registry-connection-helpers-design.md:165-195`, while plan lines 255–260 test only generic “freshness” and the TDD table at line 230 names only “stale.” Nothing requires rejection of future-dated verification, `expires_at <= verified_at`, or an expiry interval exceeding policy `max_age_seconds`. A loader can therefore satisfy the listed stale test while allowing an attestation to remain valid longer than registry policy permits.

3. The governed-surface inventory is empirically incomplete. Plan lines 20 and 78 claim five helpers plus Tabby and `governed_existing_files=6`; lines 217–221 defer only `vnc-ace-linux-2.sh`. The tracked tree also contains `scripts/operations/connection/.fuse_hidden0002aeb10000414f` and `.fuse_hidden0002aeb100013f84`, both byte-identical VNC/SSH helper copies containing a fixed operator/host target. They also exist in merged commit `24d6c66d`. Plan lines 138 and 235 require every target-bearing surface to be classified, but the plan neither names, deletes, nor explicitly defers these unstable artifact paths.

4. The linked-worktree acceptance criterion conflicts with the declared scope. Plan lines 281–283 and 320–321 claim `install-hooks.sh` will work in normal and linked worktrees, while risk lines 388–391 say #3549 will change only the endpoint-guard insertion path and defer broader installer hardening to #3435. Yet `scripts/enforcement/install-hooks.sh:32`, `:47`, `:73`, and `:248` still construct `${REPO_ROOT}/.git/hooks/...`; in a linked worktree `.git` is a file, and the first `cp` at line 38 exits under `set -e`. Resolving only the new guard’s insertion path cannot make the installer pass a real linked-worktree test. The plan must either authorize conversion of every hook destination in this installer or narrow the acceptance claim and defer linked-worktree support.

5. The review-artifact pointers do not resolve. Plan lines 9 and 116–118 name `2026-07-16-plan-3549-{claude,codex,gemini}.md`, but all three files are absent; only `*-round1.md` and `*-round2.md` exist. Plan line 359 additionally claims the canonical Gemini stub was retained, which is false in the reviewed tree. Current review evidence must be written to revision-stamped, non-empty paths and the plan pointers updated before the review gate is represented as complete.

6. Plan line 317 specifies bare `python scripts/enforcement/check-connection-helper-endpoints.py --staged`, contradicting the repository command contract requiring `uv run` for Python. This also assumes a `python` executable exists independently of the plan’s uv-managed runtime. Use the reviewed runtime form consistently or explicitly justify a directly executable stdlib hook entry point.

## Blockers
- Finding 1 — add fail-closed duplicate-key handling and RED tests for both YAML documents.
- Finding 2 — define and test the complete timestamp ordering and maximum-age contract.
- Finding 3 — reconcile all tracked `.fuse_hidden*` target-bearing artifacts with the exact manifest and changed-path authority.
- Finding 4 — resolve the installer scope contradiction before claiming linked-worktree support.
