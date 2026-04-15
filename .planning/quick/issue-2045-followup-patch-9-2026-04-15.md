Another focused #2045 patch wave landed locally after Codex rereview14:

- defined the single authoritative 12-heading oracle for exemplar-plan validation in one place
- made evidence ownership explicit so `tests/evidence/*.log` is canonical and not duplicated by conflicting writers
- made `GEMINI.md` decisively validation-only unless contradiction is found
- clarified that #2046/#2047 exemplar failures produce prerequisite-drift follow-up work rather than blocking via unauthorized edits
- tightened acceptance criteria to distinguish current-revision review completeness, validation-only surfaces, and allowed policy states

Launching another focused Codex rerun now.
