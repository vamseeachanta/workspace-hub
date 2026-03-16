---
name: agent-orchestration-hierarchical
description: 'Sub-skill of agent-orchestration: Hierarchical (+3).'
version: 1.1.0
category: coordination
type: reference
scripts_exempt: true
---

# Hierarchical (+3)

## Hierarchical


Coordinator delegates to specialized workers:

```
        ┌─────────────────┐
        │   Coordinator   │
        └────────┬────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼

*See sub-skills for full details.*

## Mesh


Peer-to-peer collaboration:

```
┌───────┐     ┌───────┐
│Agent A│◄───►│Agent B│
└───┬───┘     └───┬───┘
    │      ╲  ╱   │
    │       ╲╱    │
    │       ╱╲    │
    │      ╱  ╲   │

*See sub-skills for full details.*

## Star


Central hub with peripheral agents:

```
         ┌───────┐
         │Agent A│
         └───┬───┘
             │
┌───────┐  ┌─▼─┐  ┌───────┐
│Agent B├──►Hub◄──┤Agent C│
└───────┘  └─┬─┘  └───────┘

*See sub-skills for full details.*

## Ring


Sequential processing:

```
┌───────┐     ┌───────┐
│Agent A│────►│Agent B│
└───┬───┘     └───┬───┘
    ▲             │
    │             ▼
┌───┴───┐     ┌───────┐
│Agent D│◄────│Agent C│

*See sub-skills for full details.*
