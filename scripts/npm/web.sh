#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BACKEND_PORT="${LAZYEDIT_PORT:-${PORT:-18787}}"
EXPO_PORT="${EXPO_PORT:-18791}"
EXPO_PUBLIC_API_URL="${EXPO_PUBLIC_API_URL:-http://localhost:${BACKEND_PORT}}"
EXPO_MAX_WORKERS="${EXPO_MAX_WORKERS:-4}"
ENV_FILE="${ENV_FILE:-$ROOT_DIR/.env}"

if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

cd "$ROOT_DIR/app"
if [[ ! -d node_modules ]]; then
  npm install
fi
EXPO_PUBLIC_API_URL="${EXPO_PUBLIC_API_URL:-http://localhost:${BACKEND_PORT}}" \
  npx expo start --web --port "$EXPO_PORT" --max-workers "$EXPO_MAX_WORKERS"
