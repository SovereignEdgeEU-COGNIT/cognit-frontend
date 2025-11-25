#!/bin/bash
#
# Build script for opennebula-cognit-frontend Debian package
#
# Usage: ./build.sh [version]
#   version: Package version (default: 1.0.0)
#
# Requirements:
#   - debhelper
#   - dh-python
#   - python3, python3-venv, python3-pip
#
# The resulting .deb package will be in the parent directory
#

set -e

VERSION="${1:-1.0.0}"
PKG_VERSION="${2:-1}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"

echo "=== Building opennebula-cognit-frontend ${VERSION}-${PKG_VERSION} ==="
echo "Project directory: ${PROJECT_DIR}"

# Check dependencies
for cmd in dpkg-buildpackage python3 pip; do
    if ! command -v $cmd &> /dev/null; then
        echo "ERROR: $cmd is required but not installed." >&2
        exit 1
    fi
done

cd "${PROJECT_DIR}"

# Create debian directory symlink if not exists
if [ ! -d debian ] && [ ! -L debian ]; then
    ln -s packaging/debian debian
fi

# Update changelog version
cat > packaging/debian/changelog << EOF
opennebula-cognit-frontend (${VERSION}-${PKG_VERSION}) unstable; urgency=medium

  * Build for version ${VERSION}-${PKG_VERSION}

 -- OpenNebula Systems <contact@opennebula.io>  $(date -R)
EOF

# Build the package
echo "=== Running dpkg-buildpackage ==="
dpkg-buildpackage -us -uc -b

echo ""
echo "=== Build complete ==="
echo "Package created in: $(dirname "${PROJECT_DIR}")"
ls -la "$(dirname "${PROJECT_DIR}")"/*.deb 2>/dev/null || echo "No .deb files found"

