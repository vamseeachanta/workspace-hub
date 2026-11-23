---
name: github-actions-1-basic-workflow-structure
description: 'Sub-skill of github-actions: 1. Basic Workflow Structure.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 1. Basic Workflow Structure

## 1. Basic Workflow Structure


```yaml
# .github/workflows/ci.yml
name: CI Pipeline

# Workflow triggers
on:
  push:
    branches: [main, develop]
    paths:
      - 'src/**'
      - 'tests/**'
      - 'pyproject.toml'
  pull_request:
    branches: [main]
    types: [opened, synchronize, reopened]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deployment environment'
        required: true
        default: 'staging'
        type: choice
        options:
          - staging
          - production
      debug:
        description: 'Enable debug mode'
        required: false
        type: boolean
        default: false

# Environment variables for all jobs
env:
  PYTHON_VERSION: '3.11'
  NODE_VERSION: '20'
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

# Concurrency control
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

# Workflow permissions
permissions:
  contents: read
  packages: write
  pull-requests: write

jobs:
  lint:
    name: Code Quality
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'

      - name: Install linters
        run: |
          pip install ruff mypy

      - name: Run linting
        run: |
          ruff check src/
          ruff format --check src/

      - name: Type checking
        run: mypy src/ --ignore-missing-imports

  test:
    name: Test Suite
    needs: lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"

      - name: Run tests
        run: |
          pytest tests/ -v --cov=src --cov-report=xml --cov-report=html

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.xml
          fail_ci_if_error: true

  build:
    name: Build Package
    needs: test
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.version.outputs.version }}
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install build tools
        run: pip install build

      - name: Get version
        id: version
        run: |
          VERSION=$(python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")
          echo "version=$VERSION" >> $GITHUB_OUTPUT

      - name: Build package
        run: python -m build

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: dist-${{ steps.version.outputs.version }}
          path: dist/
          retention-days: 5
```
