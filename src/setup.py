import os

from .config import USE_MONGO_DB, AGG_DATA_LOCATION, TELEGRAM_ADMIN_USER_ID
from .logger import logger
from .user_configuration import LocalUserConfiguration, MongoDBUserConfiguration


def do_setup():
    admin_user_id = TELEGRAM_ADMIN_USER_ID

    # Set up required user files:
    try:
        logger.info(f"Creating default bot configuration for Telegram user {admin_user_id}...")

        if not USE_MONGO_DB:
            LocalUserConfiguration(admin_user_id).whitelist_user(is_admin=True)
        else:
            MongoDBUserConfiguration(admin_user_id).whitelist_user(is_admin=True)

        # Create empty aggregate as placeholder if it doesn't already exist:
        if not os.path.isdir(os.path.dirname(AGG_DATA_LOCATION)):
            os.mkdir(os.path.dirname(AGG_DATA_LOCATION))
            with open(AGG_DATA_LOCATION, 'w') as outfile:
                outfile.write("{}")

        logger.info("Setup complete! You can now run the bot module using: python3 -m bot")
    except Exception as exc:
        logger.exception("An unexpected error occurred during setup", exc_info=exc)
