#!/usr/bin/env python3
"""Read-only syntax inventory of text captures in tracked Python/shell helpers.

No discovered script is imported or executed. Candidates are not data-flow proof.
Python 3.11 subprocess, Frequently Used Arguments, specifies newline conversion:
https://docs.python.org/3.11/library/subprocess.html#frequently-used-arguments
Bash Command Substitution specifies deletion of trailing newline characters:
https://www.gnu.org/software/bash/manual/html_node/Command-Substitution.html
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import html
import json
import os
import re
import subprocess
from pathlib import Path

# Reviewed content contracts; the source functions are evidence, not a heuristic.
# The pointer repair's existing byte implementation is retained without changes.
BYTE_PRESERVING = {
    'scripts/readiness/repair-sibling-sso-flow.py':
        'rewrite_agents_pointer reads bytes, uses surrogateescape, writes bytes',
    'scripts/client_llm_wiki/bootstrap_renderer.py':
        '_write_all writes member.data bytes; decode is validation only',
}

# Reviewed exclusions, based on the named source functions. These promise
# generated/semantic output, not preservation of an original file's raw bytes.
REVIEWED_OTHER = {
    'scripts/skills/generate_skills_index.py':
        'committed_skill_md captures path metadata; generated index is serialized anew',
    'scripts/kanban/reconcile.py':
        'reconcile preserves card values; dump_yaml serializes generated boards',
    'scripts/workflow/build_session_review.py':
        'derive_payload_from_git parses history metadata into a generated payload',
    'scripts/quality/check_ruff_ratchet.py':
        '_write_baseline serializes generated counts; subprocess captures diagnostics',
    'scripts/quality/check_mypy_ratchet.py':
        'baseline writer serializes generated counts; subprocess captures diagnostics',
    'scripts/quality/check_complexity_ratchet.py':
        'baseline writer serializes generated counts; subprocess captures diagnostics',
    'scripts/legal/public_redaction.py':
        '_read decodes file bytes, not subprocess output; documented decoding removes BOM',
    'scripts/operations/storage/repository_size_guard.py':
        'inspect_tree captures bytes; default decode consumes a tree identifier only',
}


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f'{_call_name(node.value)}.{node.attr}'
    return ''


def _text_options(node: ast.Call) -> bool:
    for keyword in node.keywords:
        if keyword.arg in {'text', 'universal_newlines', 'encoding', 'errors'} and not (
            isinstance(keyword.value, ast.Constant) and keyword.value.value in (False, None)
        ):
            return True
    return False


def _site(node: ast.Call, kind: str, scope: str) -> dict:
    # SHA-256 is an integrity identifier, not a measured acceptance threshold.
    # Python 3.11 hashlib: https://docs.python.org/3.11/library/hashlib.html
    return {'line': node.lineno, 'kind': kind, 'scope': scope,
            'fingerprint': hashlib.sha256(ast.dump(node).encode('utf-8')).hexdigest()}


def inspect_python(source: str) -> dict:
    try:
        tree = ast.parse(source)
    except (SyntaxError, UnicodeError, ValueError):
        return {'sites': [], 'rewrite': None, 'error': 'NOT_EVALUATED: Python syntax'}
    sites = []
    rewrite = False
    aliases = {'subprocess'}
    functions = {'run', 'check_output', 'check_call', 'Popen'}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            aliases.update(a.asname or a.name for a in node.names if a.name == 'subprocess')
        elif isinstance(node, ast.ImportFrom) and node.module == 'subprocess':
            functions.update(a.asname or a.name for a in node.names)

    class Visitor(ast.NodeVisitor):
        scope = '<module>'

        def visit_FunctionDef(self, node):
            old = self.scope
            self.scope = node.name
            self.generic_visit(node)
            self.scope = old

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_Call(self, node):
            nonlocal rewrite
            name = _call_name(node.func)
            tail = name.rsplit('.', 1)[-1]
            known_process = name.split('.')[0] in aliases or name in functions
            if _text_options(node) and (known_process or tail not in {'open', 'read_text', 'write_text', 'decode', 'encode'}):
                sites.append(_site(node, 'text capture', self.scope))
            elif known_process and any(k.arg is None for k in node.keywords):
                sites.append(_site(node, 'dynamic options', self.scope))
            if tail == 'decode':
                explicit = bool(node.args) or any(k.arg == 'encoding' for k in node.keywords)
                sites.append(_site(node, 'explicit decode' if explicit else 'default decode', self.scope))
            if tail in {'write', 'writelines', 'write_text', 'write_bytes', 'rename', 'copy', 'copyfile', 'copy2'} or name == 'os.replace':
                rewrite = True
            if tail in {'open', 'fdopen'}:
                modes = list(node.args[1:]) + [k.value for k in node.keywords if k.arg == 'mode']
                if any(isinstance(m, ast.Constant) and isinstance(m.value, str)
                       and re.fullmatch(r'[rwaxbt+]+', m.value)
                       and any(c in m.value for c in 'wax+') for m in modes):
                    rewrite = True
            self.generic_visit(node)

    Visitor().visit(tree)
    return {'sites': sorted(sites, key=lambda s: (s['line'], s['kind'])),
            'rewrite': rewrite, 'error': None}


def inspect_shell(source: str) -> dict:
    """Conservative lexical scan; comments skipped, heredocs retained as candidates.

    Substitution removes trailing LF. It does not itself normalize embedded CR;
    later echo, word splitting or filters may introduce additional losses.
    """
    sites = []
    rewrite = False
    for line_number, line in enumerate(source.splitlines(), start=1):
        if line.lstrip().startswith('#'):
            continue
        if re.search(r'\$\((?!\()|`', line):
            sites.append({'line': line_number, 'kind': 'shell substitution'})
        if re.search(r'(?:text|universal_newlines)\s*=\s*True|encoding\s*=|\.decode\(', line):
            sites.append({'line': line_number, 'kind': 'embedded text candidate'})
        if re.search(r'(?<![<>=])>{1,2}(?![=&])|\b(?:cp|mv|tee|patch)\b|\bsed\s+-[^\s]*i|\.write(?:_text|_bytes)?\(', line):
            rewrite = True
    return {'sites': sites, 'rewrite': rewrite, 'error': None}


def script_paths(root: Path) -> list[str]:
    """Git ls-files -z is NUL-delimited (Git ls-files, -z); decode paths explicitly.

    https://git-scm.com/docs/git-ls-files#Documentation/git-ls-files.txt--z
    Include visible new scripts so regeneration is stable before/after staging.
    """
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    result = subprocess.run(
        ['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z', '--', 'scripts/'],
        cwd=root, env=env, capture_output=True, check=True,
    )
    return sorted({os.fsdecode(p) for p in result.stdout.split(b'\0') if p})


def inventory(root: Path, paths: list[str]) -> tuple[list[dict], dict]:
    rows = []
    mapping = {}
    for relative in sorted(set(paths)):
        path = root / relative
        if Path(relative).is_absolute() or '..' in Path(relative).parts or not relative.startswith('scripts/'):
            raise ValueError('expected repository-relative regular script')
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
            code = f'S{len(mapping) + 1:03d}'
            mapping[code] = {'path': relative, 'sha256': None}
            rows.append({'file': code, 'line': None, 'mode': 'NOT_EVALUATED',
                         'promise': 'NOT_EVALUATED', 'capture': 'non-regular path',
                         'verdict': 'NOT_EVALUATED: path not followed'})
            continue
        raw = path.read_bytes()
        first_line = raw.split(b'\n', 1)[0]
        python = path.suffix == '.py' or (first_line.startswith(b'#!') and b'python' in first_line)
        shell = path.suffix in {'.sh', '.bash'} or (first_line.startswith(b'#!') and b'sh' in first_line)
        if not (python or shell):
            continue
        source = raw.decode('utf-8', errors='surrogateescape')
        result = inspect_python(source) if python else inspect_shell(source)
        if not result['sites'] and not result['error'] and relative not in BYTE_PRESERVING:
            continue
        # Codes are display positions, not persistent identities. All paths are
        # local-only so identifiers embedded in filenames never reach the page.
        code = f'S{len(mapping) + 1:03d}'
        mapping[code] = {'path': relative, 'sha256': hashlib.sha256(raw).hexdigest()}
        promise = ('yes' if relative in BYTE_PRESERVING else
                   'no' if relative in REVIEWED_OTHER else 'NOT_EVALUATED')
        mode = 'rewrite candidate' if result['rewrite'] else 'read-only candidate'
        if result['rewrite'] is None:
            mode = 'NOT_EVALUATED'
        for site in result['sites'] or [{'line': None, 'kind': result['error'] or 'binary content path'}]:
            rows.append({'file': code, 'line': site['line'], 'mode': mode,
                         'promise': promise, 'capture': site['kind'],
                         'verdict': BYTE_PRESERVING.get(relative, REVIEWED_OTHER.get(
                             relative, 'NOT_EVALUATED: review contract and data flow'))})
    return rows, mapping


def guard_source(source: str, allowlist: list[dict]) -> list[str]:
    """Reject unreviewed text modes, implicit decode and content-command reuse.

    Exact AST fingerprints keep an exception from covering newly added calls.
    No data-flow proof is claimed for constructed commands or arbitrary wrappers.
    """
    result = inspect_python(source)
    if result['error']:
        return [result['error']]
    findings = []
    used = set()
    for site in result['sites']:
        if site['kind'] == 'explicit decode':
            continue
        matches = [i for i, entry in enumerate(allowlist)
                   if entry.get('scope') == site['scope']
                   and entry.get('fingerprint') == site['fingerprint']
                   and entry.get('reason', '').strip()]
        if len(matches) == 1 and matches[0] not in used:
            used.add(matches[0])
        else:
            findings.append(f"line {site['line']}: unreviewed {site['kind']}")
    # A metadata helper must not be reused to fetch file content as text.
    # Git show DESCRIPTION and git-cat-file -p describe content-producing uses.
    text_wrappers = {'git_output'} | {
        site['scope'] for site in result['sites']
        if site['kind'] == 'text capture' and site['scope'] != '<module>'
    }
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Call) and _call_name(node.func) in text_wrappers and any(
            isinstance(value, ast.Constant) and value.value in ('show', 'cat-file')
            for argument in [*node.args, *(k.value for k in node.keywords)]
            for value in ast.walk(argument)
        ):
            findings.append(f'line {node.lineno}: content command needs byte capture')
    findings.extend('stale allowlist entry' for i in range(len(allowlist)) if i not in used)
    return findings


def guard_repository(root: Path) -> list[str]:
    policy = json.loads((root / 'config/quality/byte-capture-allowlist.json').read_bytes())
    if set(policy) != set(BYTE_PRESERVING):
        return ['allowlist coverage differs from reviewed byte contracts']
    findings = []
    for relative in BYTE_PRESERVING:
        source = (root / relative).read_bytes().decode('utf-8', errors='surrogateescape')
        # Report only stable codes to avoid leaking identifiers in source paths.
        code = f'B{list(BYTE_PRESERVING).index(relative) + 1:03d}'
        findings.extend(f'{code}: {finding}' for finding in guard_source(source, policy[relative]))
    return findings


def render_report(rows: list[dict]) -> str:
    def cell(value):
        return html.escape(str(value if value is not None else 'n/a'))
    body = '\n'.join('<tr>' + ''.join(f'<td>{cell(row[k])}</td>' for k in
                     ('file', 'line', 'mode', 'promise', 'capture', 'verdict')) + '</tr>' for row in rows)
    return '''<!doctype html>
<html lang="en"><meta charset="utf-8"><title>Byte capture inventory</title>
<style>body{font-family:system-ui;max-width:90em;margin:2em auto}table{border-collapse:collapse}td,th{border:1px solid #bbb;padding:.4em;text-align:left}thead{position:sticky;top:0;background:white}</style>
<h1>Byte capture inventory</h1>
<p>Summary: read-only syntax scan of current Python and shell helpers under scripts/.
Every displayed file uses an opaque code. The code-to-path table and source digests
remain in a separate local file; no source text or paths are emitted here.</p>
<h2>Revision history</h2>
<table><tr><th>Revision</th><th>Date</th><th>Change and reason</th></tr>
<tr><td>A</td><td>2026-10-22</td><td>Record capture candidates and reviewed byte paths to prevent newline conversion during repairs.</td></tr></table>
<h2>Method and limits</h2>
<p>AST inspection includes text, universal_newlines, encoding and errors options,
subprocess aliases, injected runners, dynamic keyword options and explicit/default
decode calls. Shell inspection includes substitutions, legacy backticks and embedded
Python candidates. Write indicators are conservative: logging and generated outputs
can appear as rewrites; read-only candidates can call indirect writers. Decode calls
may consume files rather than subprocesses. NOT_EVALUATED means that a byte contract
and capture-to-write data flow have not been established; it does not mean safe.</p>
<p>Non-regular paths, including symbolic links, are recorded without following them.
Syntax errors remain visible as NOT_EVALUATED. Detection cannot resolve arbitrary
wrappers, constructed shell commands, sourced helpers or runtime option dictionaries.</p>
<p>Reviewed contracts and exclusions are recorded in BYTE_PRESERVING and REVIEWED_OTHER.
The pointer repair already
captures its content as bytes; its subprocess text calls read metadata. The bootstrap
writer writes original member bytes after validation. No content subprocess change
is required in either reviewed utility. Other candidates require manual triage before
claiming audit closure. No shared Git helper is introduced: fewer than three reviewed
utilities need a content-capture fix. Existing snapshot relabelling is outside scope.</p>
<p>Regenerate with scripts/quality/byte_capture_audit.py, supplying --report and
--local-map destinations explicitly. The mapping destination must be outside the
repository. Codes can change on regeneration; retain the paired map for lookup.</p>
<h2>Sources</h2><ul>
<li><a href="https://docs.python.org/3.11/library/subprocess.html#frequently-used-arguments">Python 3.11 subprocess: newline conversion in text mode</a></li>
<li><a href="https://docs.python.org/3.11/library/functions.html#open">Python 3.11 open: newline and surrogateescape</a></li>
<li><a href="https://docs.python.org/3.11/library/codecs.html#module-encodings.utf_8_sig">Python 3.11 codecs: BOM bytes and signature handling</a></li>
<li><a href="https://git-scm.com/docs/git-show">Git show: plain blob contents</a></li>
<li><a href="https://git-scm.com/docs/git-ls-files">Git ls-files: NUL-separated filenames</a></li>
<li><a href="https://git-scm.com/docs/git-hash-object">Git hash-object: disposable blob fixtures</a></li>
<li><a href="https://git-scm.com/docs/git-init">Git init: isolated test repositories</a></li>
<li><a href="https://www.gnu.org/software/bash/manual/html_node/Command-Substitution.html">Bash: trailing newline removal</a></li></ul>
<h2>Capture sites</h2><table><thead><tr><th>File code</th><th>Line</th><th>Rewrite or read-only</th><th>Byte preservation promised</th><th>Capture</th><th>Verdict</th></tr></thead>
<tbody>''' + body + '</tbody></table></html>\n'


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--local-map', type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    if args.local_map.resolve().is_relative_to(root):
        parser.error('local mapping must be outside the repository')
    rows, mapping = inventory(root, script_paths(root))
    args.local_map.write_text(json.dumps(mapping, indent=2) + '\n', encoding='utf-8')
    args.report.write_text(render_report(rows), encoding='utf-8')
    print(f'{len(mapping)} utilities; {len(rows)} capture sites')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
