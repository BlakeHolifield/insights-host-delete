import requests
import traceback

from requests.auth import HTTPBasicAuth
from utils import config, host_delete_logging
from mq import kafka_consumer

logger = host_delete_logging.initialize_logging()


def handle_message(parsed):
    try:
        send_request(parsed["rhel_machine_id"], parsed["account"])
    except KeyError as e:
        logger.exception("Missing Key in Message: %s", e)


def send_request(rhel_machine_id, account):
    logger.debug("sending delete request to legacy")
    URL = "{0}/{1}?account_number={2}".format(config.LEGACY_URL, rhel_machine_id, account)
    r = requests.delete(URL, auth=HTTPBasicAuth(config.LEGACY_USERNAME, config.LEGACY_PASSWORD))
    logger.debug(r.text)


def main():

    logger = host_delete_logging.initialize_logging()
    logger.info("Starting legacy host deletion service")
    config.log_config()

    consumer = kafka_consumer.init_consumer()

    for data in consumer:
        handle_message(data.value)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        the_error = traceback.format_exc()
        logger.error(f"Insights Host Delete Service failed with error: {the_error}")
