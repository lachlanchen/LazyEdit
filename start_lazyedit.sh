#!/bin/bash

# Source the config file
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
source "$SCRIPT_DIR/lazyedit_config.sh"
BASHRC_PATH="${BASHRC_PATH:-$HOME/.bashrc}"
EXPO_APP_DIR="${EXPO_APP_DIR:-/home/lachlan/ProjectsLFS/LazyEdit/app}"
BACKEND_PORT="${BACKEND_PORT:-8081}"
EXPO_PORT="${EXPO_PORT:-8091}"
EXPO_PUBLIC_API_URL="${EXPO_PUBLIC_API_URL:-http://localhost:${BACKEND_PORT}}"

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

# Check if the tmux session 'la-lazyedit' already exists
tmux has-session -t la-lazyedit 2>/dev/null

# Check the exit status of the previous command
if [ $? != 0 ]; then
    # If the session does not exist, create it
    tmux new -d -s la-lazyedit -n lazyedit

    # Wait a bit to ensure that commands are sent after the session is properly set up
    sleep 2

    # Split into left/right panes (left: backend, right: Expo app)
    tmux split-window -h -t la-lazyedit:0

    # Left pane: backend
    if [ -f "$BASHRC_PATH" ]; then
        tmux send-keys -t la-lazyedit:0.0 "source \"$BASHRC_PATH\"" C-m
    fi
    if [ -n "$CONDA_PATH" ] && [ -f "$CONDA_PATH" ]; then
        tmux send-keys -t la-lazyedit:0.0 "source \"$CONDA_PATH\"" C-m
    fi
    tmux send-keys -t la-lazyedit:0.0 "conda activate \"$CONDA_ENV\"" C-m

    # Wait for the conda environment to activate
    sleep 4

    tmux send-keys -t la-lazyedit:0.0 "cd \"$LAZYEDIT_DIR\"" C-m
    tmux send-keys -t la-lazyedit:0.0 "python app.py $APP_ARGS" C-m

    # Right pane: Expo app
    if [ -f "$BASHRC_PATH" ]; then
        tmux send-keys -t la-lazyedit:0.1 "source \"$BASHRC_PATH\"" C-m
    fi
    tmux send-keys -t la-lazyedit:0.1 "cd \"$EXPO_APP_DIR\"" C-m
    tmux send-keys -t la-lazyedit:0.1 "export EXPO_PUBLIC_API_URL=\"$EXPO_PUBLIC_API_URL\"" C-m
    tmux send-keys -t la-lazyedit:0.1 "npx expo start --web --port $EXPO_PORT" C-m
else
    echo "Tmux session 'la-lazyedit' already exists."
fi
