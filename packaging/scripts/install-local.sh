#!/bin/bash
#
# Local installation script for testing (without building .deb)
# This simulates what the package installation would do
#
# Usage: sudo ./install-local.sh
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"

if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo ./install-local.sh)"
    exit 1
fi

echo "=== Installing opennebula-cognit-frontend locally ==="

# Create oneadmin user/group if they don't exist
if ! getent group oneadmin > /dev/null; then
    groupadd -r oneadmin
    echo "Created oneadmin group"
fi

if ! getent passwd oneadmin > /dev/null; then
    useradd -r -g oneadmin -d /var/lib/one -s /bin/bash oneadmin
    mkdir -p /var/lib/one
    chown oneadmin:oneadmin /var/lib/one
    echo "Created oneadmin user"
fi

# Create directories
echo "Creating directories..."
mkdir -p /usr/lib/one/cognit-frontend
mkdir -p /usr/share/one/cognit-frontend
mkdir -p /etc/one
mkdir -p /var/log/one

# Install Python source
echo "Installing Python source files..."
cp -a "${PROJECT_DIR}/src/"*.py /usr/lib/one/cognit-frontend/

# Create and install Python venv
echo "Creating Python virtual environment..."
python3 -m venv /usr/share/one/cognit-frontend/python-venv
/usr/share/one/cognit-frontend/python-venv/bin/pip install --upgrade pip
/usr/share/one/cognit-frontend/python-venv/bin/pip install -r "${PROJECT_DIR}/requirements.txt"

# Install configuration
echo "Installing configuration..."
cp -a "${PROJECT_DIR}/share/etc/cognit-frontend.conf" /etc/one/

# Install systemd service
echo "Installing systemd service..."
cp -a "${PROJECT_DIR}/packaging/systemd/opennebula-cognit-frontend.service" /lib/systemd/system/

# Install logrotate
echo "Installing logrotate configuration..."
cp -a "${PROJECT_DIR}/packaging/logrotate/opennebula-cognit-frontend" /etc/logrotate.d/

# Set permissions
echo "Setting permissions..."
chown -R root:oneadmin /usr/lib/one/cognit-frontend
chmod 0750 /usr/lib/one/cognit-frontend
find /usr/lib/one/cognit-frontend -type f -name "*.py" -exec chmod 0750 {} \;

chown -R root:oneadmin /usr/share/one/cognit-frontend
chmod -R 0755 /usr/share/one/cognit-frontend

chown root:oneadmin /etc/one/cognit-frontend.conf
chmod 0640 /etc/one/cognit-frontend.conf

chown oneadmin:oneadmin /var/log/one

# Enable and start service
echo "Enabling and starting service..."
systemctl daemon-reload
systemctl enable opennebula-cognit-frontend
systemctl start opennebula-cognit-frontend

echo ""
echo "=== Installation complete ==="
echo ""
echo "Service status:"
systemctl status opennebula-cognit-frontend --no-pager || true
echo ""
echo "Test the API:"
echo "  curl http://localhost:1338/docs"

