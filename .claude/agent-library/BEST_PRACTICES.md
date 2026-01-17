# Agent Development Best Practices

> **Consolidated from 26+ repositories**
> **Last Updated:** 2025-10-05
> **Source:** Workspace-hub multi-repository analysis

## Overview

This document consolidates best practices identified across all agent implementations in workspace-hub, including:
- **78+ agents** across 26 repositories
- **3 agent ecosystems**: Claude Flow (54), Domain-Specific (11), Workflow Automation (6)
- **3 configuration patterns**: YAML, JSON, MCP Registry

## 1. Configuration Best Practices

### 1.1 Essential Configuration Elements

**ALL agents must include:**

```yaml
# Minimum required fields
name: "agent-name"
version: "1.0.0"  # Semantic versioning
type: "domain-expert | general-purpose | workflow-automation"
description: "Clear, concise purpose statement"
created: "2025-10-05T00:00:00Z"
updated: "2025-10-05T00:00:00Z"
status: "active | beta | deprecated"

capabilities:
  - capability_1
  - capability_2
  - capability_3

specialization: "specific-domain | general-purpose"
```

### 1.2 Advanced Configuration Patterns

**Domain-Expert Agents** (YAML format):

```yaml
name: "domain-expert-name"
type: "domain-expert"
version: "3.0.0"
specialization: "focused-domain"

# Domain expertise declaration
domain_expertise:
  software: ["tool1", "tool2", "tool3"]
  analysis_types: ["analysis1", "analysis2"]
  industry_standards: ["DNV-RP-C205", "API RP 2SK", "ISO 19901-7"]
  external_sources:
    - source: "EIA Data"
      url: "https://example.com"
      refresh: "1d"  # Daily refresh
    - source: "Technical Standards"
      refresh: "1m"  # Monthly refresh

# Capabilities with auto-refresh
capabilities:
  auto_refresh: true
  chunking_strategies:
    - semantic
    - fixed_size
    - paragraph
    - section
    - hybrid
    - phased
  context_engineering: true
  cross_module_collaboration: true

# Context optimization
module_config:
  name: "module-name"
  specialization: "focused-area"
  context_optimization:
    cross_references:
      - "other-agent-1"
      - "other-agent-2"
    focused_domain: "specific-domain"
    max_context_size: 16000
    attention_manipulation: true
    context_layers: true

# Processing configuration
processing_config:
  module_optimization:
    context_size: 16000
    refresh_priority: "high"  # high | medium | low
  phased_approach:
    enabled: true
    phases:
      - discovery
      - quality
      - extraction
      - synthesis
      - validation
      - integration
    quality_threshold: 0.8  # 0.0-1.0

# Best practices flags
best_practices:
  automated_refresh: true
  incremental_knowledge_building: true
  modular_agent_management: true
  phased_document_approach: true
  rag_optimization: true
  scratchpad_processing: true
```

**Engineering Tool Agents** (JSON format):

```json
{
  "name": "Tool Agent",
  "version": "1.0.0",
  "type": "engineering-tool",
  "description": "Purpose and capabilities",

  "capabilities": [
    "batch_processing",
    "parametric_design",
    "fem_preprocessing",
    "marine_engineering"
  ],

  "settings": {
    "parallel_workers": 4,
    "cache_enabled": true,
    "validation_level": "strict"
  },

  "integrations": {
    "agent_name": {
      "enabled": true,
      "agent_path": "../relative/path",
      "data_exchange": ["geometry", "results"]
    }
  },

  "api": {
    "enabled": true,
    "host": "localhost",
    "port": 8000,
    "cors": {
      "enabled": true,
      "origins": ["http://localhost:3000"]
    },
    "rate_limit": {
      "requests": 60,
      "window": "1m"
    }
  },

  "performance": {
    "batch_size": 100,
    "timeout": 300,
    "retry_attempts": 3
  }
}
```

### 1.3 Cross-Repository References

**Standard reference formats:**

```yaml
# Reference workspace-hub central registry
primary_agent: "@workspace-hub/.claude/agents/domain/engineering/aqwa.yaml"

# Reference hub repository (assetutilities)
sub_agents:
  - "@assetutilities/agents/registry/sub-agents/workflow-automation"
  - "@assetutilities/agents/registry/sub-agents/visualization-automation"

# Reference other repositories
cross_references:
  - "@digitalmodel/agents/orcaflex"
  - "@worldenergydata/agents/financial-analysis"

# Relative path references (within same repo)
integrations:
  signal_analysis: "../../src/modules/signal_analysis"
  orcaflex_agent: "../orcaflex"
```

