"""Small, independently counted integer-width fixtures, not production limits.

Basis: scripts/lib/strict_json.py loads() documents decimal digits without a
sign. Python's integer-string conversion limit also excludes the sign, raises
ValueError on overflow, and accepts zero to disable the interpreter guard:
https://docs.python.org/3/library/stdtypes.html#integer-string-conversion-length-limitation
Its minimum enabled limit exceeds every literal here; no large integer is built.

Hand counts: '12' has two digits, '123' three, '1234' four, '0' and '1' one each.
A minus sign adds no digits. Expected signed integers below are literal values,
independent of the decoder. Budgets three and one are synthetic caller choices;
zero is an invalid budget, and boolean/float budgets must not act as integers.
"""
import json
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
APPLICATION_REJECTION = {
    'kind': 'InputError',
    'message': 'invalid JSON input',
    'details': {'error': {'code': 'invalid_json'}},
}

WORKER = dedent('''
    import json
    import sys
    from scripts.lib.strict_json import InputError, loads

    _, guard_state = sys.argv
    case = json.load(sys.stdin)
    getter = getattr(sys, 'get_int_max_str_digits', None)
    setter = getattr(sys, 'set_int_max_str_digits', None)
    original = getter() if getter and setter else None
    try:
        if guard_state == 'disabled':
            assert original is not None, 'limited coverage: guard API unavailable'
            setter(0)  # Python guard documentation: zero disables the limit.
        active = getter() if original is not None else None
        raw = case['raw'].encode('ascii')
        try:
            # Exact byte allowance; a scalar has no open containers, so the
            # smallest positive depth budget (one) cannot reject these inputs.
            value = loads(raw, max_bytes=len(raw), max_depth=1,
                          max_integer_digits=case['budget'])
        except InputError as error:
            assert type(error) is InputError
            result = {'kind': 'InputError', 'message': str(error),
                      'details': error.as_dict()}
        else:
            assert type(value) is int
            result = {'kind': 'accepted', 'value': value}
    finally:
        if original is not None:
            setter(original)
    restored = getter() if original is not None else None
    print(json.dumps({'original': original, 'active': active,
                      'restored': restored, 'result': result}))
''')


def run_case(raw, budget, guard_state):
    """Change guard settings only in a disposable interpreter and restore them."""
    if guard_state == 'disabled' and not HAS_GUARD:
        pytest.skip('limited coverage: integer-string guard API unavailable')
    original = sys.get_int_max_str_digits() if HAS_GUARD else None
    command = [sys.executable]
    if HAS_GUARD:
        # Preserve the caller's original setting even when supplied via -X.
        command.extend(['-X', f'int_max_str_digits={original}'])
    command.extend(['-c', WORKER, guard_state])
    completed = subprocess.run(
        command, input=json.dumps({'raw': raw, 'budget': budget}), cwd=ROOT,
        capture_output=True, text=True, check=True,
        timeout=30,  # Synthetic harness wait budget in seconds, not a JSON limit.
    )
    observed = json.loads(completed.stdout)
    assert observed['original'] == original
    assert observed['active'] == (0 if guard_state == 'disabled' else original)
    assert observed['restored'] == original
    if HAS_GUARD:
        assert sys.get_int_max_str_digits() == original
    return observed['result']


@pytest.mark.parametrize('guard_state', ['original', 'disabled'])
@pytest.mark.parametrize('raw,budget,expected', [
    ('12', 3, 12),       # Two digits: below three.
    ('-12', 3, -12),     # Two digits: below three, sign excluded.
    ('123', 3, 123),     # Three digits: exactly three.
    ('-123', 3, -123),   # Three digits: exactly three, sign excluded.
    ('1234', 3, None),   # Four digits: above three.
    ('-1234', 3, None),  # Four digits: above three, sign excluded.
    ('0', 3, 0),         # One digit: below three.
    ('-0', 3, 0),        # One digit: below three; negative zero equals zero.
    ('0', 1, 0),         # One digit: exactly one.
    ('-0', 1, 0),        # One digit: exactly one, sign excluded.
])
def test_signed_integer_width_boundaries(raw, budget, expected, guard_state):
    observed = run_case(raw, budget, guard_state)
    if expected is None:
        assert observed == APPLICATION_REJECTION
    else:
        assert observed == {'kind': 'accepted', 'value': expected}


@pytest.mark.parametrize('guard_state', ['original', 'disabled'])
@pytest.mark.parametrize('raw,budget', [
    ('1234', 3),   # Four digits exceed three, far below the interpreter minimum.
    ('-1234', 3),  # Same four digits with a sign; still application rejection.
    ('0', 0),     # Zero has one digit; a zero budget is invalid.
    ('1', True),  # One digit fits budget one, but a boolean is not a budget.
    ('1', False),  # One digit; a false boolean must also be rejected.
    ('1', 1.0),   # One digit fits one, but a float is not an integer budget.
    ('-123', 3.0),  # Three digits fit three; a float budget remains invalid.
])
def test_integer_rejection_is_application_owned(raw, budget, guard_state):
    assert run_case(raw, budget, guard_state) == APPLICATION_REJECTION
