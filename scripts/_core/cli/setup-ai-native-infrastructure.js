#!/usr/bin/env node
// ABOUTME: CLI entrypoint for AI-native infrastructure scaffolding.
// ABOUTME: Applies standardized structure across workspace repositories.

const path = require('path');
const {
  ensureInfrastructure
} = require('../../src/workspace_hub/automation/ai-native-infrastructure');

const parseArguments = (argv) => {
  const options = {
    dryRun: false,
    includeRoot: true,
    skip: undefined,
    root: path.resolve(__dirname, '..', '..')
  };

  for (const argument of argv) {
    if (argument === '--dry-run') {
      options.dryRun = true;
      continue;
    }

    if (argument === '--no-root') {
      options.includeRoot = false;
      continue;
    }

    if (argument.startsWith('--root=')) {
      options.root = path.resolve(argument.slice(7));
      continue;
    }

    if (argument.startsWith('--skip=')) {
      const values = argument.slice(7);
      options.skip = values
        .split(',')
        .map((value) => value.trim())
        .filter(Boolean);
      continue;
    }
  }

  return options;
};

const printSummary = (summary) => {
  const lines = [];
  lines.push(`Processed repositories: ${summary.processed}`);
  lines.push(`Skipped repositories: ${summary.skipped.join(', ') || 'none'}`);

  const createdEntries = Object.entries(summary.created);
  for (const [repo, pathsCreated] of createdEntries) {
    lines.push(`\n${repo}:`);
    if (pathsCreated.length === 0) {
      lines.push('  ✓ already compliant');
      continue;
    }

    for (const relativePath of pathsCreated) {
      lines.push(`  + ${relativePath}`);
    }
  }

  if (summary.errors.length > 0) {
    lines.push('\nErrors:');
    for (const error of summary.errors) {
      lines.push(`  - ${error.repo}: ${error.message}`);
    }
  }

  process.stdout.write(`${lines.join('\n')}\n`);
};

const main = () => {
  const options = parseArguments(process.argv.slice(2));
  const { root, dryRun, includeRoot, skip } = options;

  const summary = ensureInfrastructure(root, { dryRun, includeRoot, skip });
  printSummary(summary);

  if (summary.errors.length > 0) {
    process.exitCode = 1;
  }
};

main();
