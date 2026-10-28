"""Small, independent vectors for the bounded JSON public contract.

Plan-lite
Scope: the tests will cover UTF-8 byte budgets, signed integer widths,
container depths, short reads, bounded overflow consumption and sanitized
errors through loads() and read(), using small independent literal vectors.
Acceptance: the 62 cases in this module and the 69 existing input-boundary
cases will pass; byte, digit, depth and stream counts will match their literal
expectations; the required test file and ignore exception will remain visible
to Git. Resource failures will be exercised with synthetic exceptions.
Exclusions: production loaders, public interfaces, production limit choices,
gates and workflows will remain unchanged. Actual memory exhaustion and
process termination will not be exercised.

Basis: scripts/lib/strict_json.py module, loads() and read() docstrings;
RFC 8259 sections 4/5 (containers), 6 (numbers), 7 (strings), 8.1 (UTF-8)
and 9 (caller-selected limits). All budgets and chunk sizes below are test
parameters, not recommended production limits. No exhaustion is attempted.

Hand counts: ASCII occupies one byte; the chosen accented character occupies
two UTF-8 bytes and the chosen supplementary character four. Quotes add two
bytes and an array adds two more. A minus sign adds a byte but no decimal
digit. Each array/object opener adds one container, including empty containers.
Stream request/count vectors are hand calculations: budget plus one probe byte,
less bytes already returned; EOF returns zero bytes. Integer literals are the
decimal values written in their inputs, with negative zero equal to zero.
Git ignore exit statuses follow git-check-ignore(1), EXIT STATUS.
"""

import os
import subprocess
from io import BytesIO
from pathlib import Path

import pytest

from lib.strict_json import InputError, loads, read


def assert_rejected(operation):
    """Every rejection must match the fixed public InputError contract."""
    with pytest.raises(InputError) as caught:
        operation()
    error = caught.value
    assert error.as_dict() == {'error': {'code': 'invalid_json'}}
    assert str(error) == 'invalid JSON input'
    assert error.args == ('invalid JSON input',)
    assert repr(error) == "InputError('invalid JSON input')"
    assert error.__cause__ is None
    assert error.__context__ is None


@pytest.mark.parametrize('raw,exact_budget,smaller_budget,expected', [
    (b'"a"', 3, 2, 'a'),
    (b'"\xc3\xa9"', 4, 3, '\u00e9'),
    (b'"\xf0\x9f\x98\x80"', 6, 5, '\U0001f600'),
    (b'["\xc3\xa9"]', 6, 5, ['\u00e9']),
])
def test_json_byte_budget_counts_utf8(raw, exact_budget, smaller_budget, expected):
    # Hand byte counts above; depth and width of one are test parameters.
    assert len(raw) == exact_budget
    assert loads(raw, max_bytes=exact_budget, max_depth=1,
                 max_integer_digits=1) == expected
    assert_rejected(lambda: loads(raw, max_bytes=smaller_budget, max_depth=1,
                                  max_integer_digits=1))


@pytest.mark.parametrize('raw,width,expected', [
    (b'0', 1, 0),
    (b'-0', 1, 0),
    (b'9', 1, 9),
    (b'-9', 1, -9),
    (b'99', 3, 99),
    (b'-99', 3, -99),
    (b'123', 3, 123),
    (b'-123', 3, -123),
])
def test_json_integer_width_boundaries(raw, width, expected):
    # RFC number grammar: one/three digit test widths ignore the minus sign.
    assert loads(raw, max_bytes=len(raw), max_depth=1,
                 max_integer_digits=width) == expected


@pytest.mark.parametrize('raw,width', [
    (b'10', 1), (b'-10', 1),
    (b'1234', 3), (b'-1234', 3),
    (b'+123', 3), (b'012', 3),
])
def test_json_integer_over_width_or_invalid_sign_is_rejected(raw, width):
    # Two/four digits exceed test widths; RFC numbers forbid plus/leading zero.
    assert_rejected(lambda: loads(raw, max_bytes=len(raw), max_depth=1,
                                  max_integer_digits=width))


