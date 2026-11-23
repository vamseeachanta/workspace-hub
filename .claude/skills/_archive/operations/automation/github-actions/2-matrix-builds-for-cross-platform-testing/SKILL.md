---
name: github-actions-2-matrix-builds-for-cross-platform-testing
description: 'Sub-skill of github-actions: 2. Matrix Builds for Cross-Platform Testing.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 2. Matrix Builds for Cross-Platform Testing

## 2. Matrix Builds for Cross-Platform Testing


```yaml
# .github/workflows/matrix-test.yml
name: Cross-Platform Tests

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test-matrix:
    name: Test (${{ matrix.os }}, Python ${{ matrix.python-version }})
    runs-on: ${{ matrix.os }}

    strategy:
      fail-fast: false
      max-parallel: 4
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ['3.10', '3.11', '3.12']
        include:
          # Additional configuration for specific combinations
          - os: ubuntu-latest
            python-version: '3.12'
            coverage: true
          # Experimental Python version
          - os: ubuntu-latest
            python-version: '3.13-dev'
            experimental: true
        exclude:
          # Skip Windows + Python 3.10 (known issues)
          - os: windows-latest
            python-version: '3.10'

    continue-on-error: ${{ matrix.experimental || false }}

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'
          cache-dependency-path: |
            pyproject.toml
            requirements*.txt

      - name: Install dependencies (Unix)
        if: runner.os != 'Windows'
        run: |
          pip install -e ".[dev]"

      - name: Install dependencies (Windows)
        if: runner.os == 'Windows'
        run: |
          pip install -e ".[dev]"
        shell: pwsh

      - name: Run tests
        run: |
          pytest tests/ -v --tb=short
        env:
          CI: true
          PLATFORM: ${{ matrix.os }}

      - name: Run tests with coverage
        if: matrix.coverage
        run: |
          pytest tests/ -v --cov=src --cov-report=xml

      - name: Upload coverage
        if: matrix.coverage
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.xml

  test-summary:
    name: Test Summary
    needs: test-matrix
    if: always()
    runs-on: ubuntu-latest
    steps:
      - name: Check matrix results
        run: |
          if [ "${{ needs.test-matrix.result }}" == "failure" ]; then
            echo "Some matrix jobs failed"
            exit 1
          fi
          echo "All matrix jobs passed"
```
