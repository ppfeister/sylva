import configparser
import os
import platformdirs
import subprocess

from . import __short_name__

__config_dir = platformdirs.user_config_dir(__short_name__.lower())
__config_path = f"{__config_dir}/config.ini"

class InteractiveConfig():
    def __init__(self):
        self.config = config
        self.config_path = get_config_path()
    def launch_preferred_editor(self):
        EDITOR = os.environ.get('EDITOR')
        if not EDITOR:
            print('$EDITOR is not set on your system.')
            print(f'{__short_name__} config may be edited manually at {self.config_path}')
            return
        try:
            subprocess.call([EDITOR, self.config_path])
        except FileNotFoundError as e:
            if e.filename == EDITOR:
                print(f'Failed to find preferred editor {EDITOR}')
                print(f'{__short_name__} config may be edited manually at {self.config_path}')
            elif e.filename == self.config_path:
                print(f'Unable to find {self.config_path}')
                print('This is highly unusual. Please report this issue.')
            else:
                raise e

def get_config_path() -> str:
    return __config_path

def check_option(section:str, key:str, default:str='') -> str:
    """Check the value of a config option.
    
    Returns the value of the option if it exists, otherwise returns an empty
    string or the value of 'default' if it is provided."""
    try:
        return config[section][key]
    except KeyError:
        return default

def new_config():
    print(f"Seems to be your first time using {__short_name__}. Let's create a config file for you.")
    os.makedirs(__config_dir, exist_ok=True)
    with open(__config_path, "x") as configfile:
        config.write(configfile)

def update_config():
    config["General"] = {
        "debug": check_option(section="General", key="debug", default="False"),
        "log_level": check_option(section="General", key="log_level", default="INFO"),
    }
    config["Cache"] = {
        "enabled": check_option(section="Cache", key="enabled", default="True"),
        "ttl": check_option(section="Cache", key="ttl", default="86400"),
    }
    config["Keys"] = {
        "HIBP": check_option(section="Keys", key="HIBP"),
    }
    with open(__config_path, "w") as configfile:
        config.write(configfile)

def load_config():
    if not os.path.isfile(__config_path):
        new_config()
    else:
        config.read(__config_path)
    update_config()


    return config

config = configparser.ConfigParser()
load_config()
