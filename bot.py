"""Asynchronous Rubika Bot API client."""
import asyncio, json, os
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
import httpx
from .logger import LogLevel, RubPlusLogger
try:
    from .metadata import GlyphWeaver
except ImportError:
    GlyphWeaver = None

class RubPlus:
    """Async Rubika client. Construction is offline; call await start() to poll."""
    def __init__(self, token: str, debug: bool = False, skip_old_messages: bool = True,
                 log_level: str = "info", log_file: Optional[str] = None,
                 offset_file: str = "rubplus_offset.json", request_timeout: float = 30.0,
                 client: Optional[httpx.AsyncClient] = None):
        if not isinstance(token, str) or len(token.strip()) < 10:
            raise ValueError("A valid Rubika bot token is required.")
        if request_timeout <= 0: raise ValueError("request_timeout must be positive")
        levels = {"error": LogLevel.ERROR, "warning": LogLevel.WARNING, "info": LogLevel.INFO, "debug": LogLevel.DEBUG}
        if log_level.lower() not in levels: raise ValueError("Invalid log_level")
        self.token, self.debug, self.skip_old_messages = token.strip(), debug, skip_old_messages
        self._base_url = f"https://botapi.rubika.ir/v3/{self.token}"
        self._client = client or httpx.AsyncClient(timeout=request_timeout)
        self._owns_client = client is None
        self._handlers: Dict[str, Callable] = {}
        self._running, self._offset = False, None
        self._offset_file = offset_file
        self._start_time = int(datetime.now().timestamp())
        self._processed_count = 0
        self._auto_delete_tasks = set()
        self.logger = RubPlusLogger(level=levels[log_level.lower()], log_file=log_file)
        self._load_offset()
        self._glyphweaver = GlyphWeaver() if GlyphWeaver else None

    def _load_offset(self):
        if not self._offset_file or not os.path.isfile(self._offset_file): return
        try:
            with open(self._offset_file, "r", encoding="utf-8") as f: data = json.load(f)
            value = data.get("offset") if isinstance(data, dict) else None
            self._offset = str(value) if value is not None else None
        except (OSError, ValueError, TypeError) as exc: self.logger.warning(f"Cannot load offset: {exc}")

    def _save_offset(self, offset):
        if not self._offset_file: return
        tmp = self._offset_file + ".tmp"
        try:
            os.makedirs(os.path.dirname(os.path.abspath(self._offset_file)), exist_ok=True)
            with open(tmp, "w", encoding="utf-8") as f: json.dump({"offset": offset}, f)
            os.replace(tmp, self._offset_file)
        except OSError as exc:
            self.logger.warning(f"Cannot save offset: {exc}")
            try: os.remove(tmp)
            except OSError: pass

    def on(self, event: str):
        if not isinstance(event, str) or not event.strip(): raise ValueError("event must be non-empty")
        def decorator(func):
            if not callable(func): raise TypeError("handler must be callable")
            self._handlers[event] = func
            return func
        return decorator

    async def _post(self, method: str, data: Dict[str, Any]):
        try:
            response = await self._client.post(f"{self._base_url}/{method}", json=data)
            response.raise_for_status()
            result = response.json()
            if not isinstance(result, dict): return {"status": "ERROR", "error": "Invalid API JSON object"}
            if result.get("status") != "OK" and self.debug: self.logger.warning(f"{method}: {result.get('status')}")
            return result
        except (httpx.HTTPError, ValueError) as exc:
            if self.debug: self.logger.error(f"{method} failed: {exc}")
            return {"status": "ERROR", "error": str(exc)}

    async def me(self): return await self._post("getMe", {})
    async def check_connection(self):
        result = await self.me()
        if result.get("status") != "OK": raise RuntimeError(f"Rubika getMe failed: {result}")
        self.logger.startup("1.5.2"); self.logger.connected()
        return result

    async def send(self, chat_id: str, text: str, reply_to=None, keyboard=None, auto_delete=None, parse_mode=None):
        if not chat_id: raise ValueError("chat_id is required")
        if not isinstance(text, str): raise TypeError("text must be a string")
        final_text, metadata = text, None
        if parse_mode and parse_mode.upper() == "HTML":
            if self._glyphweaver is None: raise RuntimeError('Install HTML extra: pip install "rubplus[html]"')
            parsed = self._glyphweaver.parse(text, "HTML"); final_text, metadata = parsed.get("text", text), parsed.get("metadata")
        elif parse_mode and parse_mode.upper() != "MARKDOWN": raise ValueError("Unsupported parse_mode")
        data = {"chat_id": chat_id, "text": final_text}
        if reply_to: data["reply_to_message_id"] = reply_to
        if metadata: data["metadata"] = metadata
        if keyboard is not None:
            if not callable(getattr(keyboard, "to_dict", None)): raise TypeError("keyboard must provide to_dict()")
            data["chat_keypad"], data["chat_keypad_type"] = keyboard.to_dict(), "New"
        result = await self._post("sendMessage", data)
        if auto_delete is not None:
            if auto_delete < 0: raise ValueError("auto_delete must be non-negative")
            mid = result.get("data", {}).get("message_id") if result.get("status") == "OK" else None
            if mid:
                task = asyncio.create_task(self._auto_delete(chat_id, mid, auto_delete))
                self._auto_delete_tasks.add(task); task.add_done_callback(self._auto_delete_tasks.discard)
        return result

    async def edit(self, chat_id, msg_id, text, parse_mode=None):
        metadata = None
        if parse_mode and parse_mode.upper() == "HTML":
            if self._glyphweaver is None: raise RuntimeError('Install HTML extra: pip install "rubplus[html]"')
            parsed = self._glyphweaver.parse(text, "HTML"); text, metadata = parsed.get("text", text), parsed.get("metadata")
        data = {"chat_id": chat_id, "message_id": msg_id, "text": text}
        if metadata: data["metadata"] = metadata
        return await self._post("editMessageText", data)
    async def delete(self, chat_id, msg_id): return await self._post("deleteMessage", {"chat_id": chat_id, "message_id": msg_id})
    async def forward(self, from_chat, to_chat, msg_id): return await self._post("forwardMessage", {"from_chat_id": from_chat, "to_chat_id": to_chat, "message_id": msg_id})
    async def _auto_delete(self, chat_id, msg_id, delay):
        await asyncio.sleep(delay); await self.delete(chat_id, msg_id)

    async def _send_file(self, method_name, chat_id, path, caption=""):
        try: from .methods.file import FileMethods
        except ImportError as exc: raise NotImplementedError("File upload module is missing from this package build.") from exc
        methods = FileMethods(self._client, self._base_url)
        method = getattr(methods, method_name, None)
        if method is None: raise NotImplementedError(f"{method_name} is unavailable")
        return await method(chat_id, path, caption)
    async def photo(self, chat_id, path, caption=""): return await self._send_file("send_photo", chat_id, path, caption)
    async def video(self, chat_id, path, caption=""): return await self._send_file("send_video", chat_id, path, caption)
    async def audio(self, chat_id, path, caption=""): return await self._send_file("send_audio", chat_id, path, caption)
    async def file(self, chat_id, path, caption=""): return await self._send_file("send_document", chat_id, path, caption)

    async def ban(self, chat_id, user_id): return await self._post("banChatMember", {"chat_id": chat_id, "user_id": user_id})
    async def unban(self, chat_id, user_id): return await self._post("unbanChatMember", {"chat_id": chat_id, "user_id": user_id})
    async def chat(self, chat_id): return await self._post("getChat", {"chat_id": chat_id})
    async def leave(self, chat_id): return await self._post("leaveChat", {"chat_id": chat_id})
    async def poll(self, chat_id, question, options: List[str], is_anonymous=True, allows_multiple_answers=False, is_quiz=False, correct_option_index=None):
        if not options or not all(isinstance(x, str) and x for x in options): raise ValueError("options must be non-empty strings")
        data = {"chat_id": chat_id, "question": question, "options": options, "is_anonymous": is_anonymous, "allows_multiple_answers": allows_multiple_answers}
        if is_quiz:
            if correct_option_index is None or not 0 <= correct_option_index < len(options): raise ValueError("Invalid correct_option_index")
            data.update({"type": "Quiz", "correct_option_index": correct_option_index})
        return await self._post("sendPoll", data)
    async def location(self, chat_id, lat, lon): return await self._post("sendLocation", {"chat_id": chat_id, "latitude": str(lat), "longitude": str(lon)})
    async def contact(self, chat_id, phone, first, last=""):
        data = {"chat_id": chat_id, "phone_number": phone, "first_name": first}
        if last: data["last_name"] = last
        return await self._post("sendContact", data)
    async def set_keypad(self, chat_id, keyboard): return await self._post("editChatKeypad", {"chat_id": chat_id, "chat_keypad": keyboard.to_dict(), "chat_keypad_type": "New"})
    async def remove_keypad(self, chat_id): return await self._post("editChatKeypad", {"chat_id": chat_id, "chat_keypad_type": "Remove"})
    async def commands(self, cmds): return await self._post("setCommands", {"bot_commands": cmds})

    async def _dispatch_update(self, update):
        if not isinstance(update, dict): raise ValueError("Update must be an object")
        kind, chat_id = update.get("type"), update.get("chat_id")
        if kind == "NewMessage":
            raw = update.get("new_message")
            if not isinstance(raw, dict): raise ValueError("NewMessage has no message object")
            message = dict(raw)
            try: msg_time = int(message.get("time", 0))
            except (ValueError, TypeError): msg_time = 0
            if self.skip_old_messages and msg_time and msg_time <= self._start_time: return
            info = message.get("file")
            if isinstance(info, dict):
                name = str(info.get("file_name", "")).lower()
                kind_key = "photo" if name.endswith((".jpg", ".jpeg", ".png", ".gif", ".webp")) else "video" if name.endswith((".mp4", ".avi", ".mkv", ".mov")) else "audio" if name.endswith((".mp3", ".ogg", ".wav", ".m4a")) else "document"
                message[kind_key] = True; message["file_info"] = info
            message["chat_id"] = chat_id
            async def reply_func(reply_text, rid=message.get("message_id"), cid=chat_id): return await self.send(cid, reply_text, reply_to=rid)
            message["reply"] = reply_func
            handler = self._handlers.get("message")
            if handler: await handler(message)
            self._processed_count += 1
        elif kind == "UpdatedMessage":
            raw = update.get("updated_message")
            if isinstance(raw, dict):
                message = dict(raw); message["chat_id"] = chat_id
                handler = self._handlers.get("edited_message")
                if handler: await handler(message)

    async def _poll(self):
        self._running = True; self.logger.info("Polling started")
        while self._running:
            try:
                params = {"limit": 50}
                if self._offset: params["offset_id"] = self._offset
                result = await self._post("getUpdates", params)
                if result.get("status") != "OK": await asyncio.sleep(5); continue
                payload = result.get("data") or {}; updates = payload.get("updates") or []
                next_offset, succeeded = payload.get("next_offset_id"), True
                for update in updates:
                    try: await self._dispatch_update(update)
                    except asyncio.CancelledError: raise
                    except Exception as exc:
                        succeeded = False; self.logger.error(f"Update handler failed: {exc}"); break
                if succeeded and next_offset is not None and str(next_offset) != self._offset:
                    self._offset = str(next_offset); self._save_offset(self._offset)
                await asyncio.sleep(1)
            except asyncio.CancelledError: raise
            except Exception as exc: self.logger.error(f"Polling error: {exc}"); await asyncio.sleep(5)
        self.logger.info("Polling stopped")

    async def start(self, validate_token=True):
        if self._running: raise RuntimeError("Polling already running")
        if validate_token: await self.check_connection()
        await self._poll()
    async def stop(self): self._running = False
    async def close(self):
        await self.stop()
        tasks = list(self._auto_delete_tasks)
        for task in tasks: task.cancel()
        if tasks: await asyncio.gather(*tasks, return_exceptions=True)
        if self._owns_client and not self._client.is_closed: await self._client.aclose()
    async def __aenter__(self): return self
    async def __aexit__(self, exc_type, exc, tb): await self.close()
    def run(self):
        try: asyncio.get_running_loop()
        except RuntimeError:
            try: asyncio.run(self.start())
            except KeyboardInterrupt: self.logger.info("Bot interrupted")
            finally:
                if self._owns_client and not self._client.is_closed: asyncio.run(self.close())
        else: raise RuntimeError("Inside an event loop use: await bot.start()")
