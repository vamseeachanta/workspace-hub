"""Boundary vectors derived independently from literal grammar and byte counts.

RFC 8259 sections 4, 6, 7, 8.1 and 9 define the JSON syntax/encoding.
Limits below are test inputs, not production defaults: b'{}' has two bytes,
'[[0]]' has two open containers and '1234' has four decimal digits.
YAML scalar expectations follow YAML 1.1 type definitions and PyYAML's resolvers;
HTML expectations follow WHATWG parsing, script data end tag open state.
"""
import argparse
import json
from html.parser import HTMLParser
from io import BytesIO

import pytest
from lib.safe_cli import SafeArgumentParser
from lib.script_json import script_json
from lib.strict_json import InputError, load, loads, read
from lib.strict_yaml import exact_bool, exact_int, strict_yaml_load


def decode(raw, **limits):
    # Fixture envelope: at most 128 bytes, four levels, three integer digits.
    return loads(raw, max_bytes=128, max_depth=4, max_integer_digits=3, **limits)


@pytest.mark.parametrize('raw', [
    b'[[[[[0]]]]]', b'1234', b'NaN', b'Infinity', b'-Infinity',
    b'"\xff"', b'{"x":1,"x":2}', b'1e9999', b'{', b'"a" trailing',
])
def test_bad_json_is_structured_and_private(raw):
    with pytest.raises(InputError) as caught:
        decode(raw)
    assert str(caught.value) == 'invalid JSON input'
    assert caught.value.as_dict() == {'error': {'code': 'invalid_json'}}
    assert caught.value.__cause__ is None
    assert caught.value.__context__ is None


def test_size_valid_and_boundary(tmp_path):
    path = tmp_path / 'PRIVATE_SENTINEL.json'
    path.write_bytes(b'{}')
    assert load(path, max_bytes=2, max_depth=1, max_integer_digits=1) == {}
    with pytest.raises(InputError) as caught:
        load(path, max_bytes=1, max_depth=1, max_integer_digits=1)
    assert str(path) not in str(caught.value)
    assert 'PRIVATE_SENTINEL' not in str(caught.value)
    assert read(BytesIO(b'{}'), max_bytes=2, max_depth=1, max_integer_digits=1) == {}


def test_depth_counts_containers_only():
    assert loads(b'[[0]]', max_bytes=5, max_depth=2, max_integer_digits=1) == [[0]]
    assert decode(b'{"x":"[\\\"{]}","y":-123}') == {'x': '["{]}', 'y': -123}


@pytest.mark.parametrize('error', [RecursionError, MemoryError, UnicodeDecodeError,
                                  OverflowError, ValueError])
def test_decoder_exception_boundary(monkeypatch, error):
    def fail(*args, **kwargs):
        if error is UnicodeDecodeError:
            raise error('utf8', b'x', 0, 1, 'PRIVATE_SENTINEL')
        raise error('PRIVATE_SENTINEL')
    monkeypatch.setattr(json, 'loads', fail)
    with pytest.raises(InputError, match='^invalid JSON input$'):
        decode(b'{}')


def test_huge_integer_and_depth_without_runtime_dependence():
    # 5000 exceeds fixture width 3; 2000 open brackets exceed fixture depth 4.
    for raw in (b'9' * 5000, b'[' * 2000 + b'0' + b']' * 2000):
        with pytest.raises(InputError):
            loads(raw, max_bytes=len(raw), max_depth=4, max_integer_digits=3)


@pytest.mark.parametrize('value', [True, 1.0, '1', None])
def test_exact_int(value):
    with pytest.raises(ValueError, match='invalid YAML input'):
        exact_int(value)


def test_yaml_duplicates_and_scalar_types():
    for text in ('x: 1\nx: 2', 'true: a\n1: b', 'x: &a {k: 1}\ny: {<<: *a, k: 2}'):
        with pytest.raises(ValueError, match='^invalid YAML input$'):
            strict_yaml_load(text)
    assert exact_int(1) == 1
    assert exact_bool(True) is True
    with pytest.raises(ValueError):
        exact_bool(1)
    values = strict_yaml_load('[no, on, 1e3, 0o17]')
    assert values == [False, True, '1e3', '0o17']
    assert [type(v) for v in values] == [bool, bool, str, str]


def assert_private_cli(parser, args, capsys):
    """Reusable argparse contract: Python 3.11 argparse documents status 2."""
    with pytest.raises(SystemExit) as caught:
        parser.parse_args(args)
    assert caught.value.code == 2
    captured = capsys.readouterr()
    assert 'PRIVATE_SENTINEL' not in captured.out + captured.err
    assert captured.err.startswith('usage: boundary ')
    assert captured.err.endswith('boundary: error: invalid arguments\n')


