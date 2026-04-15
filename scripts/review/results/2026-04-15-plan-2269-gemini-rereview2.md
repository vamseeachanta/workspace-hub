# Adversarial Re-Review — Plan #2269 (Gemini, wave 2)

Date: 2026-04-15
Issue: #2269
Plan: docs/plans/2026-04-15-issue-2269-openfoam-v2312-baseline-workflow-and-validation.md
Reviewer: Gemini CLI
Reviewer mode: adversarial
Overall verdict: MAJOR
Ready for user approval: No
Retrieval adequacy: excellent

Top blockers
1. pytest harness remains hard to test without dependency injection for bootstrap paths
2. YAML handover between wrapper and runner is still underspecified
3. canonical path policy is contradictory between fault-tolerance and normalization

Critical findings
- the proposed testing strategy is still incompatible with a hardcoded bash-wrapper design unless dependency injection or isolation is planned
- Bash-native YAML merging remains a schema-corruption risk unless the implementation language/tool is chosen explicitly

High findings
- define the YAML normalization tool/language explicitly (`yq`, embedded Python, or equivalent exact choice)
- provide concrete type mapping or YAML snippet for `tutorials`
- specify benchmark trigger mechanism (`--benchmark` flag or documentation-only/manual)

Medium findings
- choose an exact discoverability surface rather than “docs/README.md or equivalent”
- clarify override propagation from wrapper to runner

Required revisions before user approval
1. Add dependency injection for bootstrap-path testing (for example `OPENFOAM_BASHRC_PATHS` override for tests).
2. Define the YAML handover/normalization mechanism explicitly.
3. Commit to either a single canonical path or an explicitly permanent two-path supported baseline.
4. Add a concrete YAML snippet/type mapping for `tutorials`.
5. State exactly how the optional benchmark is invoked.
