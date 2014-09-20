from __future__ import print_function

import os
import copy

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

from fabric.api import local, task, lcd
from fabric.colors import red


FILE_ROOT = os.path.abspath(os.path.dirname(__file__))
CONFIG_FILE_PATH = "{}{}".format(FILE_ROOT, "/call_congress.config")

DEVELOPMENT_ENV = "development"
PRODUCTION_ENV = "production"

DEVELOPMENT_ENV_VARIABLES = [
    "SUNLIGHTLABS_KEY",
    "TWILIO_ACCOUNT_SID",
    "TWILIO_AUTH_TOKEN",
    "TW_NUMBER",
    "REDISTOGO_URL"
]

PRODUCTION_ENV_VARIABLES = [
    "SUNLIGHTLABS_KEY",
    "TWILIO_ACCOUNT_SID",
    "TWILIO_AUTH_TOKEN",
    "APPLICATION_ROOT",
    "REDISTOGO_URL",
    "TASKFORCE_KEY",
]

@task
def create_env():
    """
    Sets up the virtualenv and downloads the dependencies with pip and creates
    a default config file
    """
    local("virtualenv venv")
    # When using pip install it complained about the mysql-connector-python lib
    # not being in a standard location
    virtualenv("pip install -r requirements.txt --allow-external " + \
               "mysql-connector-python")

    if not os.path.isfile(CONFIG_FILE_PATH):
        generate_example_config()

@task
def run(env=None):
    """
    Runs the application in a specified environment
    """
    if env is None:
        print(red("[Warning] ") + "No environment specified.")
        env = DEVELOPMENT_ENV

    env = str(env)
    if env != DEVELOPMENT_ENV and env != PRODUCTION_ENV:
        tag = red("[Warning] ")
        environments = "{} or {}".format(DEVELOPMENT_ENV, PRODUCTION_ENV)
        print(tag + "Invalid environment specified, use " + environments)
        env = DEVELOPMENT_ENV

    create_env()
    print("[Info] Running {} environment.".format(env))
    if env == DEVELOPMENT_ENV:
        print(red("[Warning] ") + "ngrok not started automatically, you " + \
              "need to start it manually")
        virtualenv("python app.py", env)
    else:
        virtualenv("foreman start", env)

@task
def generate_example_config():
    """
    Generates a default config file at CONFIG_FILE_PATH
    """
    if os.path.isfile(CONFIG_FILE_PATH):
        tag = red("[Warning] ")
        print(tag + "Config file already exists, not generating a new one.")
        return

    print("Generating config file at {}".format(CONFIG_FILE_PATH))
    config = configparser.RawConfigParser()

    def __set_section(config, section, variables):
        """
        Helper function to set up a config section from an array
        """
        config.add_section(section)
        for item in variables:
            config.set(section, item, "")

    __set_section(config, PRODUCTION_ENV, PRODUCTION_ENV_VARIABLES)
    __set_section(config, DEVELOPMENT_ENV, DEVELOPMENT_ENV_VARIABLES)

    with open(CONFIG_FILE_PATH, 'wb') as config_file:
        config.write(config_file)


@task
def update_data():
    """
    Updates the districts and legislators CSV files in the `data/` folder
    """
    with lcd(FILE_ROOT + "/data"):
        local('curl -kO "http://unitedstates.sunlightfoundation.com/legislators/legislators.csv"')
        local('curl -kO "http://assets.sunlightfoundation.com/data/districts.csv"')

@task
def clean():
    """
    Removes all compiled python files from the project
    """
    local("rm -rf *.pyc")

def virtualenv(command, env=None):
    """
    Runs a command in the virtual environment
    """
    if env is None:
        local('source venv/bin/activate && {}'.format(command),
              shell='/bin/bash')
        return

    env_prefix = generate_env_command_prefix(env)
    local('source venv/bin/activate && {}{}'.format(env_prefix, command),
          shell='/bin/bash')

def generate_env_command_prefix(env=None):
    """
    Reads the Config file and sets up an env command based on their values
    """
    if env is None:
        env = DEVELOPMENT_ENV

    export_str = "env "
    env_variables = parse_config(env)
    for variable in env_variables:
        if not env_variables[variable]:
            tag = red("[Warning] ")
            print("{}{} not set in your config file.".format(tag, variable))
            continue
        export_str += "{}={} ".format(variable.upper(), env_variables[variable])

    export_str += "ENV={} ".format(env)
    return export_str

def parse_config(section):
    """
    Looks for the default config file (ENV_FILE_PATH) and defaults to the
    example config file defined in this repository.

    Returns a dictionary with the config values
    """
    if not os.path.isfile(CONFIG_FILE_PATH):
        print("[Warning] No config file found.")
        generate_example_config()

    def __parse_config_for(section, variables):
        """
        Helper function to parse a set of variables out of a given config file
        and section.
        """
        config = configparser.RawConfigParser()
        config.read(CONFIG_FILE_PATH)

        values = {}
        for key in variables:
            values[key] = config.get(section, key)

        return values

    if section == PRODUCTION_ENV:
        return __parse_config_for(section, PRODUCTION_ENV_VARIABLES)
    else:
        return __parse_config_for(section, DEVELOPMENT_ENV_VARIABLES)

