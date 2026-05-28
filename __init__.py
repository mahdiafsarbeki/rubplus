"""
RubPlus - Official Rubika Bot API Wrapper
Version 1.5.1 - Full HTML Support
"""

from .bot import RubPlus
from .logger import RubPlusLogger
from .keyboard import InlineKeyboard, ReplyKeyboard
from .filters import Filters
from .webhook import Webhook

# ایمپورت GlyphWeaver از metadata
try:
    from .metadata import GlyphWeaver
except ImportError:
    GlyphWeaver = None

__version__ = "1.5.1"

__all__ = [
    "RubPlus",
    "RubPlusLogger", 
    "InlineKeyboard", 
    "ReplyKeyboard", 
    "Filters", 
    "Webhook",
    "GlyphWeaver"
]