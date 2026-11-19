"""Composable message filters for RubPlus."""

import re
from typing import Any, Callable, Dict


class Filter:
    """Callable filter supporting &, | and ~ composition."""

    def __init__(self, func: Callable[[Dict[str, Any]], bool]):
        if not callable(func):
            raise TypeError("func must be callable")
        self.func = func

    def __call__(self, message: Dict[str, Any]) -> bool:
        return bool(self.func(message))

    def __and__(self, other: "Filter") -> "Filter":
        if not isinstance(other, Filter):
            return NotImplemented
        return Filter(lambda message: self(message) and other(message))

    def __or__(self, other: "Filter") -> "Filter":
        if not isinstance(other, Filter):
            return NotImplemented
        return Filter(lambda message: self(message) or other(message))

    def __invert__(self) -> "Filter":
        return Filter(lambda message: not self(message))


def text() -> Filter:
    return Filter(lambda m: isinstance(m.get("text"), str))


def media() -> Filter:
    return Filter(lambda m: bool(m.get("file") or m.get("file_info")))


def private() -> Filter:
    return Filter(lambda m: str(m.get("chat_id", "")).startswith("b0"))


def group() -> Filter:
    return Filter(lambda m: str(m.get("chat_id", "")).startswith("g0"))


def command(cmd: str) -> Filter:
    name = cmd.lstrip("/")
    return Filter(lambda m: str(m.get("text", "")).split(maxsplit=1)[0:1] == [f"/{name}"])


def regex(pattern: str) -> Filter:
    compiled = re.compile(pattern, re.IGNORECASE)
    return Filter(lambda m: bool(compiled.search(str(m.get("text", "")))))


def contains(word: str) -> Filter:
    needle = word.casefold()
    return Filter(lambda m: needle in str(m.get("text", "")).casefold())


def startswith(prefix: str) -> Filter:
    return Filter(lambda m: str(m.get("text", "")).startswith(prefix))


def endswith(suffix: str) -> Filter:
    return Filter(lambda m: str(m.get("text", "")).endswith(suffix))


def length(min_len: int = 0, max_len: int = 1000) -> Filter:
    if min_len < 0 or max_len < min_len:
        raise ValueError("Require 0 <= min_len <= max_len")
    return Filter(lambda m: min_len <= len(str(m.get("text", ""))) <= max_len)


def sender(user_id: str) -> Filter:
    return Filter(lambda m: m.get("sender_id") == user_id)


def private_command(cmd: str = "") -> Filter:
    """Match a command in a private chat; empty cmd accepts any slash command."""
    command_filter = (
        Filter(lambda m: str(m.get("text", "")).startswith("/"))
        if not cmd else command(cmd)
    )
    return private() & command_filter


private_text = private() & text()
group_text = group() & text()
start_command = private_command("start")
help_command = command("help")
any_message = Filter(lambda _message: True)


class Filters:
    """Namespace-style compatibility API: Filters.text(), Filters.command(), etc."""

    text = staticmethod(text)
    media = staticmethod(media)
    private = staticmethod(private)
    group = staticmethod(group)
    command = staticmethod(command)
    regex = staticmethod(regex)
    contains = staticmethod(contains)
    startswith = staticmethod(startswith)
    endswith = staticmethod(endswith)
    length = staticmethod(length)
    sender = staticmethod(sender)
    private_command = staticmethod(private_command)
    private_text = private_text
    group_text = group_text
    start_command = start_command
    help_command = help_command
    any_message = any_message
