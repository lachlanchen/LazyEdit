#!/bin/bash
# install_chrome_driver_for_selenium.sh
# Automatically installs Chrome/Chromium, the matching driver, and sets up aliases
# Usage: ./install_chrome_driver_for_selenium.sh [chrome|chromium] [--display=:X]

set -e  # Exit on error

# Function to display usage
usage() {
    echo "Usage: $0 [chrome|chromium] [--display=:X]"
    echo "  chrome|chromium - Browser to install (default: chrome)"
    echo "  --display=:X    - X display to use (default: :0)"
    echo "Examples:"
    echo "  $0                      # Install Chrome with display :0"
    echo "  $0 chromium             # Install Chromium with display :0"
    echo "  $0 chrome --display=:1  # Install Chrome with display :1"
}

# Function to install Chrome
install_chrome() {
    echo "=== Installing Google Chrome ==="
    
    # Check if Chrome is already installed
    if command -v google-chrome &> /dev/null; then
        echo "Google Chrome is already installed."
    else
        echo "Adding Google Chrome repository..."
        wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg
        echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list > /dev/null
        
        echo "Updating package lists..."
        sudo apt update
        
        echo "Installing Google Chrome..."
        sudo apt install -y google-chrome-stable
    fi
}

# Function to install Chromium
install_chromium() {
    echo "=== Installing Chromium ==="
    
    # Check if Chromium is already installed
    if command -v chromium-browser &> /dev/null; then
        echo "Chromium is already installed."
    else
        echo "Installing Chromium..."
        sudo apt update
        sudo apt install -y chromium-browser
    fi
}

# Function to get Chrome version
get_chrome_version() {
    echo "=== Detecting Chrome version ==="
    CHROME_VERSION=$(google-chrome --version | cut -d ' ' -f 3)
    echo "Detected Google Chrome version: $CHROME_VERSION"
}

# Function to get Chromium version
get_chromium_version() {
    echo "=== Detecting Chromium version ==="
    CHROMIUM_VERSION=$(chromium-browser --version | cut -d ' ' -f 2)
    echo "Detected Chromium version: $CHROMIUM_VERSION"
}

# Function to download Chrome Driver
download_chrome_driver() {
    echo "=== Downloading Chrome Driver for version $CHROME_VERSION ==="
    
    # Download the appropriate driver
    wget -q -O chromedriver.zip "https://storage.googleapis.com/chrome-for-testing-public/$CHROME_VERSION/linux64/chromedriver-linux64.zip"
    
    # Unzip the driver
    unzip -q -o chromedriver.zip
    
    # Move to /usr/local/bin
    sudo mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver
    sudo chmod +x /usr/local/bin/chromedriver
    
    # Clean up
    rm -rf chromedriver.zip chromedriver-linux64
    
    echo "Chrome Driver installed to /usr/local/bin/chromedriver"
}

# Function to download Chromium Driver (uses chrome driver underneath)
download_chromium_driver() {
    echo "=== Downloading Chromium Driver for version $CHROMIUM_VERSION ==="
    
    # Download the appropriate driver
    # Note: For newer versions, Chromium uses the same driver as Chrome
    wget -q -O chromedriver.zip "https://storage.googleapis.com/chrome-for-testing-public/$CHROMIUM_VERSION/linux64/chromedriver-linux64.zip"
    
    # Unzip the driver
    unzip -q -o chromedriver.zip
    
    # Move to /usr/local/bin
    sudo mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver
    sudo chmod +x /usr/local/bin/chromedriver
    
    # Create a symlink for chromium-driver if it doesn't exist
    if [ ! -f /usr/local/bin/chromium-driver ]; then
        sudo ln -s /usr/local/bin/chromedriver /usr/local/bin/chromium-driver
    fi
    
    # Clean up
    rm -rf chromedriver.zip chromedriver-linux64
    
    echo "Chromium Driver installed to /usr/local/bin/chromedriver with symlink at /usr/local/bin/chromium-driver"
}

