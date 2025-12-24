import os
import json
import httpx
import asyncio
from database import save_chat_log, get_recent_history, search_products_db, search_knowledge_base
from calculator import calculate_system

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# System Prompt now includes a placeholder for dynamic context if needed, 
# but usually we append context as a separate message.
SYSTEM_PROMPT_BASE = """
You are MeeSaya (မီးဆရာ), a professional Solar Consultant.
Speak ONLY in Burmese.
Tone: Friendly, Expert (Male Engineer Persona).

**INSTRUCTIONS:**
- Use the provided CONTEXT to answer market/troubleshooting questions.
- If user gives watts/appliances, output JSON: `{"tool": "calculate", "watts": 2000, "hours": 4, "housing": "home"}`.
- If user asks for product price/stock, output JSON: `{"tool": "search", "query": "Growatt"}`.
- Otherwise, reply normally.
"""

async def send_chat_action(chat_id, action="typing"):
    """Async chat action"""
    try:
        async with httpx.AsyncClient() as client:
            await client.post(f"{TELEGRAM_API_URL}/sendChatAction", json={"chat_id": chat_id, "action": action})
    except: pass

async def send_message(chat_id, text):
    """Async message sender"""
    clean_text = text.replace("**", "*")
    async with httpx.AsyncClient() as client:
        await client.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": clean_text, "parse_mode": "Markdown"})

async def call_llm(messages, temperature=0.3):
    try:
        # Using Gemini 2.0 Flash Lite Preview as requested
        model = "google/gemini-2.5-flash-lite" 
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model, 
                    "messages": messages,
                    "temperature": temperature
                }
            )
            
            if r.status_code != 200:
                print(f"❌ OpenRouter API Error ({r.status_code}): {r.text}")
                return None

            result = r.json()
            
            if 'choices' not in result:
                return None
                
            return result['choices'][0]['message']['content']
        
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return None

async def process_ai_message(chat_id, user_text):
    chat_id = str(chat_id)
    
    # 1. Immediate Feedback
    await send_chat_action(chat_id, "typing")
    
    # 2. Retrieve Data (Async Parallel)
    history_task = asyncio.create_task(get_recent_history(chat_id))
    rag_task = asyncio.create_task(search_knowledge_base(user_text))
    
    history = await history_task
    rag_context = await rag_task
    
    # 3. Construct Contextual Prompt
    context_msg = ""
    if rag_context:
        context_msg = f"CONTEXT (FROM KNOWLEDGE BASE):\n{rag_context}\n\nUse this context to answer if relevant."
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT_BASE}] + history
    
    if context_msg:
         messages.append({"role": "system", "content": context_msg})
         
    messages.append({"role": "user", "content": user_text})
    
    # 4. First Pass (Decision)
    ai_response = await call_llm(messages)
    
    if not ai_response:
        await send_message(chat_id, "System Error (AI Model). Please try again later.")
        return

    tool_output_text = ""
    tool_data = None
    
    # 5. Check for Tool Usage
    if "{" in ai_response and "tool" in ai_response:
        try:
            # Clean json string if mixed with text
            start_idx = ai_response.find("{")
            end_idx = ai_response.rfind("}")
            json_str = ai_response[start_idx:end_idx+1]
            
            tool_data = json.loads(json_str)
            
            if tool_data['tool'] == 'calculate':
                await send_message(chat_id, "🔍 တွက်ချက်နေပါသည်... (Calculating...)")
                await send_chat_action(chat_id, "typing")
                
                res = await calculate_system(tool_data['watts'], tool_data['hours'], tool_data.get('housing', 'home'))
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
                items = await search_products_db(tool_data['query'])
                tool_output_text = "INVENTORY SEARCH RESULTS:\n" + "\n".join(items)

        except Exception as e:
            print(f"Tool Error: {e}")

    # 6. Final Pass (Explanation)
    if tool_output_text:
        messages.append({"role": "assistant", "content": json.dumps(tool_data)})
        messages.append({"role": "system", "content": f"TOOL RESULT: {tool_output_text}. Now write the final helpful response in Burmese."})
        final_response = await call_llm(messages, temperature=0.6)
        
        if not final_response:
            final_response = "Calculation done.\n" + tool_output_text
    else:
        final_response = ai_response

    # 7. Logging & Response
    await save_chat_log(chat_id, "user", user_text)
    await save_chat_log(chat_id, "assistant", final_response)
    await send_message(chat_id, final_response)