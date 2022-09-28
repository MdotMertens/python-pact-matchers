import pytest

import time

from os import remove
from pathlib import Path
from os.path import isfile

from pact import MessageConsumer, MessagePact, Provider
from pact.matchers import Like, Term

from delivery import handler

PACT_DIR = Path(__file__).parent / "pact"

CONSUMER_NAME = "DeliveryLambda"
PROVIDER_NAME = "DeliveryEvents"

PACT_FILE = (
    f"{PACT_DIR}/{CONSUMER_NAME.lower().replace(' ', '_')}-"
    + f"{PROVIDER_NAME.lower().replace(' ', '_')}.json"
)


def cleanup_json(file):
    """
    Remove existing json file before test if any
    """
    if isfile(f"{file}"):
        remove(f"{file}")


@pytest.fixture(scope="session")
def pact_no_publish(request):
    version = 1

    pact = MessageConsumer(CONSUMER_NAME, version=version).has_pact_with(
        Provider(PROVIDER_NAME),
        publish_to_broker=False,
        pact_dir=PACT_DIR,
    )

    yield pact


def progressive_delay(
    file,
    time_to_wait=10,
    second_interval=0.5,
    verbose=False,
):
    """
    progressive delay
    defaults to wait up to 5 seconds with 0.5 second intervals
    """
    time_counter = 0
    while not isfile(file):
        time.sleep(second_interval)
        time_counter += 1
        if verbose:
            print(f"Trying for {time_counter*second_interval} seconds")
        if time_counter > time_to_wait:
            if verbose:
                print(f"Already waited {time_counter*second_interval} seconds")
            break


def test_throw_exception_handler(pact_no_publish: MessagePact):
    cleanup_json(PACT_FILE)

    wrong_event = {"event": "delivery:created", "delivery_type": "unsupported"}

    (
        pact_no_publish.given("Unsupported delivery type")
        .expects_to_receive("Delivery")
        .with_content(wrong_event)
        .with_metadata({"Content-Type": "application/json"})
    )

    with pytest.raises(Exception):
        with pact_no_publish:
            handler(event=wrong_event, context={})

    progressive_delay(f"{PACT_FILE}")
    assert isfile(f"{PACT_FILE}") == 0


def test_right_delivery_type(pact_no_publish: MessagePact):
    cleanup_json(PACT_FILE)

    event = {
        "event": "delivery:created",
        "delivery_type": "standard",
        "customer": Like("string")
    }

    (
        pact_no_publish.given("Delivery has standard shipping")
        .expects_to_receive("delivery:created")
        .with_content(event)
        .with_metadata({"Content-Type": "application/json"})
    )

    with pact_no_publish:
        handler(event=event, context={})

    progressive_delay(f"{PACT_FILE}")
    assert isfile(f"{PACT_FILE}") == 1
