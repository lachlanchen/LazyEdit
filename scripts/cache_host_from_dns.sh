#!/usr/bin/env bash
set -euo pipefail

DEFAULT_HOSTNAME="lazyingart"
ETC_HOSTS="${ETC_HOSTS:-/etc/hosts}"
HOSTS_COMMENT="${HOSTS_COMMENT:-# lazyedit-host-cache}"
HOST_NAME="${HOST_NAME:-$DEFAULT_HOSTNAME}"
HOST_IP="${HOST_IP:-}"
RESOLVED_IP=""
RESOLUTION_SOURCE=""
declare -a DNS_SERVERS=()
declare -a ALIASES=()

usage() {
  cat <<'EOF'
Usage:
  cache_host_from_dns.sh [--hostname NAME] [--dns-server IP] [--ip IP] [--alias NAME ...]

Default:
  cache_host_from_dns.sh
  -> resolves "lazyingart" using discovered DNS servers, then caches the result in /etc/hosts

Examples:
  cache_host_from_dns.sh
  cache_host_from_dns.sh --hostname lazyingart
  cache_host_from_dns.sh --hostname lazyingart --dns-server 192.168.1.1
  cache_host_from_dns.sh --hostname lazyingart --alias lazyingart.local

Notes:
  - If --ip is provided, DNS lookup is skipped.
  - The script is idempotent for the target hostname.
  - If a stale /etc/hosts entry exists for the hostname, it is replaced.
  - You can override the target file for testing with ETC_HOSTS=/path/to/file.
EOF
}

is_loopback_or_empty() {
  case "${1:-}" in
    ""|127.*|::1|0.0.0.0)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

add_dns_server() {
  local candidate="${1:-}"
  local existing

  is_loopback_or_empty "$candidate" && return 0

  for existing in "${DNS_SERVERS[@]:-}"; do
    if [ "$existing" = "$candidate" ]; then
      return 0
    fi
  done

  DNS_SERVERS+=("$candidate")
}

detect_dns_servers() {
  local server
  local gateway
  local conf

  if command -v resolvectl >/dev/null 2>&1; then
    while IFS= read -r server; do
      add_dns_server "$server"
    done < <(resolvectl dns 2>/dev/null | awk '{for (i = 1; i <= NF; i++) if ($i ~ /^([0-9]{1,3}\.){3}[0-9]{1,3}$/ || $i ~ /:/) print $i}')
  fi

  for conf in /run/systemd/resolve/resolv.conf /etc/resolv.conf; do
    [ -r "$conf" ] || continue
    while IFS= read -r server; do
      add_dns_server "$server"
    done < <(awk '/^nameserver[[:space:]]+/ {print $2}' "$conf")
  done

  gateway="$(ip route show default 2>/dev/null | awk '/default/ {print $3; exit}')"
  add_dns_server "$gateway"
}

resolve_with_nslookup() {
  local host="$1"
  local dns_server="$2"

  nslookup "$host" "$dns_server" 2>/dev/null \
    | awk '
        BEGIN { seen = 0 }
        /^Name:/ { seen = 1; next }
        seen && /^Address: / { print $2; exit }
      '
}

resolve_with_dig() {
  local host="$1"
  local dns_server="$2"
  local ip=""

  ip="$(dig +time=2 +tries=1 +short @"$dns_server" "$host" A 2>/dev/null | awk 'NF { print; exit }')"
  if [ -n "$ip" ]; then
    printf '%s\n' "$ip"
    return 0
  fi

  dig +time=2 +tries=1 +short @"$dns_server" "$host" AAAA 2>/dev/null | awk 'NF { print; exit }'
}

