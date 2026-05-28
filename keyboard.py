"""
Keyboard Types for RubPlus
"""

from typing import List, Dict, Any


class InlineButton:
    """دکمه شیشه‌ای"""
    
    def __init__(self, text: str, callback_data: str):
        self.text = text
        self.callback_data = callback_data
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "button_text": self.text,
            "id": self.callback_data,
            "type": "Simple"
        }


class InlineKeyboard:
    """کیبورد شیشه‌ای (زیر پیام)"""
    
    def __init__(self):
        self._rows: List[List[InlineButton]] = []
    
    def row(self, *buttons: InlineButton) -> 'InlineKeyboard':
        self._rows.append(list(buttons))
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "rows": [
                {"buttons": [btn.to_dict() for btn in row]}
                for row in self._rows
            ]
        }


class ReplyKeyboard:
    """کیبورد معمولی (پایین صفحه)"""
    
    def __init__(self, resize: bool = True, one_time: bool = False):
        self._rows: List[List[str]] = []
        self.resize_keyboard = resize
        self.one_time_keyboard = one_time
    
    def row(self, *buttons: str) -> 'ReplyKeyboard':
        self._rows.append(list(buttons))
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
    """اجبار به ریپلای کردن"""
    
    def to_dict(self) -> Dict[str, Any]:
        return {"force_reply": True}