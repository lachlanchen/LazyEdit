#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CONDA_ENV="${CONDA_ENV:-lazyedit}"
WHISPER_ENV="${LAZYEDIT_WHISPER_ENV:-whisper}"
CAPTION_ENV="${LAZYEDIT_CAPTION_ENV:-caption}"
TORCH_INDEX_URL="${LAZYEDIT_TORCH_INDEX_URL:-https://download.pytorch.org/whl/cu128}"
SETUP_WEB=1
SETUP_MAIN=1
SETUP_WHISPER=1
SETUP_CAPTION=1
INSTALL_SYSTEM=0
UPDATE_ENVS="${LAZYEDIT_UPDATE_CONDA_ENVS:-0}"

usage() {
  cat <<'EOF'
Usage: npm run setup -- [options]

Options:
  --skip-web        Do not run npm install in app/
  --skip-main       Do not create/update the main lazyedit conda env
  --skip-whisper    Do not create/update the whisper conda env
  --skip-caption    Do not create/update the caption conda env
  --install-system  Install/check system packages with scripts/ensure_lazyedit_runtime.sh
  --update-envs     Update existing conda envs from env files; default creates only when missing
  -h, --help        Show this help

Environment:
  CONDA_ENV=lazyedit
  LAZYEDIT_WHISPER_ENV=whisper
  LAZYEDIT_CAPTION_ENV=caption
  LAZYEDIT_TORCH_INDEX_URL=https://download.pytorch.org/whl/cu128
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-web) SETUP_WEB=0; shift ;;
    --skip-main) SETUP_MAIN=0; shift ;;
    --skip-whisper) SETUP_WHISPER=0; shift ;;
    --skip-caption) SETUP_CAPTION=0; shift ;;
    --install-system) INSTALL_SYSTEM=1; shift ;;
    --update-envs) UPDATE_ENVS=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

need_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

find_conda_sh() {
  for candidate in \
    "${CONDA_PATH:-}" \
    "$HOME/miniconda3/etc/profile.d/conda.sh" \
    "$HOME/anaconda3/etc/profile.d/conda.sh"
  do
    if [[ -n "$candidate" && -f "$candidate" ]]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done
  return 1
}

has_conda_env() {
  conda env list | awk '{print $1}' | grep -qx "$1"
}

ensure_conda_env() {
  local env_name="$1"
  local env_file="$2"
  if has_conda_env "$env_name"; then
    if [[ "$UPDATE_ENVS" == "1" ]]; then
      echo "Updating conda env $env_name from $env_file"
      conda env update -n "$env_name" -f "$env_file"
    else
      echo "Conda env $env_name already exists; skipping update."
    fi
  else
    echo "Creating conda env $env_name from $env_file"
    conda env create -n "$env_name" -f "$env_file"
  fi
}

pip_install() {
  local env_name="$1"
  shift
  conda run -n "$env_name" python -m pip install "$@"
}

env_escape() {
  printf '%s' "$1" | sed 's/[\/&]/\\&/g'
}

upsert_env() {
  local key="$1"
  local value="$2"
  local env_file="$ROOT_DIR/.env"
  touch "$env_file"
  if grep -qE "^${key}=" "$env_file"; then
    sed -i "s/^${key}=.*/${key}=$(env_escape "$value")/" "$env_file"
  else
    printf '%s=%s\n' "$key" "$value" >> "$env_file"
  fi
}

write_runtime_env() {
  if [[ ! -f "$ROOT_DIR/.env" && -f "$ROOT_DIR/.env.example" ]]; then
    cp "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"
  fi
  mkdir -p "$ROOT_DIR/DATA"
  local conda_prefix
  conda_prefix="$(conda info --base)"
  upsert_env "LAZYEDIT_UPLOAD_DIR" "$ROOT_DIR/DATA"
  upsert_env "LAZYEDIT_WHISPER_SCRIPT" "$ROOT_DIR/whisper_with_lang_detect/vad_lang_subtitle.py"
  upsert_env "LAZYEDIT_WHISPER_PYTHON" "$conda_prefix/envs/$WHISPER_ENV/bin/python"
  upsert_env "LAZYEDIT_CAPTION_PYTHON" "$conda_prefix/envs/$CAPTION_ENV/bin/python"
  upsert_env "LAZYEDIT_CAPTION_PRIMARY_ROOT" "$ROOT_DIR/vit-gpt2-image-captioning"
  upsert_env "LAZYEDIT_CAPTION_FALLBACK_CWD" "$ROOT_DIR"
  upsert_env "LAZYEDIT_AI_PROVIDER" "deepseek"
  upsert_env "LAZYEDIT_AI_MODEL" "deepseek-v4-flash"
  upsert_env "LAZYEDIT_TRANSLATION_PROVIDER" "deepseek"
  upsert_env "LAZYEDIT_TRANSLATION_MODEL" "deepseek-v4-flash"
  upsert_env "LAZYEDIT_SUBTITLE_CORRECTION_PROVIDER" "deepseek"
  upsert_env "LAZYEDIT_SUBTITLE_CORRECTION_MODEL" "deepseek-v4-pro"
  upsert_env "LAZYEDIT_SUBTITLE_CORRECTION_MODELS" "deepseek-v4-pro,deepseek-v4-flash"
  upsert_env "LAZYEDIT_SUBTITLE_CORRECTION_FALLBACK_MODEL" "deepseek-v4-flash"
  upsert_env "LAZYEDIT_SUBTITLE_CORRECTION_MAX_RETRIES" "1"
}

need_command npm
need_command node

CONDA_SH="$(find_conda_sh || true)"
if [[ -z "$CONDA_SH" ]]; then
  echo "Could not find conda.sh. Install Miniconda/Anaconda or set CONDA_PATH." >&2
  exit 1
fi

# shellcheck disable=SC1090
source "$CONDA_SH"
need_command conda

if [[ "$SETUP_WEB" == "1" ]]; then
  echo "Installing Expo app dependencies..."
  npm --prefix "$ROOT_DIR/app" install
fi

if [[ "$SETUP_MAIN" == "1" ]]; then
  ensure_conda_env "$CONDA_ENV" "$ROOT_DIR/environment.yml"
fi

if [[ "$SETUP_WHISPER" == "1" ]]; then
  ensure_conda_env "$WHISPER_ENV" "$ROOT_DIR/environment.whisper.yml"
  pip_install "$WHISPER_ENV" --upgrade pip
  pip_install "$WHISPER_ENV" --index-url "$TORCH_INDEX_URL" torch torchaudio torchvision
  pip_install "$WHISPER_ENV" -r "$ROOT_DIR/requirements-whisper.txt"
fi

if [[ "$SETUP_CAPTION" == "1" ]]; then
  ensure_conda_env "$CAPTION_ENV" "$ROOT_DIR/environment.caption.yml"
  pip_install "$CAPTION_ENV" --upgrade pip
  pip_install "$CAPTION_ENV" --index-url "$TORCH_INDEX_URL" torch torchvision
  pip_install "$CAPTION_ENV" -r "$ROOT_DIR/requirements-caption.txt"
  if [[ -d "$ROOT_DIR/vit-gpt2-image-captioning" ]]; then
    pip_install "$CAPTION_ENV" -e "$ROOT_DIR/vit-gpt2-image-captioning"
  fi
fi

write_runtime_env

if [[ "$INSTALL_SYSTEM" == "1" ]]; then
  "$ROOT_DIR/scripts/ensure_lazyedit_runtime.sh" --install-system --target-user "$(id -un)" --deploy-dir "$ROOT_DIR"
fi

"$ROOT_DIR/scripts/npm/doctor.sh"
