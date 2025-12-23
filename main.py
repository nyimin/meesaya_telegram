from fastapi import FastAPI, Request, BackgroundTasks
from chat_logic import process_ai_message
import os
import requests
import uvicorn

app = FastAPI()

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
APP_PUBLIC_URL = os.environ.get("APP_PUBLIC_URL")

@app.on_event("startup")
async def startup_event():
    if not TELEGRAM_BOT_TOKEN or not APP_PUBLIC_URL:
        return
    webhook_url = f"{APP_PUBLIC_URL}/webhook"
    requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook?url={webhook_url}")

@app.get("/")
def home():
    return {"status": "MeeSaya Bot v2.0 (Sales Agent) Active"}

@app.post("/webhook")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        data = await request.json()
    except:
        return {"status": "error"}
    
    if "message" in data:
        msg = data["message"]
        chat_id = msg.get("chat", {}).get("id")
        text = msg.get("text", "")
        
        if chat_id and text:
            # Process in background to avoid Telegram timeout
            background_tasks.add_task(process_ai_message, chat_id, text)
            
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)