## 2. Agent Development Best Practices

### 2.1 Capability Declaration

**Clear, searchable capabilities:**

```yaml
capabilities:
  # Domain-specific
  - "offshore_hydrodynamics"
  - "mooring_analysis"
  - "wave_force_calculation"

  # Processing capabilities
  - "batch_processing"
  - "parallel_execution"
  - "incremental_learning"

  # Integration capabilities
  - "cross_agent_collaboration"
  - "data_export_import"
  - "api_integration"

  # Quality features
  - "automated_validation"
  - "quality_thresholds"
  - "error_handling"
```

### 2.2 Context Optimization

**Maximize context efficiency:**

```yaml
context_optimization:
  # Focus domain to reduce noise
  focused_domain: "offshore-engineering"

  # Cross-reference related agents
  cross_references:
    - "orcaflex"
    - "ansys-mechanical"

  # Set context limits
  max_context_size: 16000

  # Enable smart attention
  attention_manipulation: true
  context_layers: true

  # Repository awareness
  repositories:
    - "digitalmodel"
    - "worldenergydata"
    - "assetutilities"
```

### 2.3 Phased Processing Approach

**For complex documents/tasks:**

```yaml
phased_approach:
  enabled: true

  phases:
    # 1. Discovery - Understand structure
    - name: "discovery"
      goal: "Map document structure and identify key sections"

    # 2. Quality - Assess content quality
    - name: "quality"
      goal: "Evaluate content completeness and accuracy"
      threshold: 0.7

    # 3. Extraction - Pull relevant information
    - name: "extraction"
      goal: "Extract domain-specific data and insights"

    # 4. Synthesis - Combine information
    - name: "synthesis"
      goal: "Integrate extracted data into coherent model"

    # 5. Validation - Verify results
    - name: "validation"
      goal: "Validate against standards and requirements"
      threshold: 0.8

    # 6. Integration - Final assembly
    - name: "integration"
      goal: "Integrate with other agents and export results"

  # Auto-proceed if quality meets threshold
  auto_proceed_threshold: 0.8
```

### 2.4 Chunking Strategies

**Multiple strategies for different content:**

```yaml
chunking_strategies:
  # Semantic chunking (preferred for technical docs)
  - type: "semantic"
    method: "sentence-boundary"
    preserve_context: true

  # Fixed size (for consistent processing)
  - type: "fixed_size"
    size: 1000
    overlap: 100

  # Paragraph-based (for structured docs)
  - type: "paragraph"
    preserve_headers: true

  # Section-based (for large docs)
  - type: "section"
    hierarchy_aware: true

  # Hybrid approach (combine multiple)
  - type: "hybrid"
    primary: "semantic"
    fallback: "fixed_size"

  # Phased processing (progressive refinement)
  - type: "phased"
    phases: 6
    quality_gates: true
```

### 2.5 Auto-Refresh & Knowledge Updates

**Keep agent knowledge current:**

```yaml
auto_refresh:
  enabled: true
  schedule:
    # Market data - refresh daily
    - source: "energy_prices"
      interval: "1d"
      priority: "high"

    # Regulations - refresh weekly
    - source: "industry_regulations"
      interval: "1w"
      priority: "medium"

    # Standards - refresh monthly
    - source: "technical_standards"
      interval: "1m"
      priority: "low"

  # Incremental learning
  incremental_knowledge:
    enabled: true
    retention: "90d"  # Keep learnings for 90 days

  # Validation after refresh
  validation:
    enabled: true
    threshold: 0.8
    rollback_on_failure: true
```

## 3. Integration Best Practices

### 3.1 Cross-Agent Communication

**Explicit integration declarations:**

```yaml
# In agent configuration
integrations:
  orcaflex:
    enabled: true
    agent_path: "../orcaflex"
    data_exchange:
      input: ["geometry", "environmental_conditions"]
      output: ["rao_data", "wave_forces"]
    bidirectional: true

  ansys_mechanical:
    enabled: true
    agent_path: "../../ansys/mechanical"
    data_exchange:
      input: ["structural_model"]
      output: ["stress_results", "fatigue_analysis"]
    bidirectional: false
```

