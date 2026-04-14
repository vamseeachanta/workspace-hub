# AI Usage Guidelines Compliance System

> **Quick Start Guide for Enforcement Infrastructure**
> **Path Update (2026-02-17)**: Compliance scripts now live under `scripts/operations/compliance/`.

## Current Canonical Commands

```bash
./scripts/operations/compliance/verify_compliance.sh
./scripts/operations/compliance/check_governance.sh --mode warn --scope changed
./scripts/operations/compliance/validate_work_queue_schema.sh --mode warn --scope changed
./scripts/operations/compliance/audit_wrk_location.sh --mode warn --scope all
./scripts/operations/compliance/audit_skill_symlink_policy.sh --mode warn --scope all
```

## 🎯 Purpose

This compliance system ensures that **all AI agents and users** across all 26+ workspace-hub repositories follow proven best practices that deliver:

- **90% time savings** vs. asking AI to describe scripts
- **Very low error rates** with reproducible workflows
- **Excellent version control** and audit trails
- **Consistent patterns** across all repositories

## 🚀 Quick Start

### For Repository Owners

**1. Setup Compliance in Your Repository:**
```bash
cd /path/to/your/repo

# Run setup script from workspace-hub
/mnt/github/workspace-hub/scripts/setup_compliance.sh .

# Verify compliance
./scripts/verify_compliance.sh

# Install git hooks
./scripts/install_compliance_hooks.sh
```

**2. Review Compliance Report:**
```bash
# Check what was done
cat compliance_report.txt

# Aim for 90%+ compliance score
```

**3. Commit Changes:**
```bash
git add .
git commit -m "Add AI usage guidelines compliance

- AI_USAGE_GUIDELINES.md with enforcement
- CLAUDE.md with critical enforcement section
- Compliance verification scripts
- Git hooks for automatic checks
- Template files for workflows"
```

---

### For AI Agents (Claude, OpenAI, Factory.ai)

**MANDATORY BEHAVIOR:**

When user violates best practices (e.g., "Describe what this script does"):

**❌ WRONG RESPONSE:**
```
Here's what the script does: [long description]
```

**✅ CORRECT RESPONSE:**
```
I notice you're asking me to describe the script (⭐ PRETTY BAD effectiveness).

Instead, let me follow the ⭐⭐⭐⭐⭐ BEST PRACTICE:

1. I'll prepare the YAML input file in config/input/
2. I'll provide you the exact bash command to run
3. You execute the command and we review ACTUAL results

This approach is 90% faster with very low error rate.

See docs/ai/AI_USAGE_GUIDELINES.md for the full effectiveness matrix.

Should I proceed with the correct approach?
```

**KEY RULES:**
1. ✅ Always reference `docs/ai/AI_USAGE_GUIDELINES.md`
2. ✅ Explain the effectiveness matrix (⭐ ratings)
3. ✅ Stop and wait for user agreement
4. ✅ Guide user to ⭐⭐⭐⭐⭐ patterns
5. ❌ Never proceed with ⭐ (bad) patterns

---

## 📁 File Structure

```
repository/
├── CLAUDE.md                              # AI agent config with enforcement
├── docs/
│   ├── AI_USAGE_GUIDELINES.md            # Best practices (⭐⭐⭐⭐⭐ patterns)
│   ├── AI_AGENT_GUIDELINES.md            # Agent-specific guidelines
│   ├── DEVELOPMENT_WORKFLOW.md           # 6-phase workflow
│   ├── COMPLIANCE_ENFORCEMENT.md         # This system (detailed)
│   └── README_COMPLIANCE.md              # This file (quick start)
├── templates/
│   ├── user_prompt.md                    # User requirements template
│   ├── input_config.yaml                 # YAML config template
│   ├── pseudocode.md                     # Algorithm design template
│   ├── run_tests.sh                      # Test execution template
│   └── workflow.sh                       # Complete workflow automation
├── scripts/
│   ├── verify_compliance.sh              # Compliance checking
│   ├── setup_compliance.sh               # Auto-setup infrastructure
│   ├── install_compliance_hooks.sh       # Git hooks installation
│   └── propagate_guidelines.sh           # Deploy to all repos
├── config/
│   └── input/                            # YAML input files
├── docs/
│   └── pseudocode/                       # Algorithm designs
└── .git/
    └── hooks/                            # Pre-commit, commit-msg, post-checkout
```

---

## 🛠️ Available Tools

### 1. Compliance Verification

**Script:** `scripts/verify_compliance.sh`

**Purpose:** Check if repository follows best practices

