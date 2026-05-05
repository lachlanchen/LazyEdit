# LazyEdit npmjs Publish and Install Plan

## Scope
- Publish the LazyEdit CLI/package `@lazyingart/lazyedit` from this repo.
- Ensure users can run `npm install`/`npx lazyedit` and then configure Python environments via commands in this repo.
- Preserve existing deployment behavior (`LAZYEDIT_PORT=18787`, `EXPO_PUBLIC_API_URL` default to backend, tmux/session flow, `python` from conda).

## 1) Current Publish Readiness (already present)
- `package.json` already exposes CLI entrypoint `lazyedit` via `scripts/npm/lazyedit-cli.js`.
- npm scripts already cover setup/start/doctor/startup:
  - `npm run setup` -> `scripts/npm/setup.sh`
  - `npm run doctor` -> `scripts/npm/doctor.sh`
  - `npm run start` -> `scripts/npm/start.sh`
  - `npm run backend` -> `scripts/npm/backend.sh`
  - `npm run web` -> `scripts/npm/web.sh`
- `npm run setup` already installs:
  - Expo app deps (`app/`)
  - `lazyedit`, `whisper`, `caption` conda envs (from environment files)
  - runtime env defaults into `.env` (model/provider defaults included)
- Current blocker for direct publish: root `package.json` has `"private": true`.

## 2) Changes required before `npm publish` (repo-side plan)
1. `package.json` adjustments
   - set `"private": false`.
   - set package metadata for scoped publish:
     - `"name": "@lazyingart/lazyedit"`
     - `"publishConfig": {"access": "restricted"}`
   - add `license` field if missing (Apache-2.0 recommended to match repo).
   - optionally set `"files"` to only include:
     - scripts
     - package.json
     - README/docs refs
     - start/setup wrappers used at runtime
   - keep `bin` unchanged so `npx lazyedit` works.

2. Add publish hygiene files
   - add `.npmignore` (or `package.json.files`) to exclude:
     - `DATA/`, `translation_logs/`, `temp/`, `words.db`, `lazyedit.db`,
     - large media and generated subtitle/metadata artifacts,
     - local secrets and install artifacts.
   - do not include runtime machine state files (`lazyedit.db`, `words.db`) in package.

3. Add explicit install helper docs in package docs
   - document required host prerequisites:
     - Node 20+
     - conda (`lazyedit`, `whisper`, `caption` env names expected)
     - ffmpeg, tmux, HandBrakeCLI
   - document required environment variables for deployment:
     - `LAZYEDIT_PORT`, `EXPO_PUBLIC_API_URL`, `LAZYEDIT_DIR`, `CONDA_ENV`.

4. Add/verify `scripts/npm` command mapping for user-facing setup flow
   - `lazyedit setup [options]` remains the documented bootstrap command.
   - include a short `--skip-*` story so users with partial installs can recover.
   - include `lazyedit doctor` in install validation docs.

## 3) Publish workflow on npmjs
1. Pre-flight
   - Ensure clean tree and committed changes.
   - `npm ci` and `npm run setup`/`npm run doctor` pass on a clean machine.
2. Versioning
   - `npm version patch` / `npm version minor` as appropriate.
3. Authenticate
   - `npm login` with maintainer account for `@lazyingart`.
4. Publish
   - `npm publish --access restricted` (scoped package).
5. Post-publish checks
   - `npm view @lazyingart/lazyedit version`
   - `npm view @lazyingart/lazyedit dist-tags`

## 4) User installation and Python env bootstrap design
### What is fully possible with npm
- Yes, npm can install the package and expose the `lazyedit` CLI command.
- Yes, npm can run shell scripts (`lazyedit setup`) that call conda and pip.
- Yes, you can configure `.env` values by script from another file source.

### What should not be auto-farmed by npm `postinstall` (recommended)
- Running full conda/pip bootstrap automatically on `npm install`.
- Risks:
  - long-running, GPU-dependent operations during package install,
  - cross-platform differences (conda availability and binary download reliability),
  - sudo-required system package operations from package scripts.
- Recommended default:
  - `npm install @lazyingart/lazyedit`
  - `lazyedit setup` (manual and explicit, supports re-run).

### Planned explicit bootstrap commands for users
1. `npm install -g @lazyingart/lazyedit` (or local install in a tool node_modules)
2. `cd <project>`
3. `lazyedit setup` (or `npx @lazyingart/lazyedit setup`)
4. `lazyedit doctor`
5. `lazyedit start` or `lazyedit backend` / `lazyedit web`

## 5) Importing AAPS `.env` keys into LazyEdit `.env`
User requirement: copy keys from `~/ProjectsLFS/AAPS/.env` into LazyEdit `.env`.

- This can be done safely with key merge logic (update existing keys, append missing keys, skip blanks/comments):
  - Use `LAZYEDIT_ENV_SOURCE` env var to point to source file.
  - Use a dedicated command pattern:
    - `LAZYEDIT_ENV_SOURCE=~/ProjectsLFS/AAPS/.env lazyedit setup --with-env` (proposed option)
  - Merge behavior:
    - keep existing local comments and spacing,
    - replace values for same keys,
    - append new keys.
- Suggested precedence for merged values:
  1) explicit CLI/env args
  2) source `.env` file
  3) defaults in `scripts/npm/setup.sh` / `.env.example`

## 6) Python environment policy to include in the plan
- Keep conda-based install model, as repo already relies on:
  - `lazyedit` env for backend,
  - `whisper` env for ASR,
  - `caption` env for keyframe captioning.
- Include in docs that full ML stack installation is optional by command flags:
  - `--skip-whisper` / `--skip-caption`
  - for lightweight installs.
- Include recovery commands:
  - `npm run setup -- --update-envs`
  - `conda run -n whisper python -m pip ...` and `conda env update -n ...`.

## 7) Validation matrix (must pass before release)
- `npm pack --dry-run` should only include expected files.
- `npm run setup` completes on clean machine.
- `lazyedit --help` lists setup/doctor/start commands.
- `lazyedit setup` writes `.env` and creates envs or reports actionable errors.
- `lazyedit doctor` succeeds after setup.
- `lazyedit backend` starts on port `18787` with valid `config.py` + `.env`.
- Expo web can start with `EXPO_PUBLIC_API_URL` from `.env` or host override.

## 8) Deployment/rollback notes
- Release candidate should be published as pre-release tag first (`npm publish --tag next`), smoke test on one host, then promote with `npm dist-tag add`.
- For rollback:
  - `npm unpublish` only works short-window; normal path is `npm deprecate @lazyingart/lazyedit@<version>`.
  - Keep one pinned good version and pin CI/ansible scripts to that version if needed.

## 9) Recommended immediate actions (in order)
1. Flip publish fields in `package.json` and add `.npmignore`.
2. Add explicit `lazyedit setup --with-env` / env source merge documentation.
3. Add `references/NPMJS_PUBLISH_CHECKLIST.md` + short release PR checklist.
4. Run one local dry run (`npm pack --dry-run`) and then `npm publish --access restricted` from CI/release box.
