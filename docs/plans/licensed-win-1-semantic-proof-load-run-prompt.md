# Licensed-Win-1 Semantic-Proof Load/Run Prompt

> **Machine:** licensed-win-1 (Windows, `D:\workspace-hub`).
> **Purpose:** execute the load-only and (where bounded) run proofs defined by `docs/solver/orcawave-orcaflex-native-load-run-proof-protocol.md` for the first-wave semantic-proof fixtures.
> **Issue:** [#2475](https://github.com/vamseeachanta/workspace-hub/issues/2475). Companion fixtures: [#2455](https://github.com/vamseeachanta/workspace-hub/issues/2455), [#2456](https://github.com/vamseeachanta/workspace-hub/issues/2456), [#2457](https://github.com/vamseeachanta/workspace-hub/issues/2457).
> **Available on this machine:** Claude Code CLI, Codex CLI, Gemini CLI, Python, Git Bash, OrcFxAPI. **Not available:** Hermes, `uv`. Use `python` (not `uv run`) everywhere.

This prompt is self-contained — an operator (human or agent) can paste the agent-facing block below into a single `claude -p` / `codex -p` invocation, or follow it manually step by step.

## When to use this prompt

Use it when both of these are true:

1. The dev-primary deterministic semantic-proof tests for the target fixture have shipped and are CLOSED (issues #2455 / #2456 / #2457 in the first wave).
2. The licensed machine is reachable, OrcFxAPI imports successfully, and the local `D:\workspace-hub` clone is up to date.

If either is false, comment on #2475 explaining the gap and stop — do not attempt level 2 against an unverified level 1.

## Prerequisites (run once per session)

```powershell
cd D:\workspace-hub
git pull origin main

cd digitalmodel
git pull origin main
cd ..

python -c "import OrcFxAPI; print('OrcFxAPI', OrcFxAPI.version())"
python -c "import yaml; print('pyyaml OK')"
python -c "import openpyxl; print('openpyxl OK')"
python -c "import numpy; print('numpy OK')"
```

If any non-OrcFxAPI import fails, install on this machine (does not require admin):

```powershell
python -m pip install pyyaml openpyxl numpy
```

If the OrcFxAPI import fails, classify the run as `missing license/API`, write the manifest, post a GitHub comment, and stop. Do not attempt to install OrcFxAPI from this prompt.

## Agent-facing prompt (paste between the fences)

```
You are an engineering automation agent on licensed-win-1 (Windows).
Workspace: D:\workspace-hub (this repo) and D:\workspace-hub\digitalmodel (sibling repo).
Use python (not uv run). OrcFxAPI is available. Hermes is NOT available.

Operating contract: docs/solver/orcawave-orcaflex-native-load-run-proof-protocol.md
This is the protocol for issue #2475. Do not exceed the scope defined there.
Fixtures in scope: #2455 (rigid jumper PLET-to-PLEM), #2456 (lazy/steep-wave riser),
#2457 (OrcaWave L03 ship roundtrip). Do not invent new fixture families.

WORKFLOW (per fixture):

  STEP A — Discover the generated native input
    For the fixture under proof, locate the generated native input file produced
    by the dev-primary semantic-proof harness. Search both:
      digitalmodel\tests\fixtures\
      digitalmodel\src\digitalmodel\hydrodynamics\diffraction\fixtures\
    If the file is not present, classify the attempt as "missing input artifact",
    write the evidence manifest, post the GitHub comment, and move to the next
    fixture. Do not regenerate the native input on this machine — generation is
    a dev-primary responsibility.

  STEP B — Level 2: load-only proof
    For OrcaWave (.owd / .yml):
      python -c "import OrcFxAPI; d = OrcFxAPI.Diffraction(r'<input>'); print('LOADED', 'state=', d.state, 'freqs=', d.frequencyCount, 'headings=', d.headingCount, 'bodies=', d.bodyCount)"
    For OrcaFlex (.dat / .yml):
      python -c "import OrcFxAPI; m = OrcFxAPI.Model(r'<input>'); print('LOADED', 'objects=', m.objectCount)"
    Capture stdout and stderr to a console-log path that the manifest will
    reference. If the load call raises, classify as "semantic mismatch"
    (or "missing license/API" if OrcFxAPI itself failed to import).

  STEP C — Decide whether level 3 is allowed
    Refer to the protocol's §4 fixture table. Level 3 is allowed only when the
    fixture is documented as bounded (e.g., PLET-to-PLEM statics + brief
    dynamics; lazy/steep-wave riser similarly). For OrcaWave L03 ship, default
    to skip-run unless the operator confirms a reduced grid before running.
    If level 3 is not allowed, record classification "skip-run" alongside
    "pass-load" from step B and proceed to the manifest step.

  STEP D — Level 3: run proof (only when bounded)
    For OrcaWave (only with confirmed reduced grid):
      python -c "import OrcFxAPI; d = OrcFxAPI.Diffraction(r'<input>'); d.Calculate(); d.SaveResults(r'<output.owr>'); print('RAN', 'state=', d.state)"
    For OrcaFlex (with bounded StageDuration):
      python -c "import OrcFxAPI; m = OrcFxAPI.Model(r'<input>'); m.CalculateStatics(); m.RunSimulation(); m.SaveSimulation(r'<output.sim>'); print('RAN', 'objects=', m.objectCount)"
    Wrap the run with a wall-clock timer; if it exceeds 15 minutes, abort and
    classify as "runtime/disk guard exceeded" (level 2 still passes).

  STEP E — Author the evidence manifest
    Copy docs/solver/templates/semantic-proof-evidence-manifest.yaml to a
    fixture-specific path under docs/solver/proofs/<fixture-slug>-manifest.yaml
    (create the parent directory if needed). Fill every <placeholder>, including:
      - machine.hostname, machine.os, machine.workspace_root
      - solver.application, solver.application_version, solver.orcfxapi_version
        and the convenience top-level orcfxapi alias
      - git.workspace_hub_sha, git.digitalmodel_sha (use git rev-parse HEAD in each)
      - inputs and outputs paths (relative to repo root)
      - classification.primary (and secondary if applicable) per protocol §6
      - evidence.load_console / run_console / wallclock_seconds
      - links: include the #2475 protocol issue and the fixture's own issue/PR
      - audit.authored_by, audit.authored_at (ISO-8601 UTC), audit.protocol_version: v1
    Required top-level keys MUST be present and non-empty: machine, solver,
    git, inputs, outputs, classification, evidence.

  STEP F — Commit and push (workspace-hub)
    Stage only the manifest file and any small evidence artifacts (console
    excerpts, small PNG screenshots, sidecar xlsx if produced and within size
    policy). Do not commit large .sim or .owr binaries unless explicitly
    approved by the size policy.
      git add docs/solver/proofs/<fixture-slug>-manifest.yaml <other-evidence>
      git commit -m "evidence(solver): <fixture> licensed proof under #2475"
      git pull --rebase origin main
      git push origin HEAD:main
    If the rebase has conflicts outside docs/solver/proofs/, abort and post
    a blocker comment on #2475; do not force-push.

  STEP G — Post the GitHub comment
    On the fixture's issue (#2455 / #2456 / #2457) post a single concise
    comment in this Return format (see below). Cross-reference #2475 and the
    manifest path. Do not close the fixture issue from this prompt — only
    post the evidence comment.

  STEP H — Move to the next fixture
    Repeat A-G for each remaining first-wave fixture. After the last fixture,
    post a single roll-up comment on #2475 listing every manifest path and
    the per-fixture classification.

FAILURE HANDLING:
  - "semantic mismatch", "missing input artifact", "missing license/API",
    "unrelated environment failure", "runtime/disk guard exceeded": stop the
    current fixture, write the manifest with that classification, comment,
    move on.
  - Never fabricate evidence. Empty placeholders that you cannot legitimately
    fill go in as the "may be empty" defaults in the template, not as
    invented values.
  - Never modify queue code (scripts/solver/process-queue.py) or
    queue/job-schema.yaml from this prompt.

Return format (post this on each fixture issue):
```
| Field | Value |
|---|---|
| Fixture | <name> |
| Issue | #<n> |
| Proof level | level2 / level3 |
| Classification | <from protocol §6> |
| Manifest | docs/solver/proofs/<fixture-slug>-manifest.yaml |
| Workspace SHA | <short> |
| digitalmodel SHA | <short> |
| Solver | OrcaWave/OrcaFlex <version> |
| OrcFxAPI | <version> |
| Wall-clock | <seconds, if level 3> |

See protocol: docs/solver/orcawave-orcaflex-native-load-run-proof-protocol.md (#2475).
```
```

## Notes for the operator

- **Use `python`, not `uv run`.** licensed-win-1 has no `uv`, and OrcFxAPI is bound to the system Python that has the wheel installed.
- **One fixture at a time.** Even though the queue can pull multiple jobs, the proof workflow is intentionally sequential so the evidence manifest stays readable.
- **Manifest first, commit second.** The manifest is the durable artifact. If you cannot author the manifest (e.g., agent context lost), do not commit partial evidence.
- **Avoid binary commits.** Sidecar `.xlsx` is usually OK; raw `.sim` and `.owr` binaries are typically referenced by path/hash only.
- **Do not close the protocol issue (#2475) from this prompt.** Closing #2475 happens after both this prompt is shipped *and* at least one fixture has been proven through the manifest workflow.

## References

- Protocol: `docs/solver/orcawave-orcaflex-native-load-run-proof-protocol.md`
- Evidence manifest template: `docs/solver/templates/semantic-proof-evidence-manifest.yaml`
- Source plan: `docs/plans/2026-04-23-issue-2475-licensed-load-run-proof-protocol.md`
- Licensed-machine guide: `docs/plans/licensed-win-1-execution-guide.md`
- Prior licensed-machine prompts: `docs/plans/licensed-win-1-session-3-prompts.md`, `docs/plans/licensed-win-1-orcawave-orcaflex-prompts.md`
- Solver queue architecture: `docs/architecture/solver-queue.md`
