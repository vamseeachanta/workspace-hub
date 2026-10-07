"""Guard the owner-directed retirement without weakening secret checks."""
from pathlib import Path
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]


class RetirementTests(unittest.TestCase):
    def test_precommit_preserves_secrets_without_identifier_gates(self):
        config = yaml.safe_load((ROOT / '.pre-commit-config.yaml').read_text())
        hooks = [h for repo in config['repos'] for h in repo['hooks']]
        ids = {h['id'] for h in hooks}
        self.assertIn('gitleaks', ids)
        self.assertNotIn('legal-client-pii', ids)
        self.assertNotIn('legal-client-pii-commit-msg', ids)
        self.assertNotIn('client-identifier-gate', ids)
        self.assertNotIn('email-fixture-redaction-check', ids)

    def test_ci_does_not_invoke_retired_scanners(self):
        for path in (ROOT / '.github/workflows').glob('*.yml'):
            config = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
            for job in config.get('jobs', {}).values():
                for step in job.get('steps', []):
                    command = step.get('run', '')
                    with self.subTest(path=path.name):
                        self.assertNotIn('legal-sanity-scan.sh', command)
                        self.assertNotIn('scripts/legal/check-client-pii.py', command)
                        self.assertNotIn('scripts/legal/check_identifiers.py', command)

    def test_scanner_is_removed_not_replaced_with_fake_pass(self):
        self.assertFalse((ROOT / 'scripts/legal/legal-sanity-scan.sh').exists())

    def test_generators_do_not_reinstall_retired_gate(self):
        paths = ['scripts/skills/fix-coverage-gaps.py',
                 'scripts/skills/audit-prose-operations.py',
                 'scripts/memory/bridge-hermes-claude.sh',
                 'scripts/generate-resource-index.sh',
                 'scripts/email/templates/cre-listing.yaml']
        for name in paths:
            with self.subTest(path=name):
                self.assertNotIn('scripts/legal/legal-sanity-scan.sh',
                                 (ROOT / name).read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
