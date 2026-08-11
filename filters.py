"""
Enhanced Filters for RubPlus v2.0.0
"""

import re
from typing import Dict, Callable


class Filter:
    """Base filter class - composable with & and |"""
    
    def __init__(self, func: Callable[[Dict], bool]):
        self.func = func
    
    def __call__(self, message: Dict) -> bool:
        return self.func(message)
    
    def __and__(self, other: 'Filter') -> 'Filter':
        return Filter(lambda m: self(m) and other(m))
    
    def __or__(self, other: 'Filter') -> 'Filter':
        return Filter(lambda m: self(m) or other(m))
    
    def __invert__(self) -> 'Filter':
        return Filter(lambda m: not self(m))


# Basic filters
def text() -> Filter:
    """Only text messages"""
    return Filter(lambda m: m.get("text") is not None)


def media() -> Filter:
    """Only media messages"""
    return Filter(lambda m: m.get("file") is not None)


def photo() -> Filter:
    """Only photo messages"""
    return Filter(lambda m: m.get("photo") is True)


def video() -> Filter:
    """Only video messages"""
    return Filter(lambda m: m.get("video") is True)


def audio() -> Filter:
    """Only audio messages"""
    return Filter(lambda m: m.get("audio") is True)


def document() -> Filter:
    """Only document messages"""
    return Filter(lambda m: m.get("document") is True)


def private() -> Filter:
    """Only private messages"""
    return Filter(lambda m: m.get("chat_id", "").startswith("b0"))


def group() -> Filter:
    """Only group messages"""
    return Filter(lambda m: m.get("chat_id", "").startswith("g0"))


def command(cmd: str) -> Filter:
    """Only specific command"""
    return Filter(lambda m: m.get("text", "").startswith(f"/{cmd}"))


def regex(pattern: str) -> Filter:
    """Only messages matching regex pattern"""
    compiled = re.compile(pattern, re.IGNORECASE)
    return Filter(lambda m: bool(compiled.search(m.get("text", ""))))


def contains(word: str) -> Filter:
    """Only messages containing word"""
    return Filter(lambda m: word.lower() in m.get("text", "").lower())


def startswith(prefix: str) -> Filter:
    """Only messages starting with prefix"""
    return Filter(lambda m: m.get("text", "").startswith(prefix))


def endswith(suffix: str) -> Filter:
    """Only messages ending with suffix"""
    return Filter(lambda m: m.get("text", "").endswith(suffix))


def length(min_len: int = 0, max_len: int = 1000) -> Filter:
    """Only messages with specific length"""
    return Filter(lambda m: min_len <= len(m.get("text", "")) <= max_len)


def sender(user_id: str) -> Filter:
    """Only messages from specific user"""
    return Filter(lambda m: m.get("sender_id") == user_id)


def reply() -> Filter:
    """Only reply messages"""
    return Filter(lambda m: m.get("reply_to_message_id") is not None)


def edited() -> Filter:
    """Only edited messages"""
    return Filter(lambda m: m.get("is_edited") is True)


# Pre-combined filters
private_text = private() & text()
private_command = private() & command
group_text = group() & text()
start_command = private() & command("start")
help_command = command("help")
any_message = Filter(lambda m: True)
