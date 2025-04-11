#!/bin/bash

# install_lazyedit.sh - Script to install and set up the LazyEdit service
# Creates the systemd service and installs required packages

# Define current directory and conda environment
CURRENT_DIR=$(pwd)
CONDA_ENV="lazyedit"
echo "Installing LazyEdit from directory: $CURRENT_DIR"

# 1. Install required packages
echo "Installing required packages..."
sudo apt-get update
sudo apt-get install -y ffmpeg tmux

# 2. Check if conda environment exists
echo "Checking conda environment..."
source ~/miniconda3/etc/profile.d/conda.sh 2>/dev/null || source ~/anaconda3/etc/profile.d/conda.sh 2>/dev/null || echo "Warning: Could not find conda.sh"

if conda info --envs 2>/dev/null | grep -q "$CONDA_ENV"; then
    echo "Conda environment '$CONDA_ENV' already exists."
else
    echo "Creating conda environment '$CONDA_ENV'..."
    conda create -y -n "$CONDA_ENV" python=3.10
    echo "Note: You may need to manually install packages in the conda environment."
    echo "For example: conda activate $CONDA_ENV && pip install -r requirements.txt"
fi

# 3. Make scripts executable
echo "Setting executable permissions..."
chmod +x "$CURRENT_DIR/start_lazyedit.sh"

# 4. Create the systemd service file
echo "Creating systemd service..."
SERVICE_FILE="/etc/systemd/system/lazyedit.service"

echo "[Unit]
Description=LazyEdit Video Processing
After=network.target

[Service]
Type=forking
User=$(whoami)
WorkingDirectory=$CURRENT_DIR
ExecStart=/bin/bash -lc '$CURRENT_DIR/start_lazyedit.sh'

[Install]
WantedBy=multi-user.target" | sudo tee $SERVICE_FILE

# 5. Reload systemd, enable and start the service
echo "Configuring systemd service..."
sudo systemctl daemon-reload
sudo systemctl enable lazyedit.service
sudo systemctl start lazyedit.service

echo "LazyEdit installation complete. Service has been started."
echo "You can check status with: sudo systemctl status lazyedit.service"

# Note: If you need to update paths in start_lazyedit.sh, you can run the following commands:
# cp "$CURRENT_DIR/start_lazyedit.sh" "$CURRENT_DIR/start_lazyedit.sh.bak"
# sed -i "s|/home/lachlan/ProjectsLFS/lazyedit|$CURRENT_DIR|g" "$CURRENT_DIR/start_lazyedit.sh"
