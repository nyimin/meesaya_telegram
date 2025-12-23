import os
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager

DB_URL = os.environ.get("DATABASE_URL")

# Singleton Connection Pool
connection_pool = None

def init_pool():
    global connection_pool
    if not connection_pool and DB_URL:
        try:
            # sslmode='require' is standard for cloud databases (Railway/Heroku)
            connection_pool = psycopg2.pool.SimpleConnectionPool(1, 10, DB_URL, sslmode='require')
            print("✅ Database connection pool created")
        except Exception as e:
            print(f"❌ DB Connection Error: {e}")

@contextmanager
def get_db_connection():
    if not connection_pool:
        init_pool()
    
    if not connection_pool:
        raise Exception("Database not available")
        
    conn = connection_pool.getconn()
    try:
        yield conn
    finally:
        connection_pool.putconn(conn)

def save_chat_log(user_id, role, message):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO chat_history (user_id, role, message_text) VALUES (%s, %s, %s)",
                    (str(user_id), role, message)
                )
            conn.commit()
    except Exception as e:
        print(f"Log Error: {e}")

def get_recent_history(user_id, limit=6):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT role, message_text FROM chat_history
                    WHERE user_id = %s
                    ORDER BY id DESC LIMIT %s 
                """, (str(user_id), limit))
                rows = cur.fetchall()
        # Return oldest first for the LLM
        history = [{"role": ("user" if r[0]=="user" else "assistant"), "content": r[1]} for r in rows[::-1]]
        return history
    except Exception:
        return []

def search_products_db(query_text):
    """
    RAG Tool: Fuzzy search for products in the inventory.
    """
    results = []
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Search across Brand, Model, Category, or Tags
                # Matches if query is inside any of these fields
                sql = """
                    SELECT category, brand, model, specs, price, tags 
                    FROM products_inventory 
                    WHERE brand ILIKE %s OR model ILIKE %s OR category ILIKE %s
                    LIMIT 4
                """
                search_term = f"%{query_text}%"
                cur.execute(sql, (search_term, search_term, search_term))
                
                rows = cur.fetchall()
                if not rows:
                    return ["No specific products found in inventory."]
                    
                for r in rows:
                    # Format: "Battery: Lvtopsun G4 (314Ah) - 6,800,000 MMK [Best Seller]"
                    results.append(f"{r[0]}: {r[1]} {r[2]} ({r[3]}) - {r[4]:,} MMK [{r[5]}]")
                    
    except Exception as e:
        return [f"Search Error: {e}"]
        
    return results