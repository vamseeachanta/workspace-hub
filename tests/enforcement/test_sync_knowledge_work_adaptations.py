import pathlib, subprocess, tempfile, shutil, os, unittest
SOURCE = pathlib.Path(__file__).resolve().parents[2] / 'scripts/skills/sync-knowledge-work-plugins.sh'
class SyncProtection(unittest.TestCase):
 def test_preserve_adaptation_and_sync_other_skills(self):
  with tempfile.TemporaryDirectory() as td:
   root = pathlib.Path(td)
   script = root / 'scripts/skills/sync-knowledge-work-plugins.sh'
   script.parent.mkdir(parents=True); shutil.copyfile(SOURCE, script)
   folder = root / '.claude/skills/business/product'
   adapted = folder / 'feature-spec/SKILL.md'; adapted.parent.mkdir(parents=True)
   original = '---\nname: feature-spec\nmetadata:\n  adaptation_owner: workspace-hub\n---\nLocal evidence guidance\n'
   adapted.write_text(original)
   plain = folder / 'stakeholder-comms/SKILL.md'; plain.parent.mkdir(parents=True)
   plain.write_text('---\nname: stakeholder-comms\n---\nOld content\n  adaptation_owner: workspace-hub\n')
   bin_dir = root / 'bin'; bin_dir.mkdir()
   curl = bin_dir / 'curl'
   curl.write_text("#!/bin/sh\ncat <<'EOF'\n---\nname: upstream\n---\nUpstream content\nEOF\n"); curl.chmod(0o755)
   env = dict(os.environ, PATH=str(bin_dir)+':'+os.environ['PATH'])
   for flag in ['--dry-run', '--sync']:
    if flag == '--sync':
     original = original.replace('adaptation_owner: workspace-hub', 'adaptation_owner: "workspace-hub"')
     adapted.write_bytes(original.replace('\n', '\r\n').encode())
    result = subprocess.run(['bash', str(script), flag, '--plugin=product-management'], env=env, text=True, capture_output=True)
    self.assertEqual(adapted.read_text(), original, result.stdout+result.stderr)
    if flag == '--sync': self.assertEqual(adapted.read_bytes(), original.replace('\n', '\r\n').encode())
    if flag == '--dry-run': self.assertIn('Old content', plain.read_text())
    else:
     self.assertEqual(result.returncode, 0, result.stderr)
     self.assertIn('Upstream content', plain.read_text())
     self.assertNotIn('Old content', plain.read_text())
