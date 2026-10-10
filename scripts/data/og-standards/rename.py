#!/usr/bin/env python3
"""
ABOUTME: O&G Standards rename/remap mode (#3886)
ABOUTME: Carries library file renames and moved source roots into the inventory DB, FTS index and catalog

A rename on disk leaves the inventory DB, its FTS index and the generated catalog
pointing at the old name, and a full rebuild would discard extracted text and
embeddings. This mode updates the affected rows in place, by row id, so the
document id (and every chunk and embedding keyed on it) is preserved.

Rename mode reads a Markdown rename log (default: RENAME-LOG.md at the library
root) containing a table with old path, new path and SHA-256 columns. Relative
paths resolve against the library root. Every entry is validated before anything
is written: the new file must exist and hash to the logged SHA-256, the old path
must be a catalogued target_path, and the new path must not already belong to
another row. One invalid entry aborts the whole batch.

Usage:
    python rename.py --dry-run                     # show the plan, write nothing
    python rename.py                               # apply, rebuild FTS, regenerate catalog
    python rename.py --rename-log path/to/log.md --no-catalog
    python rename.py --remap-root "/old/root" "/new/root" [--dry-run]

After a rename, refresh the document index through its normal chain, starting with
scripts/data/document-index/remap_og_standards_paths.py (joins on row id).
"""

from __future__ import annotations

import argparse
import hashlib
import logging
import os
import re
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List, Optional, Sequence, Tuple

import yaml

from inventory import StandardsInventory

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

SHA256_RE = re.compile(r'^[0-9a-f]{64}$')
OLD_HEADERS = ('old', 'from', 'before', 'original')
NEW_HEADERS = ('new', 'to', 'after', 'renamed')


@dataclass(frozen=True)
class RenameEntry:
    old_path: str
    new_path: str
    sha256: str
    line: int


@dataclass
class RenameReport:
    planned: int = 0
    applied: int = 0
    already_applied: int = 0
    changes: List[Tuple[int, str, str]] = field(default_factory=list)


def _cells(line: str) -> List[str]:
    return [c.strip().strip('`').strip() for c in line.strip().strip('|').split('|')]


def _column(headers: List[str], names: Sequence[str]) -> Optional[int]:
    for i, h in enumerate(headers):
        words = re.findall(r'[a-z0-9]+', h.lower())
        if any(name in words for name in names):
            return i
    return None


def _resolve(path: str, library_root: Path) -> str:
    if path.startswith('/') or os.path.isabs(path):
        return path
    return str(Path(library_root) / path)


def parse_rename_log(path, library_root) -> List[RenameEntry]:
    """Parse the rename table in a Markdown rename log."""
    lines = Path(path).read_text(encoding='utf-8').splitlines()
    entries: List[RenameEntry] = []
    cols = None
    for lineno, line in enumerate(lines, start=1):
        if not line.lstrip().startswith('|'):
            if cols is not None and entries:
                break  # first table only
            continue
        cells = _cells(line)
        if cols is None:
            old_i, new_i = _column(cells, OLD_HEADERS), _column(cells, NEW_HEADERS)
            sha_i = next((i for i, c in enumerate(cells) if 'sha' in c.lower()), None)
            if None not in (old_i, new_i, sha_i):
                cols = (old_i, new_i, sha_i)
            continue
        if all(re.fullmatch(r':?-{3,}:?', c) for c in cells if c):
            continue  # separator row
        old_i, new_i, sha_i = cols
        get = lambda i: cells[i] if i < len(cells) else ''  # noqa: E731
        old, new, sha = get(old_i), get(new_i), get(sha_i).lower()
        if not old or not new:
            raise ValueError(f'{path} line {lineno}: missing old or new path')
        if not sha:
            raise ValueError(f'{path} line {lineno}: missing SHA-256')
        if not SHA256_RE.match(sha):
            raise ValueError(f'{path} line {lineno}: malformed SHA-256 {sha!r}')
        entries.append(RenameEntry(
            _resolve(old, library_root), _resolve(new, library_root), sha, lineno
        ))
    if cols is None:
        raise ValueError(f'{path}: no rename table (old path | new path | SHA-256) found')
    return entries


