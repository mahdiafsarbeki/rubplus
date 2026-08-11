"""
Enhanced Keyboard builders for RubPlus v2.0.0
"""

from typing import List, Dict, Any


class InlineButton:
    """Inline button (glass-like button)"""
    
    def __init__(self, text: str, callback_data: str):
        self.text = text
        self.callback_data = callback_data
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "button_text": self.text,
            "id": self.callback_data,
            "type": "Simple"
        }


class URLButton:
    """URL button"""
    
    def __init__(self, text: str, url: str):
        self.text = text
        self.url = url
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "button_text": self.text,
            "type": "Link",
            "link_url": self.url
        }


class InlineKeyboard:
    """Inline keyboard (buttons under message)"""
    
    def __init__(self):
        self._rows: List[List[Any]] = []
    
    def row(self, *buttons) -> 'InlineKeyboard':
        """Add row of buttons"""
        self._rows.append(list(buttons))
        return self
    
    def button(self, text: str, callback_data: str) -> 'InlineKeyboard':
        """Add single button"""
        if not self._rows:
            self._rows.append([])
        self._rows[-1].append(InlineButton(text, callback_data))
        return self
    
    def url_button(self, text: str, url: str) -> 'InlineKeyboard':
        """Add URL button"""
        if not self._rows:
            self._rows.append([])
        self._rows[-1].append(URLButton(text, url))
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "rows": [
                {"buttons": [btn.to_dict() for btn in row]}
                for row in self._rows
            ]
        }


class ReplyButton:
    """Reply keyboard button"""
    
    def __init__(self, text: str):
        self.text = text
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "button_text": self.text,
            "type": "Simple",
            "id": self.text
        }


class ReplyKeyboard:
    """Reply keyboard (buttons at bottom of screen)"""
    
    def __init__(self, resize: bool = True, one_time: bool = False):
        self._rows: List[List[str]] = []
        self.resize_keyboard = resize
        self.one_time_keyboard = one_time
    
    def row(self, *buttons: str) -> 'ReplyKeyboard':
        """Add row of buttons"""
        self._rows.append(list(buttons))
        return self
    
    def button(self, text: str) -> 'ReplyKeyboard':
        """Add single button"""
        if not self._rows:
            self._rows.append([])
        self._rows[-1].append(text)
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "rows": [
                {
                    "buttons": [
                        {"button_text": btn, "type": "Simple", "id": btn}
                        for btn in row
                    ]
                }
                for row in self._rows
            ],
            "resize_keyboard": self.resize_keyboard,
            "one_time_keyboard": self.one_time_keyboard
        }


class ForceReply:
    """Force reply"""
    
    def to_dict(self) -> Dict[str, Any]:
        return {"force_reply": True}


class RemoveKeyboard:
    """Remove keyboard"""
    
    def to_dict(self) -> Dict[str, Any]:
        return {"remove_keyboard": True}
