#!/bin/bash

# install_lazyedit.sh - Script to install and set up the LazyEdit service
# Creates the systemd service, config file and installs required packages

# Define current directory and user
CURRENT_DIR=$(pwd)
CURRENT_USER=$(whoami)
CONDA_ENV="lazyedit"

echo "Installing LazyEdit from directory: $CURRENT_DIR"

# 1. Install required packages
echo "Installing required packages..."
sudo apt-get update
sudo apt-get install -y ffmpeg tmux

# 2. Detect conda path
echo "Detecting conda installation..."
if [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
    CONDA_PATH="$HOME/miniconda3/etc/profile.d/conda.sh"
elif [ -f "$HOME/anaconda3/etc/profile.d/conda.sh" ]; then
    CONDA_PATH="$HOME/anaconda3/etc/profile.d/conda.sh"
else
    echo "Warning: Could not find conda.sh. Please update the config file manually."
    CONDA_PATH=""
fi

# 3. Create config file
echo "Creating config file..."
cat > "$CURRENT_DIR/lazyedit_config.sh" << EOF
#!/bin/bash

# LazyEdit configuration file - automatically generated

# Project paths
LAZYEDIT_DIR="$CURRENT_DIR"
LAZYEDIT_USER="$CURRENT_USER"

# Python/Conda settings
CONDA_PATH="$CONDA_PATH"
CONDA_ENV="$CONDA_ENV"

# App settings
APP_ARGS="-m lazyedit"

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

chmod +x "$CURRENT_DIR/lazyedit_config.sh"
echo "Config file created at $CURRENT_DIR/lazyedit_config.sh"

# 4. Update the start_lazyedit.sh script
echo "Updating start_lazyedit.sh..."
cat > "$CURRENT_DIR/start_lazyedit.sh" << EOF
#!/bin/bash

# Source the config file
SCRIPT_DIR=\$(dirname "\$(readlink -f "\$0")")
source "\$SCRIPT_DIR/lazyedit_config.sh"

# Check if the tmux session 'lazyedit' already exists
tmux has-session -t lazyedit 2>/dev/null

# Check the exit status of the previous command
if [ \$? != 0 ]; then
    # If the session does not exist, create it
    tmux new -d -s lazyedit

    # Wait a bit to ensure that commands are sent after the session is properly set up
    sleep 2

    # Activate the conda environment using the function from config
    tmux send-keys -t lazyedit "cd \$LAZYEDIT_DIR" C-m
    tmux send-keys -t lazyedit "source \$CONDA_PATH" C-m
    tmux send-keys -t lazyedit "conda activate \$CONDA_ENV" C-m

    # Wait for the conda environment to activate
    sleep 5

    # Execute the script
    tmux send-keys -t lazyedit "cd \$LAZYEDIT_DIR" C-m
    tmux send-keys -t lazyedit "python app.py \$APP_ARGS" C-m
else
    echo "Tmux session 'lazyedit' already exists."
fi
EOF

chmod +x "$CURRENT_DIR/start_lazyedit.sh"
echo "Updated start_lazyedit.sh with configuration"

# 5. Create the systemd service file
echo "Creating systemd service..."
SERVICE_FILE="/etc/systemd/system/lazyedit.service"

echo "[Unit]
Description=LazyEdit Video Processing
After=network.target

[Service]
Type=forking
User=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR
ExecStart=/bin/bash -lc '$CURRENT_DIR/start_lazyedit.sh'

[Install]
WantedBy=multi-user.target" | sudo tee $SERVICE_FILE

# 6. Reload systemd, enable and start the service
echo "Configuring systemd service..."
sudo systemctl daemon-reload
sudo systemctl enable lazyedit.service

# 7. Offer to start the service
echo "Would you like to start the lazyedit service now? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    sudo systemctl restart lazyedit.service
    echo "Service started. Check status with: sudo systemctl status lazyedit.service"
else
    echo "Service installation complete but not started."
    echo "Start manually with: sudo systemctl start lazyedit.service"
fi

echo "LazyEdit installation complete."
echo "You can check status with: sudo systemctl status lazyedit.service"
echo "View logs with: sudo journalctl -u lazyedit.service"
