#!/bin/bash
#
# Uninstall script for local installation
#
# Usage: sudo ./uninstall-local.sh
#

set -e

if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo ./uninstall-local.sh)"
    exit 1
fi

echo "=== Uninstalling opennebula-cognit-frontend ==="

# Stop and disable service
echo "Stopping service..."
systemctl stop opennebula-cognit-frontend 2>/dev/null || true
systemctl disable opennebula-cognit-frontend 2>/dev/null || true

# Remove files
echo "Removing files..."
rm -f /lib/systemd/system/opennebula-cognit-frontend.service
rm -f /etc/logrotate.d/opennebula-cognit-frontend
rm -f /etc/one/cognit-frontend.conf
rm -rf /usr/lib/one/cognit-frontend
rm -rf /usr/share/one/cognit-frontend

# Reload systemd
systemctl daemon-reload

echo ""
echo "=== Uninstallation complete ==="
echo "Note: oneadmin user/group and /var/lib/one were preserved"

