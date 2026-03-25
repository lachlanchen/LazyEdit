#!/usr/bin/env bash
set -euo pipefail

INSTALL_SYSTEM=0
TARGET_USER="${SUDO_USER:-${USER:-lachlan}}"
DEPLOY_DIR=""
QUIET=0

usage() {
  cat <<'EOF'
Usage:
  ensure_lazyedit_runtime.sh [--check-only] [--install-system] [--target-user USER] [--deploy-dir DIR] [--quiet]

Modes:
  --check-only      Validate LazyEdit runtime prerequisites without installing packages
  --install-system  Install missing system packages, then validate the full runtime

Checks:
  - tmux, ffmpeg, HandBrakeCLI
  - node, npm, npx for the target user
  - conda activation script and lazyedit env
  - caption Python path and fallback script path
  - expected repo/app entrypoint paths
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --check-only)
      INSTALL_SYSTEM=0
      shift
      ;;
    --install-system)
      INSTALL_SYSTEM=1
      shift
      ;;
    --target-user)
      [[ $# -ge 2 ]] || { echo "error: --target-user requires a value" >&2; exit 2; }
      TARGET_USER="$2"
      shift 2
      ;;
    --deploy-dir)
      [[ $# -ge 2 ]] || { echo "error: --deploy-dir requires a value" >&2; exit 2; }
      DEPLOY_DIR="$2"
      shift 2
      ;;
    --quiet)
      QUIET=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "error: unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "$DEPLOY_DIR" ]]; then
  DEPLOY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fi

if [[ ! -d "$DEPLOY_DIR" ]]; then
  echo "error: deploy directory not found: $DEPLOY_DIR" >&2
  exit 1
fi

HOME_DIR="$(getent passwd "$TARGET_USER" | cut -d: -f6 || true)"
if [[ -z "$HOME_DIR" ]]; then
  HOME_DIR="/home/$TARGET_USER"
fi

run_as_target_user() {
  local command_string="$1"

  if [[ "$(id -un)" == "$TARGET_USER" ]]; then
    HOME="$HOME_DIR" bash -lc "$command_string"
    return
  fi

  if [[ $EUID -ne 0 ]]; then
    echo "error: cannot switch to target user '$TARGET_USER' without sudo/root" >&2
    return 1
  fi

  HOME="$HOME_DIR" runuser -u "$TARGET_USER" -- bash -lc "$command_string"
}

CONFIG_PATH="$DEPLOY_DIR/lazyedit_config.sh"
ENV_FILE="$DEPLOY_DIR/.env"
if [[ -f "$CONFIG_PATH" ]]; then
  # shellcheck disable=SC1090
  source "$CONFIG_PATH"
fi
if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

LAZYEDIT_DIR="${LAZYEDIT_DIR:-$DEPLOY_DIR}"
EXPO_APP_DIR="${EXPO_APP_DIR:-$LAZYEDIT_DIR/app}"
CONDA_ENV="${CONDA_ENV:-lazyedit}"

if [[ -z "${CONDA_PATH:-}" || ! -f "${CONDA_PATH:-}" ]]; then
  for candidate in \
    "$HOME_DIR/miniconda3/etc/profile.d/conda.sh" \
    "$HOME_DIR/anaconda3/etc/profile.d/conda.sh"
  do
    if [[ -f "$candidate" ]]; then
      CONDA_PATH="$candidate"
      break
    fi
  done
fi

CAPTION_PYTHON="${LAZYEDIT_CAPTION_PYTHON:-$HOME_DIR/miniconda3/envs/caption/bin/python}"
CAPTION_FALLBACK_SCRIPT="${LAZYEDIT_CAPTION_FALLBACK_SCRIPT:-$HOME_DIR/ProjectsLFS/image_captioning/clip-gpt-captioning/src/v2c.py}"
CAPTION_FALLBACK_CWD="${LAZYEDIT_CAPTION_FALLBACK_CWD:-$LAZYEDIT_DIR}"

missing_runtime=()
missing_system_packages=()

note() {
  if [[ "$QUIET" != "1" ]]; then
    echo "$@"
  fi
}

require_command() {
  local command_name="$1"
  local apt_package="$2"

  if ! command -v "$command_name" >/dev/null 2>&1; then
    missing_runtime+=("missing command: $command_name")
    if [[ -n "$apt_package" ]]; then
      missing_system_packages+=("$apt_package")
    fi
  fi
}

require_command "tmux" "tmux"
require_command "ffmpeg" "ffmpeg"
require_command "HandBrakeCLI" "handbrake-cli"

if [[ "$INSTALL_SYSTEM" == "1" && ${#missing_system_packages[@]} -gt 0 ]]; then
  if [[ $EUID -ne 0 ]]; then
    echo "error: --install-system must be run with sudo/root" >&2
    exit 1
  fi
  mapfile -t missing_system_packages < <(printf '%s\n' "${missing_system_packages[@]}" | awk 'NF && !seen[$0]++')
  note "Installing missing system packages: ${missing_system_packages[*]}"
  export DEBIAN_FRONTEND=noninteractive
  apt-get update
  apt-get install -y "${missing_system_packages[@]}"
  missing_runtime=()
  missing_system_packages=()
  require_command "tmux" "tmux"
  require_command "ffmpeg" "ffmpeg"
  require_command "HandBrakeCLI" "handbrake-cli"
fi

if [[ ! -f "$LAZYEDIT_DIR/app.py" ]]; then
  missing_runtime+=("missing backend entrypoint: $LAZYEDIT_DIR/app.py")
fi
if [[ ! -f "$EXPO_APP_DIR/package.json" ]]; then
  missing_runtime+=("missing Expo frontend package.json: $EXPO_APP_DIR/package.json")
fi
if [[ -z "${CONDA_PATH:-}" || ! -f "${CONDA_PATH:-}" ]]; then
  missing_runtime+=("missing conda activation script for $TARGET_USER")
fi
if [[ ! -x "$CAPTION_PYTHON" ]]; then
  missing_runtime+=("missing caption Python executable: $CAPTION_PYTHON")
fi
if [[ ! -f "$CAPTION_FALLBACK_SCRIPT" ]]; then
  missing_runtime+=("missing caption fallback script: $CAPTION_FALLBACK_SCRIPT")
fi
if [[ ! -d "$CAPTION_FALLBACK_CWD" ]]; then
  missing_runtime+=("missing caption fallback working directory: $CAPTION_FALLBACK_CWD")
fi

if ! run_as_target_user "export NVM_DIR=\"$HOME_DIR/.nvm\"; [[ -s \"$HOME_DIR/.nvm/nvm.sh\" ]] && . \"$HOME_DIR/.nvm/nvm.sh\"; command -v node >/dev/null && command -v npm >/dev/null && command -v npx >/dev/null"; then
  missing_runtime+=("node/npm/npx not available for user $TARGET_USER")
fi

if [[ -n "${CONDA_PATH:-}" && -f "${CONDA_PATH:-}" ]]; then
  if ! run_as_target_user "source \"$CONDA_PATH\" >/dev/null 2>&1 && conda env list | awk '{print \$1}' | grep -qx \"$CONDA_ENV\""; then
    missing_runtime+=("missing conda environment: $CONDA_ENV")
  fi
fi

if [[ ${#missing_runtime[@]} -gt 0 ]]; then
  echo "LazyEdit runtime prerequisite check failed:" >&2
  for item in "${missing_runtime[@]}"; do
    echo "  - $item" >&2
  done
  exit 1
fi

note "LazyEdit runtime prerequisites look good."
note "  deploy dir: $LAZYEDIT_DIR"
note "  target user: $TARGET_USER"
note "  conda env: $CONDA_ENV"
note "  caption python: $CAPTION_PYTHON"
note "  caption fallback: $CAPTION_FALLBACK_SCRIPT"
