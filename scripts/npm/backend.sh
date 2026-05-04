#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CONDA_ENV="${CONDA_ENV:-lazyedit}"
BACKEND_PORT="${LAZYEDIT_PORT:-${PORT:-18787}}"
APP_ARGS="${APP_ARGS:--m lazyedit}"
ENV_FILE="${ENV_FILE:-$ROOT_DIR/.env}"

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

CONDA_SH="$(find_conda_sh || true)"
if [[ -z "$CONDA_SH" ]]; then
  echo "Could not find conda.sh. Run npm run setup first or set CONDA_PATH." >&2
  exit 1
fi

if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

# shellcheck disable=SC1090
source "$CONDA_SH"
conda activate "$CONDA_ENV"
cd "$ROOT_DIR"
LAZYEDIT_PORT="$BACKEND_PORT" python app.py $APP_ARGS
