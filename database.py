import os
from contextlib import asynccontextmanager
import asyncpg
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.environ.get("DATABASE_URL")

# Singleton Connection Pool
pool = None

async def init_pool():
    global pool
    if not DB_URL:
        print("❌ Error: DATABASE_URL is missing.")
        return

    if not pool:
        try:
            # Create a connection pool with asyncpg
            # We don't need sslmode='require' for local if standard postgres used, 
            # but usually for cloud URLs it's implied in the string or needed explicitly.
            # asyncpg usually parses the DSN.
            pool = await asyncpg.create_pool(DB_URL)
            print("✅ Async Database Pool Created")
        except Exception as e:
            print(f"❌ DB Pool Error: {e}")

async def close_pool():
    global pool
    if pool:
        await pool.close()
        print("🛑 Database Pool Closed")

@asynccontextmanager
async def get_db_connection():
    """
    Async context manager for getting a connection from the pool.
    Usage:
        async with get_db_connection() as conn:
            rows = await conn.fetch("SELECT * FROM ...")
    """
    if not pool:
        await init_pool()
    
    if not pool:
        raise Exception("Database pool not initialized")

    async with pool.acquire() as conn:
        yield conn

async def save_chat_log(user_id, role, message):
    """Async log saver"""
    try:
        async with get_db_connection() as conn:
            await conn.execute(
                "INSERT INTO chat_history (user_id, role, message_text) VALUES ($1, $2, $3)",
                str(user_id), role, message
            )
    except Exception as e:
        print(f"Log Error: {e}")

async def get_recent_history(user_id, limit=6):
    """Async history fetcher"""
    try:
        async with get_db_connection() as conn:
            rows = await conn.fetch("""
                SELECT role, message_text FROM chat_history
                WHERE user_id = $1
                ORDER BY id DESC LIMIT $2 
            """, str(user_id), limit)
        # asyncpg returns Record objects, we access them like dicts or tuples
        # Order is DESC, so we reverse it to ASC for the LLM
        return [{"role": ("user" if r['role']=="user" else "assistant"), "content": r['message_text']} for r in rows[::-1]]
    except Exception as e:
        print(f"History Error: {e}")
        return []

async def search_products_db(query_text):
    """Async product search"""
    results = []
    try:
        async with get_db_connection() as conn:
            # Simple ILIKE search used previously
            search_term = f"%{query_text}%"
            rows = await conn.fetch("""
                SELECT category, brand, model, specs, price, tags 
                FROM products_inventory 
                WHERE brand ILIKE $1 OR model ILIKE $2 OR category ILIKE $3
                LIMIT 4
            """, search_term, search_term, search_term)
            
            if not rows: return ["No specific products found."]
            for r in rows:
                results.append(f"{r['category']}: {r['brand']} {r['model']} ({r['specs']}) - {r['price']:,} MMK [{r['tags']}]")
    except Exception as e:
        return [f"Search Error: {e}"]
    return results

async def search_knowledge_base(query_text):
    """
    RAG Search: Find relevant context from the knowledge_base table.
    Uses basic keyword matching.
    """
    try:
        async with get_db_connection() as conn:
            # 1. Try Exact Phrase Match first
            search_term = f"%{query_text}%"
            rows = await conn.fetch("""
                SELECT content, category FROM knowledge_base
                WHERE content ILIKE $1 OR category ILIKE $1
                LIMIT 2
            """, search_term)
            
            # 2. If no results, try splitting words (find rows containing ANY word)
            if not rows and " " in query_text:
                words = [w for w in query_text.split() if len(w) > 3] # Filter small words
                if words:
                    # Construct dynamic query for multiple OR conditions
                    # "content ILIKE $1 OR content ILIKE $2 ..."
                    conditions = " OR ".join([f"content ILIKE ${i+1}" for i in range(len(words))])
                    args = [f"%{w}%" for w in words]
                    
                    query = f"SELECT content, category FROM knowledge_base WHERE {conditions} LIMIT 2"
                    rows = await conn.fetch(query, *args)
            
            if rows:
                return "\n".join([f"[Context: {r['category']}] {r['content']}" for r in rows])
            return ""
            
    except Exception as e:
        print(f"RAG Error: {e}")
        return ""