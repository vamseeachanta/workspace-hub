# pytest.ini Universal Configuration Package

> Complete testing standardization for 25 workspace-hub repositories
> Version: 1.0.0 | Created: 2025-01-13 | Status: Ready for Deployment

## Quick Navigation

### Start Here
1. **New to this package?** → Read [`README_PYTEST.md`](README_PYTEST.md) (10 min read)
2. **Need quick answers?** → Print [`PYTEST_QUICK_REFERENCE.md`](PYTEST_QUICK_REFERENCE.md) (1 page)
3. **Ready to deploy?** → Follow [`PYTEST_DEPLOYMENT_GUIDE.md`](PYTEST_DEPLOYMENT_GUIDE.md) (30 min)

## Files in This Package

### Configuration Templates (Copy to your repository root as `pytest.ini`)

| File | Size | Tier | Coverage | Use Case |
|------|------|------|----------|----------|
| **`pytest.ini`** | 20 KB | Universal | Configurable | Base template - start here |
| **`pytest.tier1.ini`** | 5.7 KB | 1 | 85% | Production critical repos |
| **`pytest.tier2.ini`** | 6.4 KB | 2 | 80% | Active development repos |
| **`pytest.tier3.ini`** | 8.3 KB | 3 | 75% | Maintenance/experimental repos |

### Documentation

| File | Size | Purpose |
|------|------|---------|
| **`README_PYTEST.md`** | 11 KB | Overview, quick start, troubleshooting |
| **`PYTEST_DEPLOYMENT_GUIDE.md`** | 15 KB | Complete deployment and customization guide |
| **`PYTEST_QUICK_REFERENCE.md`** | 7.1 KB | One-page cheat sheet (print this!) |
| **`INDEX.md`** | This file | Navigation guide |

### Automation

| File | Size | Purpose |
|------|------|---------|
| **`deploy_pytest_config.sh`** | 9.1 KB | Automated deployment script for all 25 repos |

**Total Package Size: 82 KB**

## Repository Tier Mapping

### Tier 1: Production Critical (85% Coverage)
```
digitalmodel
energy
frontierdeepwater

Use: pytest.tier1.ini
Characteristics: Strict quality, conservative parallelization
Philosophy: Every production change must include tests
```

### Tier 2: Development Active (80% Coverage)
```
aceengineercode
assetutilities
worldenergydata
rock-oil-field
teamresumes

Use: pytest.tier2.ini
Characteristics: Balanced quality, standard parallelization
Philosophy: Good coverage without slowing iteration
```

### Tier 3: Maintenance & Experimental (75% Coverage)
```
All others (doris, saipem, hobbies, investments, sd-work, etc.)

Use: pytest.tier3.ini
Characteristics: Pragmatic quality, maximum parallelization
Philosophy: Focus on critical functionality
```

## 60-Second Quick Start

```bash
# 1. Identify your tier (above)
# 2. Copy template
cp pytest.tier2.ini pytest.ini  # Change tier as needed

# 3. Install packages
pip install pytest pytest-cov pytest-xdist pytest-asyncio pytest-timeout

# 4. Verify setup
pytest --co

# 5. Run tests
pytest tests/ -v

# 6. Check coverage
pytest --cov --cov-report=html
open htmlcov/index.html

# 7. Commit
git add pytest.ini
git commit -m "Add pytest.ini configuration"
git push
```

## Test Marker System

Every test needs at least one primary marker:

```python
@pytest.mark.unit          # Fast, single function (~<100ms)
@pytest.mark.integration   # Components interact (~100ms-2s)
@pytest.mark.e2e          # Complete workflow (~2s+)
```

Add secondary markers as needed:

```python
@pytest.mark.slow         # Takes >2 seconds
@pytest.mark.flaky        # Sometimes fails non-deterministically
@pytest.mark.database     # Requires database
@pytest.mark.api          # Makes API calls
@pytest.mark.selenium     # Browser automation
@pytest.mark.scrapy       # Web scraping
@pytest.mark.llm          # LLM API calls
```

## Common Commands

```bash
# Run tests
pytest                          # All tests
pytest -m unit                  # Only unit tests
pytest -m "not slow"            # Skip slow tests

# Coverage
pytest --cov --cov-report=html  # HTML report

# Parallel (faster)
pytest -n 8                     # 8 workers

# Debugging
pytest -v                       # Verbose
pytest -s                       # Show prints
pytest -x                       # Stop on first failure
```

## Documentation Roadmap

**Reading Time: 45 minutes total**

### For Quick Start (10 minutes)
1. Read: `README_PYTEST.md` (overview section)
2. Print: `PYTEST_QUICK_REFERENCE.md` (keep visible)
3. Copy: Appropriate tier template
4. Test: `pytest --co`

