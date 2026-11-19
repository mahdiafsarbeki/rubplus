"""RubPlus - asynchronous Rubika Bot API wrapper."""

from .bot import RubPlus
from .filters import (
    Filter, Filters, any_message, command, contains, endswith, group,
    group_text, help_command, length, media, private, private_command,
    private_text, regex, sender, start_command, startswith, text,
)
from .keyboard import ForceReply, InlineButton, InlineKeyboard, ReplyKeyboard
from .logger import LogLevel, RubPlusLogger
from .webhook import RubPlusWebhook, Webhook

try:
    from .metadata import GlyphWeaver
except ImportError:  # HTML/Markdown conversion is an optional extra.
    GlyphWeaver = None

__version__ = "1.5.2"

__all__ = [
    "RubPlus", "Filter", "Filters", "RubPlusLogger", "LogLevel",
    "InlineButton", "InlineKeyboard", "ReplyKeyboard", "ForceReply",
    "RubPlusWebhook", "Webhook", "GlyphWeaver",
    "text", "media", "private", "group", "command", "regex",
    "contains", "startswith", "endswith", "length", "sender",
    "private_text", "private_command", "group_text",
    "start_command", "help_command", "any_message",
]
