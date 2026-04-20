# AceEngineer Ecosystem Sync — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a daily 6:00 AM CT local cron on `ace-linux-1` that reviews 6 public engineering repos, writes a digest to `workspace-hub/docs/sync-reports/`, and files deduped GitHub issues on `vamseeachanta/aceengineer-website` when release/case-study/README/showcase-label signals fire.

**Architecture:** Single Python orchestrator (`scripts/ecosystem-sync/run.py`) invoked by a flock-guarded bash entry point. Five modules with one responsibility each: `models`, `config`, `state`, `signals`, `digest`, `issues`. All detectors pure except `detect_showcase_labeled_closed_issues` which hits `gh`. Read-only on source repos; issue-only on aceengineer-website.

**Tech Stack:** Python 3.11+, `uv` for runtime, `pyyaml`, `pytest`, `gh` CLI, systemd timer, bash + flock.

**Companion spec:** `docs/plans/2026-04-19-aceengineer-ecosystem-sync-design.md` (read it first).

**Working directory:** Run all commands from `/mnt/local-analysis/workspace-hub` unless noted. No worktree required — changes are additive and isolated under `scripts/ecosystem-sync/`, `tests/ecosystem-sync/`, `.claude/cron/`.

---

## Task 1: Scaffold package + Signal dataclass

**Files:**
- Create: `scripts/ecosystem-sync/__init__.py`
- Create: `scripts/ecosystem-sync/models.py`
- Create: `tests/ecosystem-sync/__init__.py`
- Create: `tests/ecosystem-sync/test_models.py`

- [ ] **Step 1: Write the failing test**

Create `tests/ecosystem-sync/test_models.py`:

```python
from scripts.ecosystem_sync.models import Signal


def test_signal_dedupe_key_release():
    s = Signal(
        repo="digitalmodel",
        kind="release",
        title="[sync] digitalmodel released v2.1.3",
        body="body here",
        dedupe_key="release:digitalmodel:v2.1.3",
        payload={"tag": "v2.1.3"},
    )
    assert s.dedupe_key == "release:digitalmodel:v2.1.3"
    assert s.kind == "release"


def test_signal_requires_all_fields():
    import pytest
    with pytest.raises(TypeError):
        Signal(repo="x")  # missing required fields
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/ecosystem-sync/test_models.py -v
```

Expected: `ModuleNotFoundError: No module named 'scripts.ecosystem_sync'`

- [ ] **Step 3: Create package files**

Create `scripts/ecosystem-sync/__init__.py`:

```python
```

Create `tests/ecosystem-sync/__init__.py`:

```python
```

- [ ] **Step 4: Create `scripts/ecosystem-sync/models.py`**

```python
"""Shared types for the ecosystem-sync cron."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Literal

SignalKind = Literal["release", "case-study", "readme-diff", "showcase"]


@dataclass(frozen=True)
class Signal:
    repo: str
    kind: SignalKind
    title: str
    body: str
    dedupe_key: str
    payload: dict[str, Any] = field(default_factory=dict)
```

- [ ] **Step 5: Handle the dashed-package-name import**

`scripts/ecosystem-sync/` has a dash; Python imports need underscores. Create `scripts/ecosystem_sync/` as a symlink OR use a conftest.py. Prefer the symlink — it keeps the directory name consistent with the spec while letting Python import it.

```bash
cd /mnt/local-analysis/workspace-hub/scripts
ln -s ecosystem-sync ecosystem_sync
cd /mnt/local-analysis/workspace-hub
```

Verify: `ls -la scripts/ | grep ecosystem` — should show `ecosystem_sync -> ecosystem-sync`.

- [ ] **Step 6: Run test to verify it passes**

```bash
uv run pytest tests/ecosystem-sync/test_models.py -v
```

Expected: `2 passed`.

- [ ] **Step 7: Commit**

```bash
git add scripts/ecosystem-sync/ scripts/ecosystem_sync tests/ecosystem-sync/__init__.py tests/ecosystem-sync/test_models.py
git commit -m "feat(ecosystem-sync): scaffold package with Signal dataclass"
```

---

## Task 2: Config loader + YAML

**Files:**
- Create: `scripts/ecosystem-sync/config.yaml`
- Create: `scripts/ecosystem-sync/config.py`
- Create: `tests/ecosystem-sync/test_config.py`
- Create: `tests/ecosystem-sync/fixtures/configs/minimal.yaml`

- [ ] **Step 1: Write the failing test**

Create `tests/ecosystem-sync/fixtures/configs/minimal.yaml`:

```yaml
repos:
  - name: demo
    path: /tmp/demo
    readme_sections: ["Capabilities"]
issue_repo: vamseeachanta/aceengineer-website
digest_dir: docs/sync-reports
state_file: .claude/state/ecosystem-sync/last-sync.yaml
max_issues_per_run: 20
```

Create `tests/ecosystem-sync/test_config.py`:

```python
from pathlib import Path
from scripts.ecosystem_sync.config import load_config


FIXTURE = Path(__file__).parent / "fixtures" / "configs" / "minimal.yaml"


def test_load_config_parses_required_fields():
    cfg = load_config(FIXTURE)
    assert cfg.issue_repo == "vamseeachanta/aceengineer-website"
    assert cfg.max_issues_per_run == 20
    assert len(cfg.repos) == 1
    assert cfg.repos[0].name == "demo"
    assert cfg.repos[0].readme_sections == ["Capabilities"]


def test_load_config_missing_file_raises(tmp_path):
    import pytest
    with pytest.raises(FileNotFoundError):
        load_config(tmp_path / "nonexistent.yaml")
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/ecosystem-sync/test_config.py -v
```

Expected: `ModuleNotFoundError: No module named 'scripts.ecosystem_sync.config'`.

- [ ] **Step 3: Create `scripts/ecosystem-sync/config.py`**

```python
"""Config loader for the ecosystem-sync cron."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import yaml


@dataclass(frozen=True)
class RepoConfig:
    name: str
    path: str
    readme_sections: list[str]


@dataclass(frozen=True)
class SyncConfig:
    repos: list[RepoConfig]
    issue_repo: str
    digest_dir: str
    state_file: str
    max_issues_per_run: int


def load_config(path: Path) -> SyncConfig:
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    raw = yaml.safe_load(path.read_text())
    repos = [RepoConfig(**r) for r in raw["repos"]]
    return SyncConfig(
        repos=repos,
        issue_repo=raw["issue_repo"],
        digest_dir=raw["digest_dir"],
        state_file=raw["state_file"],
        max_issues_per_run=int(raw["max_issues_per_run"]),
    )
```

- [ ] **Step 4: Run test to verify it passes**

```bash
uv run pytest tests/ecosystem-sync/test_config.py -v
```

Expected: `2 passed`.

- [ ] **Step 5: Create production config `scripts/ecosystem-sync/config.yaml`**

```yaml
repos:
  - name: digitalmodel
    path: /mnt/local-analysis/workspace-hub/digitalmodel
    readme_sections: ["Capabilities", "Features"]
  - name: assethold
    path: /mnt/local-analysis/workspace-hub/assethold
    readme_sections: ["What it does", "Capabilities"]
  - name: assetutilities
    path: /mnt/local-analysis/workspace-hub/assetutilities
    readme_sections: ["Capabilities", "Features"]
  - name: CAD-DEVELOPMENTS
    path: /mnt/local-analysis/workspace-hub/CAD-DEVELOPMENTS
    readme_sections: ["Capabilities", "Features"]
  - name: doris
    path: /mnt/local-analysis/workspace-hub/doris
    readme_sections: ["Capabilities", "Features"]
  - name: frontierdeepwater
    path: /mnt/local-analysis/workspace-hub/frontierdeepwater
    readme_sections: ["Capabilities", "Features"]
issue_repo: vamseeachanta/aceengineer-website
digest_dir: docs/sync-reports
state_file: .claude/state/ecosystem-sync/last-sync.yaml
max_issues_per_run: 20
```

- [ ] **Step 6: Commit**

```bash
git add scripts/ecosystem-sync/config.py scripts/ecosystem-sync/config.yaml tests/ecosystem-sync/test_config.py tests/ecosystem-sync/fixtures/
git commit -m "feat(ecosystem-sync): config loader + 6-repo production config"
```

---

## Task 3: State load/save with change detection

**Files:**
- Create: `scripts/ecosystem-sync/state.py`
- Create: `tests/ecosystem-sync/test_state.py`

- [ ] **Step 1: Write the failing test**

Create `tests/ecosystem-sync/test_state.py`:

