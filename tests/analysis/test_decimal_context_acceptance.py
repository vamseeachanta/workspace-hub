"""Exact boundary regressions for issue 3859; all inputs are synthetic.

Hand basis: relative error = abs((calculated - expected) / expected), the
existing NumericalSolver.verify_accuracy contract. With expected=100 and
limit=0.01, calculated=101 has error=1/100 exactly; 100.9999 and 101.0001
are below and above. The zero-reference branch uses strict absolute error.
Trend stability uses abs(current - previous) <= tolerance, the existing
compare_direction contract. No engineering acceptance limit is introduced.
Python 3.11 Library Reference, decimal and fractions modules, documents exact
Decimal construction and exact Fraction conversion from finite Decimal values.
"""
import importlib.util
import sys
from decimal import (
    ROUND_DOWN,
    ROUND_UP,
    Context,
    Decimal,
    DefaultContext,
    localcontext,
)
from fractions import Fraction
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def load_module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


base = load_module('decimal_audit_base', 'src/solvers/base.py')
trend = load_module('decimal_audit_trend', 'scripts/analysis/provider_session_ecosystem_audit.py')
publication = load_module('decimal_audit_publication', 'scripts/governance/publication_eligibility.py')


class SyntheticSolver(base.NumericalSolver):
    def solve(self, parameters):
        raise NotImplementedError

    def validate_input(self, parameters):
        raise NotImplementedError


@pytest.fixture(params=['ambient-down', 'ambient-up', 'default', 'both',
                        'rounded-down', 'rounded-up'])
def hostile_context(request):
    """Alter precision, rounding, exponent bounds, clamp, flags and all traps.

    Context limits here are adversarial software fixtures, not physical limits.
    Every mutable default field is restored, including on assertion failure.
    """
    saved = DefaultContext.copy()
    hostile = Context(prec=2, rounding=ROUND_UP if request.param.endswith('up')
                      else ROUND_DOWN, Emin=-1, Emax=1, capitals=0, clamp=1,
                      flags=[], traps=[])
    for signal in hostile.traps:
        hostile.traps[signal] = not request.param.startswith('rounded')
        hostile.flags[signal] = True
    neutral = Context(prec=28, rounding=ROUND_DOWN, Emin=-999999, Emax=999999,
                      capitals=1, clamp=0, flags=[], traps=[])
    try:
        with localcontext(neutral if request.param == 'default' else hostile) as active:
            if request.param in {'default', 'both'}:
                for field in ('prec', 'rounding', 'Emin', 'Emax', 'capitals', 'clamp'):
                    setattr(DefaultContext, field, getattr(hostile, field))
                DefaultContext.flags = hostile.flags.copy()
                DefaultContext.traps = hostile.traps.copy()
            before = active.copy()
            yield
            for field in ('prec', 'rounding', 'Emin', 'Emax', 'capitals', 'clamp',
                          'flags', 'traps'):
                assert getattr(active, field) == getattr(before, field)
    finally:
        for field in ('prec', 'rounding', 'Emin', 'Emax', 'capitals', 'clamp'):
            setattr(DefaultContext, field, getattr(saved, field))
        DefaultContext.flags = saved.flags.copy()
        DefaultContext.traps = saved.traps.copy()


@pytest.mark.parametrize(('value', 'accepted'), [
    ('100.9999', True), ('101', True), ('101.0001', False),
    ('99.0001', True), ('99', True), ('98.9999', False),
])
def test_relative_boundary(hostile_context, value, accepted):
    solver = SyntheticSolver('synthetic', accuracy_tolerance=Decimal('0.01'))
    assert solver.verify_accuracy(Decimal(value), Decimal(100)) is accepted


@pytest.mark.parametrize(('value', 'accepted'), [
    ('0.009999', True), ('0.01', False), ('0.010001', False),
    ('-0.009999', True), ('-0.01', False), ('-0.010001', False),
])
def test_zero_reference_boundary(hostile_context, value, accepted):
    """Strict branch: abs(value) < 1/100, including the negative boundary."""
    solver = SyntheticSolver('synthetic', accuracy_tolerance=Decimal('0.01'))
    assert solver.verify_accuracy(Decimal(value), Decimal(0)) is accepted


