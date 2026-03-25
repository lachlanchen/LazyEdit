#!/usr/bin/env bash
set -euo pipefail

DEFAULT_IP="192.168.1.111"
DEFAULT_HOSTNAME="lazyingart"
ETC_HOSTS="${ETC_HOSTS:-/etc/hosts}"
HOST_IP="${1:-${HOST_IP:-$DEFAULT_IP}}"
HOST_NAME="${2:-${HOST_NAME:-$DEFAULT_HOSTNAME}}"
HOSTS_COMMENT="${HOSTS_COMMENT:-# lazyedit-host-cache}"

shift_args=0
if [ "$#" -ge 1 ]; then
  shift_args=1
fi
if [ "$#" -ge 2 ]; then
  shift_args=2
fi
if [ "$shift_args" -gt 0 ]; then
  shift "$shift_args"
fi
ALIASES=("$@")

usage() {
  cat <<'EOF'
Usage:
  ensure_hosts_entry.sh [ip] [hostname] [alias...]

Default:
  ensure_hosts_entry.sh
  -> adds "192.168.1.111 lazyingart" to /etc/hosts if hostname is missing

Notes:
  - Idempotent: if the hostname already exists in /etc/hosts, no duplicate is added.
  - Uses sudo automatically if /etc/hosts is not writable by the current user.
  - You can override the target file for testing with ETC_HOSTS=/path/to/file.
EOF
}

if [ "${HOST_IP:-}" = "-h" ] || [ "${HOST_IP:-}" = "--help" ]; then
  usage
  exit 0
fi

if [ -z "$HOST_IP" ] || [ -z "$HOST_NAME" ]; then
  echo "error: IP and hostname must not be empty" >&2
  exit 2
fi

if [ ! -f "$ETC_HOSTS" ]; then
  echo "error: hosts file not found: $ETC_HOSTS" >&2
  exit 1
fi

if [ ! -w "$ETC_HOSTS" ]; then
  if ! command -v sudo >/dev/null 2>&1; then
    echo "error: $ETC_HOSTS is not writable and sudo is unavailable" >&2
    exit 1
  fi
  exec sudo ETC_HOSTS="$ETC_HOSTS" HOSTS_COMMENT="$HOSTS_COMMENT" "$0" "$HOST_IP" "$HOST_NAME" "${ALIASES[@]}"
fi

if grep -Eq "^[[:space:]]*[^#].*[[:space:]]${HOST_NAME}([[:space:]]|\$)" "$ETC_HOSTS"; then
  echo "hosts entry already exists for $HOST_NAME in $ETC_HOSTS"
  exit 0
fi

backup_path="${ETC_HOSTS}.bak.$(date +%Y%m%d%H%M%S)"
cp "$ETC_HOSTS" "$backup_path"

entry="$HOST_IP $HOST_NAME"
if [ "${#ALIASES[@]}" -gt 0 ]; then
  entry="$entry ${ALIASES[*]}"
fi

printf '\n%s %s\n' "$entry" "$HOSTS_COMMENT" >> "$ETC_HOSTS"
echo "added hosts entry to $ETC_HOSTS"
echo "backup saved to $backup_path"