```python
from pathlib import Path
from scripts.ecosystem_sync.state import (
    load_state, save_state, has_substantive_change, RepoState
)


def test_load_state_missing_file_returns_empty(tmp_path):
    state = load_state(tmp_path / "missing.yaml")
    assert state == {}


def test_roundtrip(tmp_path):
    path = tmp_path / "state.yaml"
    state = {
        "digitalmodel": RepoState(
            last_sync_utc="2026-04-20T11:00:00Z",
            last_commit_sha="abc123",
            last_seen_tags=["v1.0.0"],
            last_readme_hash={"Capabilities": "sha256:xyz"},
            last_case_studies=[],
            last_closed_showcase_issues=[],
        )
    }
    save_state(path, state)
    loaded = load_state(path)
    assert loaded["digitalmodel"].last_commit_sha == "abc123"


def test_substantive_change_ignores_timestamp_only():
    before = {"digitalmodel": RepoState(
        last_sync_utc="2026-04-19T11:00:00Z",
        last_commit_sha="abc", last_seen_tags=[], last_readme_hash={},
        last_case_studies=[], last_closed_showcase_issues=[],
    )}
    after = {"digitalmodel": RepoState(
        last_sync_utc="2026-04-20T11:00:00Z",  # only this changed
        last_commit_sha="abc", last_seen_tags=[], last_readme_hash={},
        last_case_studies=[], last_closed_showcase_issues=[],
    )}
    assert has_substantive_change(before, after) is False


def test_substantive_change_detects_new_tag():
    before = {"digitalmodel": RepoState(
        last_sync_utc="2026-04-19T11:00:00Z",
        last_commit_sha="abc", last_seen_tags=["v1.0.0"], last_readme_hash={},
        last_case_studies=[], last_closed_showcase_issues=[],
    )}
    after = {"digitalmodel": RepoState(
        last_sync_utc="2026-04-20T11:00:00Z",
        last_commit_sha="abc", last_seen_tags=["v1.0.0", "v1.1.0"],
        last_readme_hash={}, last_case_studies=[], last_closed_showcase_issues=[],
    )}
    assert has_substantive_change(before, after) is True
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/ecosystem-sync/test_state.py -v
```

Expected: `ModuleNotFoundError: No module named 'scripts.ecosystem_sync.state'`.

- [ ] **Step 3: Create `scripts/ecosystem-sync/state.py`**

```python
"""Load/save the last-sync state YAML. Change-detection excludes timestamps."""
from __future__ import annotations
from dataclasses import dataclass, asdict, field
from pathlib import Path
import yaml


@dataclass
class RepoState:
    last_sync_utc: str
    last_commit_sha: str
    last_seen_tags: list[str] = field(default_factory=list)
    last_readme_hash: dict[str, str] = field(default_factory=dict)
    last_case_studies: list[str] = field(default_factory=list)
    last_closed_showcase_issues: list[int] = field(default_factory=list)


def load_state(path: Path) -> dict[str, RepoState]:
    if not path.exists():
        return {}
    raw = yaml.safe_load(path.read_text()) or {}
    return {name: RepoState(**data) for name, data in raw.items()}


def save_state(path: Path, state: dict[str, RepoState]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    serializable = {name: asdict(rs) for name, rs in state.items()}
    path.write_text(yaml.safe_dump(serializable, sort_keys=True, default_flow_style=False))


def has_substantive_change(
    before: dict[str, RepoState], after: dict[str, RepoState]
) -> bool:
    """True if any repo state changed excluding last_sync_utc."""
    def strip_timestamp(rs: RepoState) -> dict:
        d = asdict(rs)
        d.pop("last_sync_utc", None)
        return d

    before_stripped = {k: strip_timestamp(v) for k, v in before.items()}
    after_stripped = {k: strip_timestamp(v) for k, v in after.items()}
    return before_stripped != after_stripped
```

- [ ] **Step 4: Run test to verify it passes**

```bash
uv run pytest tests/ecosystem-sync/test_state.py -v
```

Expected: `4 passed`.

- [ ] **Step 5: Commit**

```bash
git add scripts/ecosystem-sync/state.py tests/ecosystem-sync/test_state.py
git commit -m "feat(ecosystem-sync): state load/save with timestamp-aware change detection"
```

---

## Task 4: Signal 1 — release tag detector

**Files:**
- Create: `scripts/ecosystem-sync/signals.py` (first detector + helpers)
- Create: `tests/ecosystem-sync/fixtures/repos/build_fixtures.sh`
- Create: `tests/ecosystem-sync/test_signals_release.py`

- [ ] **Step 1: Create fixture-builder script**

Create `tests/ecosystem-sync/fixtures/repos/build_fixtures.sh`:

```bash
#!/usr/bin/env bash
# Build small git repos for signal-detector tests.
# Idempotent: rebuilds from scratch.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
rm -rf "$HERE/repo-with-release" "$HERE/repo-with-casestudy" "$HERE/repo-with-readme"

# Fixture 1: repo with a v1.0.0 and v1.1.0 tag
mkdir -p "$HERE/repo-with-release"
cd "$HERE/repo-with-release"
git init -q -b main
git config user.email test@example.com
git config user.name test
echo "# Fixture" > README.md
git add README.md && git commit -q -m "init"
git tag v1.0.0
echo "v1.1" >> README.md
git add README.md && git commit -q -m "bump"
git tag v1.1.0
# Noise tags that MUST be filtered:
git tag nightly-2026-04-20
git tag snapshot-abc
git tag pre-release-1

# Fixture 2: repo with a new case study file
mkdir -p "$HERE/repo-with-casestudy/case-studies"
cd "$HERE/repo-with-casestudy"
git init -q -b main
git config user.email test@example.com
git config user.name test
echo "# Fixture" > README.md
git add README.md && git commit -q -m "init"
BASELINE_SHA=$(git rev-parse HEAD)
cat > case-studies/mooring-failures.md <<'MDEOF'
# Mooring failures
Case study body here.
MDEOF
cat > case-studies/_draft/wip-study.md 2>/dev/null || mkdir -p case-studies/_draft
cat > case-studies/_draft/wip-study.md <<'MDEOF'
# draft — ignore me
MDEOF
cat > case-studies/CASE_STUDY_TEMPLATE.md <<'MDEOF'
# Template — ignore me
MDEOF
git add case-studies/
git commit -q -m "add case study + draft + template"
echo "$BASELINE_SHA" > "$HERE/repo-with-casestudy.baseline-sha"

# Fixture 3: repo with README capabilities section
mkdir -p "$HERE/repo-with-readme"
cd "$HERE/repo-with-readme"
git init -q -b main
git config user.email test@example.com
git config user.name test
cat > README.md <<'MDEOF'
# Fixture

## Capabilities
- thing one
- thing two

## Other
irrelevant
MDEOF
git add README.md && git commit -q -m "init"

echo "fixtures built at $HERE"
```

Make it executable and run:

```bash
chmod +x tests/ecosystem-sync/fixtures/repos/build_fixtures.sh
bash tests/ecosystem-sync/fixtures/repos/build_fixtures.sh
```

Expected: `fixtures built at /mnt/local-analysis/workspace-hub/tests/ecosystem-sync/fixtures/repos`.

- [ ] **Step 2: Gitignore fixture git repos but keep the builder**

Add to `.gitignore` (scoped):

```bash
cat >> .gitignore <<'EOF'

# ecosystem-sync test fixtures — built locally, not committed
tests/ecosystem-sync/fixtures/repos/repo-*
tests/ecosystem-sync/fixtures/repos/*.baseline-sha

# ecosystem-sync logs
logs/ecosystem-sync/
EOF
```

- [ ] **Step 3: Write the failing test**

Create `tests/ecosystem-sync/test_signals_release.py`:

```python
from pathlib import Path
from scripts.ecosystem_sync.signals import detect_release_tag
from scripts.ecosystem_sync.state import RepoState

FIXTURE = Path(__file__).parent / "fixtures" / "repos" / "repo-with-release"


def _empty_state() -> RepoState:
    return RepoState(
        last_sync_utc="2026-04-20T00:00:00Z",
        last_commit_sha="",
        last_seen_tags=[],
    )


def test_detects_new_semver_tags():
    sigs = detect_release_tag("digitalmodel", FIXTURE, _empty_state())
    tags = sorted(s.payload["tag"] for s in sigs)
    assert tags == ["v1.0.0", "v1.1.0"]


def test_filters_nightly_snapshot_pre():
    sigs = detect_release_tag("digitalmodel", FIXTURE, _empty_state())
    for s in sigs:
        assert not s.payload["tag"].startswith(("nightly-", "snapshot-", "pre-"))


def test_known_tag_not_re-reported():
    state = RepoState(
        last_sync_utc="2026-04-20T00:00:00Z",
        last_commit_sha="",
        last_seen_tags=["v1.0.0"],
    )
    sigs = detect_release_tag("digitalmodel", FIXTURE, state)
    tags = [s.payload["tag"] for s in sigs]
    assert tags == ["v1.1.0"]


def test_dedupe_key_format():
    sigs = detect_release_tag("digitalmodel", FIXTURE, _empty_state())
    for s in sigs:
        assert s.dedupe_key == f"release:digitalmodel:{s.payload['tag']}"
```

- [ ] **Step 4: Run test to verify it fails**

```bash
uv run pytest tests/ecosystem-sync/test_signals_release.py -v
```

Expected: `ImportError: cannot import name 'detect_release_tag'`.

- [ ] **Step 5: Create `scripts/ecosystem-sync/signals.py`**

