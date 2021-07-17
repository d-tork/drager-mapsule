from os import path
import yaml

PROJ_PATH = path.normpath(path.join(path.dirname(path.realpath(__file__)), '..'))
CONFIG_PATH = path.join(PROJ_PATH, 'config')


def read_keys_file():
    keys_path = path.join(CONFIG_PATH, 'keys.yaml')
    with open(keys_path, 'r') as f:
        return yaml.safe_load(f)


keys = read_keys_file()
