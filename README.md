# Target Stock Monitor

Monitors Target products for stock availability and sends Discord notifications.

## Quick Start

1. Launch Codespaces
2. Set your Discord webhook: `export DISCORD_WEBHOOK_URL="your_webhook_url"`
3. Run: `python3 start_monitor.py`

## Files
- `target_monitor.py` - Main monitoring script
- `start_monitor.py` - Smart scheduler (recommended)
- `setup.sh` - Environment setup script
- `.devcontainer/devcontainer.json` - Codespaces configuration

## Usage
- **Smart Scheduler**: `python3 start_monitor.py` (uses ~56 hours/month)
- **Continuous**: `python3 target_monitor.py` (uses hours faster)
