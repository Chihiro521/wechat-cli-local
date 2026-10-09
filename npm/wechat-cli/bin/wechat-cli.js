#!/usr/bin/env node
'use strict';

const fs = require('node:fs');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

const platform = `${process.platform}-${process.arch}`;
if (platform !== 'win32-x64') {
  console.error(`wechat-cli-local supports Windows x64; current platform: ${platform}.`);
  process.exit(1);
}

let executable;
try {
  const manifest = require.resolve('wechat-cli-local-win32-x64/package.json');
  executable = path.join(path.dirname(manifest), 'bin', 'wechat-cli.exe');
} catch {
  console.error('The Windows binary package is missing. Reinstall with: npm install -g wechat-cli-local --include=optional');
  process.exit(1);
}
if (!fs.existsSync(executable)) {
  console.error('The Windows executable is missing. Reinstall wechat-cli-local.');
  process.exit(1);
}

const result = spawnSync(executable, process.argv.slice(2), { stdio: 'inherit' });
if (result.error) {
  console.error(`Unable to start wechat-cli: ${result.error.message}`);
  process.exit(1);
}
process.exit(result.status ?? 1);
