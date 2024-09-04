import yaml
import os

PATH = "/etc/cognit-frontend.conf"
DEFAULT = {
    'host': '0.0.0.0',
    'port': 1338,
    'one_xmlrpc': 'http://localhost:2633/RPC2',
    'ai_orchestrator_endpoint': 'http://localhost:4567',
    'log_level': 'info'
}

FALLBACK_MSG = 'Using default configuration'


if os.path.exists(PATH):
    with open(PATH, 'r') as file:
        try:
            user_config = yaml.safe_load(file)
            if user_config is None:
                user_config = {}
        except yaml.YAMLError as e:
            print(f"{e}\n{FALLBACK_MSG}")
            config = DEFAULT
else:
    print(f"{PATH} not found. {FALLBACK_MSG}.")
    config = DEFAULT

config = DEFAULT.copy()
config.update(user_config)

HOST = config['host']
PORT = config['port']
ONE_XMLRPC = config['one_xmlrpc']
LOG_LEVEL = config['log_level']
AI_ORCHESTRATOR_ENDPOINT = config['ai_orchestrator_endpoint']