def _file_sha256(path: str, chunk_size: int = 1 << 20) -> str:
    hasher = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()


def _has_column(conn, table: str, column: str) -> bool:
    return any(r[1] == column for r in conn.execute(f'PRAGMA table_info({table})'))


def _has_fts(conn) -> bool:
    return conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='documents_fts'"
    ).fetchone() is not None


def _ids_for_target(conn, target: str) -> List[int]:
    return [r[0] for r in conn.execute(
        'SELECT id FROM documents WHERE target_path = ? ORDER BY id', (target,)
    )]


def _plan(conn, entries: Sequence[RenameEntry], report: RenameReport):
    """Validate every entry; return [(entry, row_ids)] still to apply."""
    errors: List[str] = []
    pending = []
    seen_old, seen_new = set(), set()
    has_sha_col = _has_column(conn, 'documents', 'sha256')
    for e in entries:
        where = f'line {e.line}'
        if e.old_path in seen_old or e.new_path in seen_new:
            errors.append(f'{where}: path appears in more than one entry')
        seen_old.add(e.old_path)
        seen_new.add(e.new_path)

        if not os.path.isfile(e.new_path):
            errors.append(f'{where}: new file not found: {e.new_path}')
        else:
            actual = _file_sha256(e.new_path)
            if actual != e.sha256:
                errors.append(
                    f'{where}: SHA-256 mismatch for {e.new_path}: '
                    f'log {e.sha256}, file {actual}'
                )

        old_ids = _ids_for_target(conn, e.old_path)
        new_ids = _ids_for_target(conn, e.new_path)
        if old_ids and new_ids:
            errors.append(
                f'{where}: {e.new_path} is already the target of row(s) {new_ids}'
            )
        elif old_ids:
            pending.append((e, old_ids))
        elif new_ids and has_sha_col and all(
            conn.execute('SELECT sha256 FROM documents WHERE id = ?', (i,)).fetchone()[0]
            == e.sha256 for i in new_ids
        ):
            report.already_applied += 1
        else:
            errors.append(f'{where}: old path not in inventory DB: {e.old_path}')
    if errors:
        raise ValueError('rename log rejected, nothing applied:\n  ' + '\n  '.join(errors))
    return pending


def apply_renames(
    db_path,
    entries: Sequence[RenameEntry],
    dry_run: bool = True,
    parse_info: Optional[Callable[[str, str], Tuple[str, str, str]]] = None,
) -> RenameReport:
    """Validate all entries, then update target_path/filename/title/sha256 by row
    id and rebuild the FTS index, in one transaction. ``parse_info`` (filename,
    path) -> (organization, doc_type, doc_number) re-derives the identity fields
    when given, since a rename can correct the edition or publisher."""
    report = RenameReport()
    conn = sqlite3.connect(str(db_path), isolation_level=None)
    try:
        pending = _plan(conn, entries, report)
        for e, ids in pending:
            for row_id in ids:
                report.changes.append((row_id, e.old_path, e.new_path))
        report.planned = len(report.changes)
        if dry_run or not pending:
            return report

        conn.execute('BEGIN IMMEDIATE')
        try:
            if not _has_column(conn, 'documents', 'sha256'):
                conn.execute('ALTER TABLE documents ADD COLUMN sha256 TEXT')
            for e, ids in pending:
                filename = Path(e.new_path).name
                values = {
                    'target_path': e.new_path,
                    'filename': filename,
                    'extension': os.path.splitext(filename)[1].lower(),
                    'title': StandardsInventory._extract_title(filename),
                    'sha256': e.sha256,
                }
                if parse_info is not None:
                    org, doc_type, doc_number = parse_info(filename, e.new_path)
                    values.update(organization=org, doc_type=doc_type,
                                  doc_number=doc_number)
                assignments = ', '.join(f'{k} = ?' for k in values)
                for row_id in ids:
                    conn.execute(
                        f'UPDATE documents SET {assignments} WHERE id = ?',
                        (*values.values(), row_id),
                    )
            if _has_fts(conn):
                conn.execute("INSERT INTO documents_fts(documents_fts) VALUES('rebuild')")
            conn.execute('COMMIT')
        except Exception:
            conn.execute('ROLLBACK')
            raise
        report.applied = report.planned
        return report
    finally:
        conn.close()


