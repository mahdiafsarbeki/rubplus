"""
Webhook support for RubPlus
"""

import json
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, Response
import uvicorn


class RubPlusWebhook:
    """
    کلاس مدیریت Webhook برای ربات روبیکا
    """
    
    def __init__(self, bot, secret_token: Optional[str] = None):
        self.bot = bot
        self.secret_token = secret_token
        self.app = FastAPI()
        self._setup_routes()
    
    def _setup_routes(self):
        """تنظیم مسیرهای FastAPI"""
        
        @self.app.post("/webhook")
        async def webhook_handler(request: Request):
            # بررسی توکن امنیتی
            if self.secret_token:
                token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
                if token != self.secret_token:
                    return Response(status_code=403)
            
            # دریافت داده
            data = await request.json()
            
            # پردازش آپدیت
            await self._process_update(data)
            
            return {"status": "ok"}
        
        @self.app.get("/")
        async def root():
            return {"status": "RubPlus Webhook is running", "version": "1.3.0"}
    
    async def _process_update(self, update: Dict[str, Any]):
        """پردازش آپدیت دریافتی از وب‌هوک"""
        
        if update.get("type") == "NewMessage":
            message = update.get("new_message", {})
            chat_id = update.get("chat_id")
            message["chat_id"] = chat_id
            
            async def reply_func(text, rid=message.get("message_id"), cid=chat_id):
                return await self.bot.send_message(cid, text, rid)
            
            message["reply"] = reply_func
            
            if "message" in self.bot._handlers:
                await self.bot._handlers["message"](message)
    
    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """اجرای سرور Webhook"""
        print(f"\n🚀 Webhook server starting on http://{host}:{port}")
        print(f"📡 Webhook URL: http://{host}:{port}/webhook")
        print(f"🔧 Set this URL in @BotFather on Rubika\n")
        uvicorn.run(self.app, host=host, port=port)