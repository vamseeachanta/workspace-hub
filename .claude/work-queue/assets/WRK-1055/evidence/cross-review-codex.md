### Verdict: REQUEST_CHANGES

### Summary
Strengths: the plan is phased, maps cleanly to the listed acceptance criteria, and correctly identifies supply-chain trust as the main execution risk. The intent to catalog evaluated servers in `config/ai-tools/mcp-servers.yaml`, pin a specific revision, and require cross-review is good. The main blockers are sequencing and workflow correctness: the draft installs a remote MCP before a full trust gate is defined, the cross-review command as written will not exercise the plan-review path correctly, and the scope does not fully line up with the WRK body.

### Issues Found
- Sequencing bug: Phase 2 installs Semantic Scholar before the plan defines a complete pre-install trust gate. For this WRK, supply-chain review should happen before any `uvx`/`uv tool install` execution, not be partially documented afterward in `mcp-servers.yaml`. Pinning a commit SHA helps, but it is not a substitute for reviewing repo owner/source, permissions, transitive dependencies, and rollback/removal steps first.
- Cross-review step is incorrect as written. `scripts/review/cross-review.sh wrk-1055-phase-1-review-input.md all` defaults to `--type implementation`, not `plan`, and does not pass `--wrk-id WRK-1055`, so it bypasses the Stage 5 plan-review gate path defined in the script. There is also a likely path bug if the input file is written under `scripts/review/results/` but invoked without that path.
- Scope mismatch: the WRK body says active servers should be wired into Claude/Codex configs on `ace-linux-1`, but the plan explicitly defers Codex/Gemini wiring and only implements Claude. Either the WRK scope or the plan needs to be narrowed explicitly so acceptance is machine-checkable.
- Test adequacy is too thin for an install/configuration change. `claude mcp list` plus one live query proves only partial reachability. It does not verify config persistence across sessions, the actual config file mutation, failure behavior when the server is unavailable, or safe uninstall/rollback.
- The plan references a `settings.json change` in Phase 5 review input, but no earlier phase specifies which settings file will change, where it lives, or how that file will be validated. That is a scope-clarity gap and makes review evidence ambiguous.
- Phase 1 asks to create an active catalog entry before Phase 2 gathers final install facts such as exact pinned SHA and possibly final invocation syntax. That creates avoidable churn and increases the chance the catalog is initially wrong.
- Supply-chain controls are incomplete. The draft mentions commit pinning, but not whether the install source must be an official upstream repo, whether license/maintenance status will be checked, whether dependency resolution is frozen, or whether network/file-system permissions of the MCP process will be reviewed before enablement.
- The live-query test depends on external service availability and may create flaky completion criteria. The plan should separate deterministic local checks from optional external smoke tests.

### Suggestions
- Insert a dedicated pre-install trust-assessment phase before any MCP installation. Minimum checks: canonical upstream repo, maintainer identity, license, last activity, required auth, requested permissions, install path, rollback command, and whether the runtime pulls unpinned dependencies at execution time.
- Move catalog creation to after the trust assessment, or split it into `candidate` documentation first and `active` promotion only after installation succeeds. That keeps `mcp-servers.yaml` authoritative instead of aspirational.
- Fix Phase 5 to use the real review command shape, for example: `scripts/review/cross-review.sh scripts/review/results/wrk-1055-phase-1-review-input.md all --type plan --wrk-id WRK-1055`. Also state where the input file is created so the command is runnable from repo root.
- Add explicit validation for the Claude config change: identify the exact config file, verify the new MCP entry exists after install, and verify the config still parses or the CLI still starts cleanly after modification.
- Expand testing into three layers: deterministic local checks (`mcp list`, config file presence, command invocation shape), controlled smoke test (one Semantic Scholar query), and rollback test (`claude mcp remove ...` or equivalent cleanup) so the machine can be restored if the server is rejected.
- Resolve the scope conflict with the WRK record. Either update the WRK to say Claude-only for this item, or add a separate acceptance note explaining that Codex wiring is intentionally excluded and captured as follow-on work.
- Make the supply-chain policy concrete in the YAML schema. Add fields such as `source_repo`, `license`, `maintainer`, `last_reviewed`, `permissions_review`, and `rollback_command`; otherwise `trust_assessment` will become free-form and hard to audit.
- Treat registry/marketplace discovery as advisory only. Require final candidate selection to be validated against the upstream repository directly rather than trusting aggregator metadata.

### Questions for Author
- Should WRK-1055 be narrowed to Claude-only on `ace-linux-1`, or is Codex wiring still an acceptance requirement that the current draft is missing?
- What exact Claude config file is expected to change for Phase 2, and do you want that file named explicitly in the plan and review bundle?
- Do you want the additional MCP candidate to remain documentation-only, or should the plan also define what evidence is required before any future installation is allowed?
codex exit: 0