@pytest.mark.parametrize('raw,depth,expected', [
    (b'[]', 1, []),
    (b'{}', 1, {}),
    (b'[[0]]', 2, [[0]]),
    (b'{"a":{"b":0}}', 2, {'a': {'b': 0}}),
    (b'[{"a":[0]}]', 3, [{'a': [0]}]),
])
def test_json_nested_container_depth_at_limit(raw, depth, expected):
    # Depth is the literal count of simultaneously open containers, per basis.
    assert loads(raw, max_bytes=len(raw), max_depth=depth,
                 max_integer_digits=1) == expected


@pytest.mark.parametrize('raw,shallower_depth', [
    (b'[[]]', 1),
    (b'{"a":{}}', 1),
    (b'[{"a":[]}]', 2),
])
def test_json_nested_container_depth_over_limit(raw, shallower_depth):
    # Two/two/three open containers exceed these one/one/two level parameters.
    assert_rejected(lambda: loads(raw, max_bytes=len(raw),
                                  max_depth=shallower_depth,
                                  max_integer_digits=1))


@pytest.mark.parametrize('raw,depth,expected', [
    (rb'["[\"{]}"]', 1, ['["{]}']),
    (rb'{"[\"{]}":"\\[{}]"}', 1, {'["{]}': '\\[{}]'}),
    (rb'["\\", [0]]', 2, ['\\', [0]]),
    (rb'{"text":"[\"{]}","nested":[0]}', 2,
     {'text': '["{]}', 'nested': [0]}),
])
def test_json_depth_ignores_escaped_string_brackets(raw, depth, expected):
    # RFC string escapes must not hide a later real container or create one.
    assert loads(raw, max_bytes=len(raw), max_depth=depth,
                 max_integer_digits=1) == expected


@pytest.mark.parametrize('raw', [
    rb'["\\", [0]]',
    rb'{"text":"[\"{]}","nested":[0]}',
])
def test_json_depth_after_escaped_string_still_counts(raw):
    # Both literal inputs have two levels; the test parameter allows only one.
    assert_rejected(lambda: loads(raw, max_bytes=len(raw), max_depth=1,
                                  max_integer_digits=1))


class ShortReadStream(BytesIO):
    """Finite binary fixture recording requested and returned byte counts."""

    def __init__(self, raw, chunk_size):
        super().__init__(raw)
        self.chunk_size = chunk_size
        self.requests = []
        self.returned = []

    def read(self, count):
        self.requests.append(count)
        chunk = super().read(min(count, self.chunk_size))
        self.returned.append(len(chunk))
        return chunk


@pytest.mark.parametrize('raw,budget,chunk_size,expected,requests,returned', [
    (b'{"x":1}', 7, 2, {'x': 1}, [8, 6, 4, 2, 1], [2, 2, 2, 1, 0]),
    # The two-byte chunks split the two-byte UTF-8 character across reads.
    (b'"\xc3\xa9"', 4, 2, '\u00e9', [5, 3, 1], [2, 2, 0]),
    (b'{}', 2, 1, {}, [3, 2, 1], [1, 1, 0]),
])
def test_json_short_reads_preserve_complete_input(
        raw, budget, chunk_size, expected, requests, returned):
    # Literal counts follow the hand request recurrence in the module basis.
    stream = ShortReadStream(raw, chunk_size)
    assert read(stream, max_bytes=budget, max_depth=1,
                max_integer_digits=1) == expected
    assert stream.requests == requests
    assert stream.returned == returned
    assert stream.tell() == budget
    assert sum(stream.returned) == budget


@pytest.mark.parametrize('chunk_size,requests,returned', [
    (1, [3, 2, 1], [1, 1, 1]),
    (2, [3, 1], [2, 1]),
])
def test_json_stream_overflow_is_bounded(chunk_size, requests, returned):
    # Test budget two: five input bytes, exactly three consumed, two untouched.
    stream = ShortReadStream(b'{}   ', chunk_size)
    assert_rejected(lambda: read(stream, max_bytes=2, max_depth=1,
                                 max_integer_digits=1))
    assert stream.requests == requests
    assert stream.returned == returned
    assert stream.tell() == 3
    assert sum(stream.returned) == 3
    assert stream.getvalue()[stream.tell():] == b'  '