```python
"""Signal detectors. Pure for signals 1-3; detect_showcase uses gh CLI."""
from __future__ import annotations
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable
from scripts.ecosystem_sync.models import Signal
from scripts.ecosystem_sync.state import RepoState


SEMVER_RE = re.compile(r"^v?\d+\.\d+(\.\d+)?$")
NOISE_PREFIXES = ("nightly-", "snapshot-", "pre-")


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, text=True, check=True, timeout=30,
    )
    return result.stdout


def detect_release_tag(
    repo_name: str, repo_path: Path, state: RepoState,
) -> list[Signal]:
    """Signal 1: new semver tags not seen before, filtered to non-noise, <90 days old."""
    tags_out = _git(repo_path, "tag", "-l")
    all_tags = [t.strip() for t in tags_out.splitlines() if t.strip()]
    cutoff = datetime.now(timezone.utc) - timedelta(days=90)
    signals: list[Signal] = []
    known = set(state.last_seen_tags)

    for tag in all_tags:
        if tag in known:
            continue
        if tag.startswith(NOISE_PREFIXES):
            continue
        if not SEMVER_RE.match(tag):
            continue
        # Check tag age
        try:
            ts_out = _git(repo_path, "log", "-1", "--format=%cI", tag)
            tag_date = datetime.fromisoformat(ts_out.strip())
            if tag_date < cutoff:
                continue
        except (subprocess.CalledProcessError, ValueError):
            continue
        # Build body from commit log since previous semver tag
        prev = _previous_semver(all_tags, tag)
        log_range = f"{prev}..{tag}" if prev else tag
        try:
            log_out = _git(repo_path, "log", log_range, "--oneline")
            body_commits = "\n".join(log_out.splitlines()[:20])
        except subprocess.CalledProcessError:
            body_commits = "(unable to compute commit log)"
        signals.append(Signal(
            repo=repo_name,
            kind="release",
            title=f"[sync] {repo_name} released {tag}",
            body=(
                f"New release detected in `{repo_name}`: **{tag}**\n\n"
                f"## Commits since previous release\n\n```\n{body_commits}\n```\n\n"
                f"## Proposed website update\n\n"
                f"Add to changelog/releases page; consider blog post if user-facing."
            ),
            dedupe_key=f"release:{repo_name}:{tag}",
            payload={"tag": tag},
        ))
    return signals


def _previous_semver(all_tags: Iterable[str], current: str) -> str | None:
    semvers = sorted(
        [t for t in all_tags if SEMVER_RE.match(t) and not t.startswith(NOISE_PREFIXES)],
        key=_semver_key,
    )
    if current not in semvers:
        return None
    idx = semvers.index(current)
    return semvers[idx - 1] if idx > 0 else None


def _semver_key(tag: str) -> tuple[int, ...]:
    parts = tag.lstrip("v").split(".")
    return tuple(int(p) for p in parts)
```

- [ ] **Step 6: Run test to verify it passes**

```bash
uv run pytest tests/ecosystem-sync/test_signals_release.py -v
```

Expected: `4 passed`.

- [ ] **Step 7: Commit**

```bash
git add scripts/ecosystem-sync/signals.py tests/ecosystem-sync/fixtures/repos/build_fixtures.sh tests/ecosystem-sync/test_signals_release.py .gitignore
git commit -m "feat(ecosystem-sync): signal 1 — release tag detector + fixtures"
```

---

## Task 5: Signal 2 — new case-study / example file detector

**Files:**
- Modify: `scripts/ecosystem-sync/signals.py` (add function)
- Create: `tests/ecosystem-sync/test_signals_casestudy.py`

- [ ] **Step 1: Write the failing test**

Create `tests/ecosystem-sync/test_signals_casestudy.py`:

```python
from pathlib import Path
from scripts.ecosystem_sync.signals import detect_new_case_study
from scripts.ecosystem_sync.state import RepoState

FIXTURE = Path(__file__).parent / "fixtures" / "repos" / "repo-with-casestudy"
BASELINE_FILE = FIXTURE.parent / "repo-with-casestudy.baseline-sha"


def _state_with_baseline() -> RepoState:
    sha = BASELINE_FILE.read_text().strip()
    return RepoState(
        last_sync_utc="2026-04-20T00:00:00Z",
        last_commit_sha=sha,
    )


def test_detects_new_case_study():
    sigs = detect_new_case_study("digitalmodel", FIXTURE, _state_with_baseline())
    paths = sorted(s.payload["path"] for s in sigs)
    assert "case-studies/mooring-failures.md" in paths


def test_filters_draft_and_template():
    sigs = detect_new_case_study("digitalmodel", FIXTURE, _state_with_baseline())
    paths = [s.payload["path"] for s in sigs]
    assert "case-studies/_draft/wip-study.md" not in paths
    assert "case-studies/CASE_STUDY_TEMPLATE.md" not in paths


def test_dedupe_key():
    sigs = detect_new_case_study("digitalmodel", FIXTURE, _state_with_baseline())
    assert all(s.dedupe_key.startswith("case-study:digitalmodel:") for s in sigs)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/ecosystem-sync/test_signals_casestudy.py -v
```

Expected: `ImportError: cannot import name 'detect_new_case_study'`.

- [ ] **Step 3: Append to `scripts/ecosystem-sync/signals.py`**

```python
CASE_STUDY_DIRS = ("case-studies", "examples", "demos", "docs/case-studies")
CASE_STUDY_SKIP_NAMES = {"README.md", "CASE_STUDY_TEMPLATE.md"}
CASE_STUDY_SKIP_PATH_SUBSTRINGS = ("/_draft/", "/wip/", "/archive/")


def detect_new_case_study(
    repo_name: str, repo_path: Path, state: RepoState,
) -> list[Signal]:
    """Signal 2: files added under case-studies/ / examples/ / demos/ / docs/case-studies/."""
    if not state.last_commit_sha:
        return []
    try:
        diff_out = _git(
            repo_path, "diff", "--name-status",
            f"{state.last_commit_sha}..HEAD", "--",
            *CASE_STUDY_DIRS,
        )
    except subprocess.CalledProcessError:
        return []

    signals: list[Signal] = []
    for line in diff_out.splitlines():
        parts = line.split(maxsplit=1)
        if len(parts) != 2 or parts[0] != "A":
            continue
        rel_path = parts[1]
        name = Path(rel_path).name
        if name.endswith(".template.md") or name in CASE_STUDY_SKIP_NAMES:
            continue
        if any(sub in f"/{rel_path}" for sub in CASE_STUDY_SKIP_PATH_SUBSTRINGS):
            continue
        abs_path = repo_path / rel_path
        preview = ""
        if abs_path.exists():
            try:
                preview = "\n".join(abs_path.read_text().splitlines()[:40])
            except (UnicodeDecodeError, OSError):
                preview = "(binary or unreadable)"
        signals.append(Signal(
            repo=repo_name,
            kind="case-study",
            title=f"[sync] {repo_name} added {name}",
            body=(
                f"New case study / example detected in `{repo_name}`: `{rel_path}`\n\n"
                f"## First 40 lines\n\n```\n{preview}\n```\n\n"
                f"## Proposed website update\n\n"
                f"Lift into `aceengineer-website/case-studies/`, link from index.html."
            ),
            dedupe_key=f"case-study:{repo_name}:{rel_path}",
            payload={"path": rel_path},
        ))
    return signals
```

- [ ] **Step 4: Run test to verify it passes**

```bash
uv run pytest tests/ecosystem-sync/test_signals_casestudy.py -v
```

Expected: `3 passed`.

- [ ] **Step 5: Commit**

```bash
git add scripts/ecosystem-sync/signals.py tests/ecosystem-sync/test_signals_casestudy.py
git commit -m "feat(ecosystem-sync): signal 2 — new case-study / example detector"
```

---

## Task 6: Signal 3 — README capability section diff

**Files:**
- Modify: `scripts/ecosystem-sync/signals.py`
- Create: `tests/ecosystem-sync/test_signals_readme.py`

- [ ] **Step 1: Write the failing test**

Create `tests/ecosystem-sync/test_signals_readme.py`:

```python
from pathlib import Path
from scripts.ecosystem_sync.signals import (
    detect_readme_capability_diff, _extract_section, _hash_section
)
from scripts.ecosystem_sync.state import RepoState

FIXTURE = Path(__file__).parent / "fixtures" / "repos" / "repo-with-readme"


def test_extract_section_basic():
    md = "# T\n\n## Capabilities\n- one\n- two\n\n## Other\nx\n"
    assert _extract_section(md, "Capabilities").strip() == "- one\n- two"


def test_extract_section_missing_returns_empty():
    md = "# T\n## Other\nx\n"
    assert _extract_section(md, "Capabilities") == ""


def test_hash_section_ignores_trailing_whitespace():
    a = _hash_section("- one\n- two")
    b = _hash_section("- one\n- two\n\n")
    assert a == b


def test_diff_fires_on_changed_hash():
    state = RepoState(
        last_sync_utc="2026-04-20T00:00:00Z",
        last_commit_sha="",
        last_readme_hash={"Capabilities": "sha256:wrong"},
    )
    sigs = detect_readme_capability_diff(
        "digitalmodel", FIXTURE, state, sections=["Capabilities"]
    )
    assert len(sigs) == 1
    assert sigs[0].kind == "readme-diff"


def test_diff_no_fire_when_hash_matches():
    md = (FIXTURE / "README.md").read_text()
    current = _hash_section(_extract_section(md, "Capabilities"))
    state = RepoState(
        last_sync_utc="2026-04-20T00:00:00Z",
        last_commit_sha="",
        last_readme_hash={"Capabilities": current},
    )
    sigs = detect_readme_capability_diff(
        "digitalmodel", FIXTURE, state, sections=["Capabilities"]
    )
    assert sigs == []


def test_missing_section_is_silent():
    state = RepoState(
        last_sync_utc="2026-04-20T00:00:00Z", last_commit_sha="",
    )
    sigs = detect_readme_capability_diff(
        "digitalmodel", FIXTURE, state, sections=["Nonexistent Heading"]
    )
    assert sigs == []
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/ecosystem-sync/test_signals_readme.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Append to `scripts/ecosystem-sync/signals.py`**

```python
import hashlib


