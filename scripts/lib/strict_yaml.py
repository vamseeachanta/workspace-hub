"""Duplicate-rejecting PyYAML SafeLoader and exact schema scalar checks.

PyYAML resolves plain scalars with YAML 1.1 rules; this is not a YAML 1.2 loader.
See YAML 1.1 section 3.2.1.1 (unique mapping keys), boolean/int type definitions;
YAML 1.2.2 section 10.3.2 (core resolution) differs for no/on and octal syntax.
"""
import yaml


class YamlInputError(ValueError):
    """Stable public YAML schema/parse error."""

    def __init__(self):
        super().__init__('invalid YAML input')

    def as_dict(self):
        return {'error': {'code': 'invalid_yaml'}}


class StrictSafeLoader(yaml.SafeLoader):
    """Reject duplicate constructed keys, including merge collisions."""

    def construct_mapping(self, node, deep=False):
        self.flatten_mapping(node)
        result = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                duplicate = key in result
            except TypeError:
                raise YamlInputError() from None
            if duplicate:
                raise YamlInputError()
            result[key] = self.construct_object(value_node, deep=deep)
        return result


def strict_yaml_load(stream):
    """No object constructors beyond SafeLoader; no source in public errors."""
    try:
        return yaml.load(stream, Loader=StrictSafeLoader)
    except (yaml.YAMLError, ValueError, TypeError, RecursionError, MemoryError,
            OverflowError, UnicodeError, OSError):
        pass
    raise YamlInputError()


def exact_int(value):
    if type(value) is not int:
        raise YamlInputError()
    return value


def exact_bool(value):
    if type(value) is not bool:
        raise YamlInputError()
    return value
