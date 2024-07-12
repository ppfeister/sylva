from configparser import ConfigParser
from platformdirs import user_config_dir
from os.path import isfile
from os import makedirs

from .__init__ import __short_name__

__config_dir = user_config_dir("ohshint")
__config_path = f"{__config_dir}/config.ini"

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
        "HIBP": check_option("API", "HIBP"),
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
