#!/bin/bash

# Source the config file
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
source "$SCRIPT_DIR/lazyedit_config.sh"

BASHRC_PATH="${BASHRC_PATH:-$HOME/.bashrc}"
SESSION_NAME="${SESSION_NAME:-lazyedit}"
EXPO_APP_DIR="${EXPO_APP_DIR:-${LAZYEDIT_DIR}/app}"
BACKEND_PORT="${BACKEND_PORT:-18787}"
EXPO_PORT="${EXPO_PORT:-18791}"
EXPO_PUBLIC_API_URL="${EXPO_PUBLIC_API_URL:-http://localhost:${BACKEND_PORT}}"

if ! command -v tmux >/dev/null 2>&1; then
    echo "tmux is required but not found in PATH."
    exit 1
fi

if [ -z "$CONDA_PATH" ] || [ ! -f "$CONDA_PATH" ]; then
    for candidate in "$HOME/miniconda3/etc/profile.d/conda.sh" "$HOME/anaconda3/etc/profile.d/conda.sh"; do
        if [ -f "$candidate" ]; then
            CONDA_PATH="$candidate"
            break
        fi
    done
fi
if [ -z "$CONDA_ENV" ]; then
    CONDA_ENV="lazyedit"
fi

if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo "Tmux session '$SESSION_NAME' already exists; restarting."
    tmux kill-session -t "$SESSION_NAME"
fi

tmux new -d -s "$SESSION_NAME" -n lazyedit

# Wait a bit to ensure that commands are sent after the session is properly set up
sleep 2

# Split into left/right panes (left: backend, right: Expo app)
tmux split-window -h -t "$SESSION_NAME":0

# Left pane: backend
if [ -f "$BASHRC_PATH" ]; then
    tmux send-keys -t "$SESSION_NAME":0.0 "source \"$BASHRC_PATH\"" C-m
fi
if [ -n "$CONDA_PATH" ] && [ -f "$CONDA_PATH" ]; then
    tmux send-keys -t "$SESSION_NAME":0.0 "source \"$CONDA_PATH\"" C-m
fi
tmux send-keys -t "$SESSION_NAME":0.0 "conda activate \"$CONDA_ENV\"" C-m

# Wait for the conda environment to activate
sleep 4

tmux send-keys -t "$SESSION_NAME":0.0 "cd \"$LAZYEDIT_DIR\"" C-m
tmux send-keys -t "$SESSION_NAME":0.0 "LAZYEDIT_PORT=\"$BACKEND_PORT\" python app.py $APP_ARGS" C-m

# Right pane: Expo app
if [ -f "$BASHRC_PATH" ]; then
    tmux send-keys -t "$SESSION_NAME":0.1 "source \"$BASHRC_PATH\"" C-m
fi
tmux send-keys -t "$SESSION_NAME":0.1 "cd \"$EXPO_APP_DIR\"" C-m
tmux send-keys -t "$SESSION_NAME":0.1 "if [ -f \"package.json\" ] && [ ! -d \"node_modules\" ]; then npm install; fi" C-m
tmux send-keys -t "$SESSION_NAME":0.1 "if [ -f \"package.json\" ] && [ ! -d \"node_modules/expo\" ]; then npm install; fi" C-m
tmux send-keys -t "$SESSION_NAME":0.1 "export EXPO_PUBLIC_API_URL=\"$EXPO_PUBLIC_API_URL\"" C-m
tmux send-keys -t "$SESSION_NAME":0.1 "npx expo start --web --port $EXPO_PORT" C-m
