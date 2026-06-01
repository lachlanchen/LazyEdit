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
  lazyedit publish-video --video /path/to/video.mp4 --platforms shipinhao,youtube
  npm run publish-video -- --video /path/to/video.mp4 --platforms shipinhao,youtube
`);
}

if (command === 'help' || command === '--help' || command === '-h') {
  help();
  process.exit(0);
}

const npmScript = scriptMap[command];
if (command === 'publish-video') {
  const python = process.env.LAZYEDIT_PYTHON || 'python';
  const passArgs = args[0] === '--' ? args.slice(1) : args;
  const result = spawnSync(python, ['scripts/lazyedit_publish.py', ...passArgs], {
    cwd: root,
    stdio: 'inherit',
    shell: process.platform === 'win32',
  });
  process.exit(result.status ?? 1);
}

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