**Usage:**
```bash
# Standard check (warnings only)
./scripts/verify_compliance.sh

# Strict mode (fails on warnings)
./scripts/verify_compliance.sh . true

# Custom report location
./scripts/verify_compliance.sh /path/to/repo false report.txt
```

**Output:**
- Compliance score (0-100%)
- Passed/failed/warning counts
- Detailed report file
- Recommendations

**Checks:**
- ✅ Required documentation present
- ✅ Directory structure correct
- ✅ CLAUDE.md has enforcement section
- ✅ Files in correct locations
- ✅ Git repository initialized
- ✅ Templates available

---

### 2. Compliance Setup

**Script:** `scripts/setup_compliance.sh`

**Purpose:** Auto-create compliance infrastructure

**Usage:**
```bash
# Setup current repository
./scripts/setup_compliance.sh

# Setup another repository
./scripts/setup_compliance.sh /path/to/repo
```

**Creates:**
- Required directories (scripts/, config/, docs/, templates/)
- Copies guideline documents
- Copies template files
- Creates .gitignore
- Makes scripts executable

---

### 3. Git Hooks Installation

**Script:** `scripts/install_compliance_hooks.sh`

**Purpose:** Install automated compliance checks

**Usage:**
```bash
# Install in current repository
./scripts/install_compliance_hooks.sh

# Install in another repository
./scripts/install_compliance_hooks.sh /path/to/repo
```

**Hooks Installed:**

**pre-commit:**
- Runs compliance verification before commit
- Checks file organization
- Warns about misplaced files
- Does NOT block commits (informational)

**commit-msg:**
- Enhances commit messages
- Adds guideline references

**post-checkout:**
- Reminds about compliance after checkout
- Suggests running verification

---

### 4. Propagation to All Repositories

**Script:** `scripts/propagate_guidelines.sh`

**Purpose:** Deploy compliance to all 26+ repositories

**Usage:**
```bash
# Dry run (see what would happen)
./scripts/propagate_guidelines.sh true

# Actual propagation
./scripts/propagate_guidelines.sh false
```

**Process:**
1. Scans `/mnt/github/` for all repositories
2. Skips workspace-hub (source of truth)
3. Copies all guideline files
4. Copies all template files
5. Copies all scripts
6. Updates CLAUDE.md with enforcement
7. Creates directory structure
8. Installs git hooks
9. Generates report

**Output:**
- Per-repository status
- Total updated/skipped/failed counts
- Propagation report file

---

## 📊 Effectiveness Matrix

From `AI_USAGE_GUIDELINES.md`:

| Approach | Rating | Time Saved | Error Rate | Reproducibility |
|----------|--------|------------|------------|-----------------|
| **Script + AI Input + AI Command** | ⭐⭐⭐⭐⭐ | 90% | Very Low | Excellent |
| **Git Operations (Claude)** | ⭐⭐⭐⭐⭐ | 80% | Very Low | Excellent |
| **Script + Input File** | ⭐⭐⭐⭐ | 70% | Low | Very Good |
| **Preparing Input Files** | ⭐⭐⭐⭐ | 75% | Low | Very Good |
| **Script Only (no input)** | ⭐⭐⭐ | 40% | Medium | Poor |
| **LLM Descriptions** | ⭐ | -20% | N/A | None |

**Use ONLY ⭐⭐⭐⭐⭐ and ⭐⭐⭐⭐ patterns!**

---

## 🚨 Enforcement Rules

### For AI Agents

**IF user asks for ⭐ (BAD) pattern:**

1. ✅ **STOP IMMEDIATELY**
2. ✅ **REFERENCE** `docs/ai/AI_USAGE_GUIDELINES.md`
3. ✅ **EXPLAIN** the correct ⭐⭐⭐⭐⭐ approach
4. ✅ **WAIT** for user agreement
5. ✅ **GUIDE** user to proper workflow

**Example:**
```
❌ USER: "Describe what run_analysis.sh does"

✅ AI: "I notice you're asking me to describe the script.
       This is a ⭐ (PRETTY BAD) approach with -20% time savings.

       Instead, let me follow ⭐⭐⭐⭐⭐ BEST PRACTICE:
       1. Prepare YAML input file
       2. Provide exact bash command
       3. You run it and we review ACTUAL results

       90% time savings, very low errors, excellent reproducibility.

       Should I proceed with the correct approach?"
```

---

### For Users

**REQUIRED WORKFLOW:**

1. ✅ AI prepares YAML input file in `config/input/`
2. ✅ AI provides exact bash command to execute
3. ✅ User runs command with prepared input
4. ✅ Review actual results (not descriptions)
5. ✅ Use Claude for ALL git operations

