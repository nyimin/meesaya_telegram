================================================
**FILE: README.md**
================================================

# MeeSaya (မီးဆရာ) - AI Solar Sales Agent (v2.0)

MeeSaya is a **Context-Aware AI Sales Consultant** for the Myanmar Solar Energy market. Unlike standard bots that perform simple math, MeeSaya uses **Q4 2025 Market Data** to guide users toward standard commercial packages ("Tiers"), explains technical concepts in Burmese, and searches real-time inventory.

## 🚀 Key Capabilities (v2.0)

### 1. Intelligent Upselling ("The Binning Logic")
The bot does not recommend theoretical system sizes (e.g., "2.2kW"). Instead, it maps user requirements to standard market tiers to ensure availability and better value.
*   **Tier A:** Entry Level (12V) - *Lights & WiFi*
*   **Tier B:** Mid-Range (24V) - *Fridge & Lights*
*   **Tier C:** Standard Home (48V) - *1HP Aircon "Sweet Spot"* (Market Leader)
*   **Tier D:** Premium Off-Grid - *Full Home Backup*
*   **Tier E:** Portable/Condo - *EcoFlow & All-in-Ones* (For apartments)

### 2. Inventory RAG (Retrieval-Augmented Generation)
Users can ask about specific products, and the bot performs a fuzzy search on the `products_inventory` database.
*   *User:* "Do you have Jinko panels?"
*   *Bot:* "Yes, we stock **Jinko Tiger Neo (590W)** for **300,000 MMK**."

### 3. Transparent Pricing Engine
Calculates the **"Walk-Away Price"** by combining:
*   Base Hardware Cost (Inverter + Battery)
*   Installation Fee (Labor, Cabling, Breakers, Trunking)

### 4. Agent Workflow
Uses a two-step logic flow:
1.  **Thinking:** LLM analyzes intent $\to$ Selects Tool (Calculator vs. Search).
2.  **Execution:** Python executes tool $\to$ Returns raw data.
3.  **Response:** LLM interprets data $\to$ Generates natural Burmese explanation.

---

## 🛠 Tech Stack

*   **Framework:** FastAPI (Python 3.9+)
*   **AI Engine:** Google Gemini 2.0 Flash (via OpenRouter)
*   **Database:** PostgreSQL (with Connection Pooling)
*   **Platform:** Docker / Railway / Heroku

---

## 📂 Project Structure

```bash
nyimin-meesaya_telegram/
├── chat_logic.py    # The Brain: Handles Agent workflow & Prompt Engineering
├── calculator.py    # The Logic: Maps Watts/Hours -> Market Tiers (A-E)
├── database.py      # The Memory: Connection Pooling & RAG Search functions
├── init_db.py       # The Seeder: Resets DB with Q4 2025 Market Data
├── main.py          # The Interface: FastAPI Webhook for Telegram
└── Dockerfile       # Deployment config
```

---

## ⚡ Setup & Deployment

1.  **Clone & Install**
    ```bash
    git clone <repo_url>
    pip install -r requirements.txt
    ```

2.  **Environment Variables (`.env`)**
    ```env
    OPENROUTER_API_KEY=sk-or-v1-...
    TELEGRAM_BOT_TOKEN=123456:ABC...
    DATABASE_URL=postgresql://user:pass@host:5432/db
    APP_PUBLIC_URL=https://your-app.railway.app
    ```

3.  **Initialize Database**
    Run this script **once** to create tables and seed the Q4 2025 inventory/packages.
    ```bash
    python init_db.py
    ```

4.  **Run Server**
    ```bash
    uvicorn main:app --reload
    ```

---

## 🗺 Roadmap (Next Round Updates)

This section outlines the planned features to transition from **Consultation** to **Closing Sales**.

### Phase 3: Lead Capture & CRM (High Priority)
- [ ] **Buying Intent Detection:** Trigger a specific flow when user asks "Where is your shop?" or "How to order?".
- [ ] **Contact Form:** Ask for Phone Number/Location within the chat.
- [ ] **Admin Alerts:** Forward "Hot Leads" (User + Calculated System) immediately to the Admin's personal Telegram.

### Phase 4: Admin Dashboard
- [ ] **No-Code Updates:** Build a simple Streamlit/Admin UI so non-coders can update `products_inventory` prices without touching SQL.
- [ ] **Analytics:** Track which Tiers are most requested (e.g., "70% of users want Tier C").

### Phase 5: Multimedia & Vision
- [ ] **Photo Analysis:** Allow users to send a photo of their **Electricity Meter** or **Roof**, and use Gemini Vision to estimate installation complexity.
- [ ] **Voice Support:** Accept voice notes in Burmese and reply with text (using Whisper).

### Phase 6: Dynamic PDF Quoting
- [ ] **Instant Quotation:** Generate a professional PDF Proforma Invoice based on the calculated Tier and send it directly in the chat.