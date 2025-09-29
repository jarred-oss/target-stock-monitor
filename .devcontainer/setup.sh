#!/bin/bash
echo "🚀 Setting up Target Monitor environment..."

# Update system
sudo apt update -y

# Install Chrome
echo "📦 Installing Google Chrome..."
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update -y
sudo apt install -y google-chrome-stable

# Install ChromeDriver
echo "🔧 Installing ChromeDriver..."
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+')
CHROME_MAJOR_VERSION=$(echo $CHROME_VERSION | cut -d. -f1)

# Get the latest ChromeDriver version for this Chrome version
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_MAJOR_VERSION}")
wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
sudo unzip /tmp/chromedriver.zip -d /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
rm /tmp/chromedriver.zip

# Install Python requirements
echo "🐍 Installing Python packages..."
pip install -r requirements.txt

# Make scripts executable
chmod +x start_monitor.py
chmod +x target_monitor.py

echo "✅ Setup complete! Ready to run target monitor."
echo ""
echo "Next steps:"
echo "1. Set your Discord webhook: export DISCORD_WEBHOOK_URL='your_webhook_here'"
echo "2. Run the monitor: python3 start_monitor.py"
