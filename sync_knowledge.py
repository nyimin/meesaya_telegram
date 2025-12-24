import csv
import asyncio
from database import get_db_connection

CSV_FILE = "knowledge.csv"

async def sync_knowledge():
    print(f"🔄 Syncing Knowledge Base from {CSV_FILE}...")
    
    data_to_insert = []
    
    # 1. Read CSV
    try:
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['Category'] and row['Content']:
                    data_to_insert.append((row['Category'], row['Content']))
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return

    if not data_to_insert:
        print("⚠️ CSV is empty or invalid.")
        return

    # 2. Update Database (Truncate & Insert)
    try:
        async with get_db_connection() as conn:
            # We use a transaction block
            async with conn.transaction():
                # A. Clear old data
                await conn.execute("TRUNCATE TABLE knowledge_base RESTART IDENTITY;")
                print("🗑️  Cleared old Knowledge Base data.")
                
                # B. Insert new data
                await conn.executemany("""
                    INSERT INTO knowledge_base (category, content)
                    VALUES ($1, $2)
                """, data_to_insert)
                
            print(f"✅ Automatically imported {len(data_to_insert)} items from CSV.")
            
    except Exception as e:
        print(f"❌ Database Error: {e}")

if __name__ == "__main__":
    asyncio.run(sync_knowledge())
