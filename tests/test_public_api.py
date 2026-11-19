import pytest

from rubplus import Filters, RubPlus, Webhook
from rubplus.filters import command, private_text, text


def test_filter_composition():
    message = {"chat_id": "b0123", "text": "/start"}
    assert (Filters.private() & Filters.text())(message)
    assert command("start")(message)
    assert private_text(message)
    assert not (~text())(message)


def test_command_requires_exact_command_token():
    assert command("start")({"text": "/start"})
    assert not command("start")({"text": "/starter"})


def test_invalid_token_fails_without_network():
    with pytest.raises(ValueError):
        RubPlus("short")


def test_public_webhook_alias():
    from rubplus.webhook import RubPlusWebhook
    assert Webhook is RubPlusWebhook
