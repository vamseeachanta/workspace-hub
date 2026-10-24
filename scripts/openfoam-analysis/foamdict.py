"""Strict parser for generated OpenFOAM dictionaries, not a general FOAM reader.

Supports nested dictionaries, scalar entries, quoted keys and C/C++ comments.
Directives, substitutions and list dictionaries require a full OpenFOAM reader.
Basis: OpenFOAM v2312 documentation, Under relaxation / Usage; User Guide 6.3.2.
"""
import re


class DictionaryError(ValueError):
    """The generated subset cannot be parsed without ambiguity."""


TOKEN = re.compile(r'\s+|//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"|[{};]|[^\s{};"/]+|/', re.DOTALL)


def parse_dictionary(text: str) -> dict:
    """Parse the generated subset; reject duplicate keys and incomplete syntax."""
    tokens = []
    position = 0
    while position < len(text):
        if text.startswith("/*", position) and "*/" not in text[position:]:
            raise DictionaryError("unterminated comment")
        match = TOKEN.match(text, position)
        if not match:
            raise DictionaryError("invalid or unterminated quoted token")
        token = match.group()
        position = match.end()
        if token.isspace() or token.startswith(("//", "/*")):
            continue
        if token.startswith(("#", "$")):
            raise DictionaryError("directives and substitutions are unsupported")
        tokens.append(token)

    index = 0

    def entries(nested=False):
        nonlocal index
        result = {}
        while index < len(tokens):
            key = tokens[index]
            index += 1
            if key == "}":
                if not nested:
                    raise DictionaryError("unexpected closing brace")
                return result
            if key in ("{", ";"):
                raise DictionaryError("expected dictionary key")
            if key in result:
                raise DictionaryError(f"duplicate key: {key}")
            if index >= len(tokens):
                raise DictionaryError(f"missing value for {key}")
            if tokens[index] == "{":
                index += 1
                result[key] = entries(nested=True)
                if index < len(tokens) and tokens[index] == ";":
                    index += 1
            else:
                values = []
                while index < len(tokens) and tokens[index] not in (";", "{", "}"):
                    values.append(tokens[index])
                    index += 1
                if index >= len(tokens) or tokens[index] != ";":
                    raise DictionaryError(f"missing semicolon after {key}")
                if not values:
                    raise DictionaryError(f"missing value for {key}")
                index += 1
                result[key] = " ".join(values)
        if nested:
            raise DictionaryError("missing closing brace")
        return result

    return entries()


def relaxation_issues(solution: dict) -> list[str]:
    """Check only relaxation ancestry, not numerical suitability or convergence."""
    issues = []
    simple = solution.get("SIMPLE", {})
    if not isinstance(simple, dict):
        return ["SIMPLE must be a sub-dictionary"]
    consistent = simple.get("consistent", "no")
    if consistent not in ("yes", "no", "true", "false", "on", "off"):
        issues.append("SIMPLE.consistent must be a switch")
    simplec = consistent in ("yes", "true", "on")
    relaxation = solution.get("relaxationFactors", {})
    if not isinstance(relaxation, dict):
        return ["relaxationFactors must be a sub-dictionary"]
    for section, factors in relaxation.items():
        if section not in ("fields", "equations") or not isinstance(factors, dict):
            issues.append("relaxationFactors requires fields/equations sub-dictionary placement")
            continue
        for key, factor in factors.items():
            name = key.strip('"')
            if isinstance(factor, dict):
                issues.append(f"relaxation factor {key} must be scalar")
                continue
            if name in ("p", "p_rgh"):
                if section != "fields":
                    issues.append(f"pressure {key} may only appear under fields")
                if simplec:
                    issues.append(f"SIMPLEC forbids pressure relaxation: {key}")
            elif name in ("U", "k", "epsilon", "omega") or key.startswith('"'):
                if section != "equations":
                    issues.append(f"{key} may only appear under equations")
    return issues


def validate_fvsolution(text: str) -> list[str]:
    try:
        return relaxation_issues(parse_dictionary(text))
    except DictionaryError as error:
        return [str(error)]


def algorithm_issues(solution: dict, schemes: dict, control: dict) -> list[str]:
    """Reject contradictory algorithm/time categories, not unqualified coefficients.

    Sources: User Guide 6.3.3 (icoFoam/PISO); OpenFOAM v2312 documentation,
    simpleFoam Overview/Time schemes and pisoFoam Overview/Equations.
    """
    issues = []
    application = control.get("application")
    if application not in ("simpleFoam", "icoFoam", "pisoFoam"):
        return ["NOT_EVALUATED: application requires reviewed algorithm/time-scheme rules"]
    steady = application == "simpleFoam"
    expected = "SIMPLE" if steady else "PISO"
    algorithms = {key for key in ("SIMPLE", "PISO", "PIMPLE") if key in solution}
    if algorithms != {expected} or not isinstance(solution.get(expected), dict):
        issues.append(f"{application} requires only the {expected} algorithm sub-dictionary")
    ddt = schemes.get("ddtSchemes")
    if not isinstance(ddt, dict) or not isinstance(ddt.get("default"), str):
        issues.append("ddtSchemes requires a scalar default time scheme")
    else:
        # Reject field overrides as well as the default if their category conflicts.
        for key, value in ddt.items():
            if not isinstance(value, str):
                issues.append(f"ddtSchemes.{key} must be a scalar scheme")
            elif steady != (value == "steadyState"):
                issues.append(f"{application} contradicts ddtSchemes.{key}: steadyState category mismatch")
    return issues
