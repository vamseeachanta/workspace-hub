// ABOUTME: Tests ai-native infrastructure automation behaviour.
// ABOUTME: Ensures repository scaffolding follows AI-native spec expectations.

const fs = require('fs');
const os = require('os');
const path = require('path');

const {
  getRepositories,
  ensureInfrastructure
} = require('../../../../src/workspace_hub/automation/ai-native-infrastructure');

const createRepo = (rootDir, name) => {
  const repoPath = path.join(rootDir, name);
  fs.mkdirSync(repoPath, { recursive: true });
  fs.mkdirSync(path.join(repoPath, '.git'));
  return repoPath;
};

describe('ai-native infrastructure automation', () => {
  let tempRoot;

  beforeEach(() => {
    tempRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'ai-native-test-'));
    createRepo(tempRoot, 'repo-one');
    createRepo(tempRoot, 'digitalmodel');
    createRepo(tempRoot, 'assetutilities');
  });

  afterEach(() => {
    fs.rmSync(tempRoot, { recursive: true, force: true });
  });

  it('filters repositories according to default skip list', () => {
    const repositories = getRepositories(tempRoot, { includeRoot: false });
    const names = repositories.map((repo) => path.basename(repo));

    expect(names).toContain('repo-one');
    expect(names).not.toContain('digitalmodel');
    expect(names).not.toContain('assetutilities');
  });

  it('creates required ai-native structure for each repository', () => {
    const result = ensureInfrastructure(tempRoot, { includeRoot: false });

    expect(result.processed).toBe(1);
    expect(result.errors).toHaveLength(0);
    expect(result.created['repo-one']).toEqual(
      expect.arrayContaining([
        '.agent-os',
        path.join('.agent-os', 'product'),
        path.join('.agent-os', 'instructions'),
        path.join('specs', 'modules'),
        path.join('tests', 'unit'),
        path.join('tests', 'integration'),
        path.join('tests', 'fixtures'),
        path.join('docs', 'guides'),
        path.join('scripts', 'cli'),
        path.join('data', 'raw'),
        'config',
        'reports'
      ])
    );

    const repoPath = path.join(tempRoot, 'repo-one');

    const expectedPaths = [
      ['.agent-os'],
      ['.agent-os', 'product'],
      ['.agent-os', 'instructions'],
      ['specs'],
      ['specs', 'modules'],
      ['src'],
      ['tests'],
      ['tests', 'unit'],
      ['tests', 'integration'],
      ['tests', 'fixtures'],
      ['docs'],
      ['docs', 'guides'],
      ['docs', 'api'],
      ['docs', 'modules'],
      ['modules'],
      ['scripts'],
      ['scripts', 'bash'],
      ['scripts', 'powershell'],
      ['scripts', 'python'],
      ['scripts', 'cli'],
      ['data'],
      ['data', 'raw'],
      ['data', 'processed'],
      ['data', 'results'],
      ['config'],
      ['reports']
    ];

    for (const segments of expectedPaths) {
      const target = path.join(repoPath, ...segments);
      expect(fs.existsSync(target)).toBe(true);
      expect(fs.existsSync(path.join(target, '.gitkeep'))).toBe(true);
    }

    expect(fs.existsSync(path.join(tempRoot, 'digitalmodel', '.agent-os'))).toBe(false);
    expect(fs.existsSync(path.join(tempRoot, 'assetutilities', '.agent-os'))).toBe(false);
  });

  it('supports dry runs without file system mutations', () => {
    const dryRunResult = ensureInfrastructure(tempRoot, {
      includeRoot: false,
      dryRun: true
    });

    expect(dryRunResult.processed).toBe(1);
    expect(dryRunResult.created['repo-one']).toEqual(
      expect.arrayContaining(['.agent-os', path.join('specs', 'modules')])
    );

    const repoPath = path.join(tempRoot, 'repo-one');
    expect(fs.existsSync(path.join(repoPath, '.agent-os'))).toBe(false);
    expect(fs.existsSync(path.join(repoPath, 'specs'))).toBe(false);
    expect(fs.existsSync(path.join(repoPath, '.agent-os', '.gitkeep'))).toBe(false);
  });

  it('avoids adding placeholders when directory already has content', () => {
    const repoPath = path.join(tempRoot, 'repo-one');
    const guidesPath = path.join(repoPath, 'docs', 'guides');
    fs.mkdirSync(guidesPath, { recursive: true });
    fs.writeFileSync(path.join(guidesPath, 'guide.md'), '# Guide');

    const result = ensureInfrastructure(tempRoot, { includeRoot: false });

    expect(fs.existsSync(path.join(guidesPath, '.gitkeep'))).toBe(false);
    expect(result.created['repo-one']).not.toContain(path.join('docs', 'guides'));
  });
});
