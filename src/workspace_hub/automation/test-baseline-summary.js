// ABOUTME: Generates baseline test summaries across repositories.
// ABOUTME: Detects test directories, frameworks, and execution commands.

const fs = require('fs');
const path = require('path');

const {
  getRepositories
} = require('./ai-native-infrastructure');

const NODE_TEST_DEPENDENCIES = ['jest', 'mocha', 'vitest', 'ava', 'tap', 'cypress', 'playwright'];
const NODE_TEST_SCRIPTS = ['test', 'test:unit', 'test:integration', 'test:e2e', 'coverage'];

const candidateTestDirectories = ['tests', 'test', 'spec', '__tests__'];

const readFileSafe = (filePath) => {
  try {
    return fs.readFileSync(filePath, 'utf8');
  } catch (error) {
    return null;
  }
};

const readJsonSafe = (filePath) => {
  try {
    const raw = fs.readFileSync(filePath, 'utf8');
    return JSON.parse(raw);
  } catch (error) {
    return null;
  }
};

const collectChildDirectories = (absolutePath, relativePath) => {
  const entries = [];
  try {
    const children = fs.readdirSync(absolutePath, { withFileTypes: true });
    for (const child of children) {
      if (child.isDirectory()) {
        if (child.name === '__pycache__' || child.name.startsWith('.')) {
          continue;
        }
        const childRelative = path.join(relativePath, child.name);
        entries.push(childRelative);
      }
    }
  } catch (error) {
    // ignore traversal errors
  }
  return entries;
};

const findTestDirectories = (repoPath) => {
  const discovered = [];

  for (const candidate of candidateTestDirectories) {
    const absolute = path.join(repoPath, candidate);
    if (fs.existsSync(absolute) && fs.statSync(absolute).isDirectory()) {
      discovered.push(candidate);
      const children = collectChildDirectories(absolute, candidate);
      discovered.push(...children);
    }
  }

  return Array.from(new Set(discovered));
};

const detectNodeFrameworks = (packageJson) => {
  if (!packageJson) {
    return [];
  }

  const frameworks = new Set();
  const dependencySections = ['dependencies', 'devDependencies', 'optionalDependencies'];

  for (const section of dependencySections) {
    const deps = packageJson[section];
    if (!deps) {
      continue;
    }

    for (const framework of NODE_TEST_DEPENDENCIES) {
      if (Object.prototype.hasOwnProperty.call(deps, framework)) {
        frameworks.add(framework);
      }
    }
  }

  const scripts = packageJson.scripts || {};
  for (const [name, command] of Object.entries(scripts)) {
    if (command.includes('jest')) {
      frameworks.add('jest');
    }
    if (command.includes('mocha')) {
      frameworks.add('mocha');
    }
    if (command.includes('vitest')) {
      frameworks.add('vitest');
    }
    if (command.includes('playwright')) {
      frameworks.add('playwright');
    }
    if (command.includes('cypress')) {
      frameworks.add('cypress');
    }
  }

  return Array.from(frameworks);
};

const detectNodeCommands = (packageJson) => {
  if (!packageJson || !packageJson.scripts) {
    return [];
  }

  const commands = new Set();

  for (const [name] of Object.entries(packageJson.scripts)) {
    if (name === 'test') {
      commands.add('npm test');
    }
    if (NODE_TEST_SCRIPTS.includes(name)) {
      commands.add(`npm run ${name}`);
    }
  }

  return Array.from(commands);
};

const detectPytest = (repoPath) => {
  const targets = ['pyproject.toml', 'pytest.ini', 'tox.ini', 'requirements.txt'];
  for (const fileName of targets) {
    const content = readFileSafe(path.join(repoPath, fileName));
    if (!content) {
      continue;
    }
    if (content.toLowerCase().includes('pytest')) {
      return true;
    }
  }
  return false;
};

const summarizeRepository = (repoPath) => {
  const name = path.basename(repoPath);

  const testDirectories = findTestDirectories(repoPath);
  const packageJson = readJsonSafe(path.join(repoPath, 'package.json'));
  const frameworks = new Set();
  const commands = new Set();

  detectNodeFrameworks(packageJson).forEach((framework) => frameworks.add(framework));
  detectNodeCommands(packageJson).forEach((command) => commands.add(command));

  if (detectPytest(repoPath)) {
    frameworks.add('pytest');
    commands.add('pytest');
  }

  const status = frameworks.size > 0 || commands.size > 0 || testDirectories.length > 0
    ? 'configured'
    : 'missing';

  return {
    name,
    path: repoPath,
    testDirectories,
    frameworks: Array.from(frameworks).sort(),
    commands: Array.from(commands).sort(),
    status
  };
};

const collectTestBaseline = (rootPath, options = {}) => {
  const repositories = getRepositories(rootPath, options);
  const summaries = repositories.map((repoPath) => summarizeRepository(repoPath));
  summaries.skipped = repositories.skipped;
  return summaries;
};

const buildReport = (summaries, skipped = []) => {
  const totals = summaries.reduce(
    (acc, summary) => {
      acc.total += 1;
      acc.status[summary.status] = (acc.status[summary.status] || 0) + 1;
      return acc;
    },
    { total: 0, status: { configured: 0, missing: 0 } }
  );

  return {
    generatedAt: new Date().toISOString(),
    totalRepositories: totals.total,
    statusCounts: totals.status,
    skippedRepositories: skipped,
    repositories: summaries
  };
};

const ensureDirectoryExists = (directory) => {
  if (!fs.existsSync(directory)) {
    fs.mkdirSync(directory, { recursive: true });
  }
};

const writeBaselineReport = (outputPath, summaries, skipped = []) => {
  const directory = path.dirname(outputPath);
  ensureDirectoryExists(directory);
  const report = buildReport(summaries, skipped);
  fs.writeFileSync(outputPath, `${JSON.stringify(report, null, 2)}\n`, 'utf8');
  return report;
};

module.exports = {
  collectTestBaseline,
  summarizeRepository,
  writeBaselineReport,
  buildReport
};