### For Complete Understanding (30 minutes)
1. Read: `PYTEST_DEPLOYMENT_GUIDE.md` (all sections)
2. Review: Tier-specific configuration
3. Understand: Customization options
4. Study: CI/CD integration examples

### For Reference (5 minutes)
1. Bookmark: `PYTEST_QUICK_REFERENCE.md`
2. Share: Deployment guide with team
3. Automate: Use `deploy_pytest_config.sh` for bulk deployment

## Key Features

✅ **9 Test Markers** - Organized, selective test execution
✅ **Tier-Aware Coverage** - 85%/80%/75% based on criticality
✅ **Parallel Execution** - 4-8x faster with pytest-xdist
✅ **Comprehensive Docs** - 50+ KB of guides and examples
✅ **Auto Deployment** - Script for all 25 repositories
✅ **Easy Customization** - Override specific settings per repo
✅ **CI/CD Ready** - GitHub Actions examples included
✅ **Async Support** - Built-in pytest-asyncio configuration
✅ **Coverage Reports** - HTML, XML, and terminal output

## Deployment Options

### Option 1: Manual (Simple)
```bash
cp pytest.tier2.ini pytest.ini
git add pytest.ini && git commit && git push
```

### Option 2: Automated (Fast)
```bash
bash deploy_pytest_config.sh
# Script handles all 25 repos automatically
```

### Option 3: Per-Tier (Controlled)
```bash
# Process each repository individually
# Using appropriate tier template
```

## File Locations

```
/mnt/github/workspace-hub/docs/templates/

├── pytest.ini                      # Universal base
├── pytest.tier1.ini               # Tier 1 config
├── pytest.tier2.ini               # Tier 2 config
├── pytest.tier3.ini               # Tier 3 config
├── README_PYTEST.md               # Quick overview
├── PYTEST_DEPLOYMENT_GUIDE.md     # Complete guide
├── PYTEST_QUICK_REFERENCE.md      # Cheat sheet
├── deploy_pytest_config.sh        # Deployment script
└── INDEX.md                        # This file
```

## Success Indicators

After deployment, you should see:

- ✅ Consistent test discovery across all 25 repos
- ✅ Coverage threshold enforcement in CI/CD
- ✅ 4-8x faster test execution with parallelization
- ✅ Clear test organization with 9 markers
- ✅ Better developer experience with quick feedback
- ✅ Easier onboarding for new team members

## Next Steps

### Immediate (1-2 hours)
1. Read `README_PYTEST.md`
2. Review `PYTEST_QUICK_REFERENCE.md`
3. Copy template to one repository
4. Run `pytest --co` to verify
5. Run tests and check coverage

### Short Term (1 week)
1. Deploy to all 25 repositories
2. Add markers to existing tests
3. Run with coverage enforcement
4. Generate HTML coverage reports
5. Address coverage gaps

### Ongoing
1. Mark all new tests with markers
2. Check coverage before commits
3. Use markers to control test execution
4. Monitor CI/CD metrics
5. Improve coverage incrementally

## Support

### Quick Reference
- `PYTEST_QUICK_REFERENCE.md` - One-page cheat sheet

### Complete Guide
- `PYTEST_DEPLOYMENT_GUIDE.md` - Full documentation

### External Resources
- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [pytest-xdist](https://pytest-xdist.readthedocs.io/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)

### workspace-hub Standards
- See: `@docs/modules/standards/TESTING_FRAMEWORK_STANDARDS.md`

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-01-13 | Initial release with tier-specific overrides |

---

## File Size Summary

```
pytest.ini (20 KB)                    - Universal base template
pytest.tier1.ini (5.7 KB)            - Tier 1 (85% coverage)
pytest.tier2.ini (6.4 KB)            - Tier 2 (80% coverage)
pytest.tier3.ini (8.3 KB)            - Tier 3 (75% coverage)
README_PYTEST.md (11 KB)             - Overview and quick start
PYTEST_DEPLOYMENT_GUIDE.md (15 KB)   - Complete deployment guide
PYTEST_QUICK_REFERENCE.md (7.1 KB)   - One-page cheat sheet
deploy_pytest_config.sh (9.1 KB)     - Deployment automation
INDEX.md (this file) (~5 KB)         - Navigation guide
─────────────────────────────────────
Total: ~82 KB of production-ready configuration and documentation
```

---

**Ready to standardize testing across workspace-hub?**

**Start with:** `README_PYTEST.md`
**Print:** `PYTEST_QUICK_REFERENCE.md`
**Deploy with:** `deploy_pytest_config.sh` or copy appropriate tier template

