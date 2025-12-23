from database import get_db_connection

def calculate_system(watts: int, hours: int, housing_type: str = "home"):
    """
    Matches user requirements to Standard Market Packages (Tiers A-E).
    """
    
    # Convert to kW/kWh for comparison
    raw_kw = watts / 1000.0
    raw_energy_kwh = (watts * hours) / 1000.0

    match_found = None
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            
            # STRATEGY 1: PORTABLE (For Apartments/Condos)
            if housing_type in ['apartment', 'condo', 'flat']:
                cur.execute("""
                    SELECT name, inverter_kw, battery_kwh, est_price_low, description 
                    FROM market_packages 
                    WHERE is_portable = TRUE 
                    AND inverter_kw >= %s
                    ORDER BY est_price_low ASC LIMIT 1
                """, (raw_kw,))
                
                row = cur.fetchone()
                if row:
                    match_found = {
                        "strategy": "PORTABLE",
                        "tier_name": row[0],
                        "specs": f"{row[1]}kW / {row[2]}kWh",
                        "price_est": row[3],
                        "desc": row[4]
                    }

            # STRATEGY 2: HOME INSTALL (Tiers A, B, C)
            if not match_found:
                # Assign Tier based on Logic
                tier_target = 'A'
                if raw_kw > 1.5 or raw_energy_kwh > 2.0:
                    tier_target = 'B' # 3.5kW
                if raw_kw > 3.5 or raw_energy_kwh > 5.0:
                    tier_target = 'C' # 6kW (Sweet Spot)
                if raw_kw > 6.5:
                    tier_target = 'D' # Premium

                cur.execute("""
                    SELECT name, inverter_kw, battery_kwh, est_price_low, est_price_high, install_cost, description, system_voltage
                    FROM market_packages 
                    WHERE tier_code = %s
                    LIMIT 1
                """, (tier_target,))
                
                row = cur.fetchone()
                if row:
                    # Calculate "Walk Away" Price (Hardware + Install)
                    total_low = row[3] + row[5]
                    total_high = row[4] + row[5]
                    
                    match_found = {
                        "strategy": "HOME_INSTALL",
                        "tier_name": row[0],
                        "voltage": row[7],
                        "specs": {
                            "inverter": f"{row[1]}kW",
                            "battery": f"{row[2]}kWh (LiFePO4)"
                        },
                        "price_range": f"{total_low:,} - {total_high:,} MMK",
                        "install_fee": f"{row[5]:,} MMK",
                        "desc": row[6]
                    }

    if not match_found:
        return {"error": "Requirements too high (Industrial). Contact admin."}
        
    return match_found