import json
import logging
import os

import google
import requests
from google.cloud import pubsub_v1


def get_env_or_exit(env_name):
    val = os.getenv(env_name, None)
    if val is None:
        print(f"Please set {env_name}")
        exit(1)
    return val


def right_type(data):
    looking = "sdm.devices.events.DoorbellChime.Chime"
    return looking in data["resourceUpdate"]["events"]


def need_notify(message):
    # for testing purposes. Do not send notifications if SKIP_NOTIFICATIONS is set
    if os.getenv("SKIP_NOTIFICATIONS", None) is not None:
        return False

    data = json.loads(message.data)
    if data["eventThreadState"] == 'STARTED' and right_type(data):
        return True
    return False


def send_callbacks(webhook_urls):
    for url in webhook_urls:
        resp = requests.post(url)
        resp.raise_for_status()


def create_callback(urls):
    def callback(message):
        if need_notify(message):
            logging.info("Sending notifications")
            send_callbacks(urls)
        message.ack()

    return callback


def ensure_subscription(subscription, topic):
    try:
        subscriber.create_subscription(name=subscription, topic=topic, timeout=30)
    except google.api_core.exceptions.AlreadyExists:
        logging.info(f"Subscription {subscription} already exists")


def get_webhook_urls():
    urls = []
    for k, v in os.environ.items():
        if k.startswith("WEBHOOK_URL_"):
            urls.append(v)
    if not urls:
        logging.error("No webhook URLS defined. Set WEBHOOK_URL_ environment variables")
        exit(2)
    return urls


if __name__ == "__main__":
    subscription_name = get_env_or_exit("SUBSCRIPTION_NAME")
    topic_name = get_env_or_exit("TOPIC_NAME")
    webhook_urls = get_webhook_urls()

    with pubsub_v1.SubscriberClient() as subscriber:
        ensure_subscription(subscription_name, topic_name)
        future = subscriber.subscribe(subscription_name, create_callback(webhook_urls))
        try:
            future.result()
        except KeyboardInterrupt:
            future.cancel()
