Stage 6 · Cross-Review | task_agent | medium | parallel — 3 providers
Entry: WRK-NNN-lifecycle.html#s1-s5, evidence/user-review-plan-draft.yaml
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.
Mandatory: ALL 3 providers (Claude + Codex + Gemini) must review. No self-skip.
Codex quota fallback: when quota exhausted OR ≥2 Codex reviews already exist for this WRK,
cross-review.sh auto-substitutes Claude Opus (claude-opus-4-6) in the Codex slot — no user
instruction required. Result labeled "Codex-slot: Claude Opus fallback" in the review file.
Checklist:
0. EnterPlanMode — synthesize all inputs before writing any verdict artifact
1. Send cross-review-package.md to Codex and Gemini simultaneously
2. Collect all 3 verdicts (APPROVE|REVISE) with P1/P2 findings
3. Synthesize into evidence/cross-review.yaml (verdict, reviewers[], p1_findings, p2_findings)
4. Update lifecycle HTML Stage 6 section with findings
5. If REVISE: set return_to_stage in cross-review.yaml; revise plan before Stage 7
Exit: evidence/cross-review.yaml (verdict: APPROVE|REVISE; all 3 providers listed)
