from database import get_db_connection, init_pool

def init_db():
    init_pool()
    print("🔄 Initializing Database Schema...")
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            
            # --- CRITICAL FIX: DROP OLD TABLES TO ENSURE NEW COLUMNS EXIST ---
            print("⚠️ Dropping old tables to enforce new schema...")
            cur.execute("DROP TABLE IF EXISTS market_packages CASCADE;")
            cur.execute("DROP TABLE IF EXISTS products_inventory CASCADE;")
            
            # 1. CREATE TABLES
            cur.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(50),
                    role VARCHAR(20),
                    message_text TEXT,
                    timestamp TIMESTAMP DEFAULT NOW()
                );
            """)

            cur.execute("""
                CREATE TABLE market_packages (
                    id SERIAL PRIMARY KEY,
                    tier_code VARCHAR(10),
                    name VARCHAR(100),
                    system_voltage INT,
                    inverter_kw FLOAT,
                    battery_kwh FLOAT,
                    est_price_low INT,           
                    est_price_high INT,          
                    install_cost INT,
                    description TEXT,
                    is_portable BOOLEAN DEFAULT FALSE
                );
            """)

            cur.execute("""
                CREATE TABLE products_inventory (
                    id SERIAL PRIMARY KEY,
                    category VARCHAR(50),
                    brand VARCHAR(50),
                    model VARCHAR(50),
                    specs VARCHAR(50),
                    price INT,
                    warranty_years INT,
                    tags TEXT
                );
            """)

            # 2. SEED DATA
            packages = [
                ('A', 'Entry Level (12V)', 12, 1.5, 1.2, 1500000, 2400000, 300000, 'Lights, WiFi, Laptop', False),
                ('B', 'Mid-Range (24V)', 24, 3.5, 4.8, 3600000, 4300000, 600000, 'Small Fridge, Lighting, Limited Aircon', False),
                ('C', 'Standard Home (48V)', 48, 6.0, 16.0, 6600000, 7200000, 800000, '1HP Aircon (10-15hrs), Fridge, Pump', False),
                ('D', 'Premium Solar (Off-Grid)', 48, 8.0, 16.0, 14500000, 16000000, 1000000, 'Full Off-Grid, Jinko Panels included', False),
                ('E', 'EcoFlow Delta 2', 48, 1.8, 1.0, 2550000, 2550000, 0, 'Apartment Backup', True),
                ('E', 'EcoFlow Delta Pro', 48, 3.6, 3.6, 6600000, 6600000, 0, 'Condo Whole Unit', True)
            ]
            cur.executemany("""
                INSERT INTO market_packages (tier_code, name, system_voltage, inverter_kw, battery_kwh, est_price_low, est_price_high, install_cost, description, is_portable)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, packages)

            inventory = [
                ('Inverter', 'Growatt', 'SPF 6000 ES Plus', '6kW 48V', 1380000, 2, 'Market Leader'),
                ('Inverter', 'Deye', 'Hybrid', '6kW 48V', 5900000, 5, 'Premium Bundle'),
                ('Battery', 'Lvtopsun', 'G4', '314Ah 51.2V', 6800000, 10, 'Best Seller, 10Yr Warranty'),
                ('Panel', 'Jinko', 'Tiger Neo', '590W N-Type', 300000, 30, 'Tier 1 Brand'),
            ]
            cur.executemany("""
                INSERT INTO products_inventory (category, brand, model, specs, price, warranty_years, tags)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, inventory)

            conn.commit()
            print("✅ Database Reset & Seeded Successfully.")

if __name__ == "__main__":
    init_db()