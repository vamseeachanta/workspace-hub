# Holistic Resource Intelligence Plan

> **Issue:** #1575
> **Date:** 2026-04-05
> **Status:** Plan
>
> **Superseded-by:** The parent architecture for the intelligence ecosystem is now governed by
> [LLM-Wiki + Resource/Document Intelligence Operating Model](llm-wiki-resource-doc-intelligence-operating-model.md) (#2205).
> This plan retains useful historical context on resource tracking architecture but is no longer
> the governing document for intelligence ecosystem design.

## 1. Problem Statement

ACE Engineer's workspace-hub ecosystem contains knowledge resources scattered across:
- `/mnt/ace` — local drive with standards and project files
- DDE remote drive — 14.6 GB / 5,456 PDFs
- Conference collections — 38,526 papers across 30 collections
- Online resource registry — 247 tracked resources in `data/document-index/online-resource-registry.yaml`
- Document intelligence pipeline results

Currently there's no unified view of what resources exist, their status, or opportunities to cross-leverage across engineering domains.

## 2. Unified Resource Tracking Architecture

### 2.1 Master Resource Registry
A unified registry extending `online-resource-registry.yaml` that covers ALL resource types:

| Resource Type | Source | Status Tracking | Refresh Frequency |
|---|---|---|---|
| Standards orgs | `/mnt/ace/O&G-Standards/` | File count, last modified | Weekly scan |
| Conference papers | DDE + mounted drives | Indexed %, summarized % | Monthly |
| Online APIs | Registry YAML | Health check, response time | Daily |
| Extracted methods | `data/doc-intelligence/` | Promoted to digitalmodel % | On extraction |
| Excel calculations | `data/catalog.yaml` | Extracted, validated, converted | On change |
| GitHub repos | workspace-hub | Commit activity, issue status | Daily |

### 2.2 Resource Metadata Schema
Every tracked resource should capture:
```yaml
resource:
  id: unique_identifier
  name: Human-readable name
  type: standards | conference | online_api | excel | code | report
  domain: marine | structural | pipeline | materials | ...
  location: /path/remote/https://
  size_mb: estimated_size
  file_count: number_of_files
  status: discovered | indexed | summarized | extracted | promoted
  quality_score: 0-100
  last_checked: ISO8601_timestamp
  cross_references: [list_of_related_resource_ids]
```

## 3. /mnt/ace Backup Monitoring

### 3.1 Current State
`/mnt/ace` contains the primary backup of standards documents and project files. Currently monitored ad-hoc.

### 3.2 Monitoring Strategy
1. **Baseline Scan:** Run `find /mnt/ace -type f | wc -l` and `du -sh /mnt/ace` to establish baseline
2. **Change Detection:** Weekly rsync dry-run or inotify-based monitoring for new/modified files
3. **Delta Cataloging:** When changes detected, catalog new files into the document intelligence pipeline automatically
4. **Health Dashboard:** Simple metrics tracking:
   - Total files on `/mnt/ace`
   - New files since last scan
   - Files added to pipeline
   - Cross-reference matches found

### 3.3 Automation Approach
```bash
#!/bin/bash
# Weekly ace backup monitor
baseline="/mnt/local-analysis/workspace-hub/data/ace-baseline.txt"
current="/tmp/ace-current.txt"

find /mnt/ace -type f -printf '%T@ %s %p\n' | sort -k3 > "$current"
if [ -f "$baseline" ]; then
    new_files=$(comm -13 <(cut -d' ' -f3 "$baseline" | sort) <(cut -d' ' -f3 "$current" | sort) | wc -l)
    echo "New files on /mnt/ace: $new_files"
fi
cp "$current" "$baseline"
```

## 4. Cross-Domain Leverage Opportunities

### 4.1 Identified Opportunities
1. **Marine <-> Structural:** SNAME structural papers inform digitalmodel/structural design patterns
2. **Pipeline <-> Geotechnical:** Soil-pipe interaction papers apply to both domains
3. **Standards <-> All Domains:** API, DNV, ISO standards cross-reference to every engineering domain
4. **Conference Papers <-> Digitalmodel:** 38K conference papers contain validation cases for digitalmodel modules
5. **Excel Calculations <-> Digitalmodel:** 3,683 worked examples can become test fixtures

### 4.2 Leverage Pipeline
```
Source Resource -> Classification -> Cross-Reference Map -> Target Domain Alert
```
When a new resource is classified, the system checks which domains it applies to and generates alerts for domain owners.

## 5. Unified Resource Dashboard Architecture

### 5.1 Dashboard Design
An interactive HTML dashboard (`data/dashboard/resource-intelligence.html`) showing:
1. **Resource Overview:** Total by type, status pie chart, growth trend
2. **Domain Coverage Heatmap:** Rows = domains, columns = resource types, cells = count
3. **Pipeline Progress Funnel:** Discovered -> Indexed -> Summarized -> Extracted -> Promoted
4. **Cross-Reference Graph:** Connected domain-resource network visualization (Plotly)
5. **Health Status:** API endpoints, drive mounts, file counts with trend lines
6. **GTM Alignment Matrix:** Resource coverage vs job market demand skills

### 5.2 Data Sources
- `data/document-index/registry.yaml` — master document counts
- `data/document-index/online-resource-registry.yaml` — online resource status
- `data/catalog.yaml` — excel and calculation inventory
- `/mnt/ace` scan results — backup drive status
- GitHub API — repo and issue activity

### 5.3 Refresh Schedule
- **Real-time:** API health checks
- **Daily:** Registry YAML updates
- **Weekly:** /mnt/ace scan, cross-reference analysis
- **Monthly:** Full dashboard rebuild

## 6. Implementation Phases

### Phase 1: Discovery (Week 1)
- Scan all resource locations, establish baselines
- Build unified registry YAML
- Generate first dashboard snapshot

### Phase 2: Automation (Week 2-3)
- Implement change detection for /mnt/ace
- Build automated cross-reference matching
- Set up scheduled dashboard refresh (cron)

### Phase 3: Intelligence Layer (Week 4)
- Implement cross-domain opportunity detection
- Add GTM alignment scoring
- Set up alerting for significant changes
- Build trend reporting

## 7. Metrics and KPIs

| Metric | Target | Current |
|---|---|---|
| Resources tracked | 100% | Partial (247 online only) |
| /mnt/ace scanned | Weekly | Ad-hoc |
| Cross-references mapped | 80% | Unknown |
| Dashboard freshness | < 24h | N/A (doesn't exist) |
| Cross-domain alerts | Automated | None |
| Resource-to-code promotion rate | Track baseline | N/A |
