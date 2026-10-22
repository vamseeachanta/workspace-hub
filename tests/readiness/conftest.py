"""Keep existing collector regression tests independent of installed software."""
import subprocess
from pathlib import Path

import pytest
from collector_sandbox import sandbox_env
from test_reconcile_inputs import fixture as reconciliation_fixture

fixture = reconciliation_fixture


@pytest.fixture(autouse=True)
def isolate_collector_processes(request, tmp_path, monkeypatch):
    modules = {'test_collect_equality', 'test_collect_equality_ps1_schema',
               'test_equality_tree_cleanliness', 'test_publish_equality'}
    if request.module.__name__.split('.')[-1] not in modules:
        return
    original = subprocess.Popen

    def controlled(args, *positional, **kwargs):
        text = ' '.join(str(x) for x in args) if isinstance(args, (list, tuple)) else str(args)
        if any(name in text for name in ('collect-equality.sh', 'probe-solvers.sh',
                                         'publish-equality.sh', 'equality-matrix-cron.sh',
                                         'curate-session-memory.sh')):
            kwargs['env'] = sandbox_env(tmp_path, kwargs.get('env'))
            if 'publish-equality.sh' in text and '--repo' in args:
                root = Path(args[args.index('--repo') + 1])
                kwargs['env'].setdefault('EQ_STATE_DIR', str(root / '.claude/state'))
        return original(args, *positional, **kwargs)

    monkeypatch.setattr(subprocess, 'Popen', controlled)
