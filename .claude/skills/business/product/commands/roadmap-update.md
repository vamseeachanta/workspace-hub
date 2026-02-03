---
name: roadmap-update
type: command
plugin: product-management
source: https://github.com/anthropics/knowledge-work-plugins
---

# /roadmap-update - Update Product Roadmap

Generate or update a product roadmap with status, priorities, and dependencies.

## Usage

```
/roadmap-update [operation]
```

## Workflow

### 1. Understand Current State

If a project tracker is connected, pull the current roadmap items. Otherwise, ask the user for current state.

### 2. Determine Operation

Support these operations:
- **Add** new items to the roadmap
- **Update** status of existing items
- **Reprioritize** existing work
- **Adjust timelines**
- **Create from scratch** a new roadmap

### 3. Generate Summary

Output includes:
- Status overview (on track / at risk / off track)
- Itemized roadmap with owners and dependencies
- Risk assessment
- Summary of changes made

### 4. Follow-Up

Offer to:
- Format for different audiences (executive, engineering, cross-functional)
- Communicate changes to stakeholders
- Update connected project tracking systems

## Key Principles

- Roadmaps are communication tools focused on themes and outcomes, not task-level details
- Understand what prompted priority shifts
- Surface capacity constraints
- Explicitly track dependencies as critical risk factors
