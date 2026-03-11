# WRK-1084 Cross-Review Results

## Codex
- **Verdict**: APPROVE
- **Findings fixed**:
  - HIGH: Added license gate (Step 2) to adoption workflow — permissive/restrictive/no-license routing
  - MEDIUM: Replaced `npx` default with passive-first (read raw GitHub SKILL.md); npx only in disposable env
  - MEDIUM: Fixed routing table (partial overlap → enhance existing, not duplicate); clarified `source:` vs `adopted_from:`

## Claude
- **Verdict**: REQUEST_CHANGES (addressed before next stage)
- **Findings fixed**:
  - P2: Fixed duplicate `3.` in skills-curation Phase 3 (→ `4. Collect research yield`)
  - P2: Fixed duplicate `3.` in skills-researcher Phase 3 (→ `4.` and `5.`)
  - P2: License gate already added in Codex round; legal-sanity-scan note implied by license gate step
  - P3: npx safety note added in Codex round

## Gemini
- Not reached (submit-to-gemini.sh routed to Claude; Gemini CLI unavailable this session)
- Route A waiver applies (single cross-review pass sufficient per work-queue SKILL.md)
