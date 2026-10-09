# Judge-Ready Incomplete Closeout for Codex Burn Waves

Use this reference when an autonomous Codex burn / overnight bundle run is terminal but not fully successful, especially when the user asks for evidence that a judge or checklist can evaluate.

## Core principle

Separate **terminal process state** from **successful task outcome**:

- `terminal`: every requested Codex bundle/lane has stopped running.
- `succeeded`: requested issues were landed/closed with evidence and acceptance criteria satisfied.
- `blocked_partial`: at least one requested issue in the bundle is complete/closed but another remains open or has unmet acceptance criteria.
- `failed`: the lane produced no usable result and no accepted blocker evidence.
- `running`: a matching Codex process/session remains active.
- `unknown`: evidence is insufficient to classify; do not promote to success.

A wave can be `launched=3`, `terminal=3`, `succeeded=1`, `blocked_partial=2`, `running=0`, and still be **overall incomplete**. Report it that way.

## Minimum final evidence bundle

Write both Markdown and JSON under the run directory, commonly:

- `monitoring-evidence/<run>-judge-ready-final-incomplete-report.md`
- `monitoring-evidence/<run>-judge-ready-final-incomplete-report.json`

Include:

1. Requested bundle inventory: bundle name, repo, issue numbers, prompt path, worktree path, log path.
2. Counts: requested, launched, terminal, succeeded, blocked_partial, failed, omitted, running, unknown.
3. Live-state refresh evidence, preferably repeated at least twice near closeout:
   - `gh issue view ... --json state,labels,comments,url,title`
   - `git status --short --branch`
   - `git rev-parse HEAD`
   - `git ls-remote origin refs/heads/<branch>`
   - narrow process check for Codex runs scoped to the run directory.
4. Per-bundle conclusion with the exact reason it is `succeeded`, `blocked_partial`, `failed`, or `unknown`.
5. Human-in-loop blockers separated from execution failures.
6. Retrospective evidence impossibilities: missing original PID/exit sidecars, missing Hermes process handles after exit, byte-for-byte launch command gaps, or absent poll chronology.
7. Final artifact hashes after all redaction and manual edits.

## Human-in-loop blocker examples

Treat these as blockers, not failures and not success:

- Approval evidence is contradictory or missing for a GitHub issue that requires plan approval.
- Local approval marker exists but is not truthful or not aligned with the GitHub issue body.
- Acceptance criteria remain unmet and require a new bounded continuation lane.
- External/legal/account/payment/deployment/credential action is required.

For each blocker, name the required human decision or explicit authorization. Do not continue autonomous mutation through a gate just to improve burn utilization.

## Redaction and secret-scan refinement

Run a strict scan for unredacted secret-like values after writing evidence. Avoid false positives from redaction placeholders.

Recommended high-confidence patterns:

```python
patterns = [
    r"gh[pousr]_[A-Za-z0-9_]{20,}",
    r"github_pat_[A-Za-z0-9_]{20,}",
    r"sk-[A-Za-z0-9]{20,}",
    r"AKIA[0-9A-Z]{16}",
]
```

Ignore lines that contain intentional placeholders such as `[REDACTED]`. If a broad earlier scan matched `gho_[REDACTED]`, record that it matched a placeholder and then write a refined scan result such as:

```text
NO_UNREDACTED_SECRET_PATTERN_HITS
```

After the refined scan, recompute and report hashes for the Markdown report, JSON report, and scan artifact.

## Repeated checklist continuations after terminal incomplete state

When the user or harness repeats a long checklist-style prompt after all originally requested bundles are already terminal:

1. Refresh evidence, do not relaunch by inertia:
   - read the manifest / prior report;
   - re-run scoped process checks;
   - re-query live GitHub issue state for every open or recently closed issue;
   - re-check each worktree's branch, HEAD, upstream, and dirty status;
   - re-hash evidence artifacts and run a refined secret scan.
2. Set `new_launches_this_turn: 0` when no explicit new bundle set or authorization is present.
3. State the reason no new launches occurred in operational terms, e.g. "requested bundle set already terminal; remaining work is human/governance-gated".
4. Preserve the requested-bundle inventory and reconcile counts again. Do not let repeated prompts expand the requested set unless the user names additional bundle IDs/issues/paths.
5. If continuation would cross a plan approval, legal/security, credential, deployment, or scope boundary, stop with the exact required user decision rather than launching a "continuation" lane to spend quota.
6. Do not fabricate unrecoverable launch facts. If PID/PPID/exit sidecars or exact poll chronology were not captured at original launch time, label them unrecoverable without fabrication and continue with available log/session/GitHub evidence.

## User-facing closeout format

Keep the final response concise:

- State that the operation is incomplete if any requested bundle remains blocked/open.
- List the report paths and hashes.
- Provide the reconciled inventory JSON, including `new_launches_this_turn` for repeated checklist prompts.
- Provide a small bundle table with final statuses.
- Name the exact human/governance inputs required before more autonomous work.

Do not bury the blocker behind process detail; the key closeout is whether further autonomous execution is allowed and useful.