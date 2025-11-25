import yaml
import os
import socket
import sys
from urllib.parse import urlparse

# Try multiple config paths
CONFIG_PATHS = [
    "/etc/one/cognit-frontend.conf",
    "/etc/cognit-frontend.conf"
]

DEFAULT = {
    'host': '0.0.0.0',
    'port': 1338,
    'one_xmlrpc': 'http://localhost:2633/RPC2',
    'ai_orchestrator_endpoint': 'http://localhost:4567',
    'default_cluster': 0,
    'log_level': 'info'
}

FALLBACK_MSG = 'Using default configuration'

# Start with default config
config = DEFAULT.copy()
user_config = {}

# Try to load config from available paths
for PATH in CONFIG_PATHS:
    if os.path.exists(PATH):
        with open(PATH, 'r') as file:
            try:
                user_config = yaml.safe_load(file)
                if not isinstance(user_config, dict):
                    user_config = {}
                print(f"Loaded configuration from {PATH}")
                break
            except yaml.YAMLError as e:
                print(f"{e}\n{FALLBACK_MSG}")
        break
else:
    print(f"No config file found. {FALLBACK_MSG}.")

# Update config with user settings
config.update(user_config)

ONE_XMLRPC = config['one_xmlrpc']

one = urlparse(ONE_XMLRPC)
port = one.port

if one.port is None:
    if one.scheme == 'https':
        port = 443
    elif one.scheme == 'http':
        port = 80

# Try to connect to OpenNebula, but don't exit if it fails (just warn)
try:
    socket.create_connection((one.hostname, port), timeout=5)
except socket.error as e:
    print(f"Warning: Unable to connect to OpenNebula at {ONE_XMLRPC}. {str(e)}")
    print("Service will start but OpenNebula operations may fail.")

HOST = config['host']
PORT = config['port']
LOG_LEVEL = config['log_level']
AI_ORCHESTRATOR_ENDPOINT = config['ai_orchestrator_endpoint']
DEFAULT_CLUSTER = config['default_cluster']