# Function to set up the aliases
setup_chrome_aliases() {
    echo "=== Setting up Chrome aliases with display $DISPLAY_NUM ==="
    
    # Create the scripts directory if it doesn't exist
    mkdir -p ~/scripts
    
    # Create the aliases file with the specified display
    cat > ~/scripts/chrome_aliases.sh << EOF
#!/bin/bash
# Chrome aliases for various platforms
# Generated by install_chrome_driver_for_selenium.sh

# Create logs directory if it doesn't exist
mkdir -p "\$HOME/chrome_dev_session_logs"

# Chrome aliases with DISPLAY=$DISPLAY_NUM
alias start_chrome_xhs='DISPLAY=$DISPLAY_NUM google-chrome --hide-crash-restore-bubble --remote-debugging-port=5003 --user-data-dir="\$HOME/chrome_dev_session_5003" https://creator.xiaohongshu.com/creator/post > "\$HOME/chrome_dev_session_logs/chrome_xhs.log" 2>&1'
alias start_chrome_douyin='DISPLAY=$DISPLAY_NUM google-chrome --hide-crash-restore-bubble --remote-debugging-port=5004 --user-data-dir="\$HOME/chrome_dev_session_5004" https://creator.douyin.com/creator-micro/content/upload > "\$HOME/chrome_dev_session_logs/chrome_douyin.log" 2>&1'
alias start_chrome_bilibili='DISPLAY=$DISPLAY_NUM google-chrome --hide-crash-restore-bubble --remote-debugging-port=5005 --user-data-dir="\$HOME/chrome_dev_session_5005" https://member.bilibili.com/platform/upload/video/frame > "\$HOME/chrome_dev_session_logs/chrome_bilibili.log" 2>&1'
alias start_chrome_shipinhao='DISPLAY=$DISPLAY_NUM google-chrome --hide-crash-restore-bubble --remote-debugging-port=5006 --user-data-dir="\$HOME/chrome_dev_session_5006" https://channels.weixin.qq.com/post/create > "\$HOME/chrome_dev_session_logs/chrome_shipinhao.log" 2>&1'
alias start_chrome_youtube='DISPLAY=$DISPLAY_NUM google-chrome --hide-crash-restore-bubble --remote-debugging-port=9222 --user-data-dir="\$HOME/chrome_dev_session_9222" https://youtube.com/upload > "\$HOME/chrome_dev_session_logs/chrome_youtube.log" 2>&1'
alias start_chrome_without_y2b='start_chrome_xhs & start_chrome_douyin & start_chrome_bilibili'
alias start_chrome_all='start_chrome_xhs & start_chrome_douyin & start_chrome_bilibili & start_chrome_shipinhao & start_chrome_youtube'
EOF
    
    # Make the file executable
    chmod +x ~/scripts/chrome_aliases.sh
    
    # Check if already sourced in .bashrc
    if ! grep -q "source ~/scripts/chrome_aliases.sh" ~/.bashrc; then
        echo "# Source Chrome aliases" >> ~/.bashrc
        echo "source ~/scripts/chrome_aliases.sh" >> ~/.bashrc
        echo "Added source command to ~/.bashrc"
    else
        echo "Chrome aliases already sourced in ~/.bashrc"
    fi
    
    # Source the file in the current session
    source ~/scripts/chrome_aliases.sh
    
    echo "Chrome aliases have been set up and are ready to use"
}

