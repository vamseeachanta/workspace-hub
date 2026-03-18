Stage 2 · Resource Intelligence | chained_agent | medium | single-thread
Entry: pending/WRK-NNN.md
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.
Checklist:
1. Search codebase — existing code, skills, tests in target repos
2. Query knowledge base — `query-knowledge.sh --category <domain>`
3. Search document-index for relevant prior art
4. **Online research** — WebSearch for standards, papers, tools, best practices
5. **Save discovered documents** to `/mnt/ace/<repo>/` with context
6. **Update document-index** — add new entries via phase-a pipeline
7. Assess complexity (simple/medium/complex)
8. Write evidence/resource-intelligence.yaml (completion_status, domain, skills.core_used ≥3)
9. Update lifecycle HTML Stage 2 section
Exit: evidence/resource-intelligence.yaml
