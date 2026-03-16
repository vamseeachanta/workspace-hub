---
name: mcp-builder-phase-1-deep-research-and-planning
description: 'Sub-skill of mcp-builder: Phase 1: Deep Research and Planning (+3).'
version: 1.2.0
category: development
type: reference
scripts_exempt: true
---

# Phase 1: Deep Research and Planning (+3)

## Phase 1: Deep Research and Planning


**Study MCP Design Principles:**
- Balance "API coverage vs. workflow tools"
- Review MCP protocol at modelcontextprotocol.io
- Learn framework specifics (TypeScript recommended)
- Analyze target API endpoints

**Key Questions:**
1. What actions does the user want to perform?
2. What API endpoints are available?
3. Which operations are read-only vs destructive?
4. How should errors be handled?

## Phase 2: Implementation


**Project Setup (TypeScript):**
```bash
mkdir my-mcp-server
cd my-mcp-server
npm init -y
npm install @modelcontextprotocol/sdk zod
npm install -D typescript @types/node
```

**tsconfig.json:**

*See sub-skills for full details.*

## Phase 3: Review and Test


**Code Quality Checklist:**
- [ ] No code duplication
- [ ] Full type coverage
- [ ] Proper error handling
- [ ] Input validation
- [ ] Rate limiting (if needed)

**Testing with MCP Inspector:**
```bash
npx @modelcontextprotocol/inspector node dist/index.js
```

## Phase 4: Create Evaluations


Generate 10 complex, realistic test questions:
- Independent (no dependencies between questions)
- Read-only (don't modify external state)
- Verifiable (clear expected answers)
