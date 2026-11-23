"""Domain decision extracted from domain-matrix.yml; contract: issue #4227.

Exit codes follow the original workflow: zero passes, one fails. Scope is
informational. A positive matrix size is required by the new fail-closed rule.
"""

import argparse


def decide(discover: str, test_domain: str, scope: str, matrix_size: int) -> tuple[int, str]:
    """Require successful discovery, successful tests and a nonempty matrix."""
    if discover != "success":
        return 1, "domain discovery failed"
    if test_domain != "success":
        return 1, "one or more domain jobs failed — see the Domain * jobs"
    if matrix_size <= 0:
        return 1, f"empty or invalid domain matrix (scope={scope!r})"
    return 0, "All domains green ✅"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("discover")
    parser.add_argument("test_domain")
    parser.add_argument("scope")
    parser.add_argument("matrix_size", type=int)
    parser.add_argument("--advisory", action="store_true", help="Keep the original job-result gate.")
    args = parser.parse_args()
    code, message = decide(args.discover, args.test_domain, args.scope, args.matrix_size)
    print(f"discover:    {args.discover}")
    print(f"test-domain: {args.test_domain}")
    print(f"scope:       {args.scope}")
    print(f"matrix size: {args.matrix_size}")
    print(("::warning::" if args.advisory else "::error::") + message if code else message)
    if args.advisory:
        return int(args.discover != "success" or args.test_domain != "success")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