### 3.2 API Best Practices

**RESTful API configuration:**

```json
{
  "api": {
    "enabled": true,
    "host": "localhost",
    "port": 8000,

    "cors": {
      "enabled": true,
      "origins": ["http://localhost:3000", "http://localhost:8080"],
      "methods": ["GET", "POST", "PUT", "DELETE"],
      "credentials": true
    },

    "authentication": {
      "type": "api_key",
      "header": "X-API-Key",
      "required": false
    },

    "rate_limit": {
      "requests": 60,
      "window": "1m",
      "strategy": "sliding_window"
    },

    "endpoints": {
      "/api/v1/analyze": {
        "methods": ["POST"],
        "description": "Run analysis",
        "timeout": 300
      },
      "/api/v1/batch": {
        "methods": ["POST"],
        "description": "Batch processing",
        "async": true,
        "progress_reporting": true
      }
    }
  }
}
```

### 3.3 Workflow Automation Integration

**Hub-based sub-agent pattern (assetutilities hub):**

```yaml
# Reference shared workflow automation from hub
workflow_automation: "@assetutilities/agents/registry/sub-agents/workflow-automation"

# Configure for your repository
workflow_config:
  repo_type: "engineering"
  features:
    - "enhanced_specs"
    - "auto_documentation"
    - "cross_repo_sync"

  # Enable specific workflows
  workflows:
    enhanced_specs:
      enabled: true
      auto_update: true
      learning: true
      templates:
        - "minimal"
        - "standard"
        - "enhanced"
```

## 4. Quality & Validation Best Practices

### 4.1 Quality Thresholds

**Progressive quality gates:**

```yaml
quality_control:
  # Discovery phase threshold
  discovery_threshold: 0.6

  # Quality assessment threshold
  quality_threshold: 0.7

  # Validation threshold (final)
  validation_threshold: 0.8

  # Auto-proceed if above threshold
  auto_proceed: true

  # Actions on failure
  on_failure:
    action: "retry_with_different_strategy"
    max_retries: 3
    fallback: "manual_review"
```

### 4.2 Error Handling

**Robust error management:**

```json
{
  "error_handling": {
    "retry": {
      "enabled": true,
      "max_attempts": 3,
      "backoff": "exponential",
      "backoff_multiplier": 2
    },

    "logging": {
      "level": "INFO",
      "file": "logs/agent.log",
      "rotation": "daily",
      "retention": "30d"
    },

    "validation": {
      "strict_mode": true,
      "schema_validation": true,
      "output_verification": true
    },

    "fallback": {
      "enabled": true,
      "fallback_agent": "general_purpose_agent",
      "notification": "admin@example.com"
    }
  }
}
```

### 4.3 Performance Monitoring

**Track and optimize performance:**

```yaml
performance_monitoring:
  enabled: true

  metrics:
    - "execution_time"
    - "memory_usage"
    - "api_calls"
    - "token_usage"
    - "cache_hit_rate"

  optimization:
    caching:
      enabled: true
      ttl: "1h"
      max_size: "1GB"

    parallel_processing:
      enabled: true
      max_workers: 4
      batch_size: 100

    context_optimization:
      enabled: true
      compression: true
      pruning: true

  reporting:
    interval: "1h"
    output: "metrics/performance.json"
    dashboard_url: "http://localhost:3000/metrics"
```

## 5. Documentation Best Practices

### 5.1 Agent Documentation Structure

**Complete documentation for each agent:**

```markdown
# Agent Name

## Overview
- **Purpose**: What this agent does
- **Domain**: Specific domain or general-purpose
- **Version**: Current version (semver)
- **Status**: active | beta | deprecated

## Capabilities
- Capability 1
- Capability 2
- Capability 3

## Usage
### Basic Usage
\`\`\`bash
droid exec --agent agent-name "task description"
\`\`\`

### Advanced Configuration
\`\`\`yaml
# Configuration example
\`\`\`

## Integration
### Compatible Agents
- agent-1 (data exchange)
- agent-2 (workflow)

### API Endpoints
- POST /api/v1/analyze
- GET /api/v1/status

## Best Practices
- Tip 1
- Tip 2
- Tip 3

## Examples
### Example 1: Basic Analysis
\`\`\`python
# Code example
\`\`\`

### Example 2: Batch Processing
\`\`\`python
# Code example
\`\`\`

## Troubleshooting
### Common Issues
- Issue 1: Solution
- Issue 2: Solution
```

