#!/bin/bash

# Define the user's home directory explicitly
HOME_DIR="/home/lachlan"

# Ensure we're in the user's home directory
cd "$HOME_DIR"

# Create or attach to the 'base' session
tmux has-session -t base 2>/dev/null || tmux new-session -d -s base

# # Create the 'sync-autopub' session and execute the rsync command within it
# if tmux has-session -t sync-autopub 2>/dev/null; then
#     echo "Session sync-autopub already exists."
# else
#     tmux new-session -d -s sync-autopub
#     # tmux send-keys -t sync-autopub "cd $HOME_DIR && rsync -avh --progress $HOME_DIR/jianguoyun/AutoPublishDATA/ $HOME_DIR/AutoPublishDATA/" C-m
#     # tmux send-keys -t sync-autopub "while true; do rsync -avh --delete --progress $HOME_DIR/jianguoyun/AutoPublishDATA/AutoPublish/ $HOME_DIR/AutoPublishDATA/AutoPublish/; sleep 10; done" C-m
#     # tmux send-keys -t sync-autopub "while true; do rsync -avh --progress $HOME_DIR/jianguoyun/AutoPublishDATA/AutoPublish/ $HOME_DIR/AutoPublishDATA/AutoPublish/; sleep 10; done" C-m
#     # tmux send-keys -t sync-autopub "while true; do rsync -rtvvv --progress /home/lachlan/jianguoyun/AutoPublishDATA/AutoPublish/ /home/lachlan/AutoPublishDATA/AutoPublish/; sleep 10; done" C-m
#     # tmux send-keys -t sync-autopub "while true; do rsync -rt --progress --whole-file /home/lachlan/jianguoyun/AutoPublishDATA/AutoPublish/ /home/lachlan/AutoPublishDATA/AutoPublish/; sleep 10; done" C-m
#     tmux send-keys -t sync-autopub "bash /home/lachlan/sync-autopub.sh" C-m
# fi
# 
# # Create the 'sync-transcription' session for syncing transcription_data directory
# if ! tmux has-session -t sync-transcription 2>/dev/null; then
#     tmux new-session -d -s sync-transcription
#     tmux send-keys -t sync-transcription "git pull && while true; do rsync -avh --progress $HOME_DIR/AutoPublishDATA/transcription_data/ $HOME_DIR/jianguoyun/AutoPublishDATA/transcription_data/; sleep 10; done" 
# fi

# Create the 'autopub-manual' session, cd to Projects/autopub_monitor, and activate Conda environment
if tmux has-session -t autopub-manual 2>/dev/null; then
    echo "Session autopub-manual already exists."
else
    tmux new-session -d -s autopub-manual
    tmux send-keys -t autopub-manual "cd $HOME_DIR/Projects/autopub_monitor" C-m
    tmux send-keys -t autopub-manual "conda activate lazyedit" C-m
    tmux send-keys -t autopub-manual "python autopub.py --use-cache --use-translation-cache --use-metadata-cache --force"
fi

############################
# The new 'lll' session for public_server_tornado.py
############################
SESSION_NAME="lll"       # name of the session
PROJECT_DIR="$HOME_DIR/Projects/lll"
CONDA_ENV_NAME="lll"

if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo "Session '$SESSION_NAME' already exists."
else
    echo "Creating tmux session '$SESSION_NAME'..."
    # Create a new detached tmux session
    tmux new-session -d -s "$SESSION_NAME"

    # Navigate to the project directory
    tmux send-keys -t "$SESSION_NAME" "cd $PROJECT_DIR" C-m

    # Activate the conda environment
    tmux send-keys -t "$SESSION_NAME" "conda activate $CONDA_ENV_NAME" C-m

    # Run your Tornado public server
    tmux send-keys -t "$SESSION_NAME" "python local_server_tornado.py" C-m

    echo "Session '$SESSION_NAME' created. local_server_tornado.py is launching."
fi

