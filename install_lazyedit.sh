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
DEPLOY_DIR="${1:-${LAZYEDIT_DIR:-$DEFAULT_DEPLOY_DIR}}"

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

# 2. Create or update config file (backup if it changes)
CONFIG_PATH="$DEPLOY_DIR/lazyedit_config.sh"
TMP_CONFIG="$(mktemp)"
cat > "$TMP_CONFIG" << EOF
#!/bin/bash

# LazyEdit configuration file - automatically generated

# Project paths
LAZYEDIT_DIR="$DEPLOY_DIR"
LAZYEDIT_USER="$TARGET_USER"

# Python/Conda settings
CONDA_PATH="$CONDA_PATH"
CONDA_ENV="$CONDA_ENV"

# App settings
APP_ARGS="-m lazyedit"
SESSION_NAME="lazyedit"

# Function to activate conda
activate_conda() {
    if [ -n "\$CONDA_PATH" ]; then
        source "\$CONDA_PATH"
        conda activate "\$CONDA_ENV" 2>/dev/null || echo "Warning: Could not activate conda environment '\$CONDA_ENV'"
    else
        echo "Warning: Conda path not set. Cannot activate environment."
    fi
}
EOF

if [[ -f "$CONFIG_PATH" ]] && cmp -s "$TMP_CONFIG" "$CONFIG_PATH"; then
    rm -f "$TMP_CONFIG"
    echo "Config unchanged: $CONFIG_PATH"
else
    if [[ -f "$CONFIG_PATH" ]]; then
        backup="${CONFIG_PATH}.bak.$(date +%Y%m%d_%H%M%S)"
        cp "$CONFIG_PATH" "$backup"
        echo "Existing config backed up to $backup"
    fi
    mv "$TMP_CONFIG" "$CONFIG_PATH"
    chmod +x "$CONFIG_PATH"
    echo "Config file written to $CONFIG_PATH"
fi

# 3. Ensure start/stop scripts exist in deploy dir
START_TEMPLATE="$SCRIPT_DIR/start_lazyedit.sh"
STOP_TEMPLATE="$SCRIPT_DIR/stop_lazyedit.sh"
START_TARGET="$DEPLOY_DIR/start_lazyedit.sh"
STOP_TARGET="$DEPLOY_DIR/stop_lazyedit.sh"

if [[ ! -f "$START_TARGET" ]]; then
    cp "$START_TEMPLATE" "$START_TARGET"
    echo "Copied start_lazyedit.sh to $START_TARGET"
else
    echo "Keeping existing start script at $START_TARGET"
fi
chmod +x "$START_TARGET"

if [[ ! -f "$STOP_TARGET" ]]; then
    cp "$STOP_TEMPLATE" "$STOP_TARGET"
    echo "Copied stop_lazyedit.sh to $STOP_TARGET"
else
    echo "Keeping existing stop script at $STOP_TARGET"
fi
chmod +x "$STOP_TARGET"

# 4. Create the systemd service file
SERVICE_FILE="/etc/systemd/system/lazyedit.service"
cat > "$SERVICE_FILE" << EOF
[Unit]
Description=LazyEdit Video Processing
After=network.target

[Service]
Type=forking
User=$TARGET_USER
WorkingDirectory=$DEPLOY_DIR
ExecStart=/bin/bash -lc '$DEPLOY_DIR/start_lazyedit.sh'
ExecStop=/bin/bash -lc '$DEPLOY_DIR/stop_lazyedit.sh'

[Install]
WantedBy=multi-user.target
EOF

chmod 644 "$SERVICE_FILE"

# 5. Reload systemd, enable and start the service
echo "Configuring systemd service..."
systemctl daemon-reload
systemctl enable lazyedit.service

# 6. Offer to start the service
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
