// ABOUTME: Provides utilities to enforce AI-native repository scaffolding.
// ABOUTME: Creates standardized directories across multiple repositories.

const fs = require('fs');
const path = require('path');

const DEFAULT_SKIP = new Set(['digitalmodel', 'assetutilities']);

const REQUIRED_STRUCTURE = [
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

const buildSkipSet = (skip) => {
  if (!skip) {
    return new Set(DEFAULT_SKIP);
  }

  if (skip instanceof Set) {
    return new Set([...DEFAULT_SKIP, ...skip]);
  }

  if (Array.isArray(skip)) {
    return new Set([...DEFAULT_SKIP, ...skip]);
  }

  return new Set(DEFAULT_SKIP);
};

const hasGitDirectory = (targetPath) => {
  try {
    return fs.statSync(path.join(targetPath, '.git')).isDirectory();
  } catch (error) {
    return false;
  }
};

const listRepositoryDirectories = (rootPath) => {
  try {
    return fs
      .readdirSync(rootPath, { withFileTypes: true })
      .filter((entry) => entry.isDirectory())
      .map((entry) => entry.name);
  } catch (error) {
    return [];
  }
};

const getRepositories = (rootPath, options = {}) => {
  const { includeRoot = true, skip } = options;
  const skipSet = buildSkipSet(skip);
  const repositories = [];
  const skipped = [];

  if (includeRoot) {
    const rootName = path.basename(rootPath);
    if (!skipSet.has(rootName) && hasGitDirectory(rootPath)) {
      repositories.push(rootPath);
    } else if (skipSet.has(rootName)) {
      skipped.push(rootName);
    }
  }

  for (const name of listRepositoryDirectories(rootPath)) {
    const fullPath = path.join(rootPath, name);

    if (skipSet.has(name)) {
      if (hasGitDirectory(fullPath)) {
        skipped.push(name);
      }
      continue;
    }

    if (hasGitDirectory(fullPath)) {
      repositories.push(fullPath);
    }
  }

  repositories.skipped = skipped;
  return repositories;
};

const directoryIsEmpty = (target) => {
  try {
    const entries = fs.readdirSync(target).filter((entry) => entry !== '.gitkeep');
    return entries.length === 0;
  } catch (error) {
    return true;
  }
};

const ensureDirectory = (repoPath, segments, dryRun) => {
  const target = path.join(repoPath, ...segments);
  const relative = path.join(...segments);
  const exists = fs.existsSync(target);
  let createdDirectory = false;

  if (!exists) {
    if (!dryRun) {
      fs.mkdirSync(target, { recursive: true });
    }
    createdDirectory = true;
  }

  const placeholderPath = path.join(target, '.gitkeep');
  const shouldHavePlaceholder = createdDirectory || directoryIsEmpty(target);
  let placeholderAdded = false;

  if (dryRun) {
    if (shouldHavePlaceholder && !fs.existsSync(placeholderPath)) {
      placeholderAdded = true;
    }
  } else if (shouldHavePlaceholder && !fs.existsSync(placeholderPath)) {
    fs.writeFileSync(placeholderPath, '');
    placeholderAdded = true;
  }

  return {
    created: createdDirectory || placeholderAdded,
    relative
  };
};

const ensureRepoStructure = (repoPath, options = {}) => {
  const { dryRun = false } = options;
  const created = [];

  for (const segments of REQUIRED_STRUCTURE) {
    const { created: changed, relative } = ensureDirectory(repoPath, segments, dryRun);
    if (changed) {
      created.push(relative);
    }
  }

  return created;
};

const ensureInfrastructure = (rootPath, options = {}) => {
  const { dryRun = false, includeRoot = true, skip } = options;
  const summary = {
    processed: 0,
    created: {},
    skipped: [],
    errors: []
  };

  const repositories = getRepositories(rootPath, { includeRoot, skip });
  summary.skipped = repositories.skipped;

  for (const repoPath of repositories) {
    const repoName = path.basename(repoPath);

    try {
      const created = ensureRepoStructure(repoPath, { dryRun });
      summary.created[repoName] = created;
      summary.processed += 1;
    } catch (error) {
      summary.errors.push({ repo: repoName, message: error.message });
    }
  }

  return summary;
};

module.exports = {
  DEFAULT_SKIP,
  REQUIRED_STRUCTURE,
  getRepositories,
  ensureRepoStructure,
  ensureInfrastructure
};
