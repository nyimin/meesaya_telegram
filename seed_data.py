import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.environ.get("DATABASE_URL")

def seed_data():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()

    print("🌱 Seeding Data...")

    # 1. MARKET PACKAGES
    # Clear existing to avoid duplicates if re-run (ignoring IDs)
    cur.execute("TRUNCATE TABLE market_packages RESTART IDENTITY;")
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

    # 2. PRODUCT INVENTORY
    cur.execute("TRUNCATE TABLE products_inventory RESTART IDENTITY;")
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

    # 3. KNOWLEDGE BASE (RAG)
    cur.execute("TRUNCATE TABLE knowledge_base RESTART IDENTITY;")
    kb_data = [
        ("Myanmar Grid Condition", "Currently, Yangon and Mandalay face rotational load shedding. Typical schedule is 4-hours ON and 4-hours OFF. Industrial zones may have different schedules."),
        ("Troubleshooting Inverter", "Error 04 on Growatt usually means Low Battery. Solution: Check battery voltage, ensure grid charging is enabled, or reduce load."),
        ("Troubleshooting Inverter", "Error 08 on Growatt means Bus Voltage High. Solution: Restart inverter. If persistent, check if solar panels are over-voltage."),
        ("Solar Market", "The price of Solar Panels in Myanmar has dropped significantly in late 2024. 550W panels are now around 280,000 MMK."),
        ("Battery Maintenance", "For Lead-Acid (Tubular) batteries, check distilled water levels every month. Do not let it dry out."),
        ("Voltage Fluctuation", "Mee La (Grid) voltage in Myanmar can fluctuate between 160V and 260V. Always use a Voltage Stabilizer (Servo) before the Inverter input."),
    ]
    cur.executemany("""
        INSERT INTO knowledge_base (category, content)
        VALUES (%s, %s)
    """, kb_data)

    conn.commit()
    conn.close()
    print("✅ Database Seeded Successfully (Packages, Inventory, Knowledge Base).")

if __name__ == "__main__":
    seed_data()
