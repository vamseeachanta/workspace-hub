"""Read-only lexical fallback over an explicit root, independent of any index.

Pages live at ``allowed_root/<domain>/wiki/**/*.md`` (case-insensitive suffix).
Only visible directories and regular pages are eligible; ``secrets`` directories
are excluded at every depth. Symlinks, device crossings below the allowed root,
and names containing control characters or backslashes are excluded before reads.

Scoring contract: count distinct case-folded Unicode word tokens present, then
their total occurrences, descending; ties use the relative POSIX page path.
Repeated query tokens do not boost rank. Excerpts start at the first matched
token, replace whitespace/control characters with spaces, and HTML escape text.
The caller supplies both result and escaped-character budgets; entities are never
split. Empty/punctuation-only queries and a zero result budget return no results.

Linux descriptor-relative O_NOFOLLOW traversal prevents symlink substitution.
O_NOATIME preserves directory and file access times. The explicit root must be
an existing absolute directory with no symlink or '..' components. Opening it
without access-time changes must be permitted; otherwise the request fails.
Unreadable, replaced, or unsupported child entries are skipped. This backend
neither imports nor consults an embeddings index, model, network or MCP transport.
"""

from __future__ import annotations

import html
import os
import re
import stat
import unicodedata
from collections import Counter
from contextlib import contextmanager
from pathlib import Path


_WORDS = re.compile(r"\w+", re.UNICODE)
_DOMAIN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*", re.ASCII)


def _visible(name: str) -> bool:
    return (not name.startswith(".") and name != "secrets" and "\\" not in name
            and not any(unicodedata.category(c).startswith("C") for c in name))


@contextmanager
def _root_directory(root):
    path = Path(root)
    if not path.is_absolute() or ".." in path.parts:
        raise ValueError("allowed_root must be absolute without parent traversal")
    if not all(hasattr(os, flag) for flag in ("O_NOFOLLOW", "O_NOATIME", "O_DIRECTORY")):
        raise RuntimeError("search requires no-follow and no-atime directory reads")
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    fd = None
    try:
        try:
            # Ancestors are opened but not enumerated. Reopen the pinned root
            # with access-time protection before any directory entries are read.
            fd = os.open(path.anchor, flags)
            for part in path.parts[1:]:  # First component is the already opened anchor.
                child = os.open(part, flags, dir_fd=fd)
                os.close(fd)
                fd = child
            child = os.open(".", flags | os.O_NOATIME, dir_fd=fd)
            os.close(fd)
            fd = child
        except (OSError, ValueError) as error:
            raise ValueError("allowed_root must permit no-follow, no-atime directory reads") from error
        yield fd
    finally:
        if fd is not None:
            os.close(fd)


@contextmanager
def _child(parent: int, name: str, device: int, *, directory: bool):
    """Pin a child descriptor and recheck type/device after opening it."""
    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NOATIME | os.O_NONBLOCK
    if directory:
        flags |= os.O_DIRECTORY
    fd = None
    try:
        fd = os.open(name, flags, dir_fd=parent)
        info = os.fstat(fd)
        valid_type = stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode)
        valid = valid_type and info.st_dev == device
    except OSError:
        valid = False
    try:
        yield fd if valid else None
    finally:
        if fd is not None:
            os.close(fd)


def _pages(directory: int, prefix: str, device: int):
    try:
        names = os.listdir(directory)
    except OSError:
        return
    for name in names:
        if not _visible(name):
            continue
        try:
            info = os.stat(name, dir_fd=directory, follow_symlinks=False)
        except OSError:
            continue
        relative = f"{prefix}/{name}"
        if stat.S_ISDIR(info.st_mode):
            with _child(directory, name, device, directory=True) as child:
                if child is not None:
                    yield from _pages(child, relative, device)
        elif stat.S_ISREG(info.st_mode) and Path(name).suffix.casefold() == ".md":
            with _child(directory, name, device, directory=False) as child:
                if child is None:
                    continue
                try:
                    # Read at most the size observed on the pinned regular file.
                    # Remaining bytes, rather than a tuning constant, bound reads.
                    remaining = os.fstat(child).st_size
                    chunks = []
                    while remaining:
                        chunk = os.read(child, remaining)
                        if not chunk:
                            break
                        chunks.append(chunk)
                        remaining -= len(chunk)
                    text = b"".join(chunks).decode("utf-8", errors="replace")
                except OSError:
                    continue
                yield relative, text


def _excerpt(text: str, start: int, budget: int) -> str:
    parts = []
    for char in text[start:]:
        if char.isspace() or unicodedata.category(char).startswith("C"):
            char = " "
        escaped = html.escape(char, quote=True)
        if len(escaped) > budget:
            break
        parts.append(escaped)
        budget -= len(escaped)
    return "".join(parts)


def wiki_search(query: str, *, allowed_root: str | os.PathLike[str],
                domain: str | None = None, top_k: int, excerpt_chars: int) -> list[dict]:
    """Return ranked relative pages with token counts and bounded HTML excerpts.

    Domain filters are exact directory names, never paths. Both limits are caller
    supplied integers (booleans excluded); top_k may be zero, excerpt_chars must
    be positive. Invalid inputs/roots raise ValueError. An unavailable child is
    omitted, so results do not certify complete coverage of an unreadable tree.
    """
    if not isinstance(query, str):
        raise ValueError("query must be a string")
    if type(top_k) is not int or top_k < 0:  # Zero means no requested results.
        raise ValueError("top_k must be a nonnegative integer")
    if type(excerpt_chars) is not int or excerpt_chars <= 0:  # An excerpt needs a positive budget.
        raise ValueError("excerpt_chars must be a positive integer")
    if domain is not None and (not isinstance(domain, str) or not _DOMAIN.fullmatch(domain)
                               or not _visible(domain)):
        raise ValueError("domain must be a visible directory name")
    try:
        root = Path(allowed_root)
    except TypeError as error:
        raise ValueError("allowed_root must be a directory path") from error
    tokens = {match.group().casefold() for match in _WORDS.finditer(query)}
    results = []
    with _root_directory(root) as root_fd:
        if not tokens or not top_k:
            return []
        device = os.fstat(root_fd).st_dev
        domains = [domain] if domain is not None else os.listdir(root_fd)
        for name in domains:
            if not _visible(name) or not _DOMAIN.fullmatch(name):
                continue
            with _child(root_fd, name, device, directory=True) as domain_fd:
                if domain_fd is None:
                    continue
                with _child(domain_fd, "wiki", device, directory=True) as wiki_fd:
                    if wiki_fd is None:
                        continue
                    for relative, text in _pages(wiki_fd, f"{name}/wiki", device):
                        matches = [match for match in _WORDS.finditer(text)
                                   if match.group().casefold() in tokens]
                        if not matches:
                            continue
                        counts = Counter(match.group().casefold() for match in matches)
                        results.append({
                            "page": relative, "domain": name,
                            "matched_terms": len(counts), "occurrences": sum(counts.values()),
                            # First match has index zero by the lexical contract.
                            "excerpt": _excerpt(text, matches[0].start(), excerpt_chars),
                        })
    results.sort(key=lambda row: (-row["matched_terms"], -row["occurrences"], row["page"]))
    return results[:top_k]