@pytest.mark.parametrize('positional', [True, False])
def test_cli_explicit_program_name(positional, capsys):
    parser = (SafeArgumentParser('boundary') if positional
              else SafeArgumentParser(prog='boundary'))
    assert parser.prog == 'boundary'
    assert_private_cli(parser, ['--PRIVATE_SENTINEL'], capsys)


def test_cli_default_program_name(monkeypatch):
    import sys
    monkeypatch.setattr(sys, 'argv', ['PRIVATE_SENTINEL'])
    assert SafeArgumentParser().prog == 'command'


@pytest.mark.parametrize('kind', ['unknown', 'value', 'exclusive'])
def test_cli_no_reflection(kind, capsys):
    parser = SafeArgumentParser(prog='boundary')
    parser.add_argument('--count', type=int)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--left')
    group.add_argument('--right', action='store_true')
    cases = {'unknown': ['--PRIVATE_SENTINEL'],
             'value': ['--count', 'PRIVATE_SENTINEL'],
             'exclusive': ['--left', 'PRIVATE_SENTINEL', '--right']}
    assert_private_cli(parser, cases[kind], capsys)
    assert issubclass(SafeArgumentParser, argparse.ArgumentParser)


class Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags, self.data = [], []

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)

    def handle_data(self, data):
        self.data.append(data)


def test_script_round_trip_and_visible_document():
    value = '</script><img src=x>&>\u2028\u2029'
    encoded = script_json({'x': value})
    assert not any(char in encoded for char in '<>&\u2028\u2029')
    document = Document()
    document.feed('<p>before</p><script type="application/json">' + encoded + '</script><p>after</p>')
    assert document.tags == ['p', 'script', 'p']
    assert document.data[0] == 'before' and document.data[-1] == 'after'
    assert json.loads(document.data[1]) == {'x': value}


@pytest.mark.parametrize('module,entry', [
    ('client_llm_wiki.bootstrap_manifest', '_strict_json'),
    ('client_llm_wiki.bootstrap_bound_manifest', '_strict_claims'),
])
@pytest.mark.parametrize('raw', [b'{"x":NaN}', b'{"x":1,"x":2}', b'"\xff"',
                                  b'[' * 2000 + b'0' + b']' * 2000],
                         ids=['constant', 'duplicate', 'encoding', 'depth'])
def test_manifest_adoption(module, entry, raw):
    import importlib
    consumer = importlib.import_module(module)
    with pytest.raises((RuntimeError, ValueError)) as caught:
        getattr(consumer, entry)(raw)
    assert str(caught.value) == 'manifest is not strict JSON'
    assert caught.value.__cause__ is None
    assert caught.value.__context__ is None


@pytest.mark.parametrize('relative', [
    'scripts/legal/manage_rule_authority.py',
    'scripts/enforcement/extract-pr-issue-references.py',
])
def test_sensitive_cli_subprocess(relative):
    import subprocess
    import sys
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    result = subprocess.run([sys.executable, str(root / relative), '--PRIVATE_SENTINEL'],
                            capture_output=True, text=True, check=False)
    assert result.returncode == 2
    assert 'usage:' in result.stderr
    assert 'PRIVATE_SENTINEL' not in result.stdout + result.stderr


def test_chart_scripts_no_breakout():
    from reporting.calc_report_html import build_chart_scripts
    hostile = '</script><img src=x>'
    for kind in ('bar', 'scatter', 'line'):
        chart = {'type': kind, 'id': hostile, 'x_label': hostile, 'y_label': hostile,
                 'datasets': [{'label': hostile, 'color': hostile, 'data': [[hostile, 1]]}]}
        result = build_chart_scripts([chart])
        assert '<' not in result
        assert r'\u003c' in result


@pytest.mark.parametrize('option', ['max_bytes', 'max_depth', 'max_integer_digits'])
@pytest.mark.parametrize('bad', [True, 0, -1, 1.0, None])
def test_invalid_resource_policy(option, bad):
    limits = {'max_bytes': 2, 'max_depth': 1, 'max_integer_digits': 1}
    limits[option] = bad
    with pytest.raises(InputError):
        loads(b'{}', **limits)


