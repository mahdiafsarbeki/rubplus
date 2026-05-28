"""
RubPlus - Official Rubika Bot API Wrapper
Version 1.5.1 - Full HTML Support with GlyphWeaver
"""

import httpx
import asyncio
import json
import os
import sys
import re
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List

from .logger import RubPlusLogger, LogLevel

# ========== ایمپورت GlyphWeaver از metadata.py ==========
try:
    from .metadata import GlyphWeaver
    HAS_GLYPHWEAVER = True
except ImportError:
    HAS_GLYPHWEAVER = False
    GlyphWeaver = None

# ========== کلاس اصلی ==========
class RubPlus:
    
    def __init__(
        self, 
        token: str, 
        debug: bool = False, 
        skip_old_messages: bool = True,
        log_level: str = "info",
        log_file: Optional[str] = None
    ):
        self.token = token
        self.debug = debug
        self.skip_old_messages = skip_old_messages
        self._base_url = f"https://botapi.rubika.ir/v3/{token}"
        
        self._client = httpx.AsyncClient(timeout=60.0)
        self._handlers: Dict[str, Callable] = {}
        self._running = False
        self._offset: Optional[str] = None
        self._offset_file = "rubplus_offset.json"
        self._start_time = int(datetime.now().timestamp())
        
        self._load_offset()
        self._processed_count = 0
        
        level_map = {
            "error": LogLevel.ERROR,
            "warning": LogLevel.WARNING,
            "info": LogLevel.INFO,
            "debug": LogLevel.DEBUG
        }
        self.logger = RubPlusLogger(
            level=level_map.get(log_level, LogLevel.INFO),
            log_file=log_file
        )
        
        self._check_initial_errors()
        
        # ========== راه‌اندازی GlyphWeaver برای تبدیل HTML ==========
        if HAS_GLYPHWEAVER:
            self._glyphweaver = GlyphWeaver()
            if self.debug:
                print("✅ GlyphWeaver loaded - HTML support enabled")
        else:
            self._glyphweaver = None
            if self.debug:
                print("⚠️ GlyphWeaver not found - HTML support disabled")
    
    def _check_initial_errors(self):
        if not self.token or len(self.token) < 10:
            self.logger.error("Invalid token", "Get a valid token from @BotFather on Rubika")
            sys.exit(1)
        
        try:
            response = httpx.post(f"{self._base_url}/getMe", json={}, timeout=10)
            result = response.json()
            
            if result.get("status") != "OK":
                error_status = result.get("status")
                if error_status == "INVALID_TOKEN":
                    self.logger.error("Invalid token", "Get a new token from @BotFather on Rubika")
                elif error_status == "INVALID_ACCESS":
                    self.logger.error("Access denied", "Make sure you have permission to use this bot")
                else:
                    self.logger.error(f"API error: {error_status}", "Check your token and try again")
                sys.exit(1)
                
        except httpx.ConnectError:
            self.logger.error("Connection lost (502)", "Check your internet connection or VPN")
            sys.exit(1)
        except httpx.TimeoutException:
            self.logger.error("Connection timeout", "Server is slow, try again later")
            sys.exit(1)
        except Exception as e:
            self.logger.error(f"Unknown error: {str(e)}", "Check your network and try again")
            sys.exit(1)
        
        self.logger.startup("1.5.1")
        self.logger.connected()
        self.logger.success()
    
    def _load_offset(self) -> None:
        try:
            if os.path.exists(self._offset_file):
                with open(self._offset_file, 'r') as f:
                    data = json.load(f)
                    self._offset = data.get('offset')
        except:
            pass
    
    def _save_offset(self, offset: str) -> None:
        try:
            with open(self._offset_file, 'w') as f:
                json.dump({'offset': offset}, f)
        except:
            pass
    
    def on(self, event: str) -> Callable:
        def decorator(func: Callable) -> Callable:
            self._handlers[event] = func
            if self.debug:
                print(f"📝 هندلر '{event}' ثبت شد")
            return func
        return decorator
    
    # ========== متد send با پشتیبانی از parse_mode ==========
    async def send(self, chat_id: str, text: str, reply_to: str = None, keyboard=None, auto_delete: int = None, parse_mode: str = None):
        final_text = text
        metadata = None
        
        # تبدیل HTML به metadata اگر GlyphWeaver موجود باشد
        if parse_mode == "HTML" and self._glyphweaver:
            parsed = self._glyphweaver.parse(text, "HTML")
            final_text = parsed.get("text", text)
            metadata = parsed.get("metadata")
        
        data = {"chat_id": chat_id, "text": final_text}
        if reply_to:
            data["reply_to_message_id"] = reply_to
        if metadata:
            data["metadata"] = metadata
        if keyboard and hasattr(keyboard, 'to_dict'):
            data["chat_keypad"] = keyboard.to_dict()
            data["chat_keypad_type"] = "New"
        
        result = await self._post("sendMessage", data)
        
        if auto_delete and result.get("status") == "OK":
            msg_id = result.get("data", {}).get("message_id")
            if msg_id:
                asyncio.create_task(self._auto_delete(chat_id, msg_id, auto_delete))
        
        return result
    
    # ========== متد edit با پشتیبانی از parse_mode ==========
    async def edit(self, chat_id: str, msg_id: str, text: str, parse_mode: str = None):
        final_text = text
        metadata = None
        
        if parse_mode == "HTML" and self._glyphweaver:
            parsed = self._glyphweaver.parse(text, "HTML")
            final_text = parsed.get("text", text)
            metadata = parsed.get("metadata")
        
        data = {"chat_id": chat_id, "message_id": msg_id, "text": final_text}
        if metadata:
            data["metadata"] = metadata
        return await self._post("editMessageText", data)
    
    async def delete(self, chat_id: str, msg_id: str):
        return await self._post("deleteMessage", {"chat_id": chat_id, "message_id": msg_id})
    
    async def forward(self, from_chat: str, to_chat: str, msg_id: str):
        return await self._post("forwardMessage", {"from_chat_id": from_chat, "to_chat_id": to_chat, "message_id": msg_id})
    
    async def _auto_delete(self, chat_id: str, msg_id: str, delay: int):
        await asyncio.sleep(delay)
        try:
            await self.delete(chat_id, msg_id)
        except:
            pass
    
    # ========== فایل ==========
    async def photo(self, chat_id: str, path: str, caption: str = ""):
        from .methods.file import FileMethods
        return await FileMethods(self._client, self._base_url).send_photo(chat_id, path, caption)
    
    async def video(self, chat_id: str, path: str, caption: str = ""):
        from .methods.file import FileMethods
        return await FileMethods(self._client, self._base_url).send_video(chat_id, path, caption)
    
    async def audio(self, chat_id: str, path: str, caption: str = ""):
        from .methods.file import FileMethods
        return await FileMethods(self._client, self._base_url).send_audio(chat_id, path, caption)
    
    async def file(self, chat_id: str, path: str, caption: str = ""):
        from .methods.file import FileMethods
        return await FileMethods(self._client, self._base_url).send_document(chat_id, path, caption)
    
    # ========== گروه ==========
    async def ban(self, chat_id: str, user_id: str):
        return await self._post("banChatMember", {"chat_id": chat_id, "user_id": user_id})
    
    async def unban(self, chat_id: str, user_id: str):
        return await self._post("unbanChatMember", {"chat_id": chat_id, "user_id": user_id})
    
    # ========== اطلاعات ==========
    async def me(self):
        return await self._post("getMe", {})
    
    async def chat(self, chat_id: str):
        return await self._post("getChat", {"chat_id": chat_id})
    
    async def leave(self, chat_id: str):
        return await self._post("leaveChat", {"chat_id": chat_id})
    
    # ========== نظرسنجی، موقعیت، مخاطب ==========
    async def poll(self, chat_id: str, question: str, options: List[str], is_anonymous: bool = True, allows_multiple_answers: bool = False, is_quiz: bool = False, correct_option_index: int = None) -> Dict[str, Any]:
        data = {
            "chat_id": chat_id,
            "question": question,
            "options": options,
            "is_anonymous": is_anonymous,
            "allows_multiple_answers": allows_multiple_answers
        }
        if is_quiz and correct_option_index is not None:
            data["type"] = "Quiz"
            data["correct_option_index"] = correct_option_index
        return await self._post("sendPoll", data)
    
    async def location(self, chat_id: str, lat: float, lon: float):
        return await self._post("sendLocation", {"chat_id": chat_id, "latitude": str(lat), "longitude": str(lon)})
    
    async def contact(self, chat_id: str, phone: str, first: str, last: str = ""):
        data = {"chat_id": chat_id, "phone_number": phone, "first_name": first}
        if last:
            data["last_name"] = last
        return await self._post("sendContact", data)
    
    # ========== کیبورد ==========
    async def set_keypad(self, chat_id: str, keyboard):
        return await self._post("editChatKeypad", {
            "chat_id": chat_id,
            "chat_keypad": keyboard.to_dict(),
            "chat_keypad_type": "New"
        })
    
    async def remove_keypad(self, chat_id: str):
        return await self._post("editChatKeypad", {"chat_id": chat_id, "chat_keypad_type": "Remove"})
    
    # ========== منوی دستورات ==========
    async def commands(self, cmds: List[Dict[str, str]]):
        return await self._post("setCommands", {"bot_commands": cmds})
    
    # ========== متدهای داخلی ==========
    async def _post(self, method: str, data: Dict) -> Dict:
        url = f"{self._base_url}/{method}"
        try:
            r = await self._client.post(url, json=data)
            result = r.json()
            if result.get("status") != "OK" and self.debug:
                print(f"⚠️ {method}: {result.get('status')}")
            return result
        except Exception as e:
            if self.debug:
                print(f"❌ خطا در {method}: {e}")
            return {"status": "ERROR", "error": str(e)}
    
    async def _poll(self) -> None:
        print("\n🚀 ربات شروع به کار کرد...")
        self._running = True
        
        while self._running:
            try:
                data = {"limit": 50}
                if self._offset:
                    data["offset_id"] = self._offset
                
                result = await self._post("getUpdates", data)
                
                if result.get("status") == "OK":
                    updates = result.get("data", {}).get("updates", [])
                    next_offset = result.get("data", {}).get("next_offset_id")
                    
                    for update in updates:
                        try:
                            if not isinstance(update, dict):
                                continue
                            
                            update_type = update.get("type")
                            chat_id = update.get("chat_id")
                            
                            if update_type == "NewMessage":
                                message = update.get("new_message", {})
                                
                                if not isinstance(message, dict):
                                    continue
                                
                                msg_time = int(message.get("time", 0))
                                
                                if self.skip_old_messages and msg_time <= self._start_time:
                                    continue
                                
                                # تشخیص فایل
                                if "file" in message and isinstance(message["file"], dict):
                                    file_info = message["file"]
                                    file_name = file_info.get("file_name", "").lower()
                                    
                                    if file_name.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                                        message["photo"] = True
                                    elif file_name.endswith(('.mp4', '.avi', '.mkv')):
                                        message["video"] = True
                                    elif file_name.endswith(('.mp3', '.ogg', '.wav')):
                                        message["audio"] = True
                                    else:
                                        message["document"] = True
                                    
                                    message["file_info"] = file_info
                                
                                message["chat_id"] = chat_id
                                
                                async def reply_func(text, rid=message.get("message_id"), cid=chat_id):
                                    return await self.send(cid, text, rid)
                                
                                message["reply"] = reply_func
                                
                                if "message" in self._handlers:
                                    await self._handlers["message"](message)
                                
                                self._processed_count += 1
                            
                            elif update_type == "UpdatedMessage" and "edited_message" in self._handlers:
                                message = update.get("updated_message", {})
                                if isinstance(message, dict):
                                    message["chat_id"] = chat_id
                                    await self._handlers["edited_message"](message)
                        
                        except Exception as e:
                            if self.debug:
                                print(f"⚠️ خطا: {e}")
                            continue
                    
                    if next_offset and next_offset != self._offset:
                        self._offset = next_offset
                        self._save_offset(next_offset)
                
                await asyncio.sleep(1)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                if self.debug:
                    print(f"⚠️ خطا: {e}")
                await asyncio.sleep(5)
    
    def run(self) -> None:
        try:
            asyncio.run(self._poll())
        except KeyboardInterrupt:
            print("\n👋 ربات متوقف شد")