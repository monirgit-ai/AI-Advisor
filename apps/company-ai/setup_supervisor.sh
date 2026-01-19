#!/bin/bash
# Setup script for Supervisor configuration

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
CONFIG_FILE="$PROJECT_DIR/supervisord.conf"
LOGS_DIR="$PROJECT_DIR/logs"

echo "Setting up Supervisor for Company AI Backend..."

# Create logs directory
echo "Creating logs directory..."
mkdir -p "$LOGS_DIR"
chmod 755 "$LOGS_DIR"

# Check if supervisor is installed
if ! command -v supervisord &> /dev/null; then
    echo "Supervisor is not installed. Installing..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y supervisor
    elif command -v pip3 &> /dev/null; then
        pip3 install supervisor
    else
        echo "Error: Cannot install supervisor. Please install it manually."
        exit 1
    fi
fi

# Check if running as root or with sudo
if [ "$EUID" -eq 0 ]; then
    # System-wide installation
    echo "Installing supervisor configuration system-wide..."
    sudo cp "$CONFIG_FILE" /etc/supervisor/conf.d/company-ai.conf
    sudo supervisorctl reread
    sudo supervisorctl update
    echo "Supervisor configuration installed successfully!"
    echo ""
    echo "To manage the service, use:"
    echo "  sudo supervisorctl status company-ai-backend"
    echo "  sudo supervisorctl start company-ai-backend"
    echo "  sudo supervisorctl stop company-ai-backend"
    echo "  sudo supervisorctl restart company-ai-backend"
else
    # User-level installation
    echo "Installing supervisor configuration for user..."
    echo "Note: For production, consider using system-wide installation with sudo"
    
    # Test configuration
    if supervisord -c "$CONFIG_FILE" -t; then
        echo "Configuration is valid!"
        echo ""
        echo "To start supervisor, run:"
        echo "  supervisord -c $CONFIG_FILE"
        echo ""
        echo "To manage the service, use:"
        echo "  supervisorctl -c $CONFIG_FILE status"
        echo "  supervisorctl -c $CONFIG_FILE start company-ai-backend"
    else
        echo "Error: Configuration validation failed"
        exit 1
    fi
fi

echo ""
echo "Setup complete! See SUPERVISOR_SETUP.md for detailed instructions."
