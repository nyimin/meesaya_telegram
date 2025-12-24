from database import get_db_connection

async def calculate_system(watts: int, hours: int, housing_type: str = "home"):
    # Convert to kW/kWh for comparison
    raw_kw = watts / 1000.0
    raw_energy_kwh = (watts * hours) / 1000.0

    match_found = None
    
    async with get_db_connection() as conn:
        
        if housing_type in ['apartment', 'condo', 'flat']:
            row = await conn.fetchrow("""
                SELECT name, inverter_kw, battery_kwh, est_price_low, description 
                FROM market_packages 
                WHERE is_portable = TRUE 
                AND inverter_kw >= $1
                ORDER BY est_price_low ASC LIMIT 1
            """, raw_kw)
            
            if row:
                match_found = {
                    "strategy": "PORTABLE",
                    "tier_name": row['name'],
                    "specs": f"{row['inverter_kw']}kW / {row['battery_kwh']}kWh",
                    "price_est": row['est_price_low'],
                    "desc": row['description']
                }

        if not match_found:
            tier_target = 'A'
            if raw_kw > 1.5 or raw_energy_kwh > 2.0:
                tier_target = 'B'
            if raw_kw > 3.5 or raw_energy_kwh > 5.0:
                tier_target = 'C'
            if raw_kw > 6.5:
                tier_target = 'D'

            row = await conn.fetchrow("""
                SELECT name, inverter_kw, battery_kwh, est_price_low, est_price_high, install_cost, description, system_voltage
                FROM market_packages 
                WHERE tier_code = $1
                LIMIT 1
            """, tier_target)
            
            if row:
                total_low = row['est_price_low'] + row['install_cost']
                total_high = row['est_price_high'] + row['install_cost']
                match_found = {
                    "strategy": "HOME_INSTALL",
                    "tier_name": row['name'],
                    "voltage": row['system_voltage'],
                    "specs": {
                        "inverter": f"{row['inverter_kw']}kW",
                        "battery": f"{row['battery_kwh']}kWh (LiFePO4)"
                    },
                    "price_range": f"{total_low:,} - {total_high:,} MMK",
                    "install_fee": f"{row['install_cost']:,} MMK",
                    "desc": row['description']
                }

    if not match_found:
        return {"error": "Requirements too high (Industrial). Contact admin."}
        
    return match_found