@pytest.mark.parametrize(('value', 'expected'), [
    ('100.9999', 'stable'), ('101', 'stable'), ('101.0001', 'worsening'),
    ('99.0001', 'stable'), ('99', 'stable'), ('98.9999', 'improving'),
])
def test_trend_boundary(hostile_context, value, expected):
    """Hand differences from 100 straddle the synthetic tolerance of 1."""
    assert trend.compare_direction(Decimal(value), Decimal(100),
                                   better_when_lower=True, tolerance=Decimal(1)) == expected


@pytest.mark.parametrize(('token', 'accepted'), [
    ('0.9999999999999999', True), ('1.0', True), ('1.0000000000000002', True),
    ('1.00000000000000001', False), ('1e-400', False),
])
def test_publication_exact_equality(hostile_context, token, accepted):
    """Shortest binary64 round trips preserve the first three decimal tokens.

    1.00000000000000001 rounds to 1.0; 1e-400 underflows to zero. Equality,
    rather than a rounded subtraction or tolerance, must reject both losses.
    """
    if accepted:
        assert publication.load_json(token) == float(token)
    else:
        with pytest.raises(publication.InvalidBundle, match='lossy_json_number'):
            publication.load_json(token)


def test_float_contract_unchanged():
    solver = SyntheticSolver('synthetic', accuracy_tolerance=0.01)
    assert solver.verify_accuracy(101.0, 100.0)
    assert not solver.verify_accuracy(101.01, 100.0)
    assert trend.compare_direction(None, 100.0, better_when_lower=True) == 'unavailable'


def test_worked_idle_example(hostile_context):
    """Issue 3859: four cores, 50.0001 percent CPU, required idle capacity 2.

    Hand calculation: 4 * (100 - 50.0001) / 100 = 1999996/1000000
    = 499999/250000 core-equivalents, short of 2 by 1/250000.
    These are the issue's diagnostic inputs, not engineering acceptance limits.
    """
    idle = Fraction(4) * (1 - Fraction(Decimal('50.0001')) / 100)
    assert idle == Fraction(499999, 250000)
    assert Fraction(2) - idle == Fraction(1, 250000)
    assert idle < 2


def test_mixed_values_keep_binary_float_value(hostile_context):
    """Binary64 0.1 exceeds decimal 1/10, so a strict comparison rejects it.

    Decimal 0.1 is below the binary64 tolerance, so the converse accepts.
    Converting floats through str would incorrectly erase that distinction.
    """
    solver = SyntheticSolver('synthetic', accuracy_tolerance=Decimal('0.1'))
    assert not solver.verify_accuracy(0.1, 0)
    solver.accuracy_tolerance = 0.1
    assert solver.verify_accuracy(Decimal('0.1'), 0)
    assert trend.compare_direction(0.1, 0, better_when_lower=True,
                                   tolerance=Decimal('0.1')) == 'worsening'


@pytest.mark.parametrize(('value', 'accepted'), [
    ('100.9999999999999999999999999999999999999999', True),
    ('101', True),
    ('101.0000000000000000000000000000000000000001', False),
])
def test_boundary_beyond_default_precision(hostile_context, value, accepted):
    """Hand inequality: these values lie below, at and above 101 exactly.

    Against reference 100 and tolerance 1/100, the relative-error boundary
    is exactly 101; a fixed 28-digit context would lose the final distinction.
    """
    solver = SyntheticSolver('synthetic', accuracy_tolerance=Decimal('0.01'))
    assert solver.verify_accuracy(Decimal(value), Decimal(100)) is accepted


@pytest.mark.parametrize('value', ['NaN', 'sNaN', 'Infinity', '-Infinity'])
def test_nonfinite_decimal_is_rejected(hostile_context, value):
    """Non-finite values have no finite rational representation."""
    solver = SyntheticSolver('synthetic', accuracy_tolerance=Decimal('0.01'))
    with pytest.raises((ValueError, OverflowError)):
        solver.verify_accuracy(Decimal(value), Decimal(100))
    with pytest.raises((ValueError, OverflowError)):
        trend.compare_direction(Decimal(value), Decimal(100), better_when_lower=True)
