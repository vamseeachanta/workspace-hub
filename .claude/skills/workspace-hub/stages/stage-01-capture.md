Stage 1 · Capture | human_interactive | light | single-thread
Entry: nothing (human initiates)
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.
Checklist:
1. Ask human: WRK title, mission, category
2. Write pending/WRK-NNN.md with valid frontmatter (id, title, status:pending, category)
3. Create assets/WRK-NNN/WRK-NNN-lifecycle.html (stage 1 chip done, stages 2-20 pending)
4. Set status chip 1 to done in lifecycle HTML
5. Confirm WRK-NNN.md frontmatter has all required fields
Exit: pending/WRK-NNN.md + WRK-NNN-lifecycle.html (Stage 1 done)
