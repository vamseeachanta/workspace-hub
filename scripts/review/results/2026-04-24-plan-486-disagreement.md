# Disagreement report — plan #486 (2026-04-24)

## Verdicts

| Provider | Verdict |
|---|---|
| adversarial | **MINOR** — plan is fundamentally sound on the high-stakes axes (hard-gate ledger call, dual-path delivery, greenfield verification, no hallucinated 17R clause citations), but contains a cluster of specification defects that must be tightened before implementation. No APPROVE because several Acceptance Criteria and TDD entries are unfalsifiable or phrased so loosely that "done" is a matter of interpretation, and Path-A/Path-B convergence is not cleanly preserved through the Files-to-Change list. |
| claude | MAJOR |
| codex | UNAVAILABLE (codex CLI failed, rc=2: error: unexpected argument '--no-interactive' found    tip: to pass '--no-interactive' as a value, use '-- --no-interactive'  Usage: codex exec [OPTIONS] [PROMPT]        codex exec [OPTIONS] <COMMAND>) |
| gemini | UNAVAILABLE (gemini CLI failed, rc=55: [31mGemini CLI is not running in a trusted directory. To proceed, either use `--skip-trust`, set the `GEMINI_CLI_TRUST_WORKSPACE=true` environment variable, or trust this directory in interactive mod) |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### adversarial

(no findings unique to this provider)

### claude

- **[MAJOR] Stale #2455 status — plan's coupling-risk analysis is predicated on #2455 being in-flight, but #2455 closed ~11 hours before plan drafting.** Plan §Resource-Intel line 84 and §Risks "Other risks" bullet both call #2455 OPEN / "in-flight". Live state: `gh issue view 2455 --repo vamseeachanta/workspace-hub` → `state: CLOSED, closedAt: 2026-04-24T01:31:34Z`. The plan's Phase-3 "Thin export here, deep integration in follow-up issue — Recommend (B)" tradeoff and `test_no_collision_with_2455` are built around a don't-collide concern that may now be moot or inverted (post-merge baseline instead). Must re-evaluate against the merged state of #2455 before implementation.
- **[MAJOR] Cross-repo issue numbering undisclosed — plan references issues in two different GitHub repos without disambiguation.** Header says `Issue https://github.com/vamseeachanta/digitalmodel/issues/486`, and §Resource-Intel lists #471/#475/#484/#485/#488 (all in `vamseeachanta/digitalmodel`) alongside #2455 (which lives in `vamseeachanta/workspace-hub`, not `digitalmodel` — confirmed by GraphQL 404 against the digitalmodel repo). Plan never states this. Implementers running `gh issue view 2455` from this repo hit workspace-hub; running from the digitalmodel clone hit a missing issue. Moreover, since the plan is committed under `workspace-hub/docs/plans/` but its primary issue is in a different repo, workspace-hub-side status automation (e.g., `status:plan-review` → `status:plan-approved` labelling per CLAUDE.md) cannot attach to #486 here.
- **[MINOR] Embedded `ConnectorProperties` "line excerpt" at §Resource-Intel lines 104-111 is paraphrase presented as quote.** Plan shows:
-    ```
-    @dataclass
-    class ConnectorProperties:
-        # installation-specific: lift/crane loads for Ballymore V2
-        ...
-    ```
-    Actual content at `jumper_lift.py:212-219`:
-    ```
-    @dataclass
-    class ConnectorProperties:
-        """Connector (hub) properties.
-        Source: Sheet 'Bare pipe', rows 18-19.
-        """
-        weight_in_air_kg: float = 1678.5
-        length_m: float = 1.3
-    ```
-    Real class is a 2-field geometric hub (weight + length), not "lift/crane loads". This mischaracterization undercuts the naming-collision risk analysis: a 2-field weight/length dataclass is much easier to disambiguate from a forthcoming `subsea.connectors.connector_design.Connector` than the plan implies, and a coordinated re-export with #475 may not match what #475's test expansion (`Add pytest test suite for jumper_lift.py (81 tests)`) actually exercises.
- **[MINOR] "Sibling submodule repo" mislabels the digitalmodel directory.** §Resource-Intel line 15 calls `digitalmodel/` a "sibling submodule repo". `/mnt/local-analysis/workspace-hub/.gitmodules` does not exist; `git -C digitalmodel remote -v` → standalone origin. It's a nested independent clone. The distinction matters: a submodule update lands via the parent repo's PR machinery (index pointer); a nested clone produces a PR in a separate repo that workspace-hub's PR-review tooling never sees. The AC "worked example runs under `uv run`" and the §Artifact-Map row "Modify (coordination) jumper_lift.py" therefore require test infrastructure and PR-routing assumptions the plan does not make explicit.
- **[MINOR] `:26` citation of `subsea-production-systems-mapping.md` is off by 30+ lines.** §Resource-Intel line 53 cites the doc at `:26` as "authoritative taxonomy linking API 17R → 'Connectors & Jumpers' → Issue #486 (Medium, Milestone #1)". Actual line 26: `| Connectors & Jumpers | 17R | Link equipment for fluid transfer |` — no issue number, no priority, no milestone. `#486 Medium` row is at line 58; the Milestone #1 reference is at line 67. The cited line supports only the taxonomy half, not the issue-assignment half.
- **[MINOR] "API RP 17B 2nd Ed 1998 & 5th Ed 2014 — Ledgered" overstates ledger content.** Ledger entry `API-RP-17B` (L4522-4530) has `title: API RP 17B.pdf` with no edition metadata — one generic PDF, no `ed_2` vs `ed_5` distinction. Plan's "both editions ledgered" cannot be verified from the ledger and may be an inference from the filesystem that hasn't been checked. Path-B AC "cite API 17B 5th Ed 2014" therefore may not be satisfiable against the current ledger entry as-is.
- **[MINOR] `test_no_collision_with_2455` is trivially-passing and does not catch what it claims to.** §TDD-Test-List row asserts "no files under `digitalmodel/docs/domains/orcaflex/templates/subsea/jumper_hybrid/` modified by this plan". But §Files-to-Change does not list any `jumper_hybrid/` path anyway, so the test passes by static inspection of the plan itself — it does not verify semantic non-collision against #2455's actual OrcaFlex generator surface. A defect-finding test would re-run #2455's own tests against the post-merge tree (now possible since #2455 closed — see finding #1).
- **[MINOR] Path A/B "no self-select" rule is violated by plan internals.** §Risks "[TRADEOFF FOR USER] — PROJECT-LEVEL GATE" states "Neither the Planner nor downstream implementers may self-select this path." But §Pseudocode line 171 already writes `check_against_code(stress_profile, standard_basis) # DNV-OS-F101 § or API 17B §` — i.e., commits the executable code shape to the Path-B ledgered-adjacents basis. Under Path A (user procures 17R), the pseudocode would cite 17R § directly. The plan thus bakes in Path B while formally reserving the choice for the user.
- **[MINOR] AC coverage for review artifacts does not match operational reality.** §Acceptance-Criteria includes "Review artifacts posted to `scripts/review/results/`" but does not specify all-three vs subset. Memory flag `feedback_codex_cli_0_124_upstream_regression.md` (2026-04-23) records that `codex exec` is blocked on the installed CLI version; memory flag `feedback_gemini_sandbox_overlay_blindness.md` records Gemini false-positive file-missing claims. The AC as-written implies a three-provider review that the repo's current tooling may not reliably produce. Plan should either down-scope to the providers that execute, or specify an explicit fallback.
- **[MINOR] Phase 3 "API-design note amendment" leaves load-bearing design work for an undefined downstream.** §Risks "Other risks" bullet: "`fatigue/hotspot_stress.py` API is internal. Mitigation: Phase 3 opens with a brief API-design note appended to this plan as an amendment (or referenced from `fatigue_bridge.py` docstring)". This defers contract design for the `fatigue/` bridge — an AC module — into a plan amendment with no gate. If Phase 3 hits the internal API and finds it unusable, there is no rollback path defined. TDD row `test_fatigue_bridge_rainflow_roundtrip` may or may not land against an API that exists in its expected shape.

### codex

(no findings unique to this provider)

### gemini

(no findings unique to this provider)

