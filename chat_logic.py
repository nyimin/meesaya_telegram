import os
import json
import requests
from database import save_chat_log, get_recent_history
from calculator import calculate_system

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# --- 1. UPDATED PERSONA (CONCISE) ---
PERSONA_DEFINITION = """
You are "MeeSaya" (မီးဆရာ), a practical Myanmar Energy Consultant. 

**Your Style:**
- **CONCISE & DIRECT:** Do not write long paragraphs. Use bullet points.
- **No Fluff:** Skip long greetings like "Mingalarpar". Go straight to the answer.
- **Male Persona:** End sentences with "Khimvyar" (ခင်ဗျာ).
- **Tone:** Professional, short, and to the point.

**Knowledge:**
- Grid is bad. Recommend "Fast Charging" (High Amps).
- 314Ah LiFePO4 is the standard.
"""

SYSTEM_INSTRUCTIONS = """
**OUTPUT RULES:**
1. **NO ENGLISH TRANSLATIONS.** Speak ONLY Burmese.
2. **FORMATTING:** Use single asterisks (*) for bullet points. Do NOT use double asterisks (**).
3. **TOOL USAGE:** 
   If user mentions appliances/watts, output JSON:
   {"tool": "calculate", "watts": 500, "hours": 4, "no_solar": false}
   If "Condo/Apartment", set "no_solar": true.
"""

FINAL_SYSTEM_PROMPT = PERSONA_DEFINITION + "\n" + SYSTEM_INSTRUCTIONS

def send_typing_action(chat_id):
    """Shows 'typing...' status in Telegram"""
    try:
        requests.post(f"{TELEGRAM_API_URL}/sendChatAction", json={"chat_id": chat_id, "action": "typing"})
    except:
        pass

def send_telegram_message(chat_id, text):
    """Sends message with Markdown formatting to fix asterisks"""
    url = f"{TELEGRAM_API_URL}/sendMessage"
    
    # Telegram Markdown V1 uses *bold*, Gemini often sends **bold**
    # We replace ** with * to prevent formatting errors
    formatted_text = text.replace("**", "*")

    payload = {
        "chat_id": chat_id,
        "text": formatted_text,
        "parse_mode": "Markdown" 
    }
    
    try:
        r = requests.post(url, json=payload)
        # Fallback: If formatting fails, send plain text
        if r.status_code != 200:
            print(f"Markdown error ({r.status_code}), sending plain text.")
            payload.pop("parse_mode")
            payload["text"] = text
            requests.post(url, json=payload)
    except Exception as e:
        print(f"Connection error: {e}")

def process_ai_message(sender_id, user_text):
    sender_id_str = str(sender_id)
    
    # 1. Show Typing Status (Makes bot feel faster)
    send_typing_action(sender_id)

    # 2. Get Context
    history = get_recent_history(sender_id_str, limit=6)
    messages = [{"role": "system", "content": FINAL_SYSTEM_PROMPT}] + history + [{"role": "user", "content": user_text}]

    # 3. Call LLM
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
            json={
                "model": "google/gemini-2.5-flash", 
                "messages": messages,
                "temperature": 0.3 # Low temperature = More concise/factual
            }
        )
        result = response.json()
        
        if 'choices' not in result:
            reply_text = "System Error ဖြစ်နေလို့ ခဏနေမှ ပြန်မေးပေးပါခင်ဗျာ။"
        else:
            ai_content = result['choices'][0]['message']['content']
            reply_text = ai_content 
            
            # 4. Check for Calculator Tool
            if "{" in ai_content and "calculate" in ai_content:
                try:
                    start = ai_content.find("{")
                    end = ai_content.rfind("}") + 1
                    data = json.loads(ai_content[start:end])
                    
                    if data.get("tool") == "calculate":
                        calc_result = calculate_system(data['watts'], data['hours'], data.get('no_solar', False))
                        specs = calc_result['system_specs']
                        ests = calc_result['estimates']
                        
                        # SHORT & CLEAN QUOTE
                        reply_text = (
                            f"*တွက်ချက်မှုရလဒ် (Estimate)*\n\n"
                            f"🔌 *System:* {specs['system_voltage']}V\n"
                            f"⚡ *Inverter:* {specs['inverter']} ({specs['inverter_size_kw']}kW)\n"
                            f"🔋 *Battery:* {specs['battery_qty']} x {specs['battery_model']}\n"
                        )
                        if specs['solar_panels_count'] > 0:
                            reply_text += f"☀️ *Solar:* {specs['solar_panels_count']} ချပ်\n"
                        
                        reply_text += f"\n💰 *ခန့်မှန်းကုန်ကျစရိတ်:* {ests['total_estimated']:,} ကျပ်"
                        
                except Exception as e:
                    print(f"Tool error: {e}")
                    reply_text = "တွက်ချက်မှု Error ဖြစ်သွားပါတယ်။ Watts ပမာဏ အတိအကျပြန်ပြောပေးပါခင်ဗျာ။"
        
        save_chat_log(sender_id_str, "assistant", reply_text)
        send_telegram_message(sender_id, reply_text)

    except Exception as e:
        print(f"Critical Error: {e}")
        send_telegram_message(sender_id, "System Error ပါခင်ဗျာ။")