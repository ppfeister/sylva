from argparse import Action as ArgparseAction
from configparser import ConfigParser
from platformdirs import user_config_dir
from os.path import isfile
from os import makedirs, environ
from subprocess import call

from .__init__ import __short_name__

__config_dir = user_config_dir(__short_name__.lower())
__config_path = f"{__config_dir}/config.ini"

class InteractiveConfig():
    def __init__(self):
        self.config = config
        self.config_path = get_config_path()
    def launch_preferred_editor(self):
        EDITOR = environ.get('EDITOR')
        if not EDITOR:
            print('$EDITOR is not set on your system.')
            print(f'{__short_name__} config may be edited manually at {self.config_path}')
            return
        try:
            call([EDITOR, self.config_path])
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

def check_option(section: str, key: str) -> str:
    try:
        return config[section][key]
    except KeyError:
        return ''

def new_config():
    print(f"Seems to be your first time using {__short_name__}. Let's create a config file for you.")
    makedirs(__config_dir, exist_ok=True)
    with open(__config_path, "x") as configfile:
        config.write(configfile)

def update_config():
    config["General"] = {
        "debug": "False",
        "log_level": "INFO",
    }
    if not config.has_section("API"):
        config.add_section("API")
    config["API"] = {
        "HIBP": check_option(section="API", key="HIBP"),
    }
    with open(__config_path, "w") as configfile:
        config.write(configfile)

def load_config():
    if not isfile(__config_path):
        new_config()
    else:
        config.read(__config_path)
    update_config()


    return config

config = ConfigParser()
load_config()
