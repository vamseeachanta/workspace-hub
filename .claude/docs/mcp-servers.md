# MCP Servers — Usage and Trust Policy

> MCP (Model Context Protocol) servers give agents authoritative, citeable access to
> external data sources. Use them instead of relying on training-time knowledge for
> domain facts, standards references, and literature searches.

## Catalog

All evaluated and active servers: `config/ai-tools/mcp-servers.yaml`

## Active Servers

### Semantic Scholar MCP

**Use when**: Engineering WRKs need literature references, design justification, or
state-of-the-art context (materials, offshore, structural, fluid dynamics, etc.).

**Example prompt**:
```
Search Semantic Scholar for papers on offshore pipeline fatigue DNV-RP-C203 published
after 2018, open access only.
```

**Installed via** (commit-pinned):
```bash
claude mcp add semantic-scholar-mcp -s project -- \
  uvx --from git+https://github.com/FujishigeTemma/semantic-scholar-mcp@95d41cfbb1d6c66d7d3ad66f42505cb5bbfe7f13 \
  semantic-scholar-mcp
```

**Integration with Stage 2 (Resource Intelligence)**: When running Resource Intelligence
for an engineering WRK, agents should query Semantic Scholar for recent publications
relevant to the task domain before planning. This avoids training-time knowledge drift
for domain facts.

## Install a New Server

1. **Identify** — find candidate in `config/ai-tools/mcp-servers.yaml` (status: pending)
   or via `registry.modelcontextprotocol.io/v0.1/servers?search=<keyword>&version=latest`

2. **Trust assessment** (all required before installation):
   - [ ] Canonical upstream repo confirmed (not a fork or aggregator mirror)
   - [ ] Maintainer identity reviewed; last commit date acceptable
   - [ ] License confirmed (OSI-approved preferred; document if absent)
   - [ ] Dependencies reviewed (`pyproject.toml` / `package.json`)
   - [ ] Permissions: what network calls does it make? File system access? Env vars?
   - [ ] Commit SHA identified (no floating `@main` installs)
   - [ ] Rollback command documented: `claude mcp remove <name>`

3. **Install** (project scope, pinned SHA):
   ```bash
   claude mcp add <name> -s project -- uvx --from git+<repo>@<SHA> <entrypoint>
   # or for PyPI-versioned packages:
   claude mcp add <name> -s project -- uvx <package>==<version>
   ```

4. **Verify**:
   ```bash
   claude mcp list          # confirm entry present
   cat .mcp.json            # confirm config written to .mcp.json
   ```

5. **Update catalog**: promote entry in `config/ai-tools/mcp-servers.yaml`
   from `status: evaluated` → `status: active`; populate `commit_sha`.

## Remove a Server

```bash
claude mcp remove <name>
# Then update config/ai-tools/mcp-servers.yaml: status: removed, removed_at: <date>
```

## Config File Location

Project-scoped MCP servers are stored in `.mcp.json` at the workspace root.
User-scoped (`-s user`) would go to `~/.claude/settings.json` — avoid user scope
to keep blast radius limited to this project.

## SHA Rotation (Update Cadence)

Pinned SHAs should be reviewed quarterly or when a security advisory is issued.
To update a pinned server:
1. Open a `chore(harness):` WRK item
2. Review the new commit diff against the pinned SHA
3. Run trust assessment checklist again
4. `claude mcp remove <name>` → re-install with new SHA → verify → update `mcp-servers.yaml`

## Supply-Chain Risk

Every MCP server runs in the agent's process and can read the full context window.
**Never install an MCP server without completing the trust checklist above.**
Prefer first-party servers (Anthropic `modelcontextprotocol/servers` monorepo) when
available. For community servers, require source code review before wiring.
