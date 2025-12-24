from fastapi import FastAPI, Request, BackgroundTasks
from chat_logic import process_ai_message
from database import init_pool, close_pool
import os
import httpx
import uvicorn
import asyncio

app = FastAPI()

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
APP_PUBLIC_URL = os.environ.get("APP_PUBLIC_URL")

@app.on_event("startup")
async def startup_event():
    # 1. Init DB Pool
    await init_pool()
    
    # 2. Set Webhook
    if TELEGRAM_BOT_TOKEN and APP_PUBLIC_URL:
        webhook_url = f"{APP_PUBLIC_URL}/webhook"
        # We can use httpx here too for consistency
        async with httpx.AsyncClient() as client:
            try:
                await client.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook?url={webhook_url}")
                print(f"✅ Webhook set to {webhook_url}")
            except Exception as e:
                print(f"❌ Webhook Error: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    await close_pool()

@app.get("/")
def home():
    return {"status": "MeeSaya Bot v2.1 (Async + RAG) Active"}

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
            # Add async task to background
            background_tasks.add_task(process_ai_message, chat_id, text)
            
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    # 'workers' is for multiprocess, but for async usually 1 worker is enough for IO bound unless CPU bound.
    # reload=True is good for dev.
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)