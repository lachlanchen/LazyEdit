#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="create-tmux-session"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
SCRIPT_PATH="/home/${SUDO_USER:-$USER}/scripts/create_tmux_session.sh"
USER_NAME="${SUDO_USER:-$USER}"

if [[ $EUID -ne 0 ]]; then
  echo "⚠️  Please run as root (sudo)." >&2
  exit 1
fi

# Ensure the create_tmux_session.sh exists
if [[ ! -x "$SCRIPT_PATH" ]]; then
  echo "❌  Can't find or execute $SCRIPT_PATH" >&2
  exit 1
fi

cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=Create TMUX Session named base at Boot
After=network.target

[Service]
Type=oneshot
User=${USER_NAME}
ExecStart=/bin/bash -c '${SCRIPT_PATH}'
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

chmod 644 "$SERVICE_FILE"
echo "✅  Written unit file to $SERVICE_FILE"

echo "🔄  Reloading systemd daemon..."
systemctl daemon-reload

echo "🔧  Enabling ${SERVICE_NAME}.service..."
systemctl enable "${SERVICE_NAME}.service"

echo "🚀  Starting ${SERVICE_NAME}.service..."
systemctl start "${SERVICE_NAME}.service"

echo "🎉  ${SERVICE_NAME}.service installed and running!"

