# Database Skill

Invoke: `/database` or load agent `@.claude/agent-library/devops/database.md`

## Quick Commands
- `/database schema <table>` - Design schema
- `/database migrate` - Generate migration
- `/database optimize <query>` - Optimize query

## Handoff to Agent
```
Task: [schema design | migration | query optimization]
Database: [PostgreSQL | MySQL | MongoDB | SQLite]
Context: [current schema or query]
```