**AVOID:**
- ❌ Asking AI to describe scripts
- ❌ Running scripts without YAML input files
- ❌ Manually constructing complex commands
- ❌ Skipping version control of configurations

---

## 📈 Compliance Levels

### Level 1: Minimal (60-70%)
- Basic directory structure
- At least one guideline document
- CLAUDE.md exists

### Level 2: Standard (70-85%)
- All required directories
- All guideline documents
- CLAUDE.md with enforcement
- Templates available

### Level 3: Full (85-95%)
- All Level 2 requirements
- Git hooks installed
- Files properly organized
- Compliance scripts present

### Level 4: Exemplary (95-100%)
- All Level 3 requirements
- CI/CD compliance checks
- Active use of ⭐⭐⭐⭐⭐ patterns
- Zero misplaced files

**Target: Level 3 (Full Compliance) minimum**

---

## 🔄 Maintenance

### Weekly
```bash
# Verify compliance in active repositories
cd /path/to/active/repo
./scripts/verify_compliance.sh
```

### Monthly
```bash
# Propagate updates to all repositories
cd /mnt/github/workspace-hub
./scripts/propagate_guidelines.sh false
```

### Quarterly
```bash
# Review and update guidelines
vim docs/ai/AI_USAGE_GUIDELINES.md
# Test changes
./scripts/verify_compliance.sh . true
# Propagate
./scripts/propagate_guidelines.sh false
```

### On New Repository
```bash
cd /path/to/new/repo
/mnt/github/workspace-hub/scripts/setup_compliance.sh .
./scripts/verify_compliance.sh
./scripts/install_compliance_hooks.sh
```

---

## 📞 Troubleshooting

**Q: Compliance script not found?**
```bash
cp /mnt/github/workspace-hub/scripts/verify_compliance.sh ./scripts/
chmod +x ./scripts/verify_compliance.sh
```

**Q: Missing guideline documents?**
```bash
/mnt/github/workspace-hub/scripts/setup_compliance.sh .
```

**Q: Git hooks not working?**
```bash
./scripts/install_compliance_hooks.sh
ls -la .git/hooks/
```

**Q: Low compliance score?**
```bash
./scripts/verify_compliance.sh
cat compliance_report.txt
# Fix issues one by one
./scripts/verify_compliance.sh  # Re-check
```

---

## 📚 Documentation

### Primary Documents

1. **AI_USAGE_GUIDELINES.md** - Best practices with effectiveness ratings
2. **AI_AGENT_GUIDELINES.md** - Agent-specific requirements
3. **DEVELOPMENT_WORKFLOW.md** - 6-phase development process
4. **COMPLIANCE_ENFORCEMENT.md** - Detailed enforcement system
5. **README_COMPLIANCE.md** - This quick start guide

### Templates

1. **user_prompt.md** - User requirements
2. **input_config.yaml** - YAML configuration
3. **pseudocode.md** - Algorithm design
4. **run_tests.sh** - Test execution
5. **workflow.sh** - Complete automation

---

## ✅ Success Criteria

**Repository Level:**
- ✅ Compliance score ≥ 90%
- ✅ Zero critical violations
- ✅ All ⭐⭐⭐⭐⭐ patterns in use
- ✅ Git hooks active

**Organization Level:**
- ✅ 100% of repositories compliant
- ✅ Consistent patterns everywhere
- ✅ Active workflow automation
- ✅ Regular updates propagated

**User Experience:**
- ✅ Faster results (90% time savings)
- ✅ Fewer errors (very low rate)
- ✅ Better reproducibility
- ✅ Clear audit trails

---

## 🎓 Key Takeaways

1. **⭐⭐⭐⭐⭐ ALWAYS**: AI prepares YAML + provides command
2. **⭐⭐⭐⭐⭐ ALWAYS**: Use Claude for git operations
3. **❌ NEVER**: Ask AI to describe scripts
4. **✅ ALWAYS**: Version control YAML configurations
5. **✅ ENFORCE**: Reference guidelines when violations occur

---

**Remember:** Compliance is about effectiveness, not bureaucracy. The ⭐⭐⭐⭐⭐ patterns exist because they deliver results faster and more reliably.

---

**Quick Links:**
- Full Guidelines: `docs/ai/AI_USAGE_GUIDELINES.md`
- Detailed Enforcement: `docs/COMPLIANCE_ENFORCEMENT.md`
- Development Workflow: `docs/workflow/DEVELOPMENT_WORKFLOW.md`
- Verify Compliance: `./scripts/verify_compliance.sh`
- Setup Compliance: `./scripts/setup_compliance.sh`

**Last Updated:** 2025-10-24