@pytest.mark.parametrize('bad_chunk', [
    None, 'UNTRUSTED_TEXT', bytearray(b'{}'), memoryview(b'{}'), 0,
])
@pytest.mark.parametrize('prefix,requests', [(b'', [3]), (b'{}', [3, 1])])
def test_json_stream_rejects_non_bytes_and_no_data(bad_chunk, prefix, requests):
    # Budget two requests three initially, then one after a complete object.
    chunks = iter([prefix, bad_chunk] if prefix else [bad_chunk])
    requested = []

    class Stream:
        def read(self, count):
            requested.append(count)
            return next(chunks)

    assert_rejected(lambda: read(Stream(), max_bytes=2, max_depth=1,
                                 max_integer_digits=1))
    assert requested == requests


def test_json_stream_rejects_more_bytes_than_requested():
    # Budget two requests three; an untrusted stream returns four instead.
    requested = []

    class Stream:
        def read(self, count):
            requested.append(count)
            return b'{}  '

    assert_rejected(lambda: read(Stream(), max_bytes=2, max_depth=1,
                                 max_integer_digits=1))
    assert requested == [3]


@pytest.mark.parametrize('raw,budget,depth,width', [
    # Each budget is a test parameter; only the named defect must reject.
    (b'{"UNTRUSTED_TEXT":', 32, 1, 1),  # Invalid syntax: missing value/closer.
    (b'"UNTRUSTED_TEXT\xff"', 32, 1, 1),  # Invalid UTF-8 byte.
    (b'"UNTRUSTED_TEXT"', 2, 1, 1),  # Byte budget exceeded.
    (b'[["UNTRUSTED_TEXT"]]', 32, 1, 1),  # Two levels exceed one.
    (b'{"UNTRUSTED_TEXT":1234}', 32, 1, 3),  # Four digits exceed three.
    (b'{"UNTRUSTED_TEXT":0,"UNTRUSTED_TEXT":1}', 64, 1, 1),  # Duplicate key.
    (b'{"UNTRUSTED_TEXT":NaN}', 32, 1, 1),  # Non-JSON number.
    (b'{"UNTRUSTED_TEXT":1e9999}', 32, 1, 1),  # Non-finite conversion.
])
def test_json_rejections_share_sanitized_envelope(raw, budget, depth, width):
    # loads() and read() must expose identical literals without decoder context.
    assert_rejected(lambda: loads(raw, max_bytes=budget, max_depth=depth,
                                  max_integer_digits=width))
    assert_rejected(lambda: read(BytesIO(raw), max_bytes=budget, max_depth=depth,
                                 max_integer_digits=width))


@pytest.mark.parametrize('failure', [OSError, ValueError, MemoryError, RecursionError])
def test_json_stream_failures_share_sanitized_envelope(failure):
    # Synthetic exceptions test handling without allocating an excessive input.
    class Stream:
        def read(self, count):
            raise failure('UNTRUSTED_TEXT')

    assert_rejected(lambda: read(Stream(), max_bytes=2, max_depth=1,
                                 max_integer_digits=1))


@pytest.mark.parametrize('relative', [
    '.gitignore', 'tests/lib/test_strict_json_boundaries.py',
])
def test_delivered_file_is_not_ignored(relative):
    root = Path(__file__).resolve().parent.parent.parent
    environment = os.environ.copy()
    for variable in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_COMMON_DIR', 'GIT_INDEX_FILE'):
        environment.pop(variable, None)
    result = subprocess.run(
        ['git', '-C', str(root), 'check-ignore', '--no-index', '--quiet', '--', relative],
        env=environment, capture_output=True, check=False,
    )
    # git-check-ignore documents status one when none of the paths are ignored.
    assert result.returncode == 1