resolve_host_ip() {
  local host="$1"
  local dns_server
  local ip=""

  ip="$(getent hosts "$host" 2>/dev/null | awk 'NF { print $1; exit }' || true)"
  if [ -n "$ip" ]; then
    RESOLVED_IP="$ip"
    RESOLUTION_SOURCE="getent"
    return 0
  fi

  if [ "${#DNS_SERVERS[@]}" -eq 0 ]; then
    detect_dns_servers
  fi

  for dns_server in "${DNS_SERVERS[@]:-}"; do
    if command -v nslookup >/dev/null 2>&1; then
      ip="$(resolve_with_nslookup "$host" "$dns_server")"
    elif command -v dig >/dev/null 2>&1; then
      ip="$(resolve_with_dig "$host" "$dns_server")"
    else
      echo "error: neither nslookup nor dig is available for DNS lookup" >&2
      return 1
    fi

    if [ -n "$ip" ]; then
      RESOLVED_IP="$ip"
      RESOLUTION_SOURCE="$dns_server"
      return 0
    fi
  done

  return 1
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    --hostname)
      [ "$#" -ge 2 ] || { echo "error: --hostname requires a value" >&2; exit 2; }
      HOST_NAME="$2"
      shift 2
      ;;
    --ip)
      [ "$#" -ge 2 ] || { echo "error: --ip requires a value" >&2; exit 2; }
      HOST_IP="$2"
      shift 2
      ;;
    --dns-server)
      [ "$#" -ge 2 ] || { echo "error: --dns-server requires a value" >&2; exit 2; }
      add_dns_server "$2"
      shift 2
      ;;
    --alias)
      [ "$#" -ge 2 ] || { echo "error: --alias requires a value" >&2; exit 2; }
      ALIASES+=("$2")
      shift 2
      ;;
    --)
      shift
      while [ "$#" -gt 0 ]; do
        ALIASES+=("$1")
        shift
      done
      ;;
    -*)
      echo "error: unknown option: $1" >&2
      exit 2
      ;;
    *)
      HOST_NAME="$1"
      shift
      while [ "$#" -gt 0 ]; do
        ALIASES+=("$1")
        shift
      done
      ;;
  esac
done

[ -n "$HOST_NAME" ] || { echo "error: hostname must not be empty" >&2; exit 2; }
[ -f "$ETC_HOSTS" ] || { echo "error: hosts file not found: $ETC_HOSTS" >&2; exit 1; }

if [ -z "$HOST_IP" ]; then
  resolve_host_ip "$HOST_NAME" || true
  HOST_IP="$RESOLVED_IP"
fi

if [ -z "$HOST_IP" ]; then
  echo "error: could not resolve $HOST_NAME via system DNS or discovered DNS servers" >&2
  if [ "${#DNS_SERVERS[@]}" -gt 0 ]; then
    echo "tried DNS servers: ${DNS_SERVERS[*]}" >&2
  fi
  exit 1
fi

if [ ! -w "$ETC_HOSTS" ]; then
  if ! command -v sudo >/dev/null 2>&1; then
    echo "error: $ETC_HOSTS is not writable and sudo is unavailable" >&2
    exit 1
  fi
  sudo_args=(ETC_HOSTS="$ETC_HOSTS" HOSTS_COMMENT="$HOSTS_COMMENT" "$0" --hostname "$HOST_NAME" --ip "$HOST_IP")
  if [ "${#ALIASES[@]}" -gt 0 ]; then
    for alias in "${ALIASES[@]}"; do
      sudo_args+=(--alias "$alias")
    done
  fi
  exec sudo "${sudo_args[@]}"
fi

current_ip="$(
  awk -v host="$HOST_NAME" '
    /^[[:space:]]*#/ { next }
    {
      line = $0
      sub(/[[:space:]]+#.*$/, "", line)
      n = split(line, a, /[[:space:]]+/)
      if (n < 2) next
      for (i = 2; i <= n; i++) {
        if (a[i] == host) {
          print a[1]
          exit
        }
      }
    }
  ' "$ETC_HOSTS"
)"

if [ "$current_ip" = "$HOST_IP" ]; then
  echo "hosts entry already resolves $HOST_NAME -> $HOST_IP in $ETC_HOSTS"
  exit 0
fi

backup_path="${ETC_HOSTS}.bak.$(date +%Y%m%d%H%M%S)"
tmpfile="$(mktemp)"
trap 'rm -f "$tmpfile"' EXIT

cp "$ETC_HOSTS" "$backup_path"

awk -v host="$HOST_NAME" '
  /^[[:space:]]*#/ { print; next }
  {
    raw = $0
    line = $0
    sub(/[[:space:]]+#.*$/, "", line)
    n = split(line, a, /[[:space:]]+/)
    remove = 0
    for (i = 2; i <= n; i++) {
      if (a[i] == host) {
        remove = 1
        break
      }
    }
    if (!remove) {
      print raw
    }
  }
' "$ETC_HOSTS" > "$tmpfile"

entry="$HOST_IP $HOST_NAME"
if [ "${#ALIASES[@]}" -gt 0 ]; then
  entry="$entry ${ALIASES[*]}"
fi

printf '\n%s %s\n' "$entry" "$HOSTS_COMMENT" >> "$tmpfile"
cat "$tmpfile" > "$ETC_HOSTS"

if [ -n "$RESOLUTION_SOURCE" ]; then
  echo "resolved $HOST_NAME -> $HOST_IP via $RESOLUTION_SOURCE"
else
  echo "using explicit IP for $HOST_NAME -> $HOST_IP"
fi
echo "updated $ETC_HOSTS"
echo "backup saved to $backup_path"
