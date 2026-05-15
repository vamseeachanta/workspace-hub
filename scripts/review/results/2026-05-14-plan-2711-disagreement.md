# Disagreement report — plan #2711 (2026-05-14)

## Verdicts

| Provider | Verdict |
|---|---|
| codex | MAJOR |
| gemini | UNAVAILABLE (gemini CLI failed, rc=0: Ripgrep is not available. Falling back to GrepTool. Error executing tool run_shell_command: Tool \"run_shell_command\" not found. Did you mean one of: \"update_topic\", \"grep_search\", \"invoke_agent\"? ) |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### codex

- Plan does not satisfy the issue’s own acceptance criteria. Issue `#2711` requires the pilot at `docs/provider-data/helix/15k-irs/` with `README.md`, `source.pdf`, `parameters.yaml`, and `orcaflex-mapping.md`, plus a license assessment in the pilot README. Plan §Files to Change instead creates `docs/provider-data/helix-esg/irs-15k/parameters.yaml`, `orcaflex-mapping.md`, and `PROVIDER_RECORD.md`, with no pilot `README.md` and no `source.pdf`. If the governance decision intentionally supersedes the issue body, the plan must explicitly amend or close those issue acceptance criteria before implementation.
- Plan mixes two repositories without an execution contract. Plan §Files to Change lists `digitalmodel/src/digitalmodel/provider_data/schema.py` and `digitalmodel/tests/provider_data/...` as if they are workspace-hub paths, but GitHub returned 404 for those paths in `vamseeachanta/workspace-hub`; the code exists under the separate repo `vamseeachanta/digitalmodel` as `src/digitalmodel/...` and `tests/...`. The plan does not say whether implementation requires two commits, which repo owns the schema, which cwd to use, or how `uv run pytest digitalmodel/tests/provider_data/ -v` is supposed to run against the separate `digitalmodel` repo.
- The proposed schema cannot encode all specifications the plan claims to capture. Plan §Deliverable says `parameters.yaml` encodes “all Helix 15k IRS specifications extracted from the brochure,” and plan §Evidence lists categorical specs including `Control System: MUX with integrated redundancy via HIPPS` and `Subsea Interface: IRS 7 18-3/4 in hydraulic connector`. Plan §Pseudocode defines `SpecValue.value: float`, and §Concrete YAML Design omits those categorical specs entirely. This fails the plan’s own “all specifications” claim and issue `#2711`’s “captures all technical parameters” criterion.
- The OrcaFlex mapping design names a non-settable field. Plan §OrcaFlex Mapping Design maps `bore_production_id_m` to “`RiserPipeProperties` inner diameter.” In `digitalmodel/src/digitalmodel/orcaflex/riser_config.py`, `RiserPipeProperties` has fields `outer_diameter` and `wall_thickness`; `inner_diameter` is a computed `@property`, not an input field. The mapping either needs to target `LineSectionProperties.inner_diameter` only or specify how OD and wall thickness will be derived to produce the bore.
- The mapping table is materially incomplete relative to the YAML. Plan §Deliverable says `orcaflex-mapping.md` maps each spec to a field or justified “no direct field,” but §OrcaFlex Mapping Design only lists six rows and does not map many YAML keys: `mwp_mpa`, `mwd_ft`, `bore_annulus_*`, `subsea_package_weight_with_safety_head_*`, `flowhead_*`, and all `control_lines_*`. Acceptance criterion says the table must be at least seven rows, but the concrete design does not provide seven rows or complete coverage.
- Plan introduces standards-dependent engineering rationale while claiming standards are out of scope. Plan §Standards says standards are “Not applicable as primary scope,” but §OrcaFlex Mapping Design says `mwp_psi` sets wall thickness “via burst check per API RP 2RD.” `digitalmodel/src/digitalmodel/orcaflex/riser_config.py` also documents API RP 2RD references for riser design inputs. If the deliverable includes API RP 2RD-derived burst-check interpretation, the plan needs standards retrieval/citation treatment or must remove that standards-backed claim.
- The design-temperature mapping is unsupported by the cited code. Plan §OrcaFlex Mapping Design maps `design_temp_min_degC` / `design_temp_max_degC` to `RiserPipeProperties.grade` material selection. In `digitalmodel/src/digitalmodel/orcaflex/riser_config.py`, `PipeGrade` is limited to `X52`, `X60`, `X65`, `X70`, and `X80`, and `RiserPipeProperties` has no temperature field or material-temperature constraint. The mapping is currently an engineering assertion, not a supported code/API mapping.

### gemini

- (none)

