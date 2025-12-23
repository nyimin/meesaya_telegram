import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def init_db():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL not set.")
        return

    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    print("🔄 Resetting Database Schema (DROP & RECREATE)...")

    # Drop old tables
    tables_to_drop = [
        "products_inverters", 
        "products_batteries", 
        "products_solar_panels", 
        "products_commercial_bess", 
        "products_portables", 
        "vendors", 
        "ref_installation_costs", 
        "market_packages",
        "chat_history"
    ]
    
    for t in tables_to_drop:
        cur.execute(f"DROP TABLE IF EXISTS {t} CASCADE;")

    # Create Tables
    cur.execute("""
        CREATE TABLE chat_history (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(50),
            role VARCHAR(10),
            message_text TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cur.execute("""
        CREATE TABLE products_inverters (
            id SERIAL PRIMARY KEY,
            brand VARCHAR(50), model VARCHAR(100), 
            type VARCHAR(50), watts INT, system_voltage INT, 
            max_ac_charge_amps INT, 
            price_mmk INT, tier VARCHAR(20),
            notes TEXT
        );
    """)

    cur.execute("""
        CREATE TABLE products_batteries (
            id SERIAL PRIMARY KEY,
            brand VARCHAR(50), model VARCHAR(100), tech_type VARCHAR(20), 
            volts FLOAT, amp_hours INT, kwh FLOAT, 
            warranty_years INT, cell_grade VARCHAR(50),
            price_mmk INT, tier VARCHAR(20),
            notes TEXT
        );
    """)

    cur.execute("""
        CREATE TABLE products_solar_panels (
            id SERIAL PRIMARY KEY,
            brand VARCHAR(50), model VARCHAR(50), watts INT,
            type VARCHAR(50), price_mmk INT, warranty_years INT
        );
    """)

    cur.execute("""
        CREATE TABLE products_commercial_bess (
            id SERIAL PRIMARY KEY,
            brand VARCHAR(50), model VARCHAR(100),
            kwh FLOAT, voltage_type VARCHAR(20), 
            price_mmk INT, description TEXT
        );
    """)

    cur.execute("""
        CREATE TABLE products_portables (
            id SERIAL PRIMARY KEY,
            brand VARCHAR(50), model VARCHAR(50),
            watts INT, kwh FLOAT, price_mmk INT,
            description TEXT
        );
    """)

    cur.execute("""
        CREATE TABLE vendors (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            category VARCHAR(50), 
            specialty TEXT,
            known_brands TEXT
        );
    """)

    cur.execute("""
        CREATE TABLE ref_installation_costs (
            voltage_tier INT PRIMARY KEY,
            base_labor_mmk INT,      
            accessory_kit_mmk INT,   
            mounting_per_panel_mmk INT,
            cabinet_cost_mmk INT
        );
    """)

    cur.execute("""
        CREATE TABLE market_packages (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),              
            inverter_watts INT,
            battery_kwh FLOAT,
            system_voltage INT,
            total_price_mmk INT,            
            includes_panels BOOLEAN,
            description TEXT
        );
    """)

    print("📥 Seeding Comprehensive Market Survey Data (Q1 2025)...")

    # Seed Inverters
    cur.executemany("""
        INSERT INTO products_inverters (brand, model, type, watts, system_voltage, max_ac_charge_amps, price_mmk, tier, notes) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, [
        ('Must', 'PV1800 Budget', 'Off-Grid', 1000, 12, 20, 360000, 'Budget', 'Entry level'),
        ('Comfos', 'CF-1500', 'Off-Grid', 1500, 12, 30, 0, 'Budget', 'Vietnam made'),
        ('Shark Topsun', '12V Off-Grid', 'Off-Grid', 1500, 12, 30, 750000, 'Budget', 'Known for durability'),
        ('Dragon Power', '24V Standard', 'Off-Grid', 3500, 24, 60, 670000, 'Budget', 'Budget mid-range'),
        ('Felicity', 'IVEM3024', 'Hybrid', 3000, 24, 60, 950000, 'Standard', 'Reliable Hybrid'),
        ('Felicity', 'IVEM5048', 'Hybrid', 5000, 48, 80, 1300000, 'Standard', 'Entry 48V Hybrid'),
        ('Growatt', 'SPF 6000 ES Plus', 'Off-Grid', 6000, 48, 100, 1385000, 'Premium', 'Market Leader'),
        ('Shark Topsun', '48V Off-Grid', 'Off-Grid', 6500, 48, 100, 1490000, 'Standard', 'High power budget'),
        ('Deye', 'SUN-6K-SG03', 'Hybrid', 6000, 48, 120, 2400000, 'Premium', 'Top tier'),
        ('Shark Topsun', '12kW High Power', 'Off-Grid', 12000, 48, 150, 4900000, 'High Power', 'Max residential')
    ])

    # Seed Batteries
    cur.executemany("""
        INSERT INTO products_batteries (brand, model, tech_type, volts, amp_hours, kwh, warranty_years, cell_grade, price_mmk, tier, notes) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, [
        ('Shark Topsun', '12V 100Ah', 'LiFePO4', 12.8, 100, 1.28, 3, 'Standard', 880000, 'Budget', 'Replace Lead Acid'),
        ('Felicity', '24V 200Ah', 'LiFePO4', 25.6, 200, 5.12, 5, 'Grade A', 2800000, 'Standard', '24V Aircon systems'),
        ('Felicity', 'FLA 100Ah', 'LiFePO4', 51.2, 100, 5.12, 7, 'Grade A', 3000000, 'Standard', '7 Year Warranty'),
        ('Deye', 'RW-L5.1', 'LiFePO4', 51.2, 100, 5.12, 10, 'Grade A', 3750000, 'Premium', 'Premium compact'),
        ('Lvtopsun', 'G3 200Ah', 'LiFePO4', 51.2, 200, 10.24, 5, 'Grade A', 5100000, 'Standard', 'Reliable workhorse'),
        ('Felicity', 'LPBF 300Ah', 'LiFePO4', 51.2, 300, 15.36, 5, 'Grade A', 5150000, 'Standard', 'Good price'),
        ('Lvtopsun', 'G4 314Ah', 'LiFePO4', 51.2, 314, 16.0, 10, 'EVE Grade A', 6800000, 'Premium', 'Market Best Seller'),
        ('Bicodi', '314Ah', 'LiFePO4', 51.2, 314, 16.0, 10, 'Grade A', 7300000, 'Premium', 'High end')
    ])

    # Seed Install Costs
    cur.executemany("""
        INSERT INTO ref_installation_costs (voltage_tier, base_labor_mmk, accessory_kit_mmk, mounting_per_panel_mmk, cabinet_cost_mmk) 
        VALUES (%s, %s, %s, %s, %s)
    """, [
        (12, 50000, 250000, 40000, 0),
        (24, 150000, 450000, 45000, 100000), 
        (48, 300000, 700000, 50000, 250000) 
    ])

    # Seed Packages
    cur.executemany("""
        INSERT INTO market_packages (name, inverter_watts, battery_kwh, system_voltage, total_price_mmk, includes_panels, description) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, [
        ('Entry 12V Lighting Set', 1500, 1.28, 12, 1500000, False, 'Shark Topsun 1.5kW + 100Ah Lithium.'),
        ('Mid-Range 24V Fridge Set', 3500, 2.56, 24, 3600000, False, '3.5kW Inverter + 24V 100Ah.'),
        ('Standard 6kW Home (Bundled)', 6000, 15.3, 48, 7400000, False, 'Growatt 6kW + Felicity/Lvtopsun 300Ah. Best Value.'),
        ('Yangon Condo All-in-One', 5000, 5.0, 48, 6200000, False, 'Growatt Cabinet style. 5kWh. fits in living room.')
    ])

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Database Fully Hydrated with Comprehensive Survey Data.")

if __name__ == "__main__":
    init_db()