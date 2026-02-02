# Packaging for opennebula-cognit-frontend

This directory contains all files needed to build the `opennebula-cognit-frontend` Debian package.

## Directory Structure

```
packaging/
├── debian/              # Debian packaging files
│   ├── changelog        # Package changelog
│   ├── compat           # Debhelper compatibility level
│   ├── control          # Package metadata and dependencies
│   ├── copyright        # License information
│   ├── postinst         # Post-installation script
│   ├── postrm           # Post-removal script
│   ├── prerm            # Pre-removal script
│   └── rules            # Build rules
├── systemd/             # Systemd service files
│   └── opennebula-cognit-frontend.service
├── logrotate/           # Log rotation configuration
│   └── opennebula-cognit-frontend
├── scripts/             # Build and installation scripts
│   ├── build.sh         # Build .deb package
│   ├── install-local.sh # Install locally for testing
│   └── uninstall-local.sh
└── README.md            # This file
```

## Building the Package

### Prerequisites

Install build dependencies:

```bash
sudo apt-get install build-essential debhelper dh-python python3 python3-venv python3-pip
```

### Build

From the repository root:

```bash
./packaging/scripts/build.sh [version] [release]
```

Example:
```bash
./packaging/scripts/build.sh 1.0.0 1
```

The `.deb` package will be created in the parent directory.

### Install the Package

```bash
sudo dpkg -i ../opennebula-cognit-frontend_1.0.0-1_all.deb
```

## Local Testing (Without Building .deb)

For quick testing without building a full package:

```bash
# Install
sudo ./packaging/scripts/install-local.sh

# Test
curl http://localhost:1338/docs

# Uninstall
sudo ./packaging/scripts/uninstall-local.sh
```

## Package Details

### Installation Paths

| Path | Contents |
|------|----------|
| `/usr/lib/one/cognit-frontend/` | Python source files |
| `/usr/share/one/cognit-frontend/python-venv/` | Bundled Python virtual environment |
| `/etc/one/cognit-frontend.conf` | Configuration file |
| `/lib/systemd/system/opennebula-cognit-frontend.service` | Systemd service |
| `/etc/logrotate.d/opennebula-cognit-frontend` | Log rotation config |

### Service Management

```bash
# Start/stop/restart
sudo systemctl start opennebula-cognit-frontend
sudo systemctl stop opennebula-cognit-frontend
sudo systemctl restart opennebula-cognit-frontend

# Check status
sudo systemctl status opennebula-cognit-frontend

# View logs
sudo journalctl -u opennebula-cognit-frontend -f
```

### Configuration

Edit `/etc/one/cognit-frontend.conf`:

```yaml
host: 0.0.0.0
port: 1338
one_xmlrpc: http://localhost:2633/RPC2
ai_orchestrator_endpoint: http://localhost:4567
default_cluster: 0
log_level: info
```

After changing configuration, restart the service:

```bash
sudo systemctl restart opennebula-cognit-frontend
```

## Dependencies

The package depends on:
- `python3` (>= 3.11)
- `opennebula-common` (provides oneadmin user/group)

Python dependencies are bundled in the virtual environment and include:
- fastapi
- uvicorn
- pyyaml
- pyone
- requests
- biscuit-python
- pydantic
- lxml

