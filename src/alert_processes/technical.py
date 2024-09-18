import time
from datetime import datetime
import os
from functools import wraps

from telebot import TeleBot

from .base import BaseAlertProcess
from ..user_configuration import LocalUserConfiguration, MongoDBUserConfiguration, get_whitelist
from ..logger import logger
from ..config import *
from ..indicators import TADatabaseClient, TAAggregateClient


class TechnicalAlertProcess(BaseAlertProcess):
    def __init__(self, telegram_bot: TeleBot):
        super().__init__(telegram_bot)
        self.polling = False  # Temporary variable to manage alerts
        self.ta_db = TADatabaseClient().fetch_ref()
        self.ta_agg_cli = TAAggregateClient()

    def poll_user_alerts(self, tg_user_id: str) -> None:
        """
        1. Load the user's configuration
        2. poll all alerts and create posts
        3. Remove alert conditions
        4. Send alerts if found

        :param tg_user_id: The Telegram user ID from the database
        """
        configuration = LocalUserConfiguration(tg_user_id) if not USE_MONGO_DB else MongoDBUserConfiguration(tg_user_id)
        alerts_database = configuration.load_alerts()
        config = configuration.load_config()

        do_update = False  # If any changes are made, update the database
        post_queue = []
        for pair in alerts_database.copy().keys():

            remove_queue = []
            for alert in alerts_database[pair]:
                if alert['alerted']:
                    remove_queue.append(alert)
                    do_update = True  # Since the alert needs to be removed from the database, signal do_update
                    continue

                if alert['type'] == "t":
                    condition, value, post_string = self.get_technical_indicator(pair, alert)

                    if condition:  # If there is a condition satisfied
                        post_queue.append((post_string, pair))
                        alert['alerted'] = True
                        do_update = True  # Since the alert needs to be updated in the database, signal do_update

            for item in remove_queue:
                alerts_database[pair].remove(item)
                if len(alerts_database[pair]) == 0:
                    alerts_database.pop(pair)

        if do_update:
            configuration.update_alerts(alerts_database)

        if len(post_queue) > 0:
            self.polling = False
            for post, pair in post_queue:
                logger.info(post)
                status = self.tg_alert(post=post, channel_ids=config['channels'], pair=pair)
                if len(status[1]) > 0:
                    logger.warn(f"Failed to send Telegram alert ({post}) to the following IDs: {status[1]}")

        if not self.polling:
            self.polling = True
            logger.info(f'Bot polling for next alert...')

    def poll_all_alerts(self) -> None:
        """
        1. Aggregate pairs across all users
        2. Fetch all pair prices
        3. Log individual user failures
        """
        for user in get_whitelist():
            self.poll_user_alerts(tg_user_id=user)

    def get_technical_indicator(self, pair: str, alert: dict) -> tuple[bool, float, str]:
        """
        Accounts for all of the implemented taapi.io indicators.
        Get the available indicators using the telegram command.
        References the alert against the temp/ta_aggregate.json file to check for satisfaction.

        :param pair: The crypto pair
        :param alert: An alert data dictionary as returned by src.io_handler.UserConfiguration.load_alerts()

        :returns: Tuple:
                  (Boolean) True if the indicator is satisfied, False if not
                  (Float) The current value of the indicator
                  (String) The formatted string to send with alerts
        """
        null_output = False, 0, ""

        aggregate = self.ta_agg_cli.load_agg()
        if aggregate == {}:
            logger.warn("Attempted to load the aggregate in get_technical_indicator() but it was empty")
            return null_output

        # Match the alert to its corresponding reference in the aggregate and check the value:
        matched_indicator = None
        formatted_alert = self.ta_agg_cli.format_alert_for_match(alert)

        # Attempt to find an existing indicator match for the alert
        for indicator in aggregate[pair][alert['interval']]:
            try:
                if all(indicator[k] == v for k, v in formatted_alert.items()):
                    matched_indicator = indicator
                    break
            except KeyError:
                continue

        if matched_indicator is None:
            raise ValueError(f"Could not match alert to indicator in the TA aggregate - Alert: {alert}")

        # If these tests pass, this is the correct indicator because the symbol, interval, and params pass
        value = matched_indicator['values'][alert['output_value']]
        if value is None:
            return null_output

        satisfied = False
        if alert['comparison'] == "ABOVE":
            if value > alert['target']:
                satisfied = True
        elif alert['comparison'] == "BELOW":
            if value < alert['target']:
                satisfied = True
        else:
            raise ValueError(f"'{alert['comparison']}' IS AN INVALID COMPARISON TYPE (ABOVE OR BELOW)")

        # Return
        if satisfied:
            indicator_str = f"{self.ta_db[alert['indicator'].upper()]['name']} ({alert['indicator'].upper()})"
            params_str = ', '.join([f'{param.upper()}={v}' for param, v in alert['params'].items()])
            post_str = f"{pair} {indicator_str} {alert['interval']} {params_str} {alert['comparison']} {alert['target']}" \
                       f" AT {value:.{OUTPUT_VALUE_PRECISION}f}\n"
            return True, value, post_str
        else:
            return null_output

    def tg_alert(self, post: str, channel_ids: list[str], pair: str) -> tuple:
        """
        Sends the post (price alert) to each registered user of the Telegram bot

        :param post: A message to send to each registered bot user
        :param channel_ids: All group ids to send the alert to (self.config_client.load_config()['channels'])
        :param pair: The binance pair corresponding to the alert (for showing chart)
        :return: Tuple = ([successful group ids], [unsuccessful group ids])
        """
        post = f"🔔 <b>TECHNICAL ALERT:</b> 🔔\n\n" + post
        if pair:
            pair_fmt = pair.replace('/', '_')
            post += f"\n<a href='https://www.binance.com/en/trade/{pair_fmt}?type=spot'><b>View {pair} Chart</b></a>"
        output = ([], [])
        for g_id in channel_ids:
            try:
                # requests.post(url=f'https://api.telegram.org/bot{self.tg_bot_token}/sendMessage',
                #               params={'chat_id': g_id, 'text': header_str + post, "parse_mode": "HTML"})
                self.telegram_bot.send_message(chat_id=g_id, text=post, parse_mode="HTML", disable_web_page_preview=True)
                output[0].append(g_id)
            except:
                output[1].append(g_id)

        return output

    def run(self):
        try:
            logger.warn(f'{type(self).__name__} started at {datetime.utcnow()} UTC+0')
            while True:
                self.poll_all_alerts()
                time.sleep(TECHNICAL_POLLING_PERIOD)
        except NotImplementedError as exc:
            logger.critical(exc_info=exc)
            # self.alert_admins(str(exc))
        except KeyboardInterrupt:
            logger.critical("KeyboardInterrupt detected. Exiting...")
            exit(0)
        except Exception as exc:
            logger.critical("An error has occurred in the technical alerts process. Trying again in 15 seconds...", exc_info=exc)
            time.sleep(15)
