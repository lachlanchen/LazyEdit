#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CONDA_ENV="${CONDA_ENV:-lazyedit}"
WHISPER_ENV="${LAZYEDIT_WHISPER_ENV:-whisper}"
CAPTION_ENV="${LAZYEDIT_CAPTION_ENV:-caption}"
FAILURES=()

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

check_command() {
  local command_name="$1"
  if command -v "$command_name" >/dev/null 2>&1; then
    echo "ok: $command_name -> $(command -v "$command_name")"
  else
    echo "missing: $command_name"
    FAILURES+=("missing command: $command_name")
  fi
}

has_conda_env() {
  conda env list | awk '{print $1}' | grep -qx "$1"
}

check_env_imports() {
  local env_name="$1"
  local label="$2"
  local code="$3"
  if ! has_conda_env "$env_name"; then
    echo "missing: conda env $env_name ($label)"
    FAILURES+=("missing conda env: $env_name")
    return
  fi
  if conda run -n "$env_name" python - <<PY
$code
PY
  then
    echo "ok: $label imports in $env_name"
  else
    echo "failed: $label imports in $env_name"
    FAILURES+=("failed imports in env: $env_name")
  fi
}

echo "LazyEdit npm doctor"
echo "root: $ROOT_DIR"

check_command node
check_command npm
check_command npx
check_command ffmpeg
check_command tmux
check_command HandBrakeCLI

if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader || true
else
  echo "note: nvidia-smi not found; Whisper will rely on CPU fallback if CUDA is unavailable."
fi

CONDA_SH="$(find_conda_sh || true)"
if [[ -z "$CONDA_SH" ]]; then
  echo "missing: conda activation script"
  FAILURES+=("missing conda activation script")
else
  # shellcheck disable=SC1090
  source "$CONDA_SH"
  echo "ok: conda -> $(conda info --base)"
  check_env_imports "$CONDA_ENV" "LazyEdit backend" "import tornado, cv2, torch, requests; print('torch cuda:', torch.cuda.is_available())"
  check_env_imports "$WHISPER_ENV" "Whisper/VAD" "import torch, torchaudio, whisper, torchcodec, soundfile; from lingua import LanguageDetectorBuilder; print('torch cuda:', torch.cuda.is_available())"
  check_env_imports "$CAPTION_ENV" "Captioning" "import torch, transformers, cv2, psutil; from PIL import Image; import Katna; print('torch cuda:', torch.cuda.is_available())"
fi

if [[ -f "$ROOT_DIR/.env" ]]; then
  echo "ok: .env exists"
else
  echo "missing: .env"
  FAILURES+=("missing .env")
fi

if [[ -d "$ROOT_DIR/app/node_modules" ]]; then
  echo "ok: app/node_modules exists"
else
  echo "missing: app/node_modules"
  FAILURES+=("missing frontend dependencies")
fi

if [[ ${#FAILURES[@]} -gt 0 ]]; then
  echo "Doctor failed:"
  printf '  - %s\n' "${FAILURES[@]}"
  exit 1
fi

echo "LazyEdit runtime looks ready."
