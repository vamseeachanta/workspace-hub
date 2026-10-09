---
name: clinical-trial-protocol
description: Generate clinical trial protocols for medical devices or drugs through
  a modular, waypoint-based architecture with research-only and full protocol modes.
type: reference
version: 1.0.0
category: science
last_updated: 2026-02-03
source: https://github.com/anthropics/knowledge-work-plugins
related_skills:
- single-cell-rna-qc
- scvi-tools
- nextflow-pipelines
- instrument-data-allotrope
- scientific-problem-selection
capabilities: []
requires: []
tags: []
scripts_exempt: true
---

# Clinical Trial Protocol

## Overview

This skill generates clinical trial protocols for **medical devices or drugs** using a **modular, waypoint-based architecture**

## Prerequisites

### 1. clinical trials MCP Server (Required)

**Installation:**
- Install via drag-and-drop `.mcpb` file into Claude Desktop
- Or configure manually in Claude Desktop settings

**Available Tools:**
`search_clinical_trials` - Search by:

condition - Disease or condition (e.g., "pancreatic cancer")
intervention - Drug, device, or treatment (e.g., "pembrolizumab", "CAR-T")
sponsor - Sponsor or collaborator name (e.g., "Pfizer", "NIH")

*See sub-skills for full details.*
### 2. FDA Database Access (Built-in)

**Purpose:** FDA regulatory pathway research via explicit database URLs

**Sources:**
- Step 1: FDA device/drug databases (510(k), PMA, De Novo, Drugs@FDA, Orange Book, Purple Book)
- All sources use direct FDA database URLs - no generic web searches
### 3. Clinical Protocol Template

**Template Files:** Any `.md` files in the `assets/` directory

**Purpose:** Reference template for protocol structure and content guidance. The system automatically detects available templates and uses them dynamically.
### 4. Python Dependencies (Required for Step 2)

**Installation:**
```bash
pip install -r requirements.txt
```

**Dependencies:**
- scipy >= 1.11.0 (statistical calculations)
- numpy >= 1.24.0 (numerical operations)

**Purpose:** Accurate statistical sample size calculations for clinical protocols

## Sub-Skills

- [EXECUTION CONTROL - READ THIS FIRST](execution-control-read-this-first/SKILL.md)
- [What This Skill Does](what-this-skill-does/SKILL.md)
- [Waypoint-Based Design (+2)](waypoint-based-design/SKILL.md)
- [How to Use](how-to-use/SKILL.md)
- [Startup: Welcome and Mode Selection (+1)](startup-welcome-and-mode-selection/SKILL.md)
- [Intervention Overview](intervention-overview/SKILL.md)
- [Similar Clinical Trials](similar-clinical-trials/SKILL.md)
- [FDA Regulatory Pathway](fda-regulatory-pathway/SKILL.md)
- [FDA Guidance Documents](fda-guidance-documents/SKILL.md)
- [Study Design Recommendations](study-design-recommendations/SKILL.md)
- [Key Insights and Recommendations](key-insights-and-recommendations/SKILL.md)
- [Full Workflow Logic](full-workflow-logic/SKILL.md)
- [Waypoint File Formats (+2)](waypoint-file-formats/SKILL.md)
- [MCP Server Unavailable (+2)](mcp-server-unavailable/SKILL.md)
- [Disclaimers](disclaimers/SKILL.md)
- [Implementation Requirements](implementation-requirements/SKILL.md)
