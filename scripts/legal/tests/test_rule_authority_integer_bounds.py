"""Guard-independent numeric boundary regressions for legal-json-v1.

Basis: docs/plans/evidence/2026-07-13-issue-3522-rule-authority-contract.md,
sections 1 and 2 (2026), unsigned 64-bit generations. The geometric sum
2**0 + ... + 2**63 = 2**64 - 1 = 18446744073709551615 gives the ceiling;
adding one is out of range. Other integer fields have smaller schema limits.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rule_authority import authority, codec


@pytest.fixture(params=["default", "disabled"])
def integer_guard(request):
    """Exercise both runtime modes and restore the process setting on every exit."""
    previous = sys.get_int_max_str_digits()
    # Python 3.11, Integer string conversion length limitation, Configuring:
    # https://docs.python.org/3.11/library/stdtypes.html#configuring-the-limit
    # Zero disables the conversion guard.
    # Its default is read from sys.int_info, never assumed by these tests.
    target = sys.int_info.default_max_str_digits if request.param == "default" else 0
    sys.set_int_max_str_digits(target)
    try:
        yield
    finally:
        sys.set_int_max_str_digits(previous)


def test_unsigned_boundary_preserves_exact_bytes(integer_guard):
    """Independent geometric-sum result above fixes both decimal text and bytes."""
    value = {"generation": 18446744073709551615}
    expected = b'{"generation":18446744073709551615}\n'
    assert codec.canonical_bytes(value) == expected
    assert codec.parse_canonical(expected) == value
    # Hash compatibility follows from unchanged bytes, independently supplied.
    assert authority._sha(value) == hashlib.sha256(expected).digest()


@pytest.mark.parametrize("sign", [1, -1], ids=["positive", "negative"])
@pytest.mark.parametrize("shape", ["root", "object", "array", "tuple", "ledger", "key"])
def test_out_of_range_integer_rejected_before_encoding(
    integer_guard, monkeypatch, sign, shape,
):
    """The ceiling plus one exceeds either allowed magnitude before JSON work."""
    value = sign * 18446744073709551616
    if shape == "object":
        value = {"generation": value}
    elif shape == "array":
        value = [value]
    elif shape == "tuple":
        value = (value,)
    elif shape == "ledger":
        value = {"entries": [{"generation": value}]}
    elif shape == "key":
        value = {value: "integer key"}

    def deny_encoding(*args, **kwargs):
        raise AssertionError("invalid integer reached JSON encoding")

    monkeypatch.setattr(codec.json, "dumps", deny_encoding)
    with pytest.raises(codec.AuthorityError, match="^schema$") as caught:
        codec.canonical_bytes(value)
    assert type(caught.value) is codec.AuthorityError
    assert caught.value.__cause__ is None


@pytest.mark.parametrize("sign", ["", "-"], ids=["positive", "negative"])
def test_huge_integer_tokens_have_application_error(integer_guard, sign):
    """A decimal token longer than the runtime default must fail in either mode.

    A string of n nines is 10**n - 1; n exceeds the default digit guard and
    the decimal width of the cited unsigned ceiling. No large int is parsed
    or stringified to construct the independent raw input.
    """
    digits = "9" * (sys.int_info.default_max_str_digits + 1)
    raw = ('{"generation":' + sign + digits + '}\n').encode("ascii")
    with pytest.raises(codec.AuthorityError, match="^schema$") as caught:
        codec.parse_canonical(raw)
    assert type(caught.value) is codec.AuthorityError
    assert caught.value.__cause__ is None


def test_huge_python_integer_never_reaches_hashing(integer_guard, monkeypatch):
    """10**(default+1) is larger than the ceiling without decimal conversion."""
    value = {"generation": 10 ** (sys.int_info.default_max_str_digits + 1)}

    def deny_hash(*args, **kwargs):
        raise AssertionError("invalid integer reached hashing")

    monkeypatch.setattr(authority.hashlib, "sha256", deny_hash)
    with pytest.raises(codec.AuthorityError, match="^schema$") as caught:
        authority._sha(value)
    assert caught.value.__cause__ is None


@pytest.mark.parametrize("token", ["18446744073709551616", "-18446744073709551616"])
def test_decimal_boundary_rejects_by_value(integer_guard, token):
    """The ceiling plus one has the same decimal width; length alone is insufficient."""
    with pytest.raises(codec.AuthorityError, match="^schema$"):
        codec.parse_canonical(('{"generation":' + token + '}\n').encode("ascii"))


@pytest.mark.parametrize("value", [True, False, 0, -1, 1.0, "1", None])
def test_generation_field_keeps_stricter_domain(value):
    """The contract requires an exact positive int, excluding bool and zero."""
    with pytest.raises(codec.AuthorityError, match="^schema$"):
        codec._generation(value)


def test_valid_scalar_bytes_and_shared_container_preserved(integer_guard):
    """Signs, zero and JSON literals keep their literal spellings and list order.

    The shared child is not a cycle. Its negative value is wire-representable
    but cannot be a generation; field validation still enforces positivity.
    """
    child = [True, False, None, 0, -18446744073709551615]
    expected_child = b'[true,false,null,0,-18446744073709551615]'
    assert codec.canonical_bytes([child, child]) == (
        b'[' + expected_child + b',' + expected_child + b']\n'
    )
    codec._generation(18446744073709551615)
    with pytest.raises(codec.AuthorityError, match="^schema$"):
        codec._generation(18446744073709551616)


def test_existing_noninteger_json_and_cycles_keep_schema_error():
    """An unsupported value and a circular list already violate legal-json-v1."""
    cycle = []
    cycle.append(cycle)
    for value in (object(), cycle):
        with pytest.raises(codec.AuthorityError, match="^schema$"):
            codec.canonical_bytes(value)
