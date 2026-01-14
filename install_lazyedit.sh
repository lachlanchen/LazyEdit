#!/bin/bash
set -euo pipefail

# install_lazyedit.sh - Script to install and set up the LazyEdit service
# Creates the systemd service, config file and installs required packages

if [[ $EUID -ne 0 ]]; then
    echo "Please run with sudo." >&2
    exit 1
fi

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
TARGET_USER="${SUDO_USER:-$USER}"
DEFAULT_DEPLOY_DIR="/home/lachlan/DiskMech/Projects/lazyedit"
RUN_DIR="$(pwd)"
DEPLOY_DIR="${1:-${LAZYEDIT_DIR:-}}"
if [[ -z "$DEPLOY_DIR" ]]; then
    if [[ -f "$RUN_DIR/app.py" ]]; then
        DEPLOY_DIR="$RUN_DIR"
    else
        DEPLOY_DIR="$DEFAULT_DEPLOY_DIR"
    fi
fi

if [[ ! -d "$DEPLOY_DIR" ]]; then
    echo "Deploy directory not found: $DEPLOY_DIR" >&2
    echo "Clone LazyEdit to that path or pass the deploy dir as the first argument." >&2
    exit 1
fi

HOME_DIR="$(getent passwd "$TARGET_USER" | cut -d: -f6)"
if [[ -z "$HOME_DIR" ]]; then
    HOME_DIR="/home/$TARGET_USER"
fi

CONDA_ENV="${CONDA_ENV:-lazyedit}"
CONDA_PATH=""
if [[ -f "$HOME_DIR/miniconda3/etc/profile.d/conda.sh" ]]; then
    CONDA_PATH="$HOME_DIR/miniconda3/etc/profile.d/conda.sh"
elif [[ -f "$HOME_DIR/anaconda3/etc/profile.d/conda.sh" ]]; then
    CONDA_PATH="$HOME_DIR/anaconda3/etc/profile.d/conda.sh"
else
    echo "Warning: Could not find conda.sh. Please update the config file manually."
fi

echo "Installing LazyEdit into: $DEPLOY_DIR"

# 1. Install required packages
echo "Installing required packages..."
apt-get update
apt-get install -y ffmpeg tmux

# 2. Validate existing scripts/config (do not generate)
CONFIG_PATH="$DEPLOY_DIR/lazyedit_config.sh"
START_TARGET="$DEPLOY_DIR/start_lazyedit.sh"
STOP_TARGET="$DEPLOY_DIR/stop_lazyedit.sh"

if [[ ! -f "$CONFIG_PATH" ]]; then
    echo "Missing config: $CONFIG_PATH" >&2
    echo "Aborting because this installer no longer generates config/scripts." >&2
    exit 1
fi
if [[ ! -f "$START_TARGET" ]]; then
    echo "Missing start script: $START_TARGET" >&2
    exit 1
fi
if [[ ! -f "$STOP_TARGET" ]]; then
    echo "Missing stop script: $STOP_TARGET" >&2
    exit 1
fi

# 3. Create the systemd service file
SERVICE_FILE="/etc/systemd/system/lazyedit.service"
cat > "$SERVICE_FILE" << EOF
[Unit]
Description=LazyEdit Video Processing
After=network.target

[Service]
Type=oneshot
RemainAfterExit=yes
User=$TARGET_USER
WorkingDirectory=$DEPLOY_DIR
ExecStart=/bin/bash -lc '$DEPLOY_DIR/start_lazyedit.sh'
ExecStop=/bin/bash -lc '$DEPLOY_DIR/stop_lazyedit.sh'

[Install]
WantedBy=multi-user.target
EOF

chmod 644 "$SERVICE_FILE"

# 4. Reload systemd, enable and start the service
echo "Configuring systemd service..."
systemctl daemon-reload
systemctl enable lazyedit.service

# 5. Offer to start the service
echo "Would you like to start the lazyedit service now? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    systemctl restart lazyedit.service
    echo "Service started. Check status with: sudo systemctl status lazyedit.service"
else
    echo "Service installation complete but not started."
    echo "Start manually with: sudo systemctl start lazyedit.service"
fi

echo "LazyEdit installation complete."
echo "You can check status with: sudo systemctl status lazyedit.service"
echo "View logs with: sudo journalctl -u lazyedit.service"
