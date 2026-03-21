Stage 1 · Capture | human_interactive | light | single-thread
Entry: nothing (human initiates)
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.
Checklist:
1. Ask human: WRK title, mission, category
2. Write pending/WRK-NNN.md with valid frontmatter (id, title, status:pending, category)
3. Run `bash scripts/work-queue/validate-wrk-frontmatter.sh WRK-NNN` — must exit 0
Exit: pending/WRK-NNN.md (Stage 1 done)
