---
name: complexity-scorer
version: 1.0.0
description: Score task complexity using keyword matching, heuristic analysis, and
  configurable threshold rules
author: workspace-hub
category: _core
tags:
- bash
- complexity
- scoring
- keywords
- analysis
- classification
platforms:
- linux
- macos
see_also:
- complexity-scorer-1-keyword-based-scoring
- complexity-scorer-3-context-aware-scoring
- complexity-scorer-5-confidence-scoring
- complexity-scorer-best-practices
---

# Complexity Scorer

## When to Use This Skill

✅ **Use when:**
- Routing tasks to different handlers based on complexity
- Recommending resources (models, workers, time estimates)
- Prioritizing work items
- Auto-classifying incoming requests
- Building intelligent dispatchers

❌ **Avoid when:**
- Simple yes/no classification
- When ML-based classification is more appropriate
- Highly domain-specific scoring that requires expertise

## Complete Example: Task Complexity Scorer

```bash
#!/bin/bash
# ABOUTME: Complete task complexity scoring system
# ABOUTME: Multi-factor scoring with recommendations

set -e

# ─────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

# Keyword patterns
OPUS_KEYWORDS="architecture|refactor|design|security|complex|multi-file|algorithm|optimization|strategy|planning|cross-repository|performance|migration"
SONNET_KEYWORDS="implement|feature|bug|fix|code review|documentation|test|update|add|create|build"
HAIKU_KEYWORDS="check|status|simple|quick|template|list|grep|find|search|summary|validation|exists|show|display"

# Repository tiers

*See sub-skills for full details.*

## Resources

- [Regular Expressions in Bash](https://mywiki.wooledge.org/RegularExpression)
- [Pattern Matching](https://www.gnu.org/software/bash/manual/html_node/Pattern-Matching.html)

---

## Version History

- **1.0.0** (2026-01-14): Initial release - extracted from workspace-hub suggest_model.sh

## Sub-Skills

- [1. Keyword-Based Scoring (+1)](1-keyword-based-scoring/SKILL.md)
- [3. Context-Aware Scoring (+1)](3-context-aware-scoring/SKILL.md)
- [5. Confidence Scoring (+1)](5-confidence-scoring/SKILL.md)
- [Best Practices](best-practices/SKILL.md)
