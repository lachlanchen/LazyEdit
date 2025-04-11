#!/bin/bash

# Create the script that starts tmux and runs the commands
echo '#!/bin/bash
sleep 10
tmux new -d -s autopub
tmux send-keys -t autopub "cd /home/lachlan/ProjectsLFS/autopub-video-processing/" C-m
tmux send-keys -t autopub "python app.py" C-m' > /home/lachlan/start_lazyedit.sh

# Make the script executable
chmod +x /home/lachlan/start_lazyedit.sh

# Create the systemd service file
echo '[Unit]
Description=Autopub Video Processing
After=network.target

[Service]
Type=simple
User=lachlan
ExecStart=/bin/bash /home/lachlan/start_lazyedit.sh

[Install]
WantedBy=multi-user.target' | sudo tee /etc/systemd/system/lazyedit.service

# Reload systemd, enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable lazyedit.service
sudo systemctl start lazyedit.service

