import os
import json
import requests
from database import save_chat_log, get_recent_history, search_products_db
from calculator import calculate_system

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

SYSTEM_PROMPT = """
You are MeeSaya (မီးဆရာ), a professional Solar Consultant.
Speak ONLY in Burmese.

**INSTRUCTIONS:**
- If user gives watts/appliances, output JSON: `{"tool": "calculate", "watts": 2000, "hours": 4, "housing": "home"}`.
- If user asks for product price/stock, output JSON: `{"tool": "search", "query": "Growatt"}`.
- Otherwise, reply normally.
"""

def send_chat_action(chat_id, action="typing"):
    """Shows 'typing...' status at top of Telegram"""
    try:
        requests.post(f"{TELEGRAM_API_URL}/sendChatAction", json={"chat_id": chat_id, "action": action})
    except: pass

def send_message(chat_id, text):
    clean_text = text.replace("**", "*")
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": clean_text, "parse_mode": "Markdown"})

def call_llm(messages, temperature=0.3):
    try:
        # Use stable model version 1.5
        model = "google/gemini-2.0-flash-exp:free" 
        
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": model, 
                "messages": messages,
                "temperature": temperature
            },
            timeout=30 
        )
        
        # DEBUG: Print exact error if not 200 OK
        if r.status_code != 200:
            print(f"❌ OpenRouter API Error ({r.status_code}): {r.text}")
            return None

        result = r.json()
        
        if 'choices' not in result:
            print(f"❌ Invalid LLM Response: {result}")
            return None
            
        return result['choices'][0]['message']['content']
        
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return None

def process_ai_message(chat_id, user_text):
    chat_id = str(chat_id)
    
    # 1. Immediate Feedback
    send_chat_action(chat_id, "typing")
    
    history = get_recent_history(chat_id)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history + [{"role": "user", "content": user_text}]
    
    # 2. First Pass (Decision)
    ai_response = call_llm(messages)
    
    if not ai_response:
        # Fallback message so user isn't ignored
        send_message(chat_id, "System Error (AI Model). Please try again later.")
        return

    tool_output_text = ""
    tool_data = None
    
    # 3. Check for Tool Usage
    if "{" in ai_response and "tool" in ai_response:
        try:
            # Tell user we are working on it
            send_message(chat_id, "🔍 တွက်ချက်နေပါသည်... (Calculating...)")
            send_chat_action(chat_id, "typing")

            json_str = ai_response[ai_response.find("{"):ai_response.rfind("}")+1]
            tool_data = json.loads(json_str)
            
            if tool_data['tool'] == 'calculate':
                res = calculate_system(tool_data['watts'], tool_data['hours'], tool_data.get('housing', 'home'))
                if "error" in res:
                    tool_output_text = f"Error: {res['error']}"
                elif res['strategy'] == 'HOME_INSTALL':
                    tool_output_text = (
                        f"RECOMMENDATION: {res['tier_name']}\n"
                        f"SPECS: {res['specs']['inverter']} + {res['specs']['battery']}\n"
                        f"VOLTAGE: {res['voltage']}V System\n"
                        f"ESTIMATED PRICE: {res['price_range']} (Includes {res['install_fee']} Installation)\n"
                        f"CAPABILITY: {res['desc']}"
                    )
                elif res['strategy'] == 'PORTABLE':
                    tool_output_text = f"RECOMMENDATION: {res['tier_name']} (Portable)\nPRICE: {res['price_est']:,} MMK"

            elif tool_data['tool'] == 'search':
                items = search_products_db(tool_data['query'])
                tool_output_text = "INVENTORY SEARCH RESULTS:\n" + "\n".join(items)

        except Exception as e:
            print(f"Tool Error: {e}")

    # 4. Final Pass (Explanation)
    if tool_output_text:
        messages.append({"role": "assistant", "content": json.dumps(tool_data)})
        messages.append({"role": "system", "content": f"TOOL RESULT: {tool_output_text}. Now write the final helpful response in Burmese."})
        final_response = call_llm(messages, temperature=0.6)
        
        # Fallback if second call fails
        if not final_response:
            final_response = "Calculation done, but I couldn't translate the result. \n" + tool_output_text
    else:
        final_response = ai_response

    # 5. Send Final Response
    save_chat_log(chat_id, "user", user_text)
    save_chat_log(chat_id, "assistant", final_response)
    send_message(chat_id, final_response)