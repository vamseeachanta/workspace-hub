---
name: mcp-registry-audit
description: Query MCP registries for engineering-domain servers — filters by keywords, ranks by relevance, assesses supply-chain trust
version: 1.0.0
category: workspace-hub
capabilities:
  - mcp_registry_query
  - engineering_server_discovery
  - supply_chain_assessment
tools: [Bash, WebFetch, Read, Write]
related_skills: [mcp-builder]
requires: []
see_also: []
tags: []
---

# MCP Registry Audit

## Quick Start

Query the official MCP registry API for engineering-relevant servers:

```bash
# Single keyword
curl -s "https://registry.modelcontextprotocol.io/v0.1/servers?q=engineering" | python3 -m json.tool

# Batch audit — loop through engineering keywords
for kw in geospatial scientific "unit conversion" weather structural marine energy geology engineering CAD FEA CFD GIS simulation math; do
  echo "=== $kw ==="
  curl -s "https://registry.modelcontextprotocol.io/v0.1/servers?q=${kw// /+}" | python3 -c "
import json, sys
data = json.load(sys.stdin)
servers = data if isinstance(data, list) else data.get('servers', data.get('results', []))
for s in servers[:5]:
    name = s.get('name', s.get('title', 'unknown'))
    print(f'  {name}')
" 2>/dev/null
done
```

## Engineering Keywords

Search the registry with these domain-specific terms:

- **Core engineering**: engineering, structural analysis, simulation, math
- **CAD/modeling**: CAD, FEA, CFD, 3D modeling
- **Geospatial**: GIS, geospatial, mapping, elevation
- **Scientific**: scientific computing, unit conversion, numerical methods
- **Energy/marine**: energy, marine, weather, offshore, geology
- **Data**: data analysis, visualization, plotting

## Trust Assessment Checklist

Evaluate each candidate server against these criteria before installation:

1. **Popularity**: GitHub stars > 10 (higher = more community vetting)
2. **Activity**: Last commit within 90 days (stale repos = security risk)
3. **Bus factor**: Multiple contributors (single-maintainer = fragile)
4. **License**: MIT or Apache-2.0 preferred; avoid AGPL/proprietary
5. **Permissions**: No excessive filesystem/network access beyond stated scope
6. **Documentation**: README has clear install instructions and usage examples
7. **Dependencies**: Review package.json/requirements.txt for supply-chain risk
8. **Namespace**: Published under recognizable org or verified author

### Trust Tiers

- **High**: 100+ stars, active, multiple contributors, permissive license
- **Medium**: 10-100 stars, recent commits, reasonable permissions
- **Low**: <10 stars or single maintainer or stale — use in sandbox only

## Additional Sources

Also check the community-curated list for servers not yet in the official registry:

- **awesome-mcp-servers**: `https://github.com/punkpeye/awesome-mcp-servers`
  - Browse by category (Developer Tools, Data, Science, etc.)
  - Cross-reference stars and activity with GitHub directly

## Output

Save audit results to `.claude/work-queue/assets/WRK-<id>/mcp-engineering-candidates.yaml`
using the YAML candidate schema (name, github, stars, domain, relevance, trust, install, notes).
