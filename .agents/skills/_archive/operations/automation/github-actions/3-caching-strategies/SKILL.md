---
name: github-actions-3-caching-strategies
description: 'Sub-skill of github-actions: 3. Caching Strategies (+1).'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 3. Caching Strategies (+1)

## 3. Caching Strategies


```yaml
# .github/workflows/caching.yml
name: Build with Caching

on: [push, pull_request]

jobs:
  build-with-cache:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Python pip cache
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
          cache-dependency-path: |
            requirements.txt
            requirements-dev.txt

      # Node modules cache
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: package-lock.json

      # Custom cache for build artifacts
      - name: Cache build outputs
        uses: actions/cache@v4
        id: build-cache
        with:
          path: |
            build/
            dist/
            .pytest_cache/
          key: build-${{ runner.os }}-${{ hashFiles('src/**', 'pyproject.toml') }}
          restore-keys: |
            build-${{ runner.os }}-

      # Docker layer cache
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Cache Docker layers
        uses: actions/cache@v4
        with:
          path: /tmp/.buildx-cache
          key: docker-${{ runner.os }}-${{ hashFiles('Dockerfile') }}
          restore-keys: |
            docker-${{ runner.os }}-

      # Rust cargo cache
      - name: Cache Cargo
        uses: actions/cache@v4
        with:
          path: |
            ~/.cargo/bin/
            ~/.cargo/registry/index/
            ~/.cargo/registry/cache/
            ~/.cargo/git/db/
            target/
          key: cargo-${{ runner.os }}-${{ hashFiles('**/Cargo.lock') }}
          restore-keys: |
            cargo-${{ runner.os }}-

      - name: Skip build if cached
        if: steps.build-cache.outputs.cache-hit == 'true'
        run: echo "Using cached build artifacts"

      - name: Build
        if: steps.build-cache.outputs.cache-hit != 'true'
        run: |
          pip install -e ".[dev]"
          python -m build

      - name: Run tests
        run: pytest tests/ -v
```


## 4. Artifact Management


```yaml
# .github/workflows/artifacts.yml
name: Build and Release Artifacts

on:
  push:
    tags: ['v*']
  workflow_dispatch:

jobs:
  build-artifacts:
    name: Build (${{ matrix.os }})
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        include:
          - os: ubuntu-latest
            artifact_name: app-linux-x64
            asset_name: app-linux-x64.tar.gz
          - os: macos-latest
            artifact_name: app-macos-x64
            asset_name: app-macos-x64.tar.gz
          - os: windows-latest
            artifact_name: app-windows-x64
            asset_name: app-windows-x64.zip

    steps:
      - uses: actions/checkout@v4

      - name: Build application
        run: |
          echo "Building for ${{ matrix.os }}"
          mkdir -p dist
          # Build commands here

      - name: Package (Unix)
        if: runner.os != 'Windows'
        run: |
          tar -czvf ${{ matrix.asset_name }} -C dist .

      - name: Package (Windows)
        if: runner.os == 'Windows'
        run: |
          Compress-Archive -Path dist/* -DestinationPath ${{ matrix.asset_name }}
        shell: pwsh

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: ${{ matrix.artifact_name }}
          path: ${{ matrix.asset_name }}
          retention-days: 30
          compression-level: 9

  create-release:
    name: Create Release
    needs: build-artifacts
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4

      - name: Download all artifacts
        uses: actions/download-artifact@v4
        with:
          path: artifacts/
          merge-multiple: false

      - name: List artifacts
        run: find artifacts/ -type f

      - name: Generate changelog
        id: changelog
        run: |
          # Extract changelog for this version
          VERSION=${GITHUB_REF#refs/tags/}
          echo "version=$VERSION" >> $GITHUB_OUTPUT

          # Generate release notes
          cat << EOF > release_notes.md
