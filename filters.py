"""
Filters for RubPlus - Simple & Powerful
"""

import re
from typing import Dict, Callable


class Filter:
    """کلاس پایه فیلترها - قابل ترکیب با & و |"""
    
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


# ========== فیلترهای پایه (به عنوان Filter) ==========

def text() -> Filter:
    """فقط پیام‌های متنی"""
    return Filter(lambda m: m.get("text") is not None)


def media() -> Filter:
    """فقط پیام‌های دارای رسانه"""
    return Filter(lambda m: m.get("file") is not None)


def private() -> Filter:
    """فقط پیام‌های خصوصی (پیوی)"""
    return Filter(lambda m: m.get("chat_id", "").startswith("b0"))


def group() -> Filter:
    """فقط پیام‌های گروهی"""
    return Filter(lambda m: m.get("chat_id", "").startswith("g0"))


def command(cmd: str) -> Filter:
    """فقط دستورات خاص (مثل /start)"""
    return Filter(lambda m: m.get("text", "").startswith(f"/{cmd}"))


def regex(pattern: str) -> Filter:
    """فقط پیام‌های مطابق با الگوی منظم"""
    compiled = re.compile(pattern, re.IGNORECASE)
    return Filter(lambda m: bool(compiled.search(m.get("text", ""))))


def contains(word: str) -> Filter:
    """فقط پیام‌های حاوی کلمه خاص"""
    return Filter(lambda m: word.lower() in m.get("text", "").lower())


def startswith(prefix: str) -> Filter:
    """فقط پیام‌هایی که با پیشوند خاص شروع می‌شوند"""
    return Filter(lambda m: m.get("text", "").startswith(prefix))


def endswith(suffix: str) -> Filter:
    """فقط پیام‌هایی که با پسوند خاص تمام می‌شوند"""
    return Filter(lambda m: m.get("text", "").endswith(suffix))


def length(min_len: int = 0, max_len: int = 1000) -> Filter:
    """فقط پیام‌هایی با طول مشخص"""
    return Filter(lambda m: min_len <= len(m.get("text", "")) <= max_len)


def sender(user_id: str) -> Filter:
    """فقط پیام‌های یک کاربر خاص"""
    return Filter(lambda m: m.get("sender_id") == user_id)


# ========== فیلترهای ترکیبی از پیش ساخته شده ==========

private_text = private() & text()
private_command = private() & command
group_text = group() & text()
start_command = private() & command("start")
help_command = command("help")
any_message = Filter(lambda m: True)