def _extract_section(markdown: str, heading: str) -> str:
    """Return body of `## <heading>` section, up to next `## ` or EOF."""
    lines = markdown.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip() == f"## {heading}":
            start = i + 1
            break
    if start is None:
        return ""
    end = len(lines)
    for j in range(start, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    return "\n".join(lines[start:end]).strip()


def _hash_section(body: str) -> str:
    normalized = "\n".join(line.rstrip() for line in body.splitlines() if line.strip())
    return "sha256:" + hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def detect_readme_capability_diff(
    repo_name: str, repo_path: Path, state: RepoState, sections: list[str],
) -> list[Signal]:
    """Signal 3: README section hash drift."""
    readme_path = repo_path / "README.md"
    if not readme_path.exists():
        return []
    try:
        md = readme_path.read_text()
    except (UnicodeDecodeError, OSError):
        return []
    signals: list[Signal] = []
    for heading in sections:
        body = _extract_section(md, heading)
        if not body:
            continue  # silent skip per spec
        current_hash = _hash_section(body)
        prev_hash = state.last_readme_hash.get(heading)
        if prev_hash == current_hash:
            continue
        hash_prefix = current_hash.split(":")[1][:8]
        signals.append(Signal(
            repo=repo_name,
            kind="readme-diff",
            title=f"[sync] {repo_name} README \"{heading}\" section changed",
            body=(
                f"README section `## {heading}` changed in `{repo_name}`.\n\n"
                f"## Current section content\n\n```\n{body}\n```\n\n"
                f"## Proposed website update\n\n"
                f"Reflect capability change in engineering.html / about.html."
            ),
            dedupe_key=f"readme-diff:{repo_name}:{heading}:{hash_prefix}",
            payload={"heading": heading, "hash": current_hash},
        ))
    return signals
```

- [ ] **Step 4: Run test to verify it passes**

```bash
uv run pytest tests/ecosystem-sync/test_signals_readme.py -v
```

Expected: `6 passed`.

- [ ] **Step 5: Commit**

```bash
git add scripts/ecosystem-sync/signals.py tests/ecosystem-sync/test_signals_readme.py
git commit -m "feat(ecosystem-sync): signal 3 — README capability section diff"
```

---

## Task 7: Signal 5 — showcase/website labeled closed issues

**Files:**
- Modify: `scripts/ecosystem-sync/signals.py`
- Create: `tests/ecosystem-sync/test_signals_showcase.py`

- [ ] **Step 1: Write the failing test**

Create `tests/ecosystem-sync/test_signals_showcase.py`:

```python
from unittest.mock import patch
from scripts.ecosystem_sync.signals import detect_showcase_labeled_closed_issues
from scripts.ecosystem_sync.state import RepoState


def _mock_gh_output(issues_by_label: dict[str, list[dict]]):
    """Return a function that mocks subprocess.run for gh issue list."""
    import json
    def fake_run(cmd, **kwargs):
        from subprocess import CompletedProcess
        for label, issues in issues_by_label.items():
            if f"--label" in cmd and label in cmd:
                return CompletedProcess(
                    cmd, 0, stdout=json.dumps(issues), stderr=""
                )
        return CompletedProcess(cmd, 0, stdout="[]", stderr="")
    return fake_run


def test_detects_new_closed_issue():
    issues = {"showcase": [
        {"number": 42, "title": "Deep-learning mooring model", "body": "body",
         "labels": [{"name": "showcase"}], "closedAt": "2026-04-20T10:00:00Z"}
    ]}
    state = RepoState(
        last_sync_utc="2026-04-20T00:00:00Z", last_commit_sha="",
        last_closed_showcase_issues=[],
    )
    with patch("subprocess.run", side_effect=_mock_gh_output(issues)):
        sigs = detect_showcase_labeled_closed_issues(
            "digitalmodel", state, since="2026-04-19"
        )
    assert len(sigs) == 1
    assert sigs[0].payload["issue_number"] == 42


def test_skips_known_issue():
    issues = {"showcase": [
        {"number": 42, "title": "T", "body": "b",
         "labels": [{"name": "showcase"}], "closedAt": "2026-04-20T10:00:00Z"}
    ]}
    state = RepoState(
        last_sync_utc="2026-04-20T00:00:00Z", last_commit_sha="",
        last_closed_showcase_issues=[42],
    )
    with patch("subprocess.run", side_effect=_mock_gh_output(issues)):
        sigs = detect_showcase_labeled_closed_issues(
            "digitalmodel", state, since="2026-04-19"
        )
    assert sigs == []


def test_skips_not_planned():
    issues = {"showcase": [
        {"number": 42, "title": "T", "body": "b",
         "labels": [{"name": "showcase"}, {"name": "not-planned"}],
         "closedAt": "2026-04-20T10:00:00Z"}
    ]}
    state = RepoState(
        last_sync_utc="2026-04-20T00:00:00Z", last_commit_sha="",
        last_closed_showcase_issues=[],
    )
    with patch("subprocess.run", side_effect=_mock_gh_output(issues)):
        sigs = detect_showcase_labeled_closed_issues(
            "digitalmodel", state, since="2026-04-19"
        )
    assert sigs == []
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/ecosystem-sync/test_signals_showcase.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Append to `scripts/ecosystem-sync/signals.py`**

```python
import json

SHOWCASE_LABELS = ("showcase", "website")
SKIP_LABELS = ("not-planned", "duplicate")


def detect_showcase_labeled_closed_issues(
    repo_name: str, state: RepoState, since: str,
) -> list[Signal]:
    """Signal 5: issues closed with showcase or website label since last sync."""
    known = set(state.last_closed_showcase_issues)
    signals: list[Signal] = []
    seen_nums: set[int] = set()

    for label in SHOWCASE_LABELS:
        try:
            result = subprocess.run(
                ["gh", "issue", "list",
                 "--repo", f"vamseeachanta/{repo_name}",
                 "--label", label, "--state", "closed",
                 "--search", f"closed:>={since}",
                 "--json", "number,title,body,labels,closedAt",
                 "--limit", "100"],
                capture_output=True, text=True, check=True, timeout=60,
            )
            issues = json.loads(result.stdout or "[]")
        except (subprocess.CalledProcessError, json.JSONDecodeError, subprocess.TimeoutExpired):
            continue

        for issue in issues:
            num = issue["number"]
            if num in known or num in seen_nums:
                continue
            labels = {l["name"] for l in issue.get("labels", [])}
            if labels & set(SKIP_LABELS):
                continue
            seen_nums.add(num)
            body = issue.get("body", "") or ""
            truncated = " ".join(body.split()[:500])
            signals.append(Signal(
                repo=repo_name,
                kind="showcase",
                title=f"[sync] {repo_name} #{num}: {issue['title']}",
                body=(
                    f"Upstream issue closed with `{label}` label.\n\n"
                    f"Link: https://github.com/vamseeachanta/{repo_name}/issues/{num}\n\n"
                    f"## Upstream body (truncated)\n\n{truncated}\n\n"
                    f"## Proposed website update\n\nBlog post / case study draft."
                ),
                dedupe_key=f"showcase:{repo_name}:{num}",
                payload={"issue_number": num, "label": label},
            ))
    return signals
```

- [ ] **Step 4: Run test to verify it passes**

```bash
uv run pytest tests/ecosystem-sync/test_signals_showcase.py -v
```

Expected: `3 passed`.

- [ ] **Step 5: Commit**

```bash
git add scripts/ecosystem-sync/signals.py tests/ecosystem-sync/test_signals_showcase.py
git commit -m "feat(ecosystem-sync): signal 5 — labeled closed-issue detector"
```

---

## Task 8: Digest renderer with golden tests

**Files:**
- Create: `scripts/ecosystem-sync/digest.py`
- Create: `tests/ecosystem-sync/test_digest.py`
- Create: `tests/ecosystem-sync/golden/empty.md`
- Create: `tests/ecosystem-sync/golden/with_signals.md`

- [ ] **Step 1: Write the failing test**

Create `tests/ecosystem-sync/test_digest.py`:

```python
from pathlib import Path
from scripts.ecosystem_sync.digest import render_digest
from scripts.ecosystem_sync.models import Signal

GOLDEN = Path(__file__).parent / "golden"


def test_render_empty_day():
    out = render_digest(
        signals_by_repo={},
        skipped={},
        date="2026-04-20",
        duration_s=42,
        repos_total=6,
        issues_filed=0,
        suppressed_signals=[],
    )
    expected = (GOLDEN / "empty.md").read_text()
    assert out == expected


def test_render_with_signals():
    sig = Signal(
        repo="digitalmodel", kind="release",
        title="[sync] digitalmodel released v2.1.3",
        body="body here",
        dedupe_key="release:digitalmodel:v2.1.3",
        payload={"tag": "v2.1.3"},
    )
    out = render_digest(
        signals_by_repo={"digitalmodel": [sig]},
        skipped={"doris": "fetch timeout"},
        date="2026-04-20",
        duration_s=47,
        repos_total=6,
        issues_filed=1,
        suppressed_signals=[],
    )
    expected = (GOLDEN / "with_signals.md").read_text()
    assert out == expected
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/ecosystem-sync/test_digest.py -v
```

Expected: `ImportError` or `FileNotFoundError` for golden files.

- [ ] **Step 3: Create `scripts/ecosystem-sync/digest.py`**

```python
"""Pure markdown renderer for the daily digest."""
from __future__ import annotations
from scripts.ecosystem_sync.models import Signal


def render_digest(
    signals_by_repo: dict[str, list[Signal]],
    skipped: dict[str, str],
    date: str,
    duration_s: int,
    repos_total: int,
    issues_filed: int,
    suppressed_signals: list[Signal],
) -> str:
    parts: list[str] = [f"# Ecosystem Sync — {date}\n"]

    total_signals = sum(len(v) for v in signals_by_repo.values()) + len(suppressed_signals)
    repos_ok = repos_total - len(skipped)

    if total_signals == 0 and not skipped:
        parts.append("_No signals detected. Nothing to propose today._\n")
    else:
        parts.append("## Signals\n")
        if not signals_by_repo:
            parts.append("_No signals from any repo._\n")
        for repo in sorted(signals_by_repo):
            parts.append(f"\n### {repo}\n")
            for sig in signals_by_repo[repo]:
                parts.append(f"- **{sig.kind}**: {sig.title}\n")
                parts.append(f"  - dedupe: `{sig.dedupe_key}`\n")

    if skipped:
        parts.append("\n## Skipped repos\n")
        for repo in sorted(skipped):
            parts.append(f"- ⚠ `{repo}`: {skipped[repo]}\n")

    if suppressed_signals:
        parts.append(f"\n## Suppressed signals ({len(suppressed_signals)})\n")
        parts.append("_20-issue cap reached; these were NOT filed as issues:_\n\n")
        for sig in suppressed_signals:
            parts.append(f"- **{sig.kind}** `{sig.repo}`: {sig.title}\n")

    parts.append(
        f"\n---\n\n"
        f"Run footer: Duration: {duration_s}s · Repos OK: {repos_ok}/{repos_total} · "
        f"Signals: {total_signals} · Issues filed: {issues_filed} · "
        f"Next run: tomorrow 06:00 CT\n"
    )
    return "".join(parts)
```

- [ ] **Step 4: Create golden `tests/ecosystem-sync/golden/empty.md`**

```markdown
# Ecosystem Sync — 2026-04-20

_No signals detected. Nothing to propose today._

---

Run footer: Duration: 42s · Repos OK: 6/6 · Signals: 0 · Issues filed: 0 · Next run: tomorrow 06:00 CT
```

- [ ] **Step 5: Create golden `tests/ecosystem-sync/golden/with_signals.md`**

```markdown
# Ecosystem Sync — 2026-04-20

## Signals

### digitalmodel

- **release**: [sync] digitalmodel released v2.1.3
  - dedupe: `release:digitalmodel:v2.1.3`

## Skipped repos

- ⚠ `doris`: fetch timeout

---

Run footer: Duration: 47s · Repos OK: 5/6 · Signals: 1 · Issues filed: 1 · Next run: tomorrow 06:00 CT
```

- [ ] **Step 6: Run test to verify it passes**

```bash
uv run pytest tests/ecosystem-sync/test_digest.py -v
```

Expected: `2 passed`. If assertion fails, review the diff and update the golden file OR fix the renderer — whichever reflects the intended output.

- [ ] **Step 7: Commit**

```bash
git add scripts/ecosystem-sync/digest.py tests/ecosystem-sync/test_digest.py tests/ecosystem-sync/golden/
git commit -m "feat(ecosystem-sync): digest renderer + golden tests"
```

---

## Task 9: Issue opener with dedupe and retry

**Files:**
- Create: `scripts/ecosystem-sync/issues.py`
- Create: `tests/ecosystem-sync/test_issues.py`

- [ ] **Step 1: Write the failing test**

Create `tests/ecosystem-sync/test_issues.py`:

```python
import json
from subprocess import CompletedProcess
from unittest.mock import patch, MagicMock
from scripts.ecosystem_sync.issues import open_issue_if_new, IssueResult
from scripts.ecosystem_sync.models import Signal


def _sig():
    return Signal(
        repo="digitalmodel", kind="release",
        title="[sync] digitalmodel released v2.1.3",
        body="body",
        dedupe_key="release:digitalmodel:v2.1.3",
        payload={"tag": "v2.1.3"},
    )


def test_skips_when_open_dup_exists():
    fake_list = CompletedProcess(
        [], 0, stdout=json.dumps([{"number": 100, "title": "[sync] digitalmodel released v2.1.3"}]),
        stderr="",
    )
    with patch("subprocess.run", return_value=fake_list):
        result = open_issue_if_new(_sig(), issue_repo="vamseeachanta/aceengineer-website")
    assert result.status == "skipped-duplicate"


def test_creates_when_no_dup():
    outputs = [
        CompletedProcess([], 0, stdout="[]", stderr=""),                     # list returns empty
        CompletedProcess([], 0, stdout="https://github.com/x/y/issues/5\n", stderr=""),  # create
    ]
    with patch("subprocess.run", side_effect=outputs):
        result = open_issue_if_new(_sig(), issue_repo="vamseeachanta/aceengineer-website")
    assert result.status == "created"
    assert "issues/5" in (result.url or "")


def test_retry_once_on_create_failure():
    from subprocess import CalledProcessError
    outputs = [
        CompletedProcess([], 0, stdout="[]", stderr=""),  # list
        CalledProcessError(1, "gh", stderr="transient"),  # create fails
        CompletedProcess([], 0, stdout="https://github.com/x/y/issues/6\n", stderr=""),  # retry
    ]
    def side_effect(*a, **k):
        val = outputs.pop(0)
        if isinstance(val, CalledProcessError):
            raise val
        return val
    with patch("subprocess.run", side_effect=side_effect), \
         patch("time.sleep"):
        result = open_issue_if_new(_sig(), issue_repo="vamseeachanta/aceengineer-website")
    assert result.status == "created"


def test_giveup_after_retry():
    from subprocess import CalledProcessError
    def side_effect(*a, **k):
        if "list" in a[0]:
            return CompletedProcess([], 0, stdout="[]", stderr="")
        raise CalledProcessError(1, "gh", stderr="permanent")
    with patch("subprocess.run", side_effect=side_effect), patch("time.sleep"):
        result = open_issue_if_new(_sig(), issue_repo="vamseeachanta/aceengineer-website")
    assert result.status == "failed"


def test_dedupe_check_failure_returns_unknown():
    from subprocess import CalledProcessError
    with patch("subprocess.run", side_effect=CalledProcessError(1, "gh")):
        result = open_issue_if_new(_sig(), issue_repo="vamseeachanta/aceengineer-website")
    assert result.status == "dedupe-check-failed"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/ecosystem-sync/test_issues.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Create `scripts/ecosystem-sync/issues.py`**

```python
"""GitHub issue filing with dedupe + retry. Never closes or edits."""
from __future__ import annotations
import json
import subprocess
import time
from dataclasses import dataclass
from typing import Literal
from scripts.ecosystem_sync.models import Signal


@dataclass(frozen=True)
class IssueResult:
    status: Literal["created", "skipped-duplicate", "failed", "dedupe-check-failed"]
    url: str | None = None
    error: str | None = None


def open_issue_if_new(signal: Signal, issue_repo: str) -> IssueResult:
    # Dedupe check
    try:
        listing = subprocess.run(
            ["gh", "issue", "list",
             "--repo", issue_repo,
             "--search", signal.title,
             "--state", "open",
             "--json", "number,title", "--limit", "20"],
            capture_output=True, text=True, check=True, timeout=30,
        )
        existing = json.loads(listing.stdout or "[]")
    except (subprocess.CalledProcessError, json.JSONDecodeError, subprocess.TimeoutExpired) as e:
        return IssueResult(status="dedupe-check-failed", error=str(e))

    if any(issue.get("title") == signal.title for issue in existing):
        return IssueResult(status="skipped-duplicate")

    # Create with one retry
    labels = [f"sync:{signal.kind}"]
    for attempt in (1, 2):
        try:
            result = subprocess.run(
                ["gh", "issue", "create",
                 "--repo", issue_repo,
                 "--title", signal.title,
                 "--body", signal.body,
                 *sum([["--label", l] for l in labels], [])],
                capture_output=True, text=True, check=True, timeout=30,
            )
            url = result.stdout.strip().splitlines()[-1] if result.stdout else None
            return IssueResult(status="created", url=url)
        except subprocess.CalledProcessError as e:
            if attempt == 2:
                return IssueResult(status="failed", error=e.stderr or str(e))
            time.sleep(10)
        except subprocess.TimeoutExpired as e:
            if attempt == 2:
                return IssueResult(status="failed", error=str(e))
            time.sleep(10)
    return IssueResult(status="failed", error="unreachable")
```

- [ ] **Step 4: Run test to verify it passes**

```bash
uv run pytest tests/ecosystem-sync/test_issues.py -v
```

Expected: `5 passed`.

- [ ] **Step 5: Commit**

```bash
git add scripts/ecosystem-sync/issues.py tests/ecosystem-sync/test_issues.py
git commit -m "feat(ecosystem-sync): issue opener with dedupe + retry-once"
```

---

## Task 10: Orchestrator (run.py) with --dry-run and --doctor

**Files:**
- Create: `scripts/ecosystem-sync/run.py`
- Create: `tests/ecosystem-sync/test_run.py`

- [ ] **Step 1: Write the failing test**

Create `tests/ecosystem-sync/test_run.py`:

```python
import subprocess
from pathlib import Path
from unittest.mock import patch
from scripts.ecosystem_sync.run import main
from scripts.ecosystem_sync.config import SyncConfig, RepoConfig


def _minimal_cfg(tmp_path: Path) -> SyncConfig:
    state_file = tmp_path / "state.yaml"
    digest_dir = tmp_path / "digests"
    return SyncConfig(
        repos=[RepoConfig(name="demo", path=str(tmp_path / "demo"), readme_sections=["Capabilities"])],
        issue_repo="vamseeachanta/aceengineer-website",
        digest_dir=str(digest_dir),
        state_file=str(state_file),
        max_issues_per_run=20,
    )


def test_doctor_success(tmp_path, monkeypatch):
    cfg = _minimal_cfg(tmp_path)
    (tmp_path / "demo").mkdir()
    subprocess.run(["git", "init", "-q", str(tmp_path / "demo")], check=True)
    state_file = Path(cfg.state_file)
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text("")
    digest_dir = Path(cfg.digest_dir)
    digest_dir.mkdir(parents=True, exist_ok=True)

    with patch("scripts.ecosystem_sync.run.load_config", return_value=cfg), \
         patch("subprocess.run") as mock_run:
        mock_run.return_value = subprocess.CompletedProcess([], 0, "ok", "")
        rc = main(["--doctor"])
    assert rc == 0


def test_doctor_fails_on_missing_repo(tmp_path):
    cfg = _minimal_cfg(tmp_path)  # demo path does NOT exist
    state_file = Path(cfg.state_file)
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text("")

    with patch("scripts.ecosystem_sync.run.load_config", return_value=cfg):
        rc = main(["--doctor"])
    assert rc != 0


def test_dry_run_writes_no_issues(tmp_path):
    cfg = _minimal_cfg(tmp_path)
    (tmp_path / "demo").mkdir()
    subprocess.run(["git", "init", "-q", str(tmp_path / "demo")], check=True)
    digest_dir = Path(cfg.digest_dir)
    digest_dir.mkdir(parents=True, exist_ok=True)
    state_file = Path(cfg.state_file)
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text("")

    with patch("scripts.ecosystem_sync.run.load_config", return_value=cfg), \
         patch("scripts.ecosystem_sync.run.open_issue_if_new") as mock_open, \
         patch("scripts.ecosystem_sync.signals.subprocess.run") as mock_sub:
        mock_sub.return_value = subprocess.CompletedProcess([], 0, "", "")
        rc = main(["--dry-run"])
    assert rc == 0
    assert mock_open.call_count == 0
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/ecosystem-sync/test_run.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Create `scripts/ecosystem-sync/run.py`**

```python
"""Ecosystem-sync orchestrator. Loads config, iterates repos, writes digest + issues."""
from __future__ import annotations
import argparse
import logging
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from scripts.ecosystem_sync.config import SyncConfig, load_config
from scripts.ecosystem_sync.state import (
    RepoState, load_state, save_state, has_substantive_change,
)
from scripts.ecosystem_sync.signals import (
    detect_release_tag, detect_new_case_study,
    detect_readme_capability_diff, detect_showcase_labeled_closed_issues,
    _hash_section, _extract_section,
)
from scripts.ecosystem_sync.digest import render_digest
from scripts.ecosystem_sync.issues import open_issue_if_new
from scripts.ecosystem_sync.models import Signal


LOG = logging.getLogger("ecosystem-sync")
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = REPO_ROOT / "scripts" / "ecosystem-sync" / "config.yaml"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Skip issue filing and state writes; print digest to stdout.")
    parser.add_argument("--doctor", action="store_true",
                        help="Validate config, repos, gh auth, state writability.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    cfg = load_config(args.config)

    if args.doctor:
        return _doctor(cfg)
    return _sync(cfg, dry_run=args.dry_run)


def _doctor(cfg: SyncConfig) -> int:
    ok = True
    for r in cfg.repos:
        p = Path(r.path)
        if not p.exists():
            LOG.error("repo missing: %s at %s", r.name, p); ok = False; continue
        if not (p / ".git").exists():
            LOG.error("not a git repo: %s", p); ok = False
    try:
        subprocess.run(["gh", "auth", "status"], check=True,
                       capture_output=True, text=True, timeout=10)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
        LOG.error("gh auth check failed: %s", e); ok = False
    state_path = Path(cfg.state_file)
    if not state_path.parent.exists():
        LOG.error("state dir missing: %s", state_path.parent); ok = False
    digest_path = Path(cfg.digest_dir)
    if not digest_path.exists():
        LOG.error("digest dir missing: %s", digest_path); ok = False
    LOG.info("doctor: %s", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def _sync(cfg: SyncConfig, dry_run: bool) -> int:
    t0 = time.time()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    since = today  # gh accepts YYYY-MM-DD
    state_path = Path(cfg.state_file)
    try:
        before = load_state(state_path)
    except Exception as e:
        LOG.error("state file unparseable: %s", e)
        return 2

    after: dict[str, RepoState] = {k: v for k, v in before.items()}
    signals_by_repo: dict[str, list[Signal]] = {}
    skipped: dict[str, str] = {}

    for r in cfg.repos:
        try:
            subprocess.run(["git", "-C", r.path, "fetch", "origin",
                            "--tags", "--prune"],
                           check=True, capture_output=True, text=True, timeout=30)
            st = before.get(r.name, RepoState(last_sync_utc=today, last_commit_sha=""))
            sigs: list[Signal] = []
            sigs += detect_release_tag(r.name, Path(r.path), st)
            sigs += detect_new_case_study(r.name, Path(r.path), st)
            sigs += detect_readme_capability_diff(r.name, Path(r.path), st, r.readme_sections)
            sigs += detect_showcase_labeled_closed_issues(r.name, st, since)
            if sigs:
                signals_by_repo[r.name] = sigs
            after[r.name] = _updated_state(r, st, Path(r.path), today)
        except Exception as e:
            LOG.exception("repo failed: %s", r.name)
            skipped[r.name] = str(e)

    all_signals: list[Signal] = [s for sigs in signals_by_repo.values() for s in sigs]
    to_file = all_signals[: cfg.max_issues_per_run]
    suppressed = all_signals[cfg.max_issues_per_run :]

    issues_filed = 0
    if not dry_run:
        for s in to_file:
            r = open_issue_if_new(s, cfg.issue_repo)
            if r.status == "created":
                issues_filed += 1
            LOG.info("issue: %s kind=%s status=%s", s.repo, s.kind, r.status)

    digest_md = render_digest(
        signals_by_repo=signals_by_repo, skipped=skipped, date=today,
        duration_s=int(time.time() - t0), repos_total=len(cfg.repos),
        issues_filed=issues_filed, suppressed_signals=suppressed,
    )

    if dry_run:
        print(digest_md)
        return 0

    digest_path = Path(cfg.digest_dir) / f"{today}.md"
    digest_path.parent.mkdir(parents=True, exist_ok=True)
    digest_path.write_text(digest_md)

    if has_substantive_change(before, after):
        save_state(state_path, after)
    return 0


def _updated_state(
    r, old: RepoState, repo_path: Path, today: str,
) -> RepoState:
    """Compute new RepoState after a successful scan."""
    # New tags observed
    try:
        tags_out = subprocess.run(
            ["git", "-C", str(repo_path), "tag", "-l"],
            capture_output=True, text=True, check=True, timeout=10,
        ).stdout
        all_tags = [t.strip() for t in tags_out.splitlines() if t.strip()]
    except Exception:
        all_tags = old.last_seen_tags
    # New commit sha
    try:
        sha = subprocess.run(
            ["git", "-C", str(repo_path), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True, timeout=10,
        ).stdout.strip()
    except Exception:
        sha = old.last_commit_sha
    # New readme hashes
    readme_path = repo_path / "README.md"
    hashes: dict[str, str] = dict(old.last_readme_hash)
    if readme_path.exists():
        try:
            md = readme_path.read_text()
            for heading in r.readme_sections:
                body = _extract_section(md, heading)
                if body:
                    hashes[heading] = _hash_section(body)
        except Exception:
            pass
    return RepoState(
        last_sync_utc=today + "T00:00:00Z",
        last_commit_sha=sha,
        last_seen_tags=all_tags,
        last_readme_hash=hashes,
        last_case_studies=old.last_case_studies,
        last_closed_showcase_issues=old.last_closed_showcase_issues,
    )


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run test to verify it passes**

```bash
uv run pytest tests/ecosystem-sync/test_run.py -v
```

Expected: `3 passed`.

- [ ] **Step 5: Commit**

```bash
git add scripts/ecosystem-sync/run.py tests/ecosystem-sync/test_run.py
git commit -m "feat(ecosystem-sync): orchestrator with --dry-run and --doctor"
```

---

## Task 11: Bash cron entry point

**Files:**
- Create: `.claude/cron/ecosystem-sync.sh`
- Create: `docs/sync-reports/.gitkeep`
- Create: `.claude/state/ecosystem-sync/last-sync.yaml`

- [ ] **Step 1: Create empty initial state**

```bash
mkdir -p .claude/state/ecosystem-sync
: > .claude/state/ecosystem-sync/last-sync.yaml
mkdir -p docs/sync-reports
: > docs/sync-reports/.gitkeep
```

- [ ] **Step 2: Create `.claude/cron/ecosystem-sync.sh`**

```bash
#!/usr/bin/env bash
# Daily ecosystem sync. See docs/plans/2026-04-19-aceengineer-ecosystem-sync-design.md
set -euo pipefail

REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
cd "$REPO_ROOT"

LOCKFILE="/tmp/ecosystem-sync.lock"
LOG_DIR="$REPO_ROOT/logs/ecosystem-sync"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/$(date -u +%Y-%m-%d).log"

# Parse args (pass-through to run.py)
EXTRA_ARGS=("$@")

exec 9>"$LOCKFILE"
if ! flock -n 9; then
  echo "$(date -u +%FT%TZ) ecosystem-sync: previous run in progress, skipped" >> "$LOG"
  exit 0
fi

echo "$(date -u +%FT%TZ) ecosystem-sync: starting" >> "$LOG"

# Pull workspace-hub to pick up latest config/state from other machines
if ! git pull --ff-only origin main >> "$LOG" 2>&1; then
  echo "$(date -u +%FT%TZ) ecosystem-sync: git pull failed" >> "$LOG"
  exit 3
fi

START=$(date +%s)
if uv run scripts/ecosystem-sync/run.py "${EXTRA_ARGS[@]}" >> "$LOG" 2>&1; then
  RC=0
else
  RC=$?
fi
END=$(date +%s)
DURATION=$((END - START))
echo "$(date -u +%FT%TZ) ecosystem-sync: rc=$RC duration=${DURATION}s" >> "$LOG"

if [[ "$RC" == "0" ]]; then
  # Attempt to commit + push state changes. One-shot rebase on reject.
  if ! git diff --quiet || ! git diff --cached --quiet; then
    git add .claude/state/ecosystem-sync/last-sync.yaml docs/sync-reports/ 2>>"$LOG"
    if ! git diff --cached --quiet; then
      git commit -m "chore(ecosystem-sync): $(date -u +%Y-%m-%d) digest + state" >> "$LOG" 2>&1 || true
      if ! git push origin main >> "$LOG" 2>&1; then
        echo "$(date -u +%FT%TZ) push rejected, attempting rebase" >> "$LOG"
        if git pull --rebase origin main >> "$LOG" 2>&1; then
          git push origin main >> "$LOG" 2>&1 || { echo "re-push failed" >> "$LOG"; exit 4; }
        else
          git rebase --abort 2>/dev/null || true
          echo "$(date -u +%FT%TZ) rebase conflict, aborted" >> "$LOG"
          exit 5
        fi
      fi
    fi
  fi
fi

exit "$RC"
```

- [ ] **Step 3: Make it executable**

```bash
chmod +x .claude/cron/ecosystem-sync.sh
```

- [ ] **Step 4: Smoke test the wrapper with --doctor**

```bash
bash .claude/cron/ecosystem-sync.sh --doctor
echo "rc=$?"
cat logs/ecosystem-sync/$(date -u +%Y-%m-%d).log | tail -20
```

Expected: non-zero RC because the 6 source repos likely aren't fully configured yet, but the shell wrapper itself runs. Log file exists and contains the `doctor` output.

- [ ] **Step 5: Commit**

```bash
git add .claude/cron/ecosystem-sync.sh .claude/state/ecosystem-sync/ docs/sync-reports/.gitkeep
git commit -m "feat(ecosystem-sync): bash cron entry with flock + one-shot rebase"
```

---

## Task 12: Audit source repos for README heading consistency

**Files:**
- Create: `scripts/ecosystem-sync/audit-readmes.sh` (one-shot utility)

- [ ] **Step 1: Create audit script**

Create `scripts/ecosystem-sync/audit-readmes.sh`:

```bash
#!/usr/bin/env bash
# Print which of "Capabilities", "Features", "What it does" headings
# are present in each source repo's top-level README.md.
set -euo pipefail

REPOS=(digitalmodel assethold assetutilities CAD-DEVELOPMENTS doris frontierdeepwater)
HEADINGS=("Capabilities" "Features" "What it does")
REPO_ROOT="$(git rev-parse --show-toplevel)"

printf "%-20s | %-12s | %-8s | %-14s\n" "REPO" "Capabilities" "Features" "What it does"
printf "%0.s-" {1..70}; echo
for r in "${REPOS[@]}"; do
  readme="$REPO_ROOT/$r/README.md"
  row="$r"
  for h in "${HEADINGS[@]}"; do
    if [[ -f "$readme" ]] && grep -q "^## $h$" "$readme"; then
      row="$row | YES"
    else
      row="$row | no"
    fi
  done
  echo "$row"
done
```

- [ ] **Step 2: Run audit**

```bash
chmod +x scripts/ecosystem-sync/audit-readmes.sh
bash scripts/ecosystem-sync/audit-readmes.sh
```

Expected: a table showing which headings each repo currently has. **Record the output in the digest for later reference.**

- [ ] **Step 3: For each repo missing ALL three headings, add a `## Capabilities` section**

For each repo where the audit shows `no / no / no`, open its README and add one concrete `## Capabilities` section with 3-5 bullets. Commit each change **in the respective repo** (these are separate git repos; switch into each before committing):

```bash
cd /mnt/local-analysis/workspace-hub/<repo-name>
# Edit README.md to add `## Capabilities` with real bullets from repo knowledge
git add README.md
git commit -m "docs(readme): add Capabilities section for aceengineer-website sync"
git push origin main
cd /mnt/local-analysis/workspace-hub
```

- [ ] **Step 4: Commit the audit script**

```bash
git add scripts/ecosystem-sync/audit-readmes.sh
git commit -m "chore(ecosystem-sync): README-heading audit script"
```

---

## Task 13: Create showcase/website labels on 6 repos

**Files:**
- Create: `scripts/ecosystem-sync/create-labels.sh`

- [ ] **Step 1: Create label-bootstrap script**

Create `scripts/ecosystem-sync/create-labels.sh`:

```bash
#!/usr/bin/env bash
# Create `showcase` and `website` labels on the 6 source repos.
# Idempotent: uses --force to update if label already exists.
set -euo pipefail
REPOS=(digitalmodel assethold assetutilities CAD-DEVELOPMENTS doris frontierdeepwater)
OWNER=vamseeachanta

for r in "${REPOS[@]}"; do
  echo "== $r =="
  gh label create showcase --repo "$OWNER/$r" \
    --color 00ABCD --description "Surfaces via ecosystem-sync to aceengineer-website" \
    --force
  gh label create website --repo "$OWNER/$r" \
    --color 5319E7 --description "Surfaces via ecosystem-sync to aceengineer-website" \
    --force
done
```

- [ ] **Step 2: Run it**

```bash
chmod +x scripts/ecosystem-sync/create-labels.sh
bash scripts/ecosystem-sync/create-labels.sh
```

Expected: two `label created` (or "label already exists, updated") lines per repo × 6 repos = 12 total messages.

- [ ] **Step 3: Verify with one repo**

```bash
gh label list --repo vamseeachanta/digitalmodel | grep -E "showcase|website"
```

Expected: two matching lines.

- [ ] **Step 4: Commit**

```bash
git add scripts/ecosystem-sync/create-labels.sh
git commit -m "chore(ecosystem-sync): create showcase/website labels in 6 source repos"
```

---

## Task 14: Backfill initial state file

**Files:**
- Modify: `.claude/state/ecosystem-sync/last-sync.yaml`

- [ ] **Step 1: Run the orchestrator once with --dry-run to discover current state**

```bash
uv run scripts/ecosystem-sync/run.py --dry-run > /tmp/first-dryrun.md 2>&1 || true
cat /tmp/first-dryrun.md | head -80
```

Expected: the digest will list EVERY existing tag, case study, and README section as new signals — because the state file is empty. This is the "backfill day" behavior called out in the spec.

- [ ] **Step 2: Build an initial state that reflects the current reality (zero signals on next run)**

Write a helper script `scripts/ecosystem-sync/backfill-state.py`:

```python
"""Generate initial last-sync.yaml reflecting current state of all 6 repos."""
from __future__ import annotations
import hashlib
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.ecosystem_sync.config import load_config
from scripts.ecosystem_sync.signals import _extract_section, _hash_section

CFG_PATH = ROOT / "scripts" / "ecosystem-sync" / "config.yaml"


def main() -> int:
    cfg = load_config(CFG_PATH)
    out: dict[str, dict] = {}
    for r in cfg.repos:
        repo_path = Path(r.path)
        if not repo_path.exists():
            print(f"skip (missing): {r.name}")
            continue
        subprocess.run(["git", "-C", str(repo_path), "fetch", "origin", "--tags", "--prune"],
                       check=True, capture_output=True, text=True, timeout=60)
        sha = subprocess.run(["git", "-C", str(repo_path), "rev-parse", "HEAD"],
                             check=True, capture_output=True, text=True, timeout=10).stdout.strip()
        tags = [t.strip() for t in subprocess.run(
            ["git", "-C", str(repo_path), "tag", "-l"],
            check=True, capture_output=True, text=True, timeout=10).stdout.splitlines() if t.strip()]

        hashes: dict[str, str] = {}
        readme = repo_path / "README.md"
        if readme.exists():
            md = readme.read_text()
            for heading in r.readme_sections:
                body = _extract_section(md, heading)
                if body:
                    hashes[heading] = _hash_section(body)

        # List current case-study files (not new → pre-populate as "already seen")
        case_studies: list[str] = []
        for sub in ("case-studies", "examples", "demos", "docs/case-studies"):
            d = repo_path / sub
            if d.exists():
                for p in sorted(d.rglob("*.md")):
                    rel = p.relative_to(repo_path).as_posix()
                    if any(s in f"/{rel}" for s in ("/_draft/", "/wip/", "/archive/")):
                        continue
                    if p.name in ("README.md", "CASE_STUDY_TEMPLATE.md") or p.name.endswith(".template.md"):
                        continue
                    case_studies.append(rel)

        out[r.name] = {
            "last_sync_utc": "2026-04-20T00:00:00Z",
            "last_commit_sha": sha,
            "last_seen_tags": tags,
            "last_readme_hash": hashes,
            "last_case_studies": case_studies,
            "last_closed_showcase_issues": [],
        }
        print(f"captured: {r.name} sha={sha[:8]} tags={len(tags)} case_studies={len(case_studies)}")

    state_file = ROOT / ".claude" / "state" / "ecosystem-sync" / "last-sync.yaml"
    state_file.write_text(yaml.safe_dump(out, sort_keys=True, default_flow_style=False))
    print(f"wrote: {state_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 3: Run the backfill**

```bash
uv run scripts/ecosystem-sync/backfill-state.py
cat .claude/state/ecosystem-sync/last-sync.yaml | head -40
```

Expected: YAML file with one entry per repo containing tags, commit sha, readme hashes, and existing case-study paths.

- [ ] **Step 4: Verify next dry-run is clean**

```bash
uv run scripts/ecosystem-sync/run.py --dry-run | tail -30
```

Expected: digest shows `_No signals detected._` or only signals from `closed:>=today` queries (which should be empty on a fresh day).

- [ ] **Step 5: Commit**

```bash
git add .claude/state/ecosystem-sync/last-sync.yaml scripts/ecosystem-sync/backfill-state.py
git commit -m "chore(ecosystem-sync): backfill initial state from current repo reality"
```

---

## Task 15: Doctor check passes on real config

**Files:** none (diagnostic only)

- [ ] **Step 1: Run doctor**

```bash
uv run scripts/ecosystem-sync/run.py --doctor
echo "rc=$?"
```

Expected: `doctor: PASS`, `rc=0`. If any check fails, fix the underlying problem (missing repo, `gh auth status` expired, etc.) before proceeding.

- [ ] **Step 2: Confirm bash wrapper also passes**

```bash
bash .claude/cron/ecosystem-sync.sh --doctor
echo "rc=$?"
```

Expected: `rc=0`.

No commit — this is verification.

---

## Task 16: Three-day dry-run burn-in

**Files:** none

- [ ] **Step 1: Run dry-run day 1, inspect manually**

```bash
bash .claude/cron/ecosystem-sync.sh --dry-run
# stdout-to-log only; digest ends up in logs/ecosystem-sync/<today>.log
tail -50 logs/ecosystem-sync/$(date -u +%Y-%m-%d).log
```

Read the digest. Look for: unexpected signals, false positives, missing obvious signals. If anomalies appear, diagnose and fix before proceeding.

- [ ] **Step 2: Wait at least 24h, then run dry-run day 2**

Same command. Compare digest day-over-day: a clean install should produce `_No signals detected._` on both days unless something real changed upstream.

- [ ] **Step 3: Day 3 dry-run**

Same command. If 3 consecutive days come back clean (or with only real, expected signals), proceed to enable the cron.

No commit — verification period.

---

## Task 17: Enable systemd cron

**Files:**
- Create: `/etc/systemd/system/ecosystem-sync.service` (root-owned)
- Create: `/etc/systemd/system/ecosystem-sync.timer` (root-owned)

- [ ] **Step 1: Verify which user should own the cron**

```bash
whoami
ls -la /mnt/local-analysis/workspace-hub/.git/
```

Expected: confirm which Unix user runs your existing `daily_readiness_cron`. Use the same user here.

- [ ] **Step 2: Create the service unit**

```bash
sudo tee /etc/systemd/system/ecosystem-sync.service > /dev/null <<'EOF'
[Unit]
Description=AceEngineer ecosystem sync (daily)
Wants=network-online.target
After=network-online.target

[Service]
Type=oneshot
User=vamsee
WorkingDirectory=/mnt/local-analysis/workspace-hub
ExecStart=/mnt/local-analysis/workspace-hub/.claude/cron/ecosystem-sync.sh
TimeoutStartSec=300
StandardOutput=append:/var/log/ecosystem-sync.log
StandardError=append:/var/log/ecosystem-sync.log
EOF
```

- [ ] **Step 3: Create the timer unit (6:00 AM Central Time)**

```bash
sudo tee /etc/systemd/system/ecosystem-sync.timer > /dev/null <<'EOF'
[Unit]
Description=Run ecosystem-sync daily at 6:00 AM CT

[Timer]
OnCalendar=*-*-* 06:00:00 America/Chicago
Persistent=true
Unit=ecosystem-sync.service

[Install]
WantedBy=timers.target
EOF
```

- [ ] **Step 4: Enable and start**

```bash
sudo systemctl daemon-reload
sudo systemctl enable ecosystem-sync.timer
sudo systemctl start ecosystem-sync.timer
systemctl list-timers ecosystem-sync.timer
```

Expected: `systemctl list-timers` shows next firing as tomorrow 06:00 CT.

- [ ] **Step 5: Trigger one test run manually**

```bash
sudo systemctl start ecosystem-sync.service
sleep 5
systemctl status ecosystem-sync.service --no-pager
tail -30 /var/log/ecosystem-sync.log
```

Expected: service status `inactive (dead)` with last `Main PID` exit=0.

- [ ] **Step 6: Document the cron in memory**

Append to `MEMORY.md` under Project:

```
- [Ecosystem sync cron](project_ecosystem_sync_cron.md) — 6am CT daily, reviews 6 public repos, files issues on aceengineer-website
```

Create `project_ecosystem_sync_cron.md` (in the auto-memory dir) with the key facts: systemd timer name, config location, what it watches, how to disable.

- [ ] **Step 7: Commit what remains in the repo**

```bash
git add MEMORY.md  # only if changed
git commit -m "docs(memory): record ecosystem-sync cron" || echo "nothing to commit"
```

(Systemd units live at `/etc/systemd/system/` — outside this repo, not committed here. Document their path in the memory file.)

---

## Self-Review

### Spec coverage check

| Spec section | Task(s) covering it |
|---|---|
| §Architecture | Tasks 10–11 |
| §Components (5 files) | Tasks 1, 2, 3, 7, 8, 9, 10 |
| §Config YAML | Task 2 |
| §State YAML + change detection | Task 3, 14 |
| §Daily run sequence | Tasks 10, 11 |
| §Dedupe rules (digest/state/issues) | Tasks 3, 9, 10 |
| §Signal 1 (release) | Task 4 |
| §Signal 2 (case study) | Task 5 |
| §Signal 3 (README diff) | Task 6 |
| §Signal 5 (labeled closed issues) | Task 7 |
| §Signal ordering + 20-cap | Task 10 |
| §Error handling (flock, git-pull, state corrupt, fetch fail, gh fail, detector exception) | Tasks 9, 10, 11 |
| §Testing (unit + integration + smoke) | Tasks 1–10, 15, 16 |
| §Observability (digest, log, issue titles) | Tasks 8, 10, 11 |
| §Preparatory PR (README audit + labels + backfill) | Tasks 12, 13, 14 |
| §Rollout sequence | Tasks 15 (doctor), 16 (dry-run), 17 (enable) |
| §Open risk: `gh` auth expiring | Task 10 (doctor check) |
| §Open risk: backfill flood | Task 14 (backfill state) |

No gaps.

### Placeholder scan

No `TBD` / `TODO` / `FIXME` / "implement later" / "similar to task N without code" in the plan. Every code step contains the full code.

### Type consistency

- `Signal` fields used identically across `models.py`, `signals.py`, `digest.py`, `issues.py`.
- `RepoState` fields used identically in `state.py`, `signals.py` detectors, `run.py` `_updated_state`.
- `SyncConfig`/`RepoConfig` used identically in `config.py`, `run.py`.
- `IssueResult.status` values (`created`, `skipped-duplicate`, `failed`, `dedupe-check-failed`) used consistently in `issues.py` and `test_issues.py`.

No drift detected.

---

## Execution handoff

Plan complete and saved to `docs/plans/2026-04-20-aceengineer-ecosystem-sync-plan.md`. Two execution options:

1. **Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration.
2. **Inline Execution** — Execute tasks in this session using `executing-plans`, batch execution with checkpoints.

Which approach?
