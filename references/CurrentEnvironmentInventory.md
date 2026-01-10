# Current Environment Inventory

This document captures the tooling, platforms, and automation already in place for the **AISecretary** project. Everything here is portable—other teams can copy these settings verbatim to bootstrap their own Android/iOS/PWA stacks with minimal changes (swap repo paths, domains, and credentials as needed).

## Local Platforms
- **Ubuntu dev machine** (`/home/lachlan/ProjectsLFS/EmailAssistant`): runs the Tornado backend (`python -m aisecondary.app`) inside the `ai` conda env and the Expo web preview.
- **Android emulator (Ubuntu)**: Android Studio is installed with an API 33+ Virtual Device. Verified that `npx expo start --android` launches the emulator.
- **macOS workstation** (`~/Local/AISecretary`): hosts the iOS simulator, Node.js toolchain, and Expo client for native testing.
- **iOS simulator (macOS)**: Xcode + CocoaPods configured; `npx expo start --ios` launches the iPhone 16 Pro simulator successfully.

## Remote Access & Sync
- **SSH access**: Ubuntu machine can reach the Mac via `ssh lachlanchen@192.168.1.122`, enabling remote script execution (e.g., kicking off Expo from Ubuntu).
- **Git remote**: Repository pushed to `git@github.com:lachlanchen/AISecretary.git`; both machines track the `main` branch.
- **Shared environment file**: Secrets and connection strings live in `.env`, providing the `DATABASE_AI_URL`, public URLs, and iCloud credentials.
- **Postgres**: Local instance with:
  - Database: `aisecondary_db`
  - Owner/user: `lachlan`
  - Password: `the11thfzpe.g.`
  - Superuser (`postgres`) password rotated to `the11th3ddaq`
  - DSN exposed via `DATABASE_AI_URL=postgresql+asyncpg://lachlan:the11thfzpe.g.@localhost:5432/aisecondary_db`
  - Additional `echomind_db` already granted to `lachlan` for related tooling.
  - Created/managed with:
    ```bash
    sudo -u postgres psql -c "create database aisecondary_db owner lachlan;"
    sudo -u postgres psql -c "grant all privileges on database aisecondary_db to lachlan;"
    sudo -u postgres psql
    ALTER USER postgres WITH PASSWORD 'the11th3ddaq';
    ALTER USER lachlan WITH PASSWORD 'the11thfzpe.g.';
    GRANT ALL PRIVILEGES ON DATABASE echomind_db TO lachlan;
    \q
    ```

## Automation Scripts
- `scripts/dev-session.sh` (Ubuntu): spins up a tmux session with backend, Expo web client, and paired ngrok tunnels. Commands are preloaded but can be left idle if you only need the panes.
- `scripts/run-mac-simulator.sh` (macOS): pulls the latest code, switches to the desired Node.js version via `nvm`, refreshes Expo dependencies (`expo-font`, `typescript`), resets Watchman, and launches `npx expo start --clear --ios` in tmux (`aisecretary-metro`). Designed to be called locally or over SSH.
- `scripts/load-env.sh`: sources `.env` and exposes shared variables to other scripts.

## Networking & Domains
- ngrok credentials allow binding multiple custom subdomains (e.g., `ai.lazying.art`, `ai-backend.lazying.art`). You can reuse these or register new domains as needed; the tooling accepts any hostname.
- Local ports are configurable. Backend defaults to `8787`, Expo defaults to `8081/8091`, but the scripts and Expo CLI support overriding with `--port` (frontend) or `PORT` env (backend). Adjust `EXPO_PUBLIC_API_URL` accordingly.
- To avoid clashes with other services, feel free to choose higher, less common ports (e.g., backend `8887`, web preview `8181`, mobile tunnel `8191`). Update `.env`, `dev-session.sh`, and `run-mac-simulator.sh` if you adopt new values.
- Spinning up another project? Allocate fresh values—new Postgres database/user, distinct ngrok domains, and unique port numbers—so services stay isolated.
- SSH access from Ubuntu to macOS (`ssh lachlanchen@192.168.1.122`) enables remote management of Expo and simulator processes.

## Backend & Frontend Status
- **Backend**: Tornado server listens on port `8787` by default; CORS is open (`*`) for Expo/web clients. Logging includes structured JSON lines for easier monitoring.
- **Frontend** (`app/`): Expo Router project, styled with light theme and bottom tab navigation (`Agenda`, `Insights`, `Assistant`, `Settings`) plus authentication flows (login, create account, forgot password). Supports Android, iOS, and web (PWA) targets.
- **ngrok domains**: Reserved subdomains `ai.lazying.art` (frontend) and `ai-backend.lazying.art` (backend) configured via ACL-bound credentials for quick tunneling.

## Known Port Usage
- Expo defaults to port `8081`; use the macOS helper `killport <port>` (add to `~/.zshrc`) to free the port when older Metro processes persist.
- Backend runs on `8787`; adjust `EXPO_PUBLIC_API_URL` when tunneling or using LAN IPs so mobile clients can reach the API.

## Setup Commands Reference

### Ubuntu (Android + backend toolchain)
- System packages & SDK deps  
  ```bash
  sudo apt update
  sudo apt install -y openjdk-17-jdk build-essential libglu1-mesa adb
  ```
- Android Studio installation & emulator provisioning (Device Manager → create Pixel device, API 33+).
- Environment for SDK tools (in `~/.bashrc`):  
  ```bash
  export ANDROID_SDK_ROOT=$HOME/Android/Sdk
  export ANDROID_HOME=$ANDROID_SDK_ROOT
  export PATH=$PATH:$ANDROID_SDK_ROOT/emulator:$ANDROID_SDK_ROOT/platform-tools:$ANDROID_SDK_ROOT/cmdline-tools/latest/bin
  ```
- Conda-managed Python backend:  
  ```bash
  conda activate ai
  python -m aisecondary.app
  ```
- Expo CLI usage (web/Android):  
  ```bash
  EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
  npx expo start --android
  ```
- ngrok tunnels (sample):  
  ```bash
  ngrok http --url=ai-backend.lazying.art 8787
  ngrok http --url=ai.lazying.art 8091
  ```

### macOS (iOS simulator)
- Node via nvm & Expo dependencies (inside `~/Local/AISecretary/app`):  
  ```bash
  nvm install 20
  nvm use 20
  npm install
  npx expo install expo-font
  npx expo install typescript@~5.3.3
  ```
- Watchman & diagnostics:  
  ```bash
  brew install watchman
  watchman watch-del-all
  watchman shutdown-server
  ```
- Expo iOS launch & troubleshooting:  
  ```bash
  npx expo start --clear --ios
  lsof -nP -iTCP:8081 -sTCP:LISTEN  # identify Metro processes
  killport() { ... }               # helper function in ~/.zshrc
  ```
- Homebrew installs used during setup: `brew install node`, `brew install watchman`.
- Xcode & simulators configured through App Store + `xcode-select --install`.

## Node/Expo Tooling Notes
- `npx` ships with `npm` (bundled with Node.js). Manage Node versions with `nvm`, set project default by running `nvm use 20` before `npm install` or Expo commands.
- Expo project scripts (`npm install`, `npx expo start --web/--android/--ios`) run from the `app/` directory. Dependencies are synced in Git, but reinstall with `rm -rf node_modules && npm install` when necessary.
- Additional Expo doctor commands used:  
  ```bash
  npx expo-doctor@latest . --fix-packages
  npx expo install --check
  ```

Keep this inventory updated as new automation, tooling, or infrastructure is added.