def test_integer_limit_with_interpreter_guard_disabled():
    import sys
    original = sys.get_int_max_str_digits()
    try:
        sys.set_int_max_str_digits(0)
        with pytest.raises(InputError):
            loads(b'9' * 5000, max_bytes=5000, max_depth=1, max_integer_digits=3)
    finally:
        sys.set_int_max_str_digits(original)


def test_json_read_is_bounded():
    class Stream:
        def read(self, count):
            # Two-byte caller budget plus exactly one overflow probe byte.
            assert count == 3
            return b'{} '
    with pytest.raises(InputError):
        read(Stream(), max_bytes=2, max_depth=1, max_integer_digits=1)


class ShortReadStream(BytesIO):
    def read(self, count):
        return super().read(min(count, 2))


@pytest.mark.parametrize('raw,expected', [
    (b'{"x":1}', {'x': 1}),
    ('["\u00e9"]'.encode('utf-8'), ['\u00e9']),
])
def test_json_read_accumulates_short_reads(raw, expected):
    stream = ShortReadStream(raw)
    assert read(stream, max_bytes=len(raw), max_depth=1,
                max_integer_digits=1) == expected
    assert stream.tell() == len(raw)


@pytest.mark.parametrize('raw,budget,consumed', [
    (b'{}TRAILING', 32, 10),
    (b'{} ', 2, 3),
])
def test_json_short_reads_reject_trailing_data_and_overflow(raw, budget, consumed):
    stream = ShortReadStream(raw)
    with pytest.raises(InputError) as caught:
        read(stream, max_bytes=budget, max_depth=1, max_integer_digits=1)
    assert stream.tell() == consumed
    assert caught.value.__context__ is None


@pytest.mark.parametrize('prefix', [b'', b'{}'])
def test_json_read_rejects_nonblocking_no_data(prefix):
    class Stream:
        def __init__(self):
            self.chunks = iter([prefix, None] if prefix else [None])

        def read(self, count):
            return next(self.chunks)

    with pytest.raises(InputError) as caught:
        read(Stream(), max_bytes=2, max_depth=1, max_integer_digits=1)
    assert caught.value.__context__ is None


def test_yaml_private_error():
    with pytest.raises(ValueError) as caught:
        strict_yaml_load('PRIVATE_SENTINEL: [')
    assert str(caught.value) == 'invalid YAML input'
    assert caught.value.as_dict() == {'error': {'code': 'invalid_yaml'}}
    assert caught.value.__context__ is None


def test_adopted_yaml_loader_rejects_duplicate(tmp_path):
    import importlib.util
    from pathlib import Path
    path = Path(__file__).resolve().parents[2] / 'scripts/enforcement/check-skill-index-coherence.py'
    spec = importlib.util.spec_from_file_location('coherence_boundary', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    fixture = tmp_path / 'keys.yaml'
    fixture.write_text('skills: []\nskills: []')
    with pytest.raises(ValueError, match='^invalid YAML input$'):
        module._load_yaml(fixture)


def test_package_import_from_repository_root():
    import subprocess
    import sys
    result = subprocess.run([sys.executable, '-c',
                             ('import scripts.client_llm_wiki.bootstrap_manifest; '
                              'import scripts.client_llm_wiki.bootstrap_bound_manifest')],
                            capture_output=True, text=True, check=False)
    assert result.returncode == 0


def test_worked_examples_exact_outputs(capsys):
    # Thirteen bytes: braces 2 + quoted keys 6 + colons 2 + digits 2 + comma 1.
    with pytest.raises(InputError) as caught:
        loads(b'{"x":1,"x":2}', max_bytes=13, max_depth=1, max_integer_digits=1)
    assert caught.value.as_dict() == {'error': {'code': 'invalid_json'}}
    parser = SafeArgumentParser(prog='boundary')
    with pytest.raises(SystemExit) as caught:
        parser.parse_args(['--PRIVATE_SENTINEL'])
    assert caught.value.code == 2
    captured = capsys.readouterr()
    assert captured.out == ''
    assert captured.err == 'usage: boundary [-h]\nboundary: error: invalid arguments\n'
    assert script_json({'x': '</script><img src=x>'}) == (
        r'{"x": "\u003c/script\u003e\u003cimg src=x\u003e"}')


def test_chart_type_is_script_data():
    from reporting.calc_report_html import build_chart_scripts
    hostile = '</script><img src=x>'
    chart = {'type': hostile, 'id': 'chart', 'x_label': 'x', 'y_label': 'y',
             'datasets': [{'label': 'series', 'data': [[0, 1]]}]}
    assert '<' not in build_chart_scripts([chart])