# Function to set up the aliases for Chromium
setup_chromium_aliases() {
    echo "=== Setting up Chromium aliases with display $DISPLAY_NUM ==="
    
    # Create the scripts directory if it doesn't exist
    mkdir -p ~/scripts
    
    # Create the aliases file with the specified display
    cat > ~/scripts/chromium_aliases.sh << EOF
#!/bin/bash
# Chromium aliases for various platforms
# Generated by install_chrome_driver_for_selenium.sh

# Create logs directory if it doesn't exist
mkdir -p "\$HOME/chromium_dev_session_logs"

# Chromium aliases with DISPLAY=$DISPLAY_NUM
alias start_chromium_xhs='DISPLAY=$DISPLAY_NUM chromium-browser --hide-crash-restore-bubble --remote-debugging-port=5003 --user-data-dir="\$HOME/chromium_dev_session_5003" https://creator.xiaohongshu.com/creator/post > "\$HOME/chromium_dev_session_logs/chromium_xhs.log" 2>&1'
alias start_chromium_douyin='DISPLAY=$DISPLAY_NUM chromium-browser --hide-crash-restore-bubble --remote-debugging-port=5004 --user-data-dir="\$HOME/chromium_dev_session_5004" https://creator.douyin.com/creator-micro/content/upload > "\$HOME/chromium_dev_session_logs/chromium_douyin.log" 2>&1'
alias start_chromium_bilibili='DISPLAY=$DISPLAY_NUM chromium-browser --hide-crash-restore-bubble --remote-debugging-port=5005 --user-data-dir="\$HOME/chromium_dev_session_5005" https://member.bilibili.com/platform/upload/video/frame > "\$HOME/chromium_dev_session_logs/chromium_bilibili.log" 2>&1'
alias start_chromium_shipinhao='DISPLAY=$DISPLAY_NUM chromium-browser --hide-crash-restore-bubble --remote-debugging-port=5006 --user-data-dir="\$HOME/chromium_dev_session_5006" https://channels.weixin.qq.com/post/create > "\$HOME/chromium_dev_session_logs/chromium_shipinhao.log" 2>&1'
alias start_chromium_youtube='DISPLAY=$DISPLAY_NUM chromium-browser --hide-crash-restore-bubble --remote-debugging-port=9222 --user-data-dir="\$HOME/chromium_dev_session_9222" https://youtube.com/upload > "\$HOME/chromium_dev_session_logs/chromium_youtube.log" 2>&1'
alias start_chromium_without_y2b='start_chromium_xhs & start_chromium_douyin & start_chromium_bilibili'
alias start_chromium_all='start_chromium_xhs & start_chromium_douyin & start_chromium_bilibili & start_chromium_shipinhao & start_chromium_youtube'
EOF
    
    # Make the file executable
    chmod +x ~/scripts/chromium_aliases.sh
    
    # Check if already sourced in .bashrc
    if ! grep -q "source ~/scripts/chromium_aliases.sh" ~/.bashrc; then
        echo "# Source Chromium aliases" >> ~/.bashrc
        echo "source ~/scripts/chromium_aliases.sh" >> ~/.bashrc
        echo "Added source command to ~/.bashrc"
    else
        echo "Chromium aliases already sourced in ~/.bashrc"
    fi
    
    # Source the file in the current session
    source ~/scripts/chromium_aliases.sh
    
    echo "Chromium aliases have been set up and are ready to use"
}

