import pytest
from pact import MessageProvider

from pathlib import Path


PACT_BROKER_URL = "http://localhost"
PACT_BROKER_USERNAME = "pactbroker"
PACT_BROKER_PASSWORD = "pactbroker"
PACT_DIR = Path(__file__).parent / "pact"


def document_created_handler():
    return {"event": "delivery:created", "delivery_type": "standard", "customer": "testCustomer"}


def test_verify_from_broker():
    provider = MessageProvider(
        message_providers={
            "Delivery has standard shipping": document_created_handler,
        },
        provider="DeliveryEvents",
        consumer="DeliveryLambda",
        pact_dir=PACT_DIR,
    )

    with provider:
        provider.verify()
