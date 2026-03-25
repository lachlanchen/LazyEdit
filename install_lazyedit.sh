#!/bin/bash
set -euo pipefail

# install_lazyedit.sh - install/update the LazyEdit systemd service safely

if [[ $EUID -ne 0 ]]; then
    echo "Please run with sudo." >&2
    exit 1
fi

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
TARGET_USER="${SUDO_USER:-$USER}"
DEFAULT_DEPLOY_DIR="/home/lachlan/DiskMech/Projects/lazyedit"
RUN_DIR="$(pwd)"
START_SERVICE="${LAZYEDIT_START:-0}"

usage() {
    cat <<'EOF'
Usage: sudo ./install_lazyedit.sh [--start] [--no-start] [DEPLOY_DIR]

Options:
  --start     Enable and restart lazyedit.service after install/update
  --no-start  Enable service only; do not start it
  -h, --help  Show this help

Environment:
  LAZYEDIT_START=1  same as --start
EOF
}

DEPLOY_DIR=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --start)
            START_SERVICE=1
            shift
            ;;
        --no-start)
            START_SERVICE=0
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        -*)
            echo "Unknown option: $1" >&2
            usage >&2
            exit 2
            ;;
        *)
            if [[ -n "$DEPLOY_DIR" ]]; then
                echo "Only one deploy directory may be provided." >&2
                usage >&2
                exit 2
            fi
            DEPLOY_DIR="$1"
            shift
            ;;
    esac
done

if [[ -z "$DEPLOY_DIR" ]]; then
    DEPLOY_DIR="${LAZYEDIT_DIR:-}"
fi
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

run_as_target_user() {
    HOME="$HOME_DIR" runuser -u "$TARGET_USER" -- bash -c "$1"
}

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
echo "Target user: $TARGET_USER"

# 1. Validate existing scripts/config (do not generate)
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

# 2. Install/check shared runtime prerequisites
PREREQ_SCRIPT="$DEPLOY_DIR/scripts/ensure_lazyedit_runtime.sh"
if [[ ! -f "$PREREQ_SCRIPT" ]]; then
    echo "Missing prerequisite checker: $PREREQ_SCRIPT" >&2
    exit 1
fi
echo "Installing/checking LazyEdit runtime prerequisites..."
"$PREREQ_SCRIPT" --install-system --target-user "$TARGET_USER" --deploy-dir "$DEPLOY_DIR"

# 3. Create/update the systemd service file
SERVICE_FILE="/etc/systemd/system/lazyedit.service"
TMP_SERVICE="$(mktemp)"
cat > "$TMP_SERVICE" << EOF
[Unit]
Description=LazyEdit Video Processing
After=network.target
RequiresMountsFor=$HOME_DIR $DEPLOY_DIR

[Service]
Type=oneshot
RemainAfterExit=yes
User=$TARGET_USER
Environment=HOME=$HOME_DIR
WorkingDirectory=$DEPLOY_DIR
ExecStart=/bin/bash -lc '$DEPLOY_DIR/start_lazyedit.sh'
ExecStop=/bin/bash -lc '$DEPLOY_DIR/stop_lazyedit.sh'

[Install]
WantedBy=multi-user.target
EOF

install -m 0644 "$TMP_SERVICE" "$SERVICE_FILE"
rm -f "$TMP_SERVICE"

# 4. Reload systemd and enable the service
echo "Configuring systemd service..."
systemctl daemon-reload
systemctl enable lazyedit.service

# 5. Optionally start the service
if [[ "$START_SERVICE" == "1" ]]; then
    systemctl restart lazyedit.service
    echo "Service started. Check status with: sudo systemctl status lazyedit.service"
else
    echo "Service installation complete but not started."
    echo "Start manually with: sudo systemctl start lazyedit.service"
fi

echo "LazyEdit installation complete."
echo "You can check status with: sudo systemctl status lazyedit.service"
echo "View logs with: sudo journalctl -u lazyedit.service"
