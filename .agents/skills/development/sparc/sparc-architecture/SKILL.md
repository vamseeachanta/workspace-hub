---
name: sparc-architecture
description: SPARC Architecture phase specialist for system design, component architecture,
  interface design, scalability planning, and technology selection
version: 1.0.0
category: development
type: hybrid
capabilities:
- system_design
- component_architecture
- interface_design
- scalability_planning
- technology_selection
tools:
- Read
- Write
- Edit
- Grep
- Glob
related_skills:
- sparc-specification
- sparc-pseudocode
- sparc-refinement
hooks:
  pre: 'echo "SPARC Architecture phase initiated"

    memory_store "sparc_phase" "architecture"

    # Retrieve pseudocode designs

    memory_search "pseudo_complete" | tail -1

    '
  post: 'echo "Architecture phase complete"

    memory_store "arch_complete_$(date +%s)" "System architecture defined"

    '
requires: []
tags: []
---

# Sparc Architecture

## Quick Start

```bash
# Invoke SPARC Architecture phase

# Or directly in Claude Code
# "Use SPARC architecture to design the system components for auth service"
```

## When to Use

- Designing system components and their boundaries
- Creating API contracts and interface definitions
- Selecting technology stacks based on requirements
- Planning for scalability and high availability
- Defining deployment and infrastructure architecture

## Prerequisites

- Completed specification and pseudocode phases
- Understanding of system design principles
- Knowledge of distributed systems patterns
- Familiarity with cloud infrastructure options

## Core Concepts

### SPARC Architecture Phase

The Architecture phase transforms algorithms into system designs:

1. **Define system components and boundaries** - Microservices, modules
2. **Design interfaces and contracts** - REST, gRPC, events
3. **Select technology stacks** - Languages, frameworks, databases
4. **Plan for scalability and resilience** - Horizontal scaling, failover
5. **Create deployment architectures** - Kubernetes, containers
### Architecture Patterns

| Pattern | Use Case | Trade-offs |
|---------|----------|------------|
| Monolith | Small teams, early stage | Simple but hard to scale |
| Microservices | Large teams, complex domains | Scalable but complex |
| Event-Driven | Async workflows, decoupling | Eventual consistency |
| Serverless | Variable workloads | Cost-efficient but cold starts |

## Implementation Pattern

### High-Level Architecture (Mermaid)

```mermaid
graph TB
    subgraph "Client Layer"
        WEB[Web App]
        MOB[Mobile App]
        API_CLIENT[API Clients]
    end

    subgraph "API Gateway"
        GATEWAY[Kong/Nginx]

*See sub-skills for full details.*
### Component Architecture

```yaml
components:
  auth_service:
    name: "Authentication Service"
    type: "Microservice"
    technology:
      language: "TypeScript"
      framework: "NestJS"
      runtime: "Node.js 18"


*See sub-skills for full details.*
### Data Architecture (SQL)

```sql
-- Entity Relationship Diagram
-- Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

*See sub-skills for full details.*

## Metrics & Success Criteria

- All components have defined interfaces
- Database schema includes appropriate indexes
- API specification is complete and versioned
- Security architecture covers auth, encryption, compliance
- Scalability plan with measurable triggers

## Integration Points

### MCP Tools

```javascript
// Store architecture decisions
  action: "store",
  key: "sparc/architecture/components",
  namespace: "coordination",
  value: JSON.stringify({
    services: ["auth-service", "user-service"],
    database: "postgresql",
    cache: "redis",
    messaging: "rabbitmq",
    timestamp: Date.now()
  })
}
```
### Hooks

```bash
# Pre-architecture hook

# Post-architecture hook
```
### Related Skills

- [sparc-specification](../sparc-specification/SKILL.md) - Requirements phase
- [sparc-pseudocode](../sparc-pseudocode/SKILL.md) - Previous phase: algorithms
- [sparc-refinement](../sparc-refinement/SKILL.md) - Next phase: TDD implementation

## References

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [12-Factor App](https://12factor.net/)

## Version History

- **1.0.0** (2026-01-02): Initial release - converted from agent to skill format

## Sub-Skills

- [Configuration](configuration/SKILL.md)
- [Example 1: API Architecture (OpenAPI) (+1)](example-1-api-architecture-openapi/SKILL.md)
- [Example 3: Security Architecture (+1)](example-3-security-architecture/SKILL.md)
- [Best Practices](best-practices/SKILL.md)

## Sub-Skills

- [Execution Checklist](execution-checklist/SKILL.md)
- [Error Handling](error-handling/SKILL.md)
