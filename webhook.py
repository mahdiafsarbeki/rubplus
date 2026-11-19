"""FastAPI webhook adapter for RubPlus.

Install the optional server dependencies with: pip install "rubplus[webhook]".
"""

from typing import Any, Dict, Optional

try:
    from fastapi import FastAPI, Header, HTTPException, Request
    from fastapi.responses import JSONResponse
except ImportError as exc:  # Keep importing the core SDK possible without FastAPI.
    FastAPI = None
    _FASTAPI_IMPORT_ERROR = exc
else:
    _FASTAPI_IMPORT_ERROR = None


class RubPlusWebhook:
    """Expose a RubPlus bot through a FastAPI application."""

    def __init__(
        self,
        bot,
        secret_token: Optional[str] = None,
        secret_header: str = "X-Rubika-Bot-Api-Secret-Token",
    ):
        if FastAPI is None:
            raise ImportError(
                'Webhook support requires FastAPI. Install it with: pip install "rubplus[webhook]"'
            ) from _FASTAPI_IMPORT_ERROR
        if not hasattr(bot, "send") or not hasattr(bot, "_handlers"):
            raise TypeError("bot must be a RubPlus instance or provide send() and _handlers")
        self.bot = bot
        self.secret_token = secret_token
        self.secret_header = secret_header
        self.app = FastAPI(title="RubPlus Webhook")
        self._setup_routes()

    def _setup_routes(self) -> None:
        @self.app.post("/webhook")
        async def webhook_handler(request: Request):
            if self.secret_token:
                supplied = request.headers.get(self.secret_header)
                if supplied is None or supplied != self.secret_token:
                    raise HTTPException(status_code=403, detail="Invalid webhook secret")
            try:
                update = await request.json()
            except Exception as exc:
                raise HTTPException(status_code=400, detail="Request body must be valid JSON") from exc
            if not isinstance(update, dict):
                raise HTTPException(status_code=400, detail="Update must be a JSON object")
            await self._process_update(update)
            return JSONResponse({"status": "ok"})

        @self.app.get("/")
        async def root():
            return {"status": "ok", "service": "RubPlus Webhook"}

    async def _process_update(self, update: Dict[str, Any]) -> None:
        update_type = update.get("type")
        if update_type == "NewMessage":
            message = update.get("new_message")
            if not isinstance(message, dict):
                return
            message = dict(message)
            chat_id = update.get("chat_id")
            message["chat_id"] = chat_id

            async def reply_func(text: str, rid=message.get("message_id"), cid=chat_id):
                return await self.bot.send(cid, text, reply_to=rid)

            message["reply"] = reply_func
            handler = self.bot._handlers.get("message")
            if handler is not None:
                await handler(message)

        elif update_type == "UpdatedMessage":
            message = update.get("updated_message")
            if isinstance(message, dict):
                message = dict(message)
                message["chat_id"] = update.get("chat_id")
                handler = self.bot._handlers.get("edited_message")
                if handler is not None:
                    await handler(message)

    def run(self, host: str = "127.0.0.1", port: int = 8000) -> None:
        try:
            import uvicorn
        except ImportError as exc:
            raise ImportError(
                'Running the webhook server requires Uvicorn. Install it with: pip install "rubplus[webhook]"'
            ) from exc
        uvicorn.run(self.app, host=host, port=port)


# Backward-compatible public name used by older examples.
Webhook = RubPlusWebhook
