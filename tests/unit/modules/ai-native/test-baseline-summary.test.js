// ABOUTME: Tests baseline test summary collection across repositories.
// ABOUTME: Validates detection of test directories, frameworks, and commands.

const fs = require('fs');
const os = require('os');
const path = require('path');

const {
  collectTestBaseline,
  summarizeRepository
} = require('../../../../src/workspace_hub/automation/test-baseline-summary');

const createRepo = (rootDir, name) => {
  const repoPath = path.join(rootDir, name);
  fs.mkdirSync(repoPath, { recursive: true });
  fs.mkdirSync(path.join(repoPath, '.git'));
  return repoPath;
};

describe('test baseline summary automation', () => {
  let tempRoot;

  beforeEach(() => {
    tempRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'test-baseline-'));
  });

  afterEach(() => {
    fs.rmSync(tempRoot, { recursive: true, force: true });
  });

  it('detects tests directory and npm test commands', () => {
    const repoPath = createRepo(tempRoot, 'js-repo');
    fs.mkdirSync(path.join(repoPath, 'tests/unit'), { recursive: true });

    const packageJson = {
      name: 'js-repo',
      scripts: {
        test: 'jest',
        'test:unit': 'jest tests/unit'
      },
      devDependencies: {
        jest: '^29.0.0'
      }
    };
    fs.writeFileSync(path.join(repoPath, 'package.json'), JSON.stringify(packageJson, null, 2));

    const summary = summarizeRepository(repoPath);

    expect(summary.testDirectories).toEqual(expect.arrayContaining(['tests', path.join('tests', 'unit')]));
    expect(summary.frameworks).toContain('jest');
    expect(summary.commands).toEqual(expect.arrayContaining(['npm test', 'npm run test:unit']));
    expect(summary.status).toBe('configured');
  });

  it('detects pytest usage from pyproject and marks repo configured', () => {
    const repoPath = createRepo(tempRoot, 'py-repo');
    fs.mkdirSync(path.join(repoPath, 'tests'), { recursive: true });

    const pyproject = `
[tool.pytest.ini_options]
addopts = "-ra"
`; 
    fs.writeFileSync(path.join(repoPath, 'pyproject.toml'), pyproject.trim());

    const summary = summarizeRepository(repoPath);

    expect(summary.frameworks).toContain('pytest');
    expect(summary.commands).toEqual(expect.arrayContaining(['pytest']));
    expect(summary.status).toBe('configured');
  });

  it('marks repository missing when no tests or configs exist', () => {
    const repoPath = createRepo(tempRoot, 'empty-repo');

    const summary = summarizeRepository(repoPath);

    expect(summary.testDirectories).toHaveLength(0);
    expect(summary.frameworks).toHaveLength(0);
    expect(summary.status).toBe('missing');
  });

  it('collects baseline for all repositories under root', () => {
    createRepo(tempRoot, 'first');
    createRepo(tempRoot, 'second');
    fs.mkdirSync(path.join(tempRoot, 'first', 'tests'), { recursive: true });

    const baseline = collectTestBaseline(tempRoot, { includeRoot: false });

    expect(baseline.length).toBe(2);
    const names = baseline.map((entry) => entry.name).sort();
    expect(names).toEqual(['first', 'second']);
  });
});