### 5.2 Internal Documentation Links

**Link to relevant documentation:**

```yaml
documentation:
  internal:
    - path: "src/modules/analysis/"
      description: "Analysis module implementation"
    - path: "specs/modules/aqwa/"
      description: "AQWA specification details"
    - path: "docs/context/"
      description: "Context optimization guide"

  external:
    - source: "DNV-RP-C205"
      url: "https://example.com/dnv-rp-c205"
      type: "standard"
    - source: "API RP 2SK"
      url: "https://example.com/api-rp-2sk"
      type: "standard"
    - source: "Energy Information Administration"
      url: "https://www.eia.gov"
      type: "data_source"
      refresh: "1d"
```

## 6. Version Control & Updates

### 6.1 Semantic Versioning

**Follow semver for agent versions:**

```yaml
# Version format: MAJOR.MINOR.PATCH
version: "3.2.1"

# Version history
version_history:
  - version: "3.2.1"
    date: "2025-10-05"
    changes:
      - "Bug fix: Corrected mooring tension calculation"
      - "Performance: Improved batch processing speed by 20%"
    breaking: false

  - version: "3.2.0"
    date: "2025-09-15"
    changes:
      - "Feature: Added support for multi-body dynamics"
      - "Feature: Integrated with OrcaFlex for coupled analysis"
    breaking: false

  - version: "3.0.0"
    date: "2025-08-01"
    changes:
      - "BREAKING: Changed configuration format to YAML"
      - "BREAKING: Updated API endpoints to v2"
      - "Feature: Phased processing approach"
    breaking: true
```

### 6.2 Changelog Maintenance

**Keep detailed changelog:**

```markdown
# Changelog

## [3.2.1] - 2025-10-05
### Fixed
- Corrected mooring tension calculation for catenary moorings
- Fixed cache invalidation issue

### Performance
- Improved batch processing speed by 20%
- Reduced memory usage by 15%

## [3.2.0] - 2025-09-15
### Added
- Multi-body dynamics support
- OrcaFlex integration for coupled analysis
- Progress reporting for long-running tasks

### Changed
- Updated context optimization algorithm
- Enhanced error messages

## [3.0.0] - 2025-08-01
### BREAKING CHANGES
- Configuration format changed from JSON to YAML
- API endpoints updated to v2 (v1 deprecated)

### Added
- Phased processing approach (6 phases)
- Quality thresholds with auto-proceed
- Cross-repository agent awareness
```

## 7. Repository-Specific Best Practices

### 7.1 Centralization Strategy

**Workspace-hub as single source of truth:**

```yaml
# In repository-specific agent
extends: "@workspace-hub/.claude/agents/domain/engineering/base-agent.yaml"

# Repository-specific overrides
overrides:
  processing_config:
    refresh_priority: "high"  # Override central config

  # Add repo-specific capabilities
  additional_capabilities:
    - "custom_workflow_1"
    - "custom_workflow_2"
```

### 7.2 Hub Repository Pattern (assetutilities)

**Shared sub-agents via hub:**

```yaml
# assetutilities as hub for workflow automation
hub_repository: "assetutilities"
reference_format: "@assetutilities/agents/registry/sub-agents/{agent-name}"

# Available shared agents
shared_agents:
  - workflow-automation (v1.0.0)
  - file-management-automation (v0.9.0)
  - visualization-automation (v0.8.5)
  - auth-system (v1.1.0)
  - git-workflow-automation (v1.0.0)

# Compatible repository types
compatible_repos:
  - engineering
  - data_science
  - project_management
  - infrastructure
  - documentation
```

### 7.3 Duplication Prevention

**Avoid duplicating across 25+ repos:**

```bash
# ❌ BAD: Copy to each repo
cp workspace-hub/agent.yaml repo1/agent.yaml
cp workspace-hub/agent.yaml repo2/agent.yaml
# ... (25 times)

# ✅ GOOD: Symlink to central
ln -s /mnt/github/workspace-hub/.claude/agents/domain/engineering/agent.yaml repo1/agents/agent.yaml

# ✅ BETTER: Reference in config
# repo1/agents/config.yaml
extends: "@workspace-hub/.claude/agents/domain/engineering/agent.yaml"

# ✅ BEST: Automated sync
bash modules/automation/sync_agent_configs.sh --pull  # Update central from repos
bash modules/automation/sync_agent_configs.sh --push  # Push central to repos
```

