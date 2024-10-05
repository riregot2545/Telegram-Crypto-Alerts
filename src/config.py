import os
from os.path import join, dirname, abspath

from dotenv import find_dotenv, load_dotenv

from .docker_helpers import get_swarm_secret

USE_DOCKER = os.getenv("USE_DOCKER", 'False').lower() in ('True', 'true', '1', 't')
if not USE_DOCKER:
    envpath = find_dotenv(raise_error_if_not_found=True, usecwd=True)
    load_dotenv(dotenv_path=envpath)

"""Telegram bot config"""
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_ADMIN_USER_ID = os.getenv("TELEGRAM_USER_ID")
MAX_ALERTS_PER_USER = int(
    os.getenv("MAX_ALERTS_PER_USER", 10))  # Integer or None (Should be set in a static configuration file)

"""Alert Handler Configuration"""
CEX_POLLING_PERIOD = int(os.getenv("CEX_POLLING_PERIOD",
                                   10))  # Delay for the CEX alert handler to pull prices and check alert conditions (in seconds)
TECHNICAL_POLLING_PERIOD = 5  # Delay for the technical alert handler check technical alert conditions (in seconds)
OUTPUT_VALUE_PRECISION = 3
SIMPLE_INDICATORS = ['PRICE']
SIMPLE_INDICATOR_COMPARISONS = ['ABOVE', 'BELOW', 'IN_RANGE', 'PCTCHG', '24HRCHG']

"""BINANCE DATA CONFIG"""
LOCATION = os.getenv("LOCATION", "global")
BINANCE_LOCATIONS = ['us', 'global']
BINANCE_PRICE_URL_GLOBAL = 'https://api.binance.com/api/v3/ticker?symbol={}&windowSize={}'  # (e.x. BTCUSDT, 1d)
BINANCE_PRICE_URL_US = 'https://api.binance.us/api/v3/ticker?symbol={}&windowSize={}'  # (e.x. BTCUSDT, 1d
BINANCE_TIMEFRAMES = ["1m", "5m", "15m", "30m", "1h", "2h", "4h", "12h", "1d", '7d']

"""SWAP DATA CONFIG"""
SWAP_POLLING_DELAY = 30  # Swap polling delay (in seconds) to handle rate limits.

"""DATABASE PREFERENCES & PATHS"""
USE_MONGO_DB = os.getenv("USE_MONGO_DB", 'False').lower() in ('True', 'true', '1', 't')
MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE")
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION")

WHITELIST_ROOT = join(dirname(abspath(__file__)), 'whitelist')
RESOURCES_ROOT = join(dirname(abspath(__file__)), 'resources')
TA_DB_PATH = join(dirname(abspath(__file__)), 'resources/indicator_format_reference.json')
AGG_DATA_LOCATION = join(dirname(abspath(__file__)), 'temp/ta_aggregate.json')

"""TAAPI.IO"""
INTERVALS = ["1m", "5m", "15m", "30m", "1h", "2h", "4h", "12h", "1d", '1w']
DEFAULT_EXCHANGE = "binance"
BULK_ENDPOINT = "https://api.taapi.io/bulk"
SUBSCRIPTION_TIERS = {"free": (1, 20), "basic": (5, 15), "pro": (30, 15),
                      "expert": (75, 15)}  # (requests, per period in seconds)
REQUEST_BUFFER = 0.05  # buffer percentage for preventing rate limit errors (e.x. 0.05 = 5% of request period, so period * 1.05)

# TA_AGGREGATE_PPERIOD = 30  # TA Aggregate polling period, to poll technical indicators

if USE_DOCKER:
    MONGODB_CONNECTION_STRING = get_swarm_secret("tg_alert_bot_mongodb_connection_string")
    TELEGRAM_BOT_TOKEN = get_swarm_secret("tg_alert_bot_telegram_bot_token")
    TELEGRAM_ADMIN_USER_ID = get_swarm_secret("tg_alert_bot_telegram_admin_user_id")

# TODO add tapapi vars and secrets
