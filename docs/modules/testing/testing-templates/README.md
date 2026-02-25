# Testing Templates Directory

This directory contains comprehensive baseline testing standards and reusable templates for all repository types in the Agent OS ecosystem.

## 📁 Directory Contents

### Core Documentation
- **[baseline-testing-standards.md](../baseline-testing-standards.md)** - Complete testing standards document
- **[implementation-guide.md](./implementation-guide.md)** - Step-by-step implementation instructions
- **[multi-language-structure.md](./multi-language-structure.md)** - Multi-language project patterns
- **[README-testing-section.md](./README-testing-section.md)** - Template for README testing sections

### Python Templates
- **[pytest.ini.template](./pytest.ini.template)** - pytest configuration
- **[pyproject.toml.pytest.template](./pyproject.toml.pytest.template)** - pytest config for pyproject.toml
- **[coveragerc.template](./coveragerc.template)** - Coverage.py configuration
- **[pyproject.toml.coverage.template](./pyproject.toml.coverage.template)** - Coverage config for pyproject.toml
- **[conftest.py.template](./conftest.py.template)** - pytest fixtures and setup
- **[requirements-test.txt.template](./requirements-test.txt.template)** - Python test dependencies

### JavaScript/Node.js Templates
- **[jest.config.js.template](./jest.config.js.template)** - Jest configuration
- **[package.json.jest.template](./package.json.jest.template)** - Jest config for package.json
- **[jest.setup.js.template](./jest.setup.js.template)** - Jest global setup and utilities
- **[babel.config.js.template](./babel.config.js.template)** - Babel configuration for Jest

### CI/CD Templates
- **[python-tests.yml.template](./python-tests.yml.template)** - GitHub Actions for Python projects
- **[node-tests.yml.template](./node-tests.yml.template)** - GitHub Actions for Node.js projects
- **[combined-tests.yml.template](./combined-tests.yml.template)** - GitHub Actions for multi-language projects

### Multi-Language Templates
- **[docker-compose.test.yml.template](./docker-compose.test.yml.template)** - Test services with Docker

## 🚀 Quick Start

### For New Projects

1. **Choose your project type:**
   - Python only → Use Python templates
   - Node.js only → Use JavaScript templates
   - Multi-language → Use combined templates

2. **Follow the implementation guide:**
   ```bash
   # Read the implementation guide
   cat docs/testing-templates/implementation-guide.md
   ```

3. **Copy relevant templates:**
   ```bash
   # Example for Python project
   cp docs/testing-templates/pytest.ini.template pytest.ini
   cp docs/testing-templates/coveragerc.template .coveragerc
   ```

### For Existing Projects

1. **Assess current setup:**
   ```bash
   # Check existing test configuration
   ls -la *test* *coverage* pytest.ini jest.config.js package.json pyproject.toml
   ```

2. **Follow migration approach in implementation guide**

3. **Gradually adopt standards:**
   - Start with configuration files
   - Add coverage requirements
   - Improve test structure
   - Implement CI/CD

## 📊 Standards Summary

### Coverage Requirements
- **Minimum**: 80% code coverage
- **Target**: 90% for critical components
- **Enforcement**: CI/CD quality gates

### Test Structure
- **Unit Tests**: Fast, isolated (70% of tests)
- **Integration Tests**: Component interaction (20% of tests)
- **E2E Tests**: Full system (10% of tests)

### CI/CD Integration
- Automated test execution on PR/push
- Multiple OS and version testing
- Coverage reporting and enforcement
- Security scanning integration

## 🔧 Template Usage

### 1. Direct Copy
```bash
# Copy template as-is
cp docs/testing-templates/pytest.ini.template pytest.ini
```

### 2. Customization
```bash
# Copy and customize
cp docs/testing-templates/jest.config.js.template jest.config.js
# Edit jest.config.js to match your project needs
```

### 3. Merge Configuration
```bash
# For pyproject.toml or package.json
# Copy relevant sections and merge into existing files
```

## 🛠️ Maintenance

### Updating Templates

When updating these templates:

1. **Test changes** in a sample project first
2. **Update version numbers** in template headers
3. **Document breaking changes** in implementation guide
4. **Notify team** of template updates

### Template Versioning

Templates follow semantic versioning:
- **Major**: Breaking changes requiring migration
- **Minor**: New features, backward compatible
- **Patch**: Bug fixes, small improvements

Current versions tracked in template headers.

## 📞 Support

### Common Questions

**Q: Which configuration format should I use?**
A: For Python: `pyproject.toml` for new projects, `pytest.ini` for existing ones. For Node.js: `jest.config.js` for complex setups, `package.json` for simple ones.

**Q: How do I handle legacy test code?**
A: Follow the migration approach in the implementation guide. Gradually migrate tests while maintaining functionality.

**Q: Can I customize the coverage thresholds?**
A: Yes, adjust the coverage percentages in the configuration files, but don't go below 80% minimum.

**Q: How do I add new testing tools?**
A: Update the relevant template and test the changes. Consider backward compatibility and team adoption.

### Getting Help

1. **Check implementation guide** for step-by-step instructions
2. **Review baseline standards** for requirements and rationale
3. **Look at example projects** that use these templates
4. **Ask team members** who have successfully implemented these standards

---

*This directory is part of the Agent OS ecosystem testing standards. Keep templates up-to-date and well-documented for team success.*