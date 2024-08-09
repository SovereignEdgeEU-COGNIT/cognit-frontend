import yaml
import os

PATH = "/etc/cognit-frontend.conf"
DEFAULT = {
    'host': '0.0.0.0',
    'port': 1337,
    'one_xmlrpc': 'http://localhost:2633/RPC2'
}


def load():
    if os.path.exists(PATH):
        with open(PATH, 'r') as file:
            try:
                user_config = yaml.safe_load(file)
                if user_config is None:
                    user_config = {}
            except yaml.YAMLError:
                print(
                    f"Error reading {PATH}. Using default configuration.")
                return DEFAULT
    else:
        print(f"{PATH} not found. Using default configuration.")
        return DEFAULT

    config = DEFAULT.copy()
    config.update(user_config)

    return config
