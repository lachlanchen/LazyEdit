#!/usr/bin/env node
const { spawnSync } = require('child_process');
const path = require('path');

const root = path.resolve(__dirname, '../..');
const command = process.argv[2] || 'help';
const args = process.argv.slice(3);

const scriptMap = {
  setup: 'setup',
  doctor: 'doctor',
  check: 'doctor',
  start: 'start',
  dev: 'dev',
  backend: 'backend',
  web: 'web',
  typecheck: 'typecheck',
};

function help() {
  console.log(`LazyEdit CLI

Usage:
  lazyedit setup [-- --update-envs]
  lazyedit doctor
  lazyedit start
  lazyedit backend
  lazyedit web
  lazyedit typecheck
`);
}

if (command === 'help' || command === '--help' || command === '-h') {
  help();
  process.exit(0);
}

const npmScript = scriptMap[command];
if (!npmScript) {
  console.error(`Unknown command: ${command}`);
  help();
  process.exit(2);
}

const npmArgs = ['run', npmScript];
if (args.length > 0) {
  npmArgs.push('--', ...args);
}

const result = spawnSync('npm', npmArgs, {
  cwd: root,
  stdio: 'inherit',
  shell: process.platform === 'win32',
});

process.exit(result.status ?? 1);
