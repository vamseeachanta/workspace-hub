## Plan (Route A inline)

1. Read workspace-hub CLAUDE.md; identify lines that could be HTML-commented
2. Edit CLAUDE.md — wrap candidates in `<!-- -->` blocks; verify injected size drops
3. Read `.claude/settings.json`; add `autoMemoryDirectory` field
4. Check `scripts/hooks/` for SessionEnd hooks; measure runtime; set timeout if needed
5. Run session-start / work-queue sanity check to confirm no regression
