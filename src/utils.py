from os import mkdir, getcwd, getenv
from os.path import isdir

from .config import *

""" -------------- UTILITIES -------------- """


def get_ratelimits() -> tuple:
    """Get the rate limits for the current tier"""
    return SUBSCRIPTION_TIERS[getenv('TAAPIIO_TIER', 'free').lower()]


def get_logfile() -> str:
    """Get logfile path & create logs dir if it doesn't exist in the current working directory"""
    log_dir = join(getcwd(), 'logs')
    if not isdir(log_dir):
        mkdir(log_dir)
    return join(log_dir, 'log.txt')


def get_help_command() -> str:
    with open(join(dirname(abspath(__file__)), 'resources/help_command.txt'), 'r') as help_file:
        return help_file.read()


def handle_env():
    """Checks if the .env file exists in the current working dir, and imports the variables if so"""
    try:
        envpath = find_dotenv(raise_error_if_not_found=True, usecwd=True)
        load_dotenv(dotenv_path=envpath)
    except:
        pass
    finally:
        mandatory_vars = ['TELEGRAM_USER_ID', 'TELEGRAM_BOT_TOKEN', "LOCATION"]
        for var in mandatory_vars:
            val = getenv(var)
            if val is None:
                raise ValueError(f"Missing environment variable: {var}")


def get_commands() -> dict:
    """Fetches the commands from the templates for the help command"""
    commands = {}

    # Define the path to the commands.txt file
    file_path = join(dirname(abspath(__file__)), 'resources', 'commands.txt')

    with open(file_path, 'r') as f:
        for line in f.readlines():
            # Splitting at the first '-' to separate command and description
            command, description = line.strip().split(' - ', 1)
            commands[command.strip()] = description.strip()

    return commands


def get_binance_price_url() -> str:
    """Get the binance price url for the location"""
    location = LOCATION
    assert location in BINANCE_LOCATIONS, f"Location must be in {BINANCE_LOCATIONS} for the Binance exchange."
    
    if location.lower() == 'us':
        return BINANCE_PRICE_URL_US
    else:
        return BINANCE_PRICE_URL_GLOBAL