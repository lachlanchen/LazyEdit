#!/bin/bash

# Source the config file
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
source "$SCRIPT_DIR/lazyedit_config.sh"
BASHRC_PATH="${BASHRC_PATH:-$HOME/.bashrc}"

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

# Check if the tmux session 'lazyedit' already exists
tmux has-session -t lazyedit 2>/dev/null

# Check the exit status of the previous command
if [ $? != 0 ]; then
    # If the session does not exist, create it
    tmux new -d -s lazyedit

    # Wait a bit to ensure that commands are sent after the session is properly set up
    sleep 2

    # Activate the conda environment using the function from config
    tmux send-keys -t lazyedit "cd \"$LAZYEDIT_DIR\"" C-m
    if [ -f "$BASHRC_PATH" ]; then
        tmux send-keys -t lazyedit "source \"$BASHRC_PATH\"" C-m
    fi
    if [ -n "$CONDA_PATH" ] && [ -f "$CONDA_PATH" ]; then
        tmux send-keys -t lazyedit "source \"$CONDA_PATH\"" C-m
    fi
    tmux send-keys -t lazyedit "conda activate \"$CONDA_ENV\"" C-m

    # Wait for the conda environment to activate
    sleep 5

    # Execute the script
    tmux send-keys -t lazyedit "cd $LAZYEDIT_DIR" C-m
    tmux send-keys -t lazyedit "python app.py $APP_ARGS" C-m
else
    echo "Tmux session 'lazyedit' already exists."
fi
