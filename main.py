from fastapi import FastAPI, Request, BackgroundTasks
from chat_logic import process_ai_message
from database import save_chat_log
import os
import requests
import uvicorn

app = FastAPI()

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
APP_PUBLIC_URL = os.environ.get("APP_PUBLIC_URL")

@app.on_event("startup")
async def startup_event():
    """
    Automatically set the Telegram webhook on startup.
    This ensures Telegram knows where to send messages after a deploy.
    """
    if not TELEGRAM_BOT_TOKEN or not APP_PUBLIC_URL:
        print("⚠️  Missing TELEGRAM_BOT_TOKEN or APP_PUBLIC_URL. Webhook not set.")
        return

    webhook_url = f"{APP_PUBLIC_URL}/webhook"
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook?url={webhook_url}"
    
    try:
        r = requests.get(telegram_url)
        print(f"🚀 Webhook setup response: {r.json()}")
    except Exception as e:
        print(f"❌ Failed to set webhook: {e}")

@app.get("/")
def home():
    return {"status": "MeeSaya Telegram Bot Active"}

@app.post("/webhook")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Handle incoming Telegram updates.
    """
    try:
        data = await request.json()
    except Exception:
        return {"status": "ignored", "reason": "invalid json"}
    
    if "message" in data:
        message = data["message"]
        chat_id = message.get("chat", {}).get("id")
        user_text = message.get("text", "")
        
        if chat_id and user_text:
            # 1. Save User Log (convert int ID to string for DB)
            save_chat_log(str(chat_id), "user", user_text)
            
            # 2. Process AI in background
            background_tasks.add_task(process_ai_message, chat_id, user_text)
            
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)