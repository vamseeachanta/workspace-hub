"""Nested integer-token regressions with synthetic caller budgets.

Basis: scripts/lib/strict_json.py loads() defines width as decimal digits
without a sign and depth as open containers. Its InputError contract supplies
the exact message/category below; tests/security/test_input_boundaries.py also
requires no exception cause/context. Regression pattern:
docs/standards/explicit-integer-json-bounds.md, "Regression pattern".

Independent hand counts: 12 has two decimal characters, 123 three, 1234 four,
and 0 one; minus signs add no magnitude digits. The caller budget is therefore
three. Root object, outer array and inner object give a maximum depth of three.
Each byte allowance is the UTF-8 length of its independently written literal.
Expected structures are literal values, never produced by the parser under test.

Plan-lite: scope is this test file. The oracle uses the independent literal
structures and hand counts above. Disposable interpreters isolate guard changes.
Acceptance runs this file and test_integer_validation_boundaries.py together:
uv run --no-project --with pytest python -m pytest
tests/security/test_integer_validation_boundaries.py
tests/security/test_nested_integer_validation_boundaries.py
-q -rA -p no:cacheprovider --basetemp="$SCRATCH/bt-combined"

Python documents zero as disabling the integer-string guard; no large integer
is constructed and no production integer ceiling is inferred:
https://docs.python.org/3/library/stdtypes.html#integer-string-conversion-length-limitation
"""
import json
import os
import subprocess
import sys
from pathlib import Path
from textwrap import dedent

import pytest


# Two ancestor steps from tests/security reach the repository root.
ROOT = Path(__file__).resolve().parents[2]
HAS_GUARD = all(hasattr(sys, name) for name in (
    'get_int_max_str_digits', 'set_int_max_str_digits',
))
HAS_FILE_FLAGS = all(hasattr(os, name) for name in ('O_NONBLOCK', 'O_NOFOLLOW'))
APPLICATION_REJECTION = {
    'kind': 'InputError',
    'message': 'invalid JSON input',
    'details': {'error': {'code': 'invalid_json'}},
}

WORKER = dedent('''
    import json
    import re
    import sys
    from io import BytesIO
    from pathlib import Path
    from scripts.lib.strict_json import InputError, load, loads, read

    _, entry, guard_state, filename = sys.argv
    case = json.load(sys.stdin)
    getter = getattr(sys, 'get_int_max_str_digits', None)
    setter = getattr(sys, 'set_int_max_str_digits', None)
    original = getter() if getter and setter else None
    raw = case['raw'].encode('utf-8')
    stream = BytesIO(raw)
    path = Path(filename)
    if entry == 'load':
        path.write_bytes(raw)
        assert path.is_file() and not path.is_symlink()
    before = (path.read_bytes() if entry == 'load' else
              stream.getvalue() if entry == 'read' else raw)
    assert before == raw
    try:
        if guard_state == 'disabled':
            assert original is not None, 'limited coverage: guard API unavailable'
            setter(0)  # Python guard documentation: zero disables the limit.
        active = getter() if original is not None else None
        # Hand counts in the module basis: three containers and three digits.
        limits = dict(max_bytes=case['byte_budget'], max_depth=3,
                      max_integer_digits=3)
        try:
            if entry == 'loads':
                value = loads(raw, **limits)
            elif entry == 'read':
                value = read(stream, **limits)
            else:
                assert entry == 'load'
                value = load(path, **limits)
        except InputError as error:
            assert type(error) is InputError
            assert error.__cause__ is None
            assert error.__context__ is None
            result = {'kind': 'InputError', 'message': str(error),
                      'details': error.as_dict()}
            public = json.dumps([result, repr(error), error.args])
            for token in re.findall(r'-?[0-9]+', case['raw']):
                assert token not in public
                assert token.lstrip('-') not in public
            assert str(path) not in public
        else:
            result = {'kind': 'accepted', 'value': value}
    finally:
        if original is not None:
            setter(original)
        restored = getter() if original is not None else None
        assert restored == original
        after = (path.read_bytes() if entry == 'load' else
                 stream.getvalue() if entry == 'read' else raw)
        assert after == before == raw
    print(json.dumps({'original': original, 'active': active,
                      'restored': restored, 'result': result,
                      'before': before.decode('utf-8'),
                      'after': after.decode('utf-8')}))
''')


def run_case(raw, entry, guard_state, tmp_path):
    """Keep guard mutation in the child and raw bytes intact on every path."""
    if guard_state == 'disabled' and not HAS_GUARD:
        pytest.skip('limited coverage: integer-string guard API unavailable')
    if entry == 'load' and not HAS_FILE_FLAGS:
        pytest.skip('limited coverage: native regular-file protections unavailable')
    original = sys.get_int_max_str_digits() if HAS_GUARD else None
    command = [sys.executable]
    if HAS_GUARD:
        # Preserve settings inherited via either the environment or -X.
        command.extend(['-X', f'int_max_str_digits={original}'])
    command.extend(['-c', WORKER, entry, guard_state, str(tmp_path / 'input.json')])
    try:
        completed = subprocess.run(
            command,
            input=json.dumps({'raw': raw, 'byte_budget': len(raw.encode('utf-8'))}),
            cwd=ROOT, capture_output=True, text=True, check=True,
            timeout=30,  # Synthetic harness wait in seconds, not a JSON budget.
        )
    finally:
        # Check the parent even when a child assertion or process fails.
        if HAS_GUARD:
            assert sys.get_int_max_str_digits() == original
    observed = json.loads(completed.stdout)
    assert observed['original'] == original
    assert observed['active'] == (0 if guard_state == 'disabled' else original)
    assert observed['restored'] == original
    assert observed['before'] == observed['after'] == raw
    return observed['result']


@pytest.mark.parametrize('guard_state', ['original', 'disabled'])
@pytest.mark.parametrize('entry', ['loads', 'read', 'load'])
def test_nested_integer_budget_is_guard_independent(entry, guard_state, tmp_path):
    assert run_case('{"outer":[12,{"leaf":-123}],"zero":0}',
                    entry, guard_state, tmp_path) == {
        'kind': 'accepted', 'value': {'outer': [12, {'leaf': -123}], 'zero': 0},
    }


@pytest.mark.parametrize('guard_state', ['original', 'disabled'])
@pytest.mark.parametrize('entry', ['loads', 'read', 'load'])
@pytest.mark.parametrize('raw', [
    '{"outer":[12,{"leaf":1234}],"zero":0}',
    '{"outer":[12,{"leaf":-1234}],"zero":0}',
], ids=['positive', 'negative'])
def test_nested_oversize_integer_has_application_error(raw, entry, guard_state,
                                                      tmp_path):
    assert run_case(raw, entry, guard_state, tmp_path) == APPLICATION_REJECTION


@pytest.mark.parametrize('guard_state', ['original', 'disabled'])
@pytest.mark.parametrize('entry', ['loads', 'read', 'load'])
def test_digit_string_is_not_an_integer_token(entry, guard_state, tmp_path):
    assert run_case('{"outer":[12,{"leaf":"1234"}],"zero":0}',
                    entry, guard_state, tmp_path) == {
        'kind': 'accepted', 'value': {'outer': [12, {'leaf': '1234'}], 'zero': 0},
    }
