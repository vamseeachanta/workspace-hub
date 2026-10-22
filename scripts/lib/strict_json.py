"""Bounded JSON boundaries; all resource policies are explicit caller inputs.

Basis: RFC 8259 (2017), sections 4 (names), 6 (numbers), 8.1 (UTF-8),
9 (implementation limits). Python 3.11 json documents decoder resource risks.
No universal size, depth or numeric width is prescribed by those documents.
"""
import json
import math
import os
import stat


class InputError(ValueError):
    """Public error with no caller content, path or decoder exception attached."""

    def __init__(self):
        super().__init__('invalid JSON input')

    def as_dict(self):
        return {'error': {'code': 'invalid_json'}}


def _limits(*values):
    if any(type(value) is not int or value <= 0 for value in values):
        raise InputError()


def _depth(text, maximum):
    depth = 0
    quoted = escaped = False
    for char in text:
        if quoted:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in '[{':
            depth += 1  # RFC 8259 sections 4/5: one opener per container.
            if depth > maximum:
                raise InputError()
        elif char in ']}':
            depth -= 1


def _pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise InputError()
        result[key] = value
    return result


def _constant(_token):
    raise InputError()


def loads(data, *, max_bytes, max_depth, max_integer_digits):
    """Decode bytes with strict syntax and fixed public failure information.

    Width counts decimal digits without a sign. Depth counts open containers.
    Memory exhaustion handling is best effort; process-level termination cannot
    be converted to an application exception.
    """
    try:
        _limits(max_bytes, max_depth, max_integer_digits)
        if type(data) is not bytes or len(data) > max_bytes:
            raise InputError()
        text = data.decode('utf-8')
        _depth(text, max_depth)

        def integer(token):
            if len(token.lstrip('-')) > max_integer_digits:
                raise InputError()
            return int(token)

        def floating(token):
            value = float(token)
            if not math.isfinite(value):
                raise InputError()
            return value

        return json.loads(text, object_pairs_hook=_pairs, parse_constant=_constant,
                          parse_int=integer, parse_float=floating)
    except (RecursionError, MemoryError, UnicodeError, OverflowError, ValueError):
        pass
    # Raise outside the handler: even __context__ must not retain input text.
    raise InputError()


def read(stream, *, max_bytes, max_depth, max_integer_digits):
    """Read at most the caller byte budget plus one overflow-detection byte.

    Short reads are accumulated until EOF or overflow. A nonblocking no-data
    result is rejected rather than treated as EOF. The caller owns stream trust,
    descriptor validation and blocking semantics.
    """
    try:
        _limits(max_bytes, max_depth, max_integer_digits)
        data = bytearray()
        while len(data) <= max_bytes:
            remaining = max_bytes + 1 - len(data)
            chunk = stream.read(remaining)
            if type(chunk) is not bytes or len(chunk) > remaining:
                raise InputError()
            if not chunk:
                break
            data.extend(chunk)
        data = bytes(data)
    except (OSError, ValueError, OverflowError, MemoryError, RecursionError):
        pass
    else:
        return loads(data, max_bytes=max_bytes, max_depth=max_depth,
                     max_integer_digits=max_integer_digits)
    raise InputError()


def load(path, *, max_bytes, max_depth, max_integer_digits):
    """Open a regular file without following its final symlink, then read.

    Retained-descriptor consumers should use read() with their existing guards.
    O_NONBLOCK avoids FIFO waits before fstat; unsupported platforms fail closed.
    Ancestor traversal and provenance remain the caller's responsibility.
    """
    descriptor = None
    try:
        _limits(max_bytes, max_depth, max_integer_digits)
        flags = os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW
        descriptor = os.open(path, flags)
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise InputError()
        with os.fdopen(descriptor, 'rb') as stream:
            descriptor = None
            return read(stream, max_bytes=max_bytes, max_depth=max_depth,
                        max_integer_digits=max_integer_digits)
    except (OSError, ValueError, OverflowError, MemoryError, RecursionError, AttributeError):
        pass
    finally:
        if descriptor is not None:
            os.close(descriptor)
    raise InputError()