## 8. Testing & Validation Best Practices

### 8.1 Agent Testing

**Comprehensive testing approach:**

```yaml
testing:
  unit_tests:
    - test: "capability_verification"
      verify: "All declared capabilities are implemented"
    - test: "configuration_validation"
      verify: "Configuration schema is valid"

  integration_tests:
    - test: "cross_agent_communication"
      agents: ["orcaflex", "aqwa"]
      verify: "Data exchange works correctly"
    - test: "api_endpoints"
      verify: "All endpoints respond correctly"

  performance_tests:
    - test: "batch_processing"
      batch_size: 1000
      max_time: 300
      verify: "Completes within time limit"
    - test: "memory_usage"
      max_memory: "2GB"
      verify: "Stays within memory limit"

  validation_tests:
    - test: "output_quality"
      threshold: 0.8
      verify: "Output meets quality threshold"
    - test: "standards_compliance"
      standards: ["DNV-RP-C205", "API RP 2SK"]
      verify: "Results comply with standards"
```

### 8.2 Continuous Validation

**Automated validation pipeline:**

```bash
#!/bin/bash
# modules/automation/validate_agent_configs.sh

# Schema validation
for config in .claude/agents/**/*.{yaml,json}; do
    validate_schema "$config"
done

# Capability verification
verify_capabilities

# Cross-reference check
check_cross_references

# Performance benchmarking
run_performance_tests

# Generate validation report
generate_report > validation_report.md
```

## 9. Security Best Practices

### 9.1 API Security

```yaml
security:
  authentication:
    type: "api_key"  # or oauth2, jwt
    required: true
    key_rotation: "30d"

  authorization:
    rbac:
      enabled: true
      roles:
        - name: "admin"
          permissions: ["read", "write", "delete", "admin"]
        - name: "user"
          permissions: ["read", "write"]
        - name: "viewer"
          permissions: ["read"]

  encryption:
    data_at_rest: true
    data_in_transit: true
    algorithm: "AES-256"

  audit:
    enabled: true
    log_all_requests: true
    retention: "90d"
    sensitive_data_masking: true
```

### 9.2 Secrets Management

```yaml
# ❌ BAD: Hardcoded secrets
api_key: "sk-1234567890abcdef"

# ✅ GOOD: Environment variables
api_key: "${API_KEY}"

# ✅ BETTER: Secrets manager
api_key:
  source: "vault"
  path: "secret/agents/api_key"

# Configuration validation
secrets_validation:
  - check: "no_hardcoded_secrets"
    action: "block"
  - check: "environment_vars_exist"
    action: "warn"
```

## 10. Summary Checklist

**Before deploying any agent:**

- [ ] **Configuration**
  - [ ] Version number (semver)
  - [ ] Clear description and purpose
  - [ ] All capabilities declared
  - [ ] Created/updated timestamps

- [ ] **Optimization**
  - [ ] Context optimization configured
  - [ ] Chunking strategy selected
  - [ ] Phased processing (if applicable)
  - [ ] Auto-refresh enabled (if needed)

- [ ] **Integration**
  - [ ] Cross-agent references documented
  - [ ] API endpoints defined (if applicable)
  - [ ] Hub integrations configured
  - [ ] Data exchange formats specified

- [ ] **Quality**
  - [ ] Quality thresholds set
  - [ ] Error handling implemented
  - [ ] Validation tests written
  - [ ] Performance benchmarks met

- [ ] **Documentation**
  - [ ] README.md created
  - [ ] API documentation complete
  - [ ] Examples provided
  - [ ] Changelog maintained

- [ ] **Security**
  - [ ] No hardcoded secrets
  - [ ] Authentication configured
  - [ ] Audit logging enabled
  - [ ] RBAC implemented (if multi-user)

- [ ] **Repository**
  - [ ] Centralized in workspace-hub
  - [ ] Cross-references use @ format
  - [ ] No unnecessary duplication
  - [ ] Sync strategy defined

---

**This document should be the authoritative guide for all agent development in workspace-hub.**

Refer to specific agent configurations in `.claude/agents/` for implementation examples.