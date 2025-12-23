from fastapi import FastAPI, Request, BackgroundTasks
from chat_logic import process_ai_message
from database import save_chat_log
import os
import requests
import uvicorn

app = FastAPI()

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
APP_PUBLIC_URL = os.environ.get("APP_PUBLIC_URL")

@app.get("/")
def home():
    return {"status": "MeeSaya Telegram Bot Active"}

@app.get("/set_webhook")
def set_webhook():
    """Helper endpoint to tell Telegram where to send messages."""
    if not TELEGRAM_BOT_TOKEN or not APP_PUBLIC_URL:
        return {"error": "Missing env vars: TELEGRAM_BOT_TOKEN or APP_PUBLIC_URL"}
    
    webhook_url = f"{APP_PUBLIC_URL}/webhook"
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook?url={webhook_url}"
    
    try:
        r = requests.get(telegram_url)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

@app.post("/webhook")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Handle incoming Telegram updates.
    Structure: {"update_id": 123, "message": {"chat": {"id": 123}, "text": "hello"}}
    """
    data = await request.json()
    
    # Check if this is a standard user message
    if "message" in data:
        message = data["message"]
        chat_id = message.get("chat", {}).get("id")
        user_text = message.get("text", "")
        
        if chat_id and user_text:
            # 1. Save User Log immediately (convert int ID to string for DB)
            save_chat_log(str(chat_id), "user", user_text)
            
            # 2. Process AI in background (returns 200 OK fast to Telegram to prevent timeouts)
            background_tasks.add_task(process_ai_message, chat_id, user_text)
            
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))