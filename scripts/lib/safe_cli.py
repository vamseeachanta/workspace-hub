"""Non-reflecting argparse failures (Python 3.11 argparse, error())."""
import argparse
import sys


class SafeArgumentParser(argparse.ArgumentParser):
    """Keep usage and exit status while withholding rejected argument values.

    Program names, usage, help, defaults and argument definitions must be trusted
    static application text. Application diagnostics still need their own policy.
    """

    def __init__(self, *args, **kwargs):
        # Avoid argparse deriving prog from a caller-controlled executable path.
        if not args and 'prog' not in kwargs:
            kwargs['prog'] = 'command'
        kwargs['exit_on_error'] = True
        super().__init__(*args, **kwargs)

    def error(self, message):
        self.print_usage(sys.stderr)
        # Python 3.11 argparse: invalid arguments conventionally exit with 2.
        self.exit(2, f'{self.prog}: error: invalid arguments\n')
