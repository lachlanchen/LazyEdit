#!/bin/bash

# Check if the tmux session 'lazyedit' already exists
tmux has-session -t lazyedit 2>/dev/null

# Check the exit status of the previous command
if [ $? != 0 ]; then
    # If the session does not exist, create it
    tmux new -d -s lazyedit

    # Wait a bit to ensure that commands are sent after the session is properly set up
    sleep 2

    # Activate the 'autopub-video' conda environment
    # tmux send-keys -t lazyedit "conda activate autopub-video" C-m
    tmux send-keys -t lazyedit "conda activate lazyedit" C-m

    # Wait for the conda environment to activate
    sleep 5

    # Change directory to the project folder
    tmux send-keys -t lazyedit "cd /home/lachlan/ProjectsLFS/lazyedit/" C-m

    # Execute the script
    tmux send-keys -t lazyedit "python app.py -m lazyedit" C-m
else
    echo "Tmux session 'lazyedit' already exists."
fi

