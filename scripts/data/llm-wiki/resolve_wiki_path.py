"""Portable path resolution for llm-wiki data directory.

Resolution order (first existing path wins):
  1. Environment variable  : $LLM_WIKI_DATA_DIR
  2. Config file           : ${REPO_ROOT}/config/llm-wiki.yaml  → data_dir field
  3. Repo symlink/dir      : ${REPO_ROOT}/data/llm-wiki
  4. Fallback              : ${REPO_ROOT}/knowledge/wikis

Usage — Python import:
    from scripts.data.llm_wiki.resolve_wiki_path import resolve_wiki_dir
    wiki_dir = resolve_wiki_dir()

Usage — CLI:
    python3 scripts/data/llm-wiki/resolve_wiki_path.py
    # prints the resolved absolute path to stdout

Ref: GH #2140
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def resolve_wiki_dir() -> Path:
    """Resolve the llm-wiki data directory using the standard resolution order.

    Returns the first path that exists on disk, or the fallback path even if
    it does not yet exist (callers can mkdir as needed).
    """
    # 1. Env var
    env_val = os.environ.get("LLM_WIKI_DATA_DIR")
    if env_val:
        p = Path(env_val).expanduser()
        if p.exists():
            return p

    # 2. Config file
    config_path = REPO_ROOT / "config" / "llm-wiki.yaml"
    if config_path.is_file():
        try:
            import yaml  # optional; degrade gracefully if not installed
            with open(config_path) as f:
                cfg = yaml.safe_load(f)
            data_dir = (cfg or {}).get("data_dir")
            if data_dir:
                p = Path(data_dir).expanduser()
                if p.exists():
                    return p
        except Exception:
            pass  # YAML not available or config malformed — skip

    # 3. Repo symlink / directory (may be a local symlink to an NFS mount)
    repo_data = REPO_ROOT / "data" / "llm-wiki"
    if repo_data.exists():
        return repo_data

    # 4. Fallback: the git-tracked knowledge/wikis directory
    return REPO_ROOT / "knowledge" / "wikis"


if __name__ == "__main__":
    print(resolve_wiki_dir())
