#!/usr/bin/env node
// ABOUTME: CLI to generate baseline test summaries across repositories.
// ABOUTME: Writes summary reports for current AI-native workspace.

const path = require('path');

const {
  collectTestBaseline,
  writeBaselineReport
} = require('../../src/workspace_hub/automation/test-baseline-summary');

const parseArguments = (argv) => {
  const options = {
    includeRoot: true,
    skip: undefined,
    root: path.resolve(__dirname, '..', '..'),
    output: path.resolve(__dirname, '..', '..', 'reports', 'test-summary', 'baseline-summary.json')
  };

  for (const argument of argv) {
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

    if (argument.startsWith('--output=')) {
      options.output = path.resolve(argument.slice(9));
      continue;
    }
  }

  return options;
};

const printSummary = (report) => {
  const lines = [];
  lines.push(`Generated at: ${report.generatedAt}`);
  lines.push(`Total repositories: ${report.totalRepositories}`);
  lines.push(`Configured: ${report.statusCounts.configured}`);
  lines.push(`Missing: ${report.statusCounts.missing}`);
  lines.push(`Skipped: ${report.skippedRepositories.join(', ') || 'none'}`);
  lines.push('\nRepositories:');

  for (const repo of report.repositories) {
    lines.push(`- ${repo.name}: ${repo.status}`);
    if (repo.frameworks.length > 0) {
      lines.push(`  frameworks: ${repo.frameworks.join(', ')}`);
    }
    if (repo.commands.length > 0) {
      lines.push(`  commands: ${repo.commands.join(', ')}`);
    }
    if (repo.testDirectories.length > 0) {
      lines.push(`  test dirs: ${repo.testDirectories.join(', ')}`);
    }
  }

  process.stdout.write(`${lines.join('\n')}\n`);
};

const main = () => {
  const options = parseArguments(process.argv.slice(2));
  const summaries = collectTestBaseline(options.root, {
    includeRoot: options.includeRoot,
    skip: options.skip
  });

  const report = writeBaselineReport(options.output, summaries, summaries.skipped || []);
  printSummary(report);
  process.stdout.write(`\nReport saved to: ${options.output}\n`);
};

main();