def _prefix_where(column: str) -> str:
    return f'({column} = ? OR substr({column}, 1, ?) = ? OR substr({column}, 1, ?) = ?)'


def remap_source_root(db_path, old_root: str, new_root: str, dry_run: bool = True) -> int:
    """Rewrite the file_path/source_dir prefix ``old_root`` to ``new_root``.

    Matches whole path components only, so /a/b does not match /a/bc. Returns
    the number of rows whose file_path is (or would be) rewritten.
    """
    old_root = old_root.rstrip('/\\')
    new_root = new_root.rstrip('/\\')
    n = len(old_root) + 1

    def params():
        return (old_root, n, old_root + '/', n, old_root + '\\')

    conn = sqlite3.connect(str(db_path), isolation_level=None)
    try:
        (count,) = conn.execute(
            f'SELECT COUNT(*) FROM documents WHERE {_prefix_where("file_path")}', params()
        ).fetchone()
        if dry_run or count == 0:
            return count
        conn.execute('BEGIN IMMEDIATE')
        try:
            for column in ('file_path', 'source_dir'):
                conn.execute(
                    f'UPDATE documents SET {column} = ? || substr({column}, ?) '
                    f'WHERE {_prefix_where(column)}',
                    (new_root, len(old_root) + 1, *params()),
                )
            conn.execute('COMMIT')
        except sqlite3.IntegrityError as exc:
            conn.execute('ROLLBACK')
            raise ValueError(f'remap would collide with an existing file_path: {exc}')
        except Exception:
            conn.execute('ROLLBACK')
            raise
        return count
    finally:
        conn.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Carry renamed library files and moved source roots into the '
                    'inventory DB, FTS index and catalog'
    )
    parser.add_argument('--config', '-c', default='config.yaml',
                        help='Path to configuration file (default: config.yaml)')
    parser.add_argument('--rename-log',
                        help='Rename log (default: <target_directory>/RENAME-LOG.md)')
    parser.add_argument('--library-root',
                        help='Root for relative log paths (default: target_directory)')
    parser.add_argument('--db', help='Inventory DB (default: database_path)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Validate and print the plan; write nothing')
    parser.add_argument('--no-catalog', action='store_true',
                        help='Do not regenerate the catalog after applying')
    parser.add_argument('--remap-root', nargs=2, metavar=('OLD', 'NEW'),
                        help='Rewrite a moved source root prefix in file_path/source_dir')
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    config_path = args.config
    if not os.path.isabs(config_path):
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), config_path)
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    db_path = args.db or config['database_path']
    library_root = args.library_root or config['target_directory']
    mode = 'DRY-RUN' if args.dry_run else 'APPLY'

    if args.remap_root:
        old_root, new_root = args.remap_root
        try:
            count = remap_source_root(db_path, old_root, new_root, dry_run=args.dry_run)
        except ValueError as exc:
            logger.error(str(exc))
            return 1
        logger.info('%s: %d row(s) %s -> %s', mode, count, old_root, new_root)
        return 0

    log_path = args.rename_log or os.path.join(library_root, 'RENAME-LOG.md')
    try:
        entries = parse_rename_log(log_path, library_root=Path(library_root))
        inventory = StandardsInventory(config_path)
        report = apply_renames(db_path, entries, dry_run=args.dry_run,
                               parse_info=inventory._parse_standard_info)
    except ValueError as exc:
        logger.error(str(exc))
        return 1

    for row_id, old, new in report.changes:
        print(f'  row {row_id:>7}  {old}\n           -> {new}')
    logger.info('%s: %d entr(ies) in log, %d row(s) to rename, %d already applied',
                mode, len(entries), report.planned, report.already_applied)

    if args.dry_run:
        return 0
    if not args.no_catalog:
        from catalog import CatalogGenerator
        generator = CatalogGenerator(config_path)
        try:
            generator.run()
        finally:
            generator.close()
    if report.applied:
        logger.info('Next: refresh the document index, starting with '
                    'scripts/data/document-index/remap_og_standards_paths.py --dry-run')
    return 0


if __name__ == '__main__':
    sys.exit(main())
