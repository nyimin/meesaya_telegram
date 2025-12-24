# MeeSaya (မီးဆရာ) - AI Solar Sales Agent (v2.1)

MeeSaya is a **Context-Aware AI Sales Consultant** for the Myanmar Solar Energy market. Unlike standard bots, MeeSaya uses **Async Architecture** and **RAG (Retrieval-Augmented Generation)** to access real-time market data, grid schedules, and technical knowledge in Burmese.

## 🚀 Key Capabilities (v2.1)

### 1. High-Performance Async Core
Built on **FastAPI + AsyncPG**, the bot can handle hundreds of concurrent users without freezing. It generates responses in parallel, ensuring a smooth experience even during high traffic.

### 2. RAG Knowledge Base
The bot understands the local context. It searches a dynamic Knowledge Base to answer questions like:
*   *"What is the load shedding schedule in Mandalay?"*
*   *"How do I fix Error 04 on my Growatt inverter?"*
*   *"Why is my battery draining so fast?"*

### 3. Intelligent Calculator ("The Sweet Spot")
Maps user requirements (Watts/Hours) to standard Myanmar market packages (Tier A-E) rather than theoretical sizes, ensuring availability and practicality.

### 4. Admin-Friendly Data Management
Inventory and Knowledge Base can be updated via a simple **CSV file**, acting as the single source of truth for the sales team.

---

## 🛠 Tech Stack

*   **Framework:** FastAPI (Async)
*   **AI Model:** Google Gemini 2.0 Flash Lite (via OpenRouter)
*   **Database:** PostgreSQL (AsyncPG + Alembic Migrations)
*   **Tools:** HTTX (Async HTTP), NumPy
*   **Platform:** Docker / Railway / Heroku

---

## 📂 Project Structure

```bash
nyimin-meesaya_telegram/
├── chat_logic.py     # The Brain: Async Agent workflow & RAG Logic
├── calculator.py     # The Logic: Async System Sizing & Tier Selection
├── database.py       # The Memory: AsyncPG Connection Pool & RAG Search
├── sync_knowledge.py # The Admin Tool: Syncs knowledge.csv to DB
├── knowledge.csv     # The Source: Editable Excel/CSV for facts
├── main.py           # The Interface: FastAPI Webhook
└── alembic/          # Database Migrations
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
    OPENROUTER_API_KEY=sk-...
    TELEGRAM_BOT_TOKEN=123:ABC...
    DATABASE_URL=postgresql://user:pass@host:5432/db
    APP_PUBLIC_URL=https://your-domain.com
    ```

3.  **Database Migration (First Run)**
    Use Alembic to create the schema safely.
    ```bash
    alembic upgrade head
    ```

4.  **Seed Data & Knowledge**
    Populate the `knowledge_base` and `products` from the CSV/Script.
    ```bash
    python seed_data.py       # Resets packages & inventory
    python sync_knowledge.py  # Updates RAG context from knowledge.csv
    ```

5.  **Run Server**
    ```bash
    uvicorn main:app --reload
    ```

---

## 🧠 Managing the Knowledge Base

To add new information (news, prices, error codes):
1.  Open `knowledge.csv`.
2.  Add a row: `Category, Content`.
    *   Example: `News, Electricity prices increased to 500 MMK/unit.`
3.  Run `python sync_knowledge.py`.
4.  The bot now "knows" this fact immediately.

---

## 🗺 Roadmap

### Phase 3: Lead Capture & CRM
- [ ] **Buying Intent Trigger:** Detect "How to buy?" and ask for phone number.
- [ ] **Admin Alerts:** Forward leads to sales team group chat.

### Phase 4: Multimedia & Vision
- [ ] **Photo Analysis:** Analyze user-uploaded meter/roof photos using Gemini Vision.
- [ ] **Voice Support:** Transcribe Burmese voice notes.