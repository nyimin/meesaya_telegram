import os
import json
import requests
from database import save_chat_log, get_recent_history, search_products_db
from calculator import calculate_system

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# --- PERSONA DEFINITION (Q4 2025 Market) ---
SYSTEM_PROMPT = """
You are MeeSaya (မီးဆရာ), a professional Solar Consultant in Myanmar.
Speak ONLY in Burmese (Burmese Language).

**MARKET KNOWLEDGE:**
1. **Standards:** 314Ah LiFePO4 (Lvtopsun G4/Deye) with 10-Year Warranty is the gold standard.
2. **Inverters:** Growatt 6kW is the market leader.
3. **Packages:**
   - 3.5kW (24V) for small homes.
   - 6kW (48V) for Aircon usage (Standard).

**INSTRUCTIONS:**
- If user gives watts/appliances, output JSON: `{"tool": "calculate", "watts": 2000, "hours": 4, "housing": "home"}`. (Use "condo" if mentioned).
- If user asks for specific product price/stock, output JSON: `{"tool": "search", "query": "Growatt"}`.
- If user asks for 2kW, explain that 2kW is not standard and recommend 3.5kW for better value.
"""

def send_message(chat_id, text):
    """Safe sender with Markdown fix"""
    clean_text = text.replace("**", "*") # Fix telegram formatting
    payload = {"chat_id": chat_id, "text": clean_text, "parse_mode": "Markdown"}
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)

def call_llm(messages, temperature=0.3):
    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
            json={
                "model": "google/gemini-2.0-flash-001", # Or 1.5-flash
                "messages": messages,
                "temperature": temperature
            },
            timeout=20
        )
        return r.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"LLM Error: {e}")
        return None

def process_ai_message(chat_id, user_text):
    chat_id = str(chat_id)
    
    # 1. Get History & Context
    history = get_recent_history(chat_id)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history + [{"role": "user", "content": user_text}]
    
    # 2. First Pass (Decision)
    ai_response = call_llm(messages)
    if not ai_response:
        return

    # 3. Tool Execution Check
    tool_output_text = ""
    tool_data = None
    
    if "{" in ai_response and "tool" in ai_response:
        try:
            # Extract JSON cleanly
            json_str = ai_response[ai_response.find("{"):ai_response.rfind("}")+1]
            tool_data = json.loads(json_str)
            
            if tool_data['tool'] == 'calculate':
                # Run Calculator
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
                    tool_output_text = (
                        f"RECOMMENDATION: {res['tier_name']} (Portable)\n"
                        f"SPECS: {res['specs']}\n"
                        f"PRICE: {res['price_est']:,} MMK\n"
                        f"NOTE: Best for apartments (No wiring)."
                    )

            elif tool_data['tool'] == 'search':
                # Run Search
                items = search_products_db(tool_data['query'])
                tool_output_text = "INVENTORY SEARCH RESULTS:\n" + "\n".join(items)

        except Exception as e:
            print(f"Tool Parsing Error: {e}")

    # 4. Second Pass (If Tool was used, get final explanation)
    if tool_output_text:
        # Feed the tool result back to the AI
        messages.append({"role": "assistant", "content": json.dumps(tool_data)})
        messages.append({"role": "system", "content": f"TOOL RESULT: {tool_output_text}. Now write the final helpful response in Burmese."})
        final_response = call_llm(messages, temperature=0.6)
    else:
        final_response = ai_response

    # 5. Save & Send
    save_chat_log(chat_id, "user", user_text)
    save_chat_log(chat_id, "assistant", final_response)
    send_message(chat_id, final_response)