# Function to verify installation
verify_installation() {
    echo "=== Verifying installation ==="
    
    # Check if Chrome/Chromium is installed
    if [ "$BROWSER_TYPE" = "chrome" ]; then
        if ! command -v google-chrome &> /dev/null; then
            echo "ERROR: Google Chrome is not installed properly"
            exit 1
        fi
        echo "✓ Google Chrome is installed"
    else
        if ! command -v chromium-browser &> /dev/null; then
            echo "ERROR: Chromium is not installed properly"
            exit 1
        fi
        echo "✓ Chromium is installed"
    fi
    
    # Check if the driver is installed
    if ! command -v chromedriver &> /dev/null; then
        echo "ERROR: Chrome Driver is not installed properly"
        exit 1
    fi
    echo "✓ Chrome Driver is installed"
    
    # Verify driver version matches browser version
    if [ "$BROWSER_TYPE" = "chrome" ]; then
        CHROME_CURRENT_VERSION=$(google-chrome --version | cut -d ' ' -f 3)
        DRIVER_VERSION=$(chromedriver --version | cut -d ' ' -f 2)
        
        if [[ "$DRIVER_VERSION" == "$CHROME_CURRENT_VERSION"* ]]; then
            echo "✓ Chrome Driver version $DRIVER_VERSION matches Chrome version $CHROME_CURRENT_VERSION"
        else
            echo "WARNING: Chrome Driver version ($DRIVER_VERSION) might not match Chrome version ($CHROME_CURRENT_VERSION)"
        fi
    else
        CHROMIUM_CURRENT_VERSION=$(chromium-browser --version | cut -d ' ' -f 2)
        DRIVER_VERSION=$(chromedriver --version | cut -d ' ' -f 2)
        
        if [[ "$DRIVER_VERSION" == "$CHROMIUM_CURRENT_VERSION"* ]]; then
            echo "✓ Chrome Driver version $DRIVER_VERSION matches Chromium version $CHROMIUM_CURRENT_VERSION"
        else
            echo "WARNING: Chrome Driver version ($DRIVER_VERSION) might not match Chromium version ($CHROMIUM_CURRENT_VERSION)"
        fi
    fi
    
    # Check if aliases are set up
    if [ "$BROWSER_TYPE" = "chrome" ]; then
        if ! type start_chrome_youtube &> /dev/null; then
            echo "WARNING: Chrome aliases are not loaded in the current session"
            echo "Please run: source ~/.bashrc"
        else
            echo "✓ Chrome aliases are set up correctly"
        fi
    else
        if ! type start_chromium_youtube &> /dev/null; then
            echo "WARNING: Chromium aliases are not loaded in the current session"
            echo "Please run: source ~/.bashrc"
        else
            echo "✓ Chromium aliases are set up correctly"
        fi
    fi
    
    echo ""
    echo "Installation completed successfully!"
    if [ "$BROWSER_TYPE" = "chrome" ]; then
        echo "You can now use the following commands:"
        echo "  start_chrome_xhs       - Start Chrome for Xiaohongshu"
        echo "  start_chrome_douyin    - Start Chrome for Douyin"
        echo "  start_chrome_bilibili  - Start Chrome for Bilibili"
        echo "  start_chrome_shipinhao - Start Chrome for Shipinhao"
        echo "  start_chrome_youtube   - Start Chrome for YouTube"
        echo "  start_chrome_without_y2b - Start Chrome for all except YouTube"
        echo "  start_chrome_all       - Start Chrome for all platforms"
    else
        echo "You can now use the following commands:"
        echo "  start_chromium_xhs       - Start Chromium for Xiaohongshu"
        echo "  start_chromium_douyin    - Start Chromium for Douyin"
        echo "  start_chromium_bilibili  - Start Chromium for Bilibili"
        echo "  start_chromium_shipinhao - Start Chromium for Shipinhao"
        echo "  start_chromium_youtube   - Start Chromium for YouTube"
        echo "  start_chromium_without_y2b - Start Chromium for all except YouTube"
        echo "  start_chromium_all       - Start Chromium for all platforms"
    fi
    
    echo ""
    echo "Using display: $DISPLAY_NUM"
    echo "Note: If the aliases aren't available, run 'source ~/.bashrc' to load them"
}

# Default values
BROWSER_TYPE="chrome"
DISPLAY_NUM=":0"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        chrome|chromium)
            BROWSER_TYPE="$1"
            shift
            ;;
        --display=*)
            DISPLAY_NUM="${1#*=}"
            shift
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Main execution
echo "Installing $BROWSER_TYPE and its WebDriver..."
echo "Using display: $DISPLAY_NUM"

# Install the selected browser
if [ "$BROWSER_TYPE" = "chrome" ]; then
    install_chrome
    get_chrome_version
    download_chrome_driver
    setup_chrome_aliases
else
    install_chromium
    get_chromium_version
    download_chromium_driver
    setup_chromium_aliases
fi

# Verify installation
verify_installation

echo "